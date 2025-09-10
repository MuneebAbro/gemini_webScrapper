#!/usr/bin/env python3
"""
Setup script for Web Scraper Knowledge Base Generator
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Scraping Configuration
MAX_PAGES=50
DELAY_BETWEEN_REQUESTS=1.0
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36

# Output Configuration
OUTPUT_DIR=knowledge_base
JSON_FILENAME=knowledge_base.json

# Content Processing
MIN_CONTENT_LENGTH=100
MAX_CONTENT_LENGTH=5000

# Gemini Model Configuration
GEMINI_MODEL=gemini-1.5-flash
MAX_TOKENS=1000
""")
        print("✓ .env file created")
        print("⚠️  Please edit .env file and add your Gemini API key")
    else:
        print("✓ .env file already exists")

def create_output_directory():
    """Create output directory"""
    output_dir = "knowledge_base"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Created output directory: {output_dir}")
    else:
        print(f"✓ Output directory already exists: {output_dir}")

def test_installation():
    """Test if the installation works"""
    print("Testing installation...")
    try:
        # Test imports
        import requests
        import bs4
        import google.generativeai
        from dotenv import load_dotenv
        
        print("✓ All required packages imported successfully")
        
        # Test config loading
        load_dotenv()
        from config import Config
        print("✓ Configuration loaded successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def main():
    print("Web Scraper Knowledge Base Generator - Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("Setup failed. Please check the error messages above.")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create output directory
    create_output_directory()
    
    # Test installation
    if test_installation():
        print("\n" + "=" * 50)
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file and add your Gemini API key")
        print("2. Run: python main.py https://example.com")
        print("3. Or run: python example_usage.py for examples")
        print("\nFor help: python main.py --help")
    else:
        print("\n" + "=" * 50)
        print("✗ Setup completed with errors")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
