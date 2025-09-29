#!/usr/bin/env python3
"""
Web Scraper Knowledge Base Generator

This script scrapes a website and creates a knowledge base in JSON format
suitable for automated chatbots using Llama AI for content processing.
"""

import argparse
import sys
import os
import logging
from typing import Optional
from tqdm import tqdm

from web_scraper import WebScraper
from llama_processor import LlamaProcessor
from knowledge_base_formatter import KnowledgeBaseFormatter
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_url(url: str) -> bool:
    """Validate if the provided URL is valid"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import requests
        import bs4
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install dependencies with: pip install -r requirements.txt")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Web Scraper Knowledge Base Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://example.com
  python main.py https://example.com --max-pages 20 --output my_kb.json
  python main.py https://example.com --no-llama --delay 2.0
        """
    )
    
    parser.add_argument('url', help='Website URL to scrape')
    parser.add_argument('--max-pages', type=int, default=Config.MAX_PAGES,
                       help=f'Maximum number of pages to scrape (default: {Config.MAX_PAGES})')
    parser.add_argument('--delay', type=float, default=Config.DELAY_BETWEEN_REQUESTS,
                       help=f'Delay between requests in seconds (default: {Config.DELAY_BETWEEN_REQUESTS})')
    parser.add_argument('--output', type=str, default=Config.JSON_FILENAME,
                       help=f'Output JSON filename (default: {Config.JSON_FILENAME})')
    parser.add_argument('--output-dir', type=str, default=Config.OUTPUT_DIR,
                       help=f'Output directory (default: {Config.OUTPUT_DIR})')
    parser.add_argument('--no-llama', action='store_true',
                       help='Skip Llama processing (faster but less structured output)')
    parser.add_argument('--min-content', type=int, default=Config.MIN_CONTENT_LENGTH,
                       help=f'Minimum content length to include (default: {Config.MIN_CONTENT_LENGTH})')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Validate URL
    if not validate_url(args.url):
        logger.error(f"Invalid URL: {args.url}")
        sys.exit(1)
    
    # Check Llama API key if not using --no-llama
    if not args.no_llama and not Config.LLAMA_API_KEY:
        logger.error("LLAMA_API_KEY not found in environment variables")
        logger.error("Please set your Llama API key or use --no-llama flag")
        logger.error("You can set it by creating a .env file with: LLAMA_API_KEY=your_key_here")
        sys.exit(1)
    
    try:
        logger.info("=" * 60)
        logger.info("Web Scraper Knowledge Base Generator")
        logger.info("=" * 60)
        logger.info(f"Target URL: {args.url}")
        logger.info(f"Max pages: {args.max_pages}")
        logger.info(f"Delay between requests: {args.delay}s")
        logger.info(f"Output directory: {args.output_dir}")
        logger.info(f"Output file: {args.output}")
        logger.info(f"Llama processing: {'Disabled' if args.no_llama else 'Enabled'}")
        logger.info("=" * 60)
        
        # Update config with command line arguments
        Config.MAX_PAGES = args.max_pages
        Config.DELAY_BETWEEN_REQUESTS = args.delay
        Config.OUTPUT_DIR = args.output_dir
        Config.JSON_FILENAME = args.output
        Config.MIN_CONTENT_LENGTH = args.min_content
        
        # Step 1: Scrape the website
        logger.info("Step 1: Starting web scraping...")
        scraper = WebScraper()
        scraped_data = scraper.scrape_website(args.url)
        
        if not scraped_data:
            logger.error("No data was scraped. Please check the URL and try again.")
            sys.exit(1)
        
        logger.info(f"Successfully scraped {len(scraped_data)} pages")
        
        # Step 2: Process with Llama (if enabled)
        if not args.no_llama:
            logger.info("Step 2: Processing content with Llama AI...")
            processor = LlamaProcessor()
            processed_data = processor.batch_process_pages(scraped_data)
        else:
            logger.info("Step 2: Skipping Llama processing...")
            # Convert scraped data to basic processed format
            processed_data = []
            for page in scraped_data:
                processed_data.append({
                    'url': page['url'],
                    'title': page['title'],
                    'summary': page.get('content', '')[:500] + "..." if len(page.get('content', '')) > 500 else page.get('content', ''),
                    'key_topics': [],
                    'faq_questions': [{
                        'question': f"What is {page['title']}?",
                        'answer': page.get('content', '')[:300] + "..." if len(page.get('content', '')) > 300 else page.get('content', '')
                    }],
                    'important_facts': [page.get('content', '')[:200] + "..." if len(page.get('content', '')) > 200 else page.get('content', '')],
                    'keywords': [],
                    'content_type': 'other',
                    'relevance_score': 0.5,
                    'processed_at': page.get('scraped_at', ''),
                    'processing_method': 'basic'
                })
        
        # Step 3: Format into knowledge base
        logger.info("Step 3: Creating knowledge base structure...")
        formatter = KnowledgeBaseFormatter()
        knowledge_base = formatter.create_knowledge_base_structure(processed_data, args.url)
        
        # Step 4: Save knowledge base
        logger.info("Step 4: Saving knowledge base...")
        kb_filepath = formatter.save_knowledge_base(knowledge_base, args.output)
        
        # Step 5: Create chatbot-ready format
        logger.info("Step 5: Creating chatbot-ready format...")
        chatbot_data = formatter.create_chatbot_ready_format(knowledge_base)
        chatbot_filepath = formatter.save_chatbot_format(chatbot_data, "chatbot_data.json")
        
        # Summary
        logger.info("=" * 60)
        logger.info("SCRAPING COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"Total pages scraped: {len(scraped_data)}")
        logger.info(f"Total FAQ questions: {len(chatbot_data['training_data'])}")
        logger.info(f"Knowledge base saved to: {kb_filepath}")
        logger.info(f"Chatbot data saved to: {chatbot_filepath}")
        logger.info("=" * 60)
        
        # Show some statistics
        if knowledge_base.get('metadata'):
            metadata = knowledge_base['metadata']
            logger.info("Statistics:")
            logger.info(f"  - Content types: {metadata.get('content_types', {})}")
            logger.info(f"  - Total keywords: {metadata.get('total_keywords', 0)}")
            logger.info(f"  - Total FAQs: {metadata.get('total_faqs', 0)}")
        
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
