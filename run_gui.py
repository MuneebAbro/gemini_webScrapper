#!/usr/bin/env python3
"""
Simple launcher script for the GUI Web Scraper
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_scraper import main
    main()
except ImportError as e:
    print(f"Error importing GUI scraper: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Error running GUI scraper: {e}")
    input("Press Enter to exit...")
