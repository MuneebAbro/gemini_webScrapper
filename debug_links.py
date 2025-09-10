#!/usr/bin/env python3
"""
Debug script to see what links are being found
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def debug_website_links(url):
    """Debug what links are found on a website"""
    print(f"Debugging links for: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            print(f"Total links found: {len(all_links)}")
            
            internal_links = []
            external_links = []
            
            base_domain = urlparse(url).netloc
            
            for link in all_links[:10]:  # Show first 10 links
                href = link['href']
                absolute_url = urljoin(url, href)
                parsed_url = urlparse(absolute_url)
                
                print(f"  Link: {href} -> {absolute_url}")
                print(f"    Domain: {parsed_url.netloc}")
                print(f"    Text: {link.get_text().strip()[:50]}")
                
                if parsed_url.netloc == base_domain:
                    internal_links.append(absolute_url)
                else:
                    external_links.append(absolute_url)
            
            print(f"\nInternal links: {len(internal_links)}")
            print(f"External links: {len(external_links)}")
            
            # Check if page has substantial content
            text_content = soup.get_text()
            print(f"Page text length: {len(text_content)}")
            print(f"Page title: {soup.find('title').get_text() if soup.find('title') else 'No title'}")
            
            return internal_links
            
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    test_sites = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://www.goodwins.co.nz"
    ]
    
    for site in test_sites:
        print(f"\n{'='*60}")
        debug_website_links(site)
        print(f"{'='*60}")
