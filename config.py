import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Llama API Configuration
    LLAMA_API_KEY = os.getenv('LLAMA_API_KEY')
    
    # Scraping Configuration
    MAX_PAGES = int(os.getenv('MAX_PAGES', 50))
    DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', 1.0))
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Output Configuration
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'knowledge_base')
    JSON_FILENAME = os.getenv('JSON_FILENAME', 'knowledge_base.json')
    
    # Content Processing
    MIN_CONTENT_LENGTH = int(os.getenv('MIN_CONTENT_LENGTH', 100))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5000))
    
    # Llama Model Configuration
    LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'llama-3.3-70b-versatile')
    LLAMA_API_URL = os.getenv('LLAMA_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1000))
    
    # Rate Limiting Configuration (30 requests per minute = 2 seconds between requests)
    LLAMA_RATE_LIMIT_DELAY = float(os.getenv('LLAMA_RATE_LIMIT_DELAY', 2.0))
