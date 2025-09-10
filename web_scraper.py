import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import logging
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        # Enhanced headers to bypass basic bot detection
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        # Robust retry strategy to handle transient network/server issues
        retry_strategy = Retry(
            total=5,
            connect=5,
            read=5,
            status=5,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_domain)
            
            # Check if URL has valid scheme and netloc
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
                
            # Check if URL belongs to the same domain
            if parsed_url.netloc != parsed_base.netloc:
                return False
                
            # Skip certain file types
            skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.zip', '.doc', '.docx'}
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip URLs with fragments (anchor links)
            if parsed_url.fragment:
                return False
                
            return True
        except Exception:
            return False
    
    def get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        try:
            logger.info(f"Fetching: {url}")
            
            # Add referer header for the request
            headers = {'Referer': url, 'Connection': 'close'}
            # Split timeout: (connect_timeout, read_timeout)
            response = self.session.get(
                url,
                headers=headers,
                timeout=(10, 25),
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check if content is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url}")
                return None
            
            # Check for Cloudflare or bot blocking
            content_text = response.text.lower()
            if 'cloudflare' in content_text and ('checking your browser' in content_text or 'please wait' in content_text):
                logger.warning(f"Cloudflare protection detected for {url}")
                # Try to extract what we can from the page
                soup = BeautifulSoup(response.content, 'lxml')
                # Look for any actual content that might be available
                if len(soup.get_text().strip()) < 100:
                    logger.warning(f"Insufficient content due to Cloudflare protection: {url}")
                    return None
                    
            soup = BeautifulSoup(response.content, 'lxml')
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    def extract_text_content(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meaningful text content from a page"""
        if not soup:
            return {}
            
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Extract main heading
        main_heading = ""
        h1_tag = soup.find('h1')
        if h1_tag:
            main_heading = h1_tag.get_text().strip()
        
        # Extract meta description
        meta_description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_description = meta_desc.get('content', '').strip()
        
        # Extract all headings
        headings = []
        for i in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{i}'):
                heading_text = heading.get_text().strip()
                if heading_text:
                    headings.append({
                        'level': i,
                        'text': heading_text
                    })
        
        # Extract paragraphs and meaningful text
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > Config.MIN_CONTENT_LENGTH:
                paragraphs.append(text)
        
        # Extract list items
        list_items = []
        for ul in soup.find_all(['ul', 'ol']):
            for li in ul.find_all('li'):
                text = li.get_text().strip()
                if len(text) > 20:  # Minimum length for list items
                    list_items.append(text)
        
        # Extract links with their text
        links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text().strip()
            if link_text and len(link_text) > 3:
                links.append({
                    'text': link_text,
                    'url': link['href']
                })
        
        # Get all text content
        all_text = soup.get_text()
        # Clean up the text
        all_text = re.sub(r'\s+', ' ', all_text).strip()
        
        return {
            'title': title,
            'main_heading': main_heading,
            'meta_description': meta_description,
            'headings': headings,
            'paragraphs': paragraphs,
            'list_items': list_items,
            'links': links,
            'all_text': all_text
        }
    
    def find_internal_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find all internal links on a page"""
        if not soup:
            return []
            
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            if self.is_valid_url(absolute_url, base_url):
                # Remove fragments and query parameters for deduplication
                clean_url = urlparse(absolute_url)._replace(fragment='', query='').geturl()
                if clean_url not in self.visited_urls:
                    links.append(clean_url)
        
        return list(set(links))  # Remove duplicates
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape a single page and return structured data"""
        soup = self.get_page_content(url)
        if not soup:
            return None
            
        content = self.extract_text_content(soup)
        internal_links = self.find_internal_links(soup, url)
        
        # Only include pages with substantial content
        content_length = len(content.get('all_text', ''))
        if content_length < Config.MIN_CONTENT_LENGTH:
            logger.info(f"Skipping page with insufficient content ({content_length} chars): {url}")
            return None
        
        page_data = {
            'url': url,
            'title': content.get('title', ''),
            'main_heading': content.get('main_heading', ''),
            'meta_description': content.get('meta_description', ''),
            'headings': content.get('headings', []),
            'paragraphs': content.get('paragraphs', []),
            'list_items': content.get('list_items', []),
            'links': content.get('links', []),
            'content': content.get('all_text', ''),
            'internal_links': internal_links,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return page_data
    
    def scrape_website(self, start_url: str) -> List[Dict]:
        """Scrape an entire website starting from a given URL"""
        logger.info(f"Starting to scrape website: {start_url}")
        
        urls_to_visit = [start_url]
        self.visited_urls = set()  # Reset visited URLs
        
        while urls_to_visit and len(self.scraped_data) < Config.MAX_PAGES:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            
            # Scrape the current page
            page_data = self.scrape_page(current_url)
            
            if page_data:
                self.scraped_data.append(page_data)
                
                # Add new internal links to the queue
                for link in page_data.get('internal_links', []):
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
                
                logger.info(f"Scraped page {len(self.scraped_data)}: {page_data['title']}")
            else:
                logger.warning(f"Failed to scrape page: {current_url}")
            
            # Add delay between requests
            time.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        logger.info(f"Scraping completed. Total pages scraped: {len(self.scraped_data)}")
        return self.scraped_data
