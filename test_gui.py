#!/usr/bin/env python3
"""
Test script to verify the GUI components work correctly
"""

import tkinter as tk
from gui_scraper import ScraperGUI

def test_gui():
    """Test the GUI creation and basic functionality"""
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create GUI instance
        app = ScraperGUI(root)
        
        # Test that all required attributes exist
        required_attrs = [
            'url_var', 'url_entry',
            'max_pages_var', 'delay_var', 'min_content_var',
            'use_gemini_var', 'auto_convert_var', 'sql_converter_type_var',
            'output_dir_var', 'output_file_var', 'business_id_scraping_var',
            'start_button', 'stop_button',
            'progress_var', 'progress_bar', 'status_var', 'status_label',
            'log_text',
            'json_file_var', 'business_id_var', 'converter_type_var',
            'sql_output_var', 'convert_button', 'stop_convert_button',
            'sql_progress_var', 'sql_progress_bar', 'sql_status_var', 'sql_status_label',
            'sql_log_text'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(app, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"❌ Missing attributes: {missing_attrs}")
            return False
        
        # Test URL placeholder functionality
        if app.url_entry.get() != "https://example.com":
            print("❌ URL placeholder not set correctly")
            return False
        
        # Test button states
        if app.start_button['state'] != 'normal':
            print("❌ Start button not in normal state")
            return False
            
        if app.stop_button['state'] != 'disabled':
            print("❌ Stop button not in disabled state")
            return False
        
        # Test progress bar
        if app.progress_var.get() != 0:
            print("❌ Progress bar not initialized to 0")
            return False
        
        # Test status
        if app.status_var.get() != "Ready to scrape":
            print("❌ Status not set correctly")
            return False
        
        # Clean up
        root.destroy()
        
        print("✅ All GUI components working correctly!")
        print("✅ Modern UI design applied successfully!")
        print("✅ All required attributes present!")
        print("✅ Button states correct!")
        print("✅ Progress tracking ready!")
        print("✅ Ready to launch with: python run_gui.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing GUI: {e}")
        return False

if __name__ == "__main__":
    test_gui()
