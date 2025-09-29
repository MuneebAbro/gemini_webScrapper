#!/usr/bin/env python3
"""
Example usage of the Web Scraper Knowledge Base Generator
"""

import json
import os
from web_scraper import WebScraper
from llama_processor import LlamaProcessor
from knowledge_base_formatter import KnowledgeBaseFormatter

def example_scrape_small_site():
    """Example: Scrape a small website without Llama processing"""
    print("Example 1: Scraping without Llama processing")
    print("-" * 50)
    
    # Initialize scraper
    scraper = WebScraper()
    
    # Scrape a small site (you can replace with any URL)
    url = "https://httpbin.org/html"  # Simple test page
    scraped_data = scraper.scrape_website(url)
    
    print(f"Scraped {len(scraped_data)} pages")
    
    # Create basic knowledge base without Llama
    formatter = KnowledgeBaseFormatter()
    
    # Convert to basic processed format
    processed_data = []
    for page in scraped_data:
        processed_data.append({
            'url': page['url'],
            'title': page['title'],
            'summary': page.get('content', '')[:500],
            'key_topics': ['web scraping', 'example'],
            'faq_questions': [{
                'question': f"What is {page['title']}?",
                'answer': page.get('content', '')[:300]
            }],
            'important_facts': [page.get('content', '')[:200]],
            'keywords': ['example', 'test'],
            'content_type': 'other',
            'relevance_score': 0.5,
            'processed_at': page.get('scraped_at', ''),
            'processing_method': 'basic'
        })
    
    # Create knowledge base
    knowledge_base = formatter.create_knowledge_base_structure(processed_data, url)
    
    # Save to file
    output_file = formatter.save_knowledge_base(knowledge_base, "example_kb.json")
    print(f"Knowledge base saved to: {output_file}")
    
    return knowledge_base

def example_with_llama():
    """Example: Scrape with Llama processing (requires API key)"""
    print("\nExample 2: Scraping with Llama processing")
    print("-" * 50)
    
    # Check if API key is available
    from config import Config
    if not Config.GEMINI_API_KEY:
        print("LLAMA_API_KEY not found. Skipping Llama example.")
        print("Set your API key in .env file to use this example.")
        return None
    
    try:
        # Initialize components
        scraper = WebScraper()
        processor = LlamaProcessor()
        formatter = KnowledgeBaseFormatter()
        
        # Scrape a simple page
        url = "https://httpbin.org/html"
        scraped_data = scraper.scrape_website(url)
        
        print(f"Scraped {len(scraped_data)} pages")
        
        # Process with Llama
        processed_data = processor.batch_process_pages(scraped_data)
        
        # Create knowledge base
        knowledge_base = formatter.create_knowledge_base_structure(processed_data, url)
        
        # Save to file
        output_file = formatter.save_knowledge_base(knowledge_base, "example_llama_kb.json")
        print(f"Knowledge base with Llama processing saved to: {output_file}")
        
        return knowledge_base
        
    except Exception as e:
        print(f"Error with Llama processing: {e}")
        return None

def display_knowledge_base_summary(kb):
    """Display a summary of the knowledge base"""
    if not kb:
        return
        
    print("\nKnowledge Base Summary:")
    print("-" * 30)
    
    metadata = kb.get('metadata', {})
    print(f"Website: {metadata.get('website_url', 'N/A')}")
    print(f"Total pages: {metadata.get('total_pages', 0)}")
    print(f"Total FAQs: {metadata.get('total_faqs', 0)}")
    print(f"Total keywords: {metadata.get('total_keywords', 0)}")
    
    # Show content types
    content_types = metadata.get('content_types', {})
    if content_types:
        print("Content types:")
        for ctype, count in content_types.items():
            print(f"  - {ctype}: {count}")
    
    # Show some FAQ questions
    faq_section = kb.get('faq_section', [])
    if faq_section:
        print(f"\nSample FAQ questions:")
        for i, faq in enumerate(faq_section[:3]):  # Show first 3
            print(f"  {i+1}. {faq.get('question', 'N/A')}")
            print(f"     Answer: {faq.get('answer', 'N/A')[:100]}...")

if __name__ == "__main__":
    print("Web Scraper Knowledge Base Generator - Examples")
    print("=" * 60)
    
    # Example 1: Basic scraping
    kb1 = example_scrape_small_site()
    display_knowledge_base_summary(kb1)
    
    # Example 2: With Llama (if API key available)
    kb2 = example_with_llama()
    if kb2:
        display_knowledge_base_summary(kb2)
    
    print("\nExamples completed!")
    print("Check the 'knowledge_base' directory for output files.")
