#!/usr/bin/env python3
"""
Test script to debug scraping issues
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import os

# Set the API key directly for testing
os.environ['GEMINI_API_KEY'] = 'AIzaSyAcKGVrpgDg5JVP8sY7d-8I32t0HfQJgVg'

def test_website_access(url):
    """Test if we can access the website"""
    print(f"Testing access to: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Connection': 'close'
    }
    
    try:
        session = requests.Session()
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
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(url, headers=headers, timeout=(10, 25), allow_redirects=True)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Try to parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')
            title = soup.find('title')
            print(f"Page Title: {title.get_text() if title else 'No title found'}")
            
            # Check for common blocking indicators
            if 'cloudflare' in response.text.lower():
                print("WARN Cloudflare protection detected")
            if 'access denied' in response.text.lower():
                print("WARN Access denied message detected")
            if 'bot' in response.text.lower() and 'blocked' in response.text.lower():
                print("WARN Bot blocking detected")
                
            return True
        else:
            print(f"ERROR HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR Request failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR Unexpected error: {e}")
        return False

def test_scraper_imports():
    """Test if all scraper components can be imported"""
    print("Testing imports...")
    
    try:
        from web_scraper import WebScraper
        print("OK WebScraper imported successfully")
        
        from llama_processor import LlamaProcessor
        print("OK LlamaProcessor imported successfully")
        
        from knowledge_base_formatter import KnowledgeBaseFormatter
        print("OK KnowledgeBaseFormatter imported successfully")
        
        from config import Config
        print("OK Config imported successfully")
        
        return True
    except ImportError as e:
        print(f"ERROR Import error: {e}")
        return False

def test_simple_scrape(url):
    """Test a simple scrape without Gemini processing"""
    print(f"\nTesting simple scrape of: {url}")
    
    try:
        from web_scraper import WebScraper
        
        scraper = WebScraper()
        scraped_data = scraper.scrape_website(url)
        
        print(f"Pages scraped: {len(scraped_data)}")
        
        if scraped_data:
            for i, page in enumerate(scraped_data[:3]):  # Show first 3 pages
                print(f"  Page {i+1}: {page['title']} - {page['url']}")
        else:
            print("No pages were scraped")
            
        return len(scraped_data) > 0
        
    except Exception as e:
        print(f"ERROR Scraping error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Web Scraper Debug Test")
    print("=" * 40)
    
    # Test imports
    if not test_scraper_imports():
        print("ERROR Import test failed")
        exit(1)
    
    # Test website access
    test_url = "https://www.pristinecarpetcare.com.au/"
    if not test_website_access(test_url):
        print("ERROR Website access test failed")
        exit(1)
    
    # Test simple scraping
    if not test_simple_scrape(test_url):
        print("ERROR Simple scraping test failed")
        exit(1)
    
    print("\nOK All tests passed! The scraper should work now.")
