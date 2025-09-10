#!/usr/bin/env python3
"""
Test scraper with different websites to find one that works
"""

import os
# Set the API key directly for testing
os.environ['GEMINI_API_KEY'] = 'AIzaSyAcKGVrpgDg5JVP8sY7d-8I32t0HfQJgVg'

from web_scraper import WebScraper

def test_multiple_sites():
    """Test scraping on multiple websites"""
    
    test_sites = [
        "https://httpbin.org/html",  # Simple test site
        "https://example.com",       # Basic example site
        "https://httpbin.org/",      # Another simple site
        "https://www.goodwins.co.nz" # The original site
    ]
    
    scraper = WebScraper()
    
    for site in test_sites:
        print(f"\n{'='*60}")
        print(f"Testing: {site}")
        print(f"{'='*60}")
        
        try:
            scraped_data = scraper.scrape_website(site)
            print(f"✅ Successfully scraped {len(scraped_data)} pages from {site}")
            
            if scraped_data:
                for i, page in enumerate(scraped_data[:2]):  # Show first 2 pages
                    print(f"  Page {i+1}: {page['title']}")
                    print(f"    URL: {page['url']}")
                    print(f"    Content length: {len(page.get('content', ''))}")
        except Exception as e:
            print(f"❌ Failed to scrape {site}: {e}")

if __name__ == "__main__":
    test_multiple_sites()
