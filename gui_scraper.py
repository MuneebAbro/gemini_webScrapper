#!/usr/bin/env python3
"""
GUI Web Scraper Knowledge Base Generator

This script provides a graphical user interface for the web scraper,
allowing users to input URLs and monitor scraping progress.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import os
import sys
import logging
import json
from typing import Optional
import re
from datetime import datetime

# Import the existing scraper modules
from web_scraper import WebScraper
from llama_processor import LlamaProcessor
from knowledge_base_formatter import KnowledgeBaseFormatter
from convert_to_sql import ChatbotToSQLConverter
from simple_sql_converter import SimpleSQLConverter
from config import Config

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Web Scraper Knowledge Base Generator")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)
        
        # Configure root window
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.scraping_thread = None
        self.sql_thread = None
        self.is_scraping = False
        self.is_converting = False
        self.log_queue = queue.Queue()
        
        # Setup modern styling
        self.setup_styles()
        
        # Setup logging to capture in GUI
        self.setup_logging()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start log monitoring
        self.monitor_log_queue()
        
    def setup_styles(self):
        """Setup modern styling for the GUI"""
        self.style = ttk.Style()
        
        # Try to use a modern theme
        try:
            # Use clam theme as base
            self.style.theme_use('clam')
            
            # Configure custom styles
            self.style.configure('Title.TLabel', 
                               font=('Segoe UI', 18, 'bold'),
                               foreground='#2c3e50',
                               background='#f0f0f0')
            
            self.style.configure('Header.TLabel', 
                               font=('Segoe UI', 12, 'bold'),
                               foreground='#34495e',
                               background='#f0f0f0')
            
            self.style.configure('Modern.TFrame', 
                               background='#ffffff',
                               relief='solid',
                               borderwidth=1)
            
            self.style.configure('Card.TFrame', 
                               background='#ffffff',
                               relief='raised',
                               borderwidth=2)
            
            self.style.configure('Primary.TButton',
                               font=('Segoe UI', 10, 'bold'),
                               foreground='white',
                               background='#3498db',
                               borderwidth=0,
                               focuscolor='none')
            
            self.style.map('Primary.TButton',
                          background=[('active', '#2980b9'),
                                    ('pressed', '#21618c')])
            
            self.style.configure('Success.TButton',
                               font=('Segoe UI', 10, 'bold'),
                               foreground='white',
                               background='#27ae60',
                               borderwidth=0,
                               focuscolor='none')
            
            self.style.map('Success.TButton',
                          background=[('active', '#229954'),
                                    ('pressed', '#1e8449')])
            
            self.style.configure('Danger.TButton',
                               font=('Segoe UI', 10, 'bold'),
                               foreground='white',
                               background='#e74c3c',
                               borderwidth=0,
                               focuscolor='none')
            
            self.style.map('Danger.TButton',
                          background=[('active', '#c0392b'),
                                    ('pressed', '#a93226')])
            
            # Note: Custom progress bar styling may not work on all systems
            # We'll use default styling with custom colors where possible
            
            self.style.configure('Modern.TNotebook',
                               background='#f0f0f0',
                               borderwidth=0)
            
            self.style.configure('Modern.TNotebook.Tab',
                               background='#bdc3c7',
                               foreground='#2c3e50',
                               padding=[20, 10],
                               font=('Segoe UI', 10, 'bold'))
            
            self.style.map('Modern.TNotebook.Tab',
                          background=[('selected', '#3498db'),
                                    ('active', '#95a5a6')])
            
            self.style.configure('Modern.TLabelFrame',
                               background='#ffffff',
                               foreground='#2c3e50',
                               font=('Segoe UI', 10, 'bold'),
                               borderwidth=2,
                               relief='solid')
            
            self.style.configure('Modern.TLabelFrame.Label',
                               background='#ffffff',
                               foreground='#2c3e50',
                               font=('Segoe UI', 10, 'bold'))
            
        except Exception as e:
            print(f"Warning: Could not apply custom styles: {e}")
            # Continue with default styling
        
    def setup_logging(self):
        """Setup logging to capture messages in GUI"""
        # Create a custom handler that puts logs in our queue
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
                
            def emit(self, record):
                self.log_queue.put(self.format(record))
        
        # Setup logger
        self.logger = logging.getLogger('scraper_gui')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # Add our queue handler
        queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        queue_handler.setFormatter(formatter)
        self.logger.addHandler(queue_handler)
        
    def create_widgets(self):
        """Create all GUI widgets with modern design"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Header section
        self.create_header(main_container)
        
        # Create notebook for tabs with modern styling
        self.notebook = ttk.Notebook(main_container, style='Modern.TNotebook')
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        
        # Create tabs
        self.create_scraping_tab()
        self.create_sql_tab()
        
    def create_header(self, parent):
        """Create a modern header section"""
        header_frame = tk.Frame(parent, bg='#2c3e50', height=80)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 0))
        header_frame.grid_propagate(False)
        header_frame.columnconfigure(0, weight=1)
        
        # Title with icon
        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=30, pady=20)
        
        title_label = tk.Label(title_frame, 
                              text="🚀 Web Scraper Knowledge Base Generator", 
                              font=('Segoe UI', 20, 'bold'),
                              fg='white',
                              bg='#2c3e50')
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = tk.Label(title_frame,
                                 text="Transform websites into structured knowledge bases",
                                 font=('Segoe UI', 11),
                                 fg='#bdc3c7',
                                 bg='#2c3e50')
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))
        
    def create_scraping_tab(self):
        """Create the web scraping tab with modern design"""
        # Main tab frame
        scraping_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(scraping_frame, text="🌐 Web Scraping")
        
        # Create scrollable frame
        canvas = tk.Canvas(scraping_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(scraping_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Configure grid weights
        scrollable_frame.columnconfigure(0, weight=1)
        
        # URL Input Card
        self.create_url_card(scrollable_frame)
        
        # Configuration Card
        self.create_config_card(scrollable_frame)
        
        # Output Card
        self.create_output_card(scrollable_frame)
        
        # Control Card
        self.create_control_card(scrollable_frame)
        
        # Progress Card
        self.create_progress_card(scrollable_frame)
        
        # Log Card
        self.create_log_card(scrollable_frame)
        
    def create_url_card(self, parent):
        """Create URL input card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#3498db', height=40)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="🌐 Website URL", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#3498db')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # URL input
        url_frame = tk.Frame(card_frame, bg='#ffffff')
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=20, pady=20)
        url_frame.columnconfigure(1, weight=1)
        
        tk.Label(url_frame, text="Website URL:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, 
                                 font=('Segoe UI', 11),
                                 relief='solid', bd=1,
                                 highlightthickness=2,
                                 highlightcolor='#3498db')
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Placeholder text
        self.url_entry.insert(0, "https://example.com")
        self.url_entry.configure(fg='#7f8c8d')
        self.url_entry.bind('<FocusIn>', self.on_url_focus_in)
        self.url_entry.bind('<FocusOut>', self.on_url_focus_out)
        
    def on_url_focus_in(self, event):
        """Handle URL entry focus in"""
        if self.url_entry.get() == "https://example.com":
            self.url_entry.delete(0, tk.END)
            self.url_entry.configure(fg='#2c3e50')
            
    def on_url_focus_out(self, event):
        """Handle URL entry focus out"""
        if not self.url_entry.get():
            self.url_entry.insert(0, "https://example.com")
            self.url_entry.configure(fg='#7f8c8d')
        
    def create_config_card(self, parent):
        """Create configuration card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(0, weight=1)
        card_frame.columnconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#27ae60', height=40)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="⚙️ Configuration", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#27ae60')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Configuration content
        config_content = tk.Frame(card_frame, bg='#ffffff')
        config_content.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20, pady=20)
        config_content.columnconfigure(1, weight=1)
        config_content.columnconfigure(3, weight=1)
        
        # Row 1: Max Pages and Delay
        tk.Label(config_content, text="Max Pages:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.max_pages_var = tk.StringVar(value=str(Config.MAX_PAGES))
        max_pages_spinbox = tk.Spinbox(config_content, from_=1, to=1000, width=10, 
                                      textvariable=self.max_pages_var,
                                      font=('Segoe UI', 10),
                                      relief='solid', bd=1)
        max_pages_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 20))
        
        tk.Label(config_content, text="Delay (seconds):", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=2, sticky=tk.W, pady=5)
        
        self.delay_var = tk.StringVar(value=str(Config.DELAY_BETWEEN_REQUESTS))
        delay_spinbox = tk.Spinbox(config_content, from_=0.1, to=10.0, increment=0.1, width=10,
                                  textvariable=self.delay_var,
                                  font=('Segoe UI', 10),
                                  relief='solid', bd=1)
        delay_spinbox.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Row 2: Min Content Length
        tk.Label(config_content, text="Min Content Length:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.min_content_var = tk.StringVar(value=str(Config.MIN_CONTENT_LENGTH))
        min_content_spinbox = tk.Spinbox(config_content, from_=10, to=1000, width=10,
                                        textvariable=self.min_content_var,
                                        font=('Segoe UI', 10),
                                        relief='solid', bd=1)
        min_content_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 20))
        
        # Row 3: Checkboxes
        checkbox_frame = tk.Frame(config_content, bg='#ffffff')
        checkbox_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.use_llama_var = tk.BooleanVar(value=bool(Config.LLAMA_API_KEY))
        llama_check = tk.Checkbutton(checkbox_frame, text="🤖 Use Llama AI Processing", 
                                     variable=self.use_llama_var,
                                     font=('Segoe UI', 10),
                                     fg='#2c3e50', bg='#ffffff',
                                     selectcolor='#ecf0f1')
        llama_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.auto_convert_var = tk.BooleanVar(value=False)
        auto_convert_check = tk.Checkbutton(checkbox_frame, text="🔄 Auto-convert to SQL after scraping", 
                                           variable=self.auto_convert_var,
                                           font=('Segoe UI', 10),
                                           fg='#2c3e50', bg='#ffffff',
                                           selectcolor='#ecf0f1')
        auto_convert_check.pack(side=tk.LEFT)
        
        # Row 4: SQL Converter Type
        sql_converter_frame = tk.Frame(config_content, bg='#ffffff')
        sql_converter_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        tk.Label(sql_converter_frame, text="SQL Converter:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').pack(side=tk.LEFT, padx=(0, 10))
        
        self.sql_converter_type_var = tk.StringVar(value="simple")
        simple_radio = tk.Radiobutton(sql_converter_frame, text="Simple", 
                                     variable=self.sql_converter_type_var, value="simple",
                                     font=('Segoe UI', 10),
                                     fg='#2c3e50', bg='#ffffff',
                                     selectcolor='#ecf0f1')
        simple_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        ai_radio = tk.Radiobutton(sql_converter_frame, text="AI", 
                                 variable=self.sql_converter_type_var, value="ai",
                                 font=('Segoe UI', 10),
                                 fg='#2c3e50', bg='#ffffff',
                                 selectcolor='#ecf0f1')
        ai_radio.pack(side=tk.LEFT)
        
    def create_output_card(self, parent):
        """Create output settings card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#9b59b6', height=40)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="📁 Output Settings", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#9b59b6')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Output content
        output_content = tk.Frame(card_frame, bg='#ffffff')
        output_content.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=20, pady=20)
        output_content.columnconfigure(1, weight=1)
        
        # Output Directory
        tk.Label(output_content, text="Output Directory:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        dir_frame = tk.Frame(output_content, bg='#ffffff')
        dir_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(0, weight=1)
        
        self.output_dir_var = tk.StringVar(value=Config.OUTPUT_DIR)
        output_dir_entry = tk.Entry(dir_frame, textvariable=self.output_dir_var, 
                                   font=('Segoe UI', 10),
                                   relief='solid', bd=1)
        output_dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_dir_btn = tk.Button(dir_frame, text="📂 Browse", 
                                  command=self.browse_output_dir,
                                  font=('Segoe UI', 9, 'bold'),
                                  bg='#95a5a6', fg='white',
                                  relief='flat', bd=0,
                                  padx=15, pady=5)
        browse_dir_btn.grid(row=0, column=1)
        
        # Output Filename
        tk.Label(output_content, text="Output Filename:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.output_file_var = tk.StringVar(value=Config.JSON_FILENAME)
        output_file_entry = tk.Entry(output_content, textvariable=self.output_file_var, 
                                    font=('Segoe UI', 10),
                                    relief='solid', bd=1)
        output_file_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Business ID (for auto SQL conversion)
        tk.Label(output_content, text="Business ID (for SQL):", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.business_id_scraping_var = tk.StringVar()
        business_id_entry = tk.Entry(output_content, textvariable=self.business_id_scraping_var, 
                                    font=('Segoe UI', 10),
                                    relief='solid', bd=1)
        business_id_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
    def create_control_card(self, parent):
        """Create control buttons card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#e67e22', height=40)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="🎮 Control Panel", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#e67e22')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(card_frame, bg='#ffffff')
        button_frame.grid(row=1, column=0, padx=20, pady=20)
        
        self.start_button = tk.Button(button_frame, text="🚀 Start Scraping", 
                                     command=self.start_scraping,
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='#27ae60', fg='white',
                                     relief='flat', bd=0,
                                     padx=30, pady=15,
                                     cursor='hand2')
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_button = tk.Button(button_frame, text="⏹️ Stop", 
                                    command=self.stop_scraping,
                                    font=('Segoe UI', 12, 'bold'),
                                    bg='#e74c3c', fg='white',
                                    relief='flat', bd=0,
                                    padx=30, pady=15,
                                    state=tk.DISABLED,
                                    cursor='hand2')
        self.stop_button.pack(side=tk.LEFT)
        
    def create_progress_card(self, parent):
        """Create progress tracking card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(0, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#3498db', height=40)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="📊 Progress", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#3498db')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Progress content
        progress_content = tk.Frame(card_frame, bg='#ffffff')
        progress_content.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=20, pady=20)
        progress_content.columnconfigure(0, weight=1)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_content, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to scrape")
        self.status_label = tk.Label(progress_content, textvariable=self.status_var,
                                    font=('Segoe UI', 11, 'bold'),
                                    fg='#2c3e50', bg='#ffffff')
        self.status_label.grid(row=1, column=0, pady=5)
        
    def create_log_card(self, parent):
        """Create log output card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20), padx=10)
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#34495e', height=40)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        header_frame.columnconfigure(0, weight=1)
        
        header_label = tk.Label(header_frame, text="📝 Log Output", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#34495e')
        header_label.grid(row=0, column=0, sticky=tk.W, padx=15, pady=10)
        
        clear_btn = tk.Button(header_frame, text="🗑️ Clear", 
                             command=self.clear_log,
                             font=('Segoe UI', 9, 'bold'),
                             bg='#e74c3c', fg='white',
                             relief='flat', bd=0,
                             padx=10, pady=5)
        clear_btn.grid(row=0, column=1, padx=15, pady=10)
        
        # Log content
        log_content = tk.Frame(card_frame, bg='#ffffff')
        log_content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        log_content.columnconfigure(0, weight=1)
        log_content.rowconfigure(0, weight=1)
        
        # Log Text Area
        self.log_text = scrolledtext.ScrolledText(log_content, height=15, width=80,
                                                 font=('Consolas', 9),
                                                 bg='#2c3e50', fg='#ecf0f1',
                                                 insertbackground='#ecf0f1',
                                                 selectbackground='#3498db',
                                                 relief='flat', bd=0)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def create_sql_tab(self):
        """Create the SQL conversion tab with modern design"""
        # Main tab frame
        sql_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(sql_frame, text="🗄️ JSON to SQL")
        
        # Create scrollable frame
        canvas = tk.Canvas(sql_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(sql_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Configure grid weights
        scrollable_frame.columnconfigure(0, weight=1)
        
        # Create SQL cards
        self.create_sql_input_card(scrollable_frame)
        self.create_sql_config_card(scrollable_frame)
        self.create_sql_output_card(scrollable_frame)
        self.create_sql_control_card(scrollable_frame)
        self.create_sql_progress_card(scrollable_frame)
        self.create_sql_log_card(scrollable_frame)
        
    def create_sql_input_card(self, parent):
        """Create SQL input file card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#e74c3c', height=40)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="📄 Input File", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#e74c3c')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Input content
        input_content = tk.Frame(card_frame, bg='#ffffff')
        input_content.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=20, pady=20)
        input_content.columnconfigure(1, weight=1)
        
        tk.Label(input_content, text="JSON File:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        file_frame = tk.Frame(input_content, bg='#ffffff')
        file_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.json_file_var = tk.StringVar()
        json_file_entry = tk.Entry(file_frame, textvariable=self.json_file_var, 
                                  font=('Segoe UI', 10),
                                  relief='solid', bd=1)
        json_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_file_btn = tk.Button(file_frame, text="📂 Browse", 
                                   command=self.browse_json_file,
                                   font=('Segoe UI', 9, 'bold'),
                                   bg='#95a5a6', fg='white',
                                   relief='flat', bd=0,
                                   padx=15, pady=5)
        browse_file_btn.grid(row=0, column=1)
        
    def create_sql_config_card(self, parent):
        """Create SQL configuration card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#f39c12', height=40)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="⚙️ Configuration", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#f39c12')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Config content
        config_content = tk.Frame(card_frame, bg='#ffffff')
        config_content.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20, pady=20)
        config_content.columnconfigure(1, weight=1)
        
        # Business ID
        tk.Label(config_content, text="Business ID:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.business_id_var = tk.StringVar()
        business_id_entry = tk.Entry(config_content, textvariable=self.business_id_var, 
                                    font=('Segoe UI', 10),
                                    relief='solid', bd=1)
        business_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Converter Type
        converter_frame = tk.Frame(config_content, bg='#ffffff')
        converter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        tk.Label(converter_frame, text="Converter Type:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').pack(side=tk.LEFT, padx=(0, 10))
        
        self.converter_type_var = tk.StringVar(value="simple")
        simple_radio = tk.Radiobutton(converter_frame, text="Simple (Keyword-based)", 
                                     variable=self.converter_type_var, value="simple",
                                     font=('Segoe UI', 10),
                                     fg='#2c3e50', bg='#ffffff',
                                     selectcolor='#ecf0f1')
        simple_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        ai_radio = tk.Radiobutton(converter_frame, text="AI (Llama-powered)", 
                                 variable=self.converter_type_var, value="ai",
                                 font=('Segoe UI', 10),
                                 fg='#2c3e50', bg='#ffffff',
                                 selectcolor='#ecf0f1')
        ai_radio.pack(side=tk.LEFT)
        
    def create_sql_output_card(self, parent):
        """Create SQL output card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#8e44ad', height=40)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="💾 Output File", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#8e44ad')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Output content
        output_content = tk.Frame(card_frame, bg='#ffffff')
        output_content.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=20, pady=20)
        output_content.columnconfigure(1, weight=1)
        
        tk.Label(output_content, text="SQL Output File:", 
                font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        output_frame = tk.Frame(output_content, bg='#ffffff')
        output_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.sql_output_var = tk.StringVar(value="knowledge_base_inserts.sql")
        sql_output_entry = tk.Entry(output_frame, textvariable=self.sql_output_var, 
                                   font=('Segoe UI', 10),
                                   relief='solid', bd=1)
        sql_output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_sql_btn = tk.Button(output_frame, text="📂 Browse", 
                                  command=self.browse_sql_output,
                                  font=('Segoe UI', 9, 'bold'),
                                  bg='#95a5a6', fg='white',
                                  relief='flat', bd=0,
                                  padx=15, pady=5)
        browse_sql_btn.grid(row=0, column=1)
        
    def create_sql_control_card(self, parent):
        """Create SQL control buttons card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#16a085', height=40)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="🎮 Control Panel", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#16a085')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(card_frame, bg='#ffffff')
        button_frame.grid(row=1, column=0, padx=20, pady=20)
        
        self.convert_button = tk.Button(button_frame, text="🔄 Convert to SQL", 
                                       command=self.start_sql_conversion,
                                       font=('Segoe UI', 12, 'bold'),
                                       bg='#27ae60', fg='white',
                                       relief='flat', bd=0,
                                       padx=30, pady=15,
                                       cursor='hand2')
        self.convert_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_convert_button = tk.Button(button_frame, text="⏹️ Stop", 
                                            command=self.stop_sql_conversion,
                                            font=('Segoe UI', 12, 'bold'),
                                            bg='#e74c3c', fg='white',
                                            relief='flat', bd=0,
                                            padx=30, pady=15,
                                            state=tk.DISABLED,
                                            cursor='hand2')
        self.stop_convert_button.pack(side=tk.LEFT)
        
    def create_sql_progress_card(self, parent):
        """Create SQL progress tracking card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=10)
        card_frame.columnconfigure(0, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#2980b9', height=40)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        
        header_label = tk.Label(header_frame, text="📊 Progress", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#2980b9')
        header_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Progress content
        progress_content = tk.Frame(card_frame, bg='#ffffff')
        progress_content.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=20, pady=20)
        progress_content.columnconfigure(0, weight=1)
        
        # Progress Bar
        self.sql_progress_var = tk.DoubleVar()
        self.sql_progress_bar = ttk.Progressbar(progress_content, variable=self.sql_progress_var, 
                                               maximum=100, length=400)
        self.sql_progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status Label
        self.sql_status_var = tk.StringVar(value="Ready to convert")
        self.sql_status_label = tk.Label(progress_content, textvariable=self.sql_status_var,
                                        font=('Segoe UI', 11, 'bold'),
                                        fg='#2c3e50', bg='#ffffff')
        self.sql_status_label.grid(row=1, column=0, pady=5)
        
    def create_sql_log_card(self, parent):
        """Create SQL log output card"""
        card_frame = tk.Frame(parent, bg='#ffffff', relief='raised', bd=2)
        card_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20), padx=10)
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure(1, weight=1)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg='#2c3e50', height=40)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header_frame.grid_propagate(False)
        header_frame.columnconfigure(0, weight=1)
        
        header_label = tk.Label(header_frame, text="📝 Log Output", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#2c3e50')
        header_label.grid(row=0, column=0, sticky=tk.W, padx=15, pady=10)
        
        clear_btn = tk.Button(header_frame, text="🗑️ Clear", 
                             command=self.clear_sql_log,
                             font=('Segoe UI', 9, 'bold'),
                             bg='#e74c3c', fg='white',
                             relief='flat', bd=0,
                             padx=10, pady=5)
        clear_btn.grid(row=0, column=1, padx=15, pady=10)
        
        # Log content
        log_content = tk.Frame(card_frame, bg='#ffffff')
        log_content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        log_content.columnconfigure(0, weight=1)
        log_content.rowconfigure(0, weight=1)
        
        # Log Text Area
        self.sql_log_text = scrolledtext.ScrolledText(log_content, height=15, width=80,
                                                     font=('Consolas', 9),
                                                     bg='#2c3e50', fg='#ecf0f1',
                                                     insertbackground='#ecf0f1',
                                                     selectbackground='#3498db',
                                                     relief='flat', bd=0)
        self.sql_log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
            
    def browse_json_file(self):
        """Browse for JSON input file"""
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.json_file_var.set(file_path)
            
    def browse_sql_output(self):
        """Browse for SQL output file"""
        file_path = filedialog.asksaveasfilename(
            title="Save SQL File As",
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        if file_path:
            self.sql_output_var.set(file_path)
            
    def validate_url(self, url: str) -> bool:
        """Validate if the provided URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
        
    def validate_inputs(self) -> bool:
        """Validate all input fields"""
        # Validate URL
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return False
            
        if not self.validate_url(url):
            messagebox.showerror("Error", "Please enter a valid URL (must start with http:// or https://)")
            return False
            
        # Validate numeric inputs
        try:
            max_pages = int(self.max_pages_var.get())
            if max_pages < 1:
                raise ValueError("Max pages must be at least 1")
        except ValueError:
            messagebox.showerror("Error", "Max pages must be a positive integer")
            return False
            
        try:
            delay = float(self.delay_var.get())
            if delay < 0:
                raise ValueError("Delay must be non-negative")
        except ValueError:
            messagebox.showerror("Error", "Delay must be a non-negative number")
            return False
            
        try:
            min_content = int(self.min_content_var.get())
            if min_content < 1:
                raise ValueError("Min content length must be at least 1")
        except ValueError:
            messagebox.showerror("Error", "Min content length must be a positive integer")
            return False
            
        # Check Llama API key if using Llama
        if self.use_llama_var.get() and not Config.LLAMA_API_KEY:
            messagebox.showerror("Error", "LLAMA_API_KEY not found in environment variables.\n"
                                         "Please set your Llama API key or uncheck 'Use Llama AI Processing'")
            return False
            
        # Check business ID if auto-convert is enabled
        if self.auto_convert_var.get():
            business_id = self.business_id_scraping_var.get().strip()
            if not business_id:
                messagebox.showerror("Error", "Business ID is required when auto-convert to SQL is enabled")
                return False
            
            # Check Llama API key if AI converter is selected for auto-conversion
            if self.sql_converter_type_var.get() == "ai" and not Config.LLAMA_API_KEY:
                messagebox.showerror("Error", "LLAMA_API_KEY not found for AI SQL converter.\n"
                                             "Please set your Llama API key or select 'Simple' converter")
                return False
            
        return True
        
    def validate_sql_inputs(self) -> bool:
        """Validate SQL conversion inputs"""
        # Validate JSON file
        json_file = self.json_file_var.get().strip()
        if not json_file:
            messagebox.showerror("Error", "Please select a JSON file")
            return False
            
        if not os.path.exists(json_file):
            messagebox.showerror("Error", f"JSON file not found: {json_file}")
            return False
            
        # Validate business ID
        business_id = self.business_id_var.get().strip()
        if not business_id:
            messagebox.showerror("Error", "Please enter a business ID")
            return False
            
        # Validate output file
        sql_output = self.sql_output_var.get().strip()
        if not sql_output:
            messagebox.showerror("Error", "Please specify an output SQL file")
            return False
            
        # Check Llama API key if using AI converter
        if self.converter_type_var.get() == "ai" and not Config.LLAMA_API_KEY:
            messagebox.showerror("Error", "LLAMA_API_KEY not found in environment variables.\n"
                                         "Please set your Llama API key or use 'Simple Converter'")
            return False
            
        return True
        
    def update_config(self):
        """Update configuration with GUI values"""
        Config.MAX_PAGES = int(self.max_pages_var.get())
        Config.DELAY_BETWEEN_REQUESTS = float(self.delay_var.get())
        Config.MIN_CONTENT_LENGTH = int(self.min_content_var.get())
        Config.OUTPUT_DIR = self.output_dir_var.get()
        Config.JSON_FILENAME = self.output_file_var.get()
        
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if not self.validate_inputs():
            return
            
        if self.is_scraping:
            return
            
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Starting scraping...")
        
        # Update config
        self.update_config()
        
        # Start scraping thread
        self.scraping_thread = threading.Thread(target=self.scrape_worker, daemon=True)
        self.scraping_thread.start()
        
    def stop_scraping(self):
        """Stop the scraping process"""
        if not self.is_scraping:
            return
            
        self.is_scraping = False
        self.status_var.set("Stopping scraping...")
        self.logger.info("Scraping stopped by user")
        
    def scrape_worker(self):
        """Worker function that runs in a separate thread"""
        try:
            url = self.url_var.get().strip()
            
            self.logger.info("=" * 60)
            self.logger.info("Web Scraper Knowledge Base Generator")
            self.logger.info("=" * 60)
            self.logger.info(f"Target URL: {url}")
            self.logger.info(f"Max pages: {Config.MAX_PAGES}")
            self.logger.info(f"Delay between requests: {Config.DELAY_BETWEEN_REQUESTS}s")
            self.logger.info(f"Output directory: {Config.OUTPUT_DIR}")
            self.logger.info(f"Output file: {Config.JSON_FILENAME}")
            self.logger.info(f"Llama processing: {'Enabled' if self.use_llama_var.get() else 'Disabled'}")
            self.logger.info("=" * 60)
            
            # Step 1: Scrape the website
            self.status_var.set("Step 1: Scraping website...")
            self.logger.info("Step 1: Starting web scraping...")
            
            scraper = WebScraper()
            
            # Create a custom scraper that reports progress
            class ProgressScraper(WebScraper):
                def __init__(self, gui_instance):
                    super().__init__()
                    self.gui = gui_instance
                    self.total_pages = 0
                    
                def scrape_website(self, start_url: str):
                    self.gui.logger.info(f"Starting to scrape website: {start_url}")
                    
                    urls_to_visit = [start_url]
                    self.visited_urls = set()
                    self.scraped_data = []
                    
                    # First pass: count total pages to visit
                    temp_visited = set()
                    temp_queue = [start_url]
                    page_count = 0
                    
                    while temp_queue and page_count < Config.MAX_PAGES:
                        current_url = temp_queue.pop(0)
                        if current_url in temp_visited:
                            continue
                        temp_visited.add(current_url)
                        page_count += 1
                        
                        # Get internal links for this page
                        soup = self.get_page_content(current_url)
                        if soup:
                            internal_links = self.find_internal_links(soup, current_url)
                            for link in internal_links:
                                if link not in temp_visited and link not in temp_queue:
                                    temp_queue.append(link)
                    
                    self.total_pages = min(page_count, Config.MAX_PAGES)
                    self.gui.logger.info(f"Estimated pages to scrape: {self.total_pages}")
                    
                    # Second pass: actual scraping with progress updates
                    while urls_to_visit and len(self.scraped_data) < Config.MAX_PAGES and self.gui.is_scraping:
                        current_url = urls_to_visit.pop(0)
                        
                        if current_url in self.visited_urls:
                            continue
                            
                        self.visited_urls.add(current_url)
                        
                        # Update progress
                        progress = (len(self.scraped_data) / self.total_pages) * 100
                        self.gui.progress_var.set(progress)
                        self.gui.status_var.set(f"Scraping page {len(self.scraped_data) + 1} of {self.total_pages}")
                        
                        # Scrape the current page
                        page_data = self.scrape_page(current_url)
                        
                        if page_data:
                            self.scraped_data.append(page_data)
                            
                            # Add new internal links to the queue
                            for link in page_data.get('internal_links', []):
                                if link not in self.visited_urls and link not in urls_to_visit:
                                    urls_to_visit.append(link)
                            
                            self.gui.logger.info(f"Scraped page {len(self.scraped_data)}: {page_data['title']}")
                        else:
                            self.gui.logger.warning(f"Failed to scrape page: {current_url}")
                        
                        # Add delay between requests
                        import time
                        time.sleep(Config.DELAY_BETWEEN_REQUESTS)
                    
                    if not self.gui.is_scraping:
                        self.gui.logger.info("Scraping interrupted by user")
                        return []
                        
                    self.gui.logger.info(f"Scraping completed. Total pages scraped: {len(self.scraped_data)}")
                    return self.scraped_data
            
            progress_scraper = ProgressScraper(self)
            scraped_data = progress_scraper.scrape_website(url)
            
            if not scraped_data:
                if self.is_scraping:
                    self.logger.error("No data was scraped. Please check the URL and try again.")
                return
            
            self.logger.info(f"Successfully scraped {len(scraped_data)} pages")
            
            # Step 2: Process with Llama (if enabled)
            if self.use_llama_var.get() and self.is_scraping:
                self.status_var.set("Step 2: Processing with Llama AI...")
                self.logger.info("Step 2: Processing content with Llama AI...")
                processor = LlamaProcessor()
                processed_data = processor.batch_process_pages(scraped_data)
            elif self.is_scraping:
                self.logger.info("Step 2: Skipping Llama processing...")
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
            
            if not self.is_scraping:
                return
                
            # Step 3: Format into knowledge base
            self.status_var.set("Step 3: Creating knowledge base...")
            self.logger.info("Step 3: Creating knowledge base structure...")
            formatter = KnowledgeBaseFormatter()
            knowledge_base = formatter.create_knowledge_base_structure(processed_data, url)
            
            # Step 4: Save knowledge base
            self.status_var.set("Step 4: Saving knowledge base...")
            self.logger.info("Step 4: Saving knowledge base...")
            kb_filepath = formatter.save_knowledge_base(knowledge_base, Config.JSON_FILENAME)
            
            # Step 5: Create chatbot-ready format
            self.status_var.set("Step 5: Creating chatbot format...")
            self.logger.info("Step 5: Creating chatbot-ready format...")
            chatbot_data = formatter.create_chatbot_ready_format(knowledge_base)
            chatbot_filepath = formatter.save_chatbot_format(chatbot_data, "chatbot_data.json")
            
            # Auto-convert to SQL if enabled
            sql_filepath = None
            if self.auto_convert_var.get() and self.is_scraping:
                self.status_var.set("Auto-converting to SQL...")
                self.logger.info("Auto-converting to SQL...")
                
                try:
                    business_id = self.business_id_scraping_var.get().strip()
                    sql_output = os.path.join(Config.OUTPUT_DIR, f"knowledge_base_inserts_{business_id}.sql")
                    
                    # Use the converter type selected in scraping tab
                    converter_type_value = self.sql_converter_type_var.get()
                    
                    # Create converter
                    if converter_type_value == "ai" and Config.GEMINI_API_KEY:
                        self.logger.info("Using AI converter for auto-conversion...")
                        converter = ChatbotToSQLConverter()
                    else:
                        self.logger.info("Using simple converter for auto-conversion...")
                        converter = SimpleSQLConverter()
                    
                    # Generate SQL statements
                    sql_statements = []
                    training_data = chatbot_data.get('training_data', [])
                    
                    for i, item in enumerate(training_data):
                        if not self.is_scraping:
                            break
                            
                        question = item.get('text', '').strip()
                        answer = item.get('response', '').strip()
                        
                        if not question or not answer:
                            continue
                        
                        # Classify category
                        if converter_type_value == "ai" and Config.GEMINI_API_KEY:
                            category = converter.classify_category_with_ai(question, answer)
                        else:
                            category = converter.classify_category_simple(question, answer)
                        
                        # Escape SQL strings
                        question_escaped = converter.escape_sql_string(question)
                        answer_escaped = converter.escape_sql_string(answer)
                        
                        # Generate SQL INSERT statement
                        sql = f"insert into knowledge_base (business_id, question, answer, category, priority)\nvalues\n('{business_id}', '{question_escaped}', '{answer_escaped}', '{category}', 1);"
                        sql_statements.append(sql)
                    
                    if self.is_scraping and sql_statements:
                        # Save SQL file
                        with open(sql_output, 'w', encoding='utf-8') as f:
                            f.write("-- SQL INSERT statements for knowledge base\n")
                            f.write("-- Generated from chatbot data\n\n")
                            
                            for sql in sql_statements:
                                f.write(sql + "\n\n")
                        
                        sql_filepath = sql_output
                        self.logger.info(f"Auto-generated {len(sql_statements)} SQL INSERT statements")
                        self.logger.info(f"SQL file saved to: {sql_filepath}")
                    
                except Exception as e:
                    self.logger.error(f"Error during auto SQL conversion: {e}")
                    # Don't fail the entire process if SQL conversion fails
            
            # Complete
            self.progress_var.set(100)
            self.status_var.set("Scraping completed successfully!")
            
            # Summary
            self.logger.info("=" * 60)
            self.logger.info("SCRAPING COMPLETED SUCCESSFULLY!")
            self.logger.info("=" * 60)
            self.logger.info(f"Total pages scraped: {len(scraped_data)}")
            self.logger.info(f"Total FAQ questions: {len(chatbot_data['training_data'])}")
            self.logger.info(f"Knowledge base saved to: {kb_filepath}")
            self.logger.info(f"Chatbot data saved to: {chatbot_filepath}")
            if sql_filepath:
                self.logger.info(f"SQL file saved to: {sql_filepath}")
            self.logger.info("=" * 60)
            
            # Show completion message
            completion_message = f"Scraping completed successfully!\n\n"
            completion_message += f"Pages scraped: {len(scraped_data)}\n"
            completion_message += f"FAQ questions: {len(chatbot_data['training_data'])}\n"
            completion_message += f"Knowledge base: {kb_filepath}\n"
            completion_message += f"Chatbot data: {chatbot_filepath}"
            if sql_filepath:
                completion_message += f"\nSQL file: {sql_filepath}"
            
            messagebox.showinfo("Success", completion_message)
            
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"An error occurred during scraping:\n{e}")
        finally:
            # Reset UI state
            self.is_scraping = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if self.progress_var.get() < 100:
                self.status_var.set("Ready to scrape")
                
    def start_sql_conversion(self):
        """Start the SQL conversion process in a separate thread"""
        if not self.validate_sql_inputs():
            return
            
        if self.is_converting:
            return
            
        self.is_converting = True
        self.convert_button.config(state=tk.DISABLED)
        self.stop_convert_button.config(state=tk.NORMAL)
        self.sql_progress_var.set(0)
        self.sql_status_var.set("Starting conversion...")
        
        # Start conversion thread
        self.sql_thread = threading.Thread(target=self.sql_conversion_worker, daemon=True)
        self.sql_thread.start()
        
    def stop_sql_conversion(self):
        """Stop the SQL conversion process"""
        if not self.is_converting:
            return
            
        self.is_converting = False
        self.sql_status_var.set("Stopping conversion...")
        self.logger.info("SQL conversion stopped by user")
        
    def sql_conversion_worker(self):
        """Worker function for SQL conversion"""
        try:
            json_file = self.json_file_var.get().strip()
            business_id = self.business_id_var.get().strip()
            sql_output = self.sql_output_var.get().strip()
            converter_type = self.converter_type_var.get()
            
            self.logger.info("=" * 60)
            self.logger.info("JSON to SQL Converter")
            self.logger.info("=" * 60)
            self.logger.info(f"Input file: {json_file}")
            self.logger.info(f"Business ID: {business_id}")
            self.logger.info(f"Output file: {sql_output}")
            self.logger.info(f"Converter type: {converter_type}")
            self.logger.info("=" * 60)
            
            # Load chatbot data
            self.sql_status_var.set("Loading JSON data...")
            self.logger.info("Loading chatbot data...")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    chatbot_data = json.load(f)
            except FileNotFoundError:
                self.logger.error(f"File not found: {json_file}")
                messagebox.showerror("Error", f"File not found: {json_file}")
                return
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in file '{json_file}': {e}")
                messagebox.showerror("Error", f"Invalid JSON in file '{json_file}': {e}")
                return
            
            training_data = chatbot_data.get('training_data', [])
            if not training_data:
                self.logger.error("No training data found in chatbot file")
                messagebox.showerror("Error", "No training data found in chatbot file")
                return
                
            self.logger.info(f"Found {len(training_data)} Q&A pairs to process")
            
            # Create converter
            if converter_type == "ai":
                self.sql_status_var.set("Initializing AI converter...")
                self.logger.info("Using AI converter with Llama...")
                converter = ChatbotToSQLConverter()
            else:
                self.sql_status_var.set("Initializing simple converter...")
                self.logger.info("Using simple keyword-based converter...")
                converter = SimpleSQLConverter()
            
            # Process data with progress updates
            self.sql_status_var.set("Converting to SQL...")
            sql_statements = []
            
            for i, item in enumerate(training_data):
                if not self.is_converting:
                    self.logger.info("Conversion interrupted by user")
                    return
                    
                question = item.get('text', '').strip()
                answer = item.get('response', '').strip()
                
                if not question or not answer:
                    self.logger.warning(f"Skipping item {i+1}: Missing question or answer")
                    continue
                
                # Update progress
                progress = ((i + 1) / len(training_data)) * 100
                self.sql_progress_var.set(progress)
                self.sql_status_var.set(f"Processing item {i+1} of {len(training_data)}")
                
                # Classify category
                if converter_type == "ai":
                    category = converter.classify_category_with_ai(question, answer)
                else:
                    category = converter.classify_category_simple(question, answer)
                
                # Escape SQL strings
                question_escaped = converter.escape_sql_string(question)
                answer_escaped = converter.escape_sql_string(answer)
                
                # Generate SQL INSERT statement
                sql = f"insert into knowledge_base (business_id, question, answer, category, priority)\nvalues\n('{business_id}', '{question_escaped}', '{answer_escaped}', '{category}', 1);"
                sql_statements.append(sql)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"Processed {i + 1}/{len(training_data)} items...")
            
            if not self.is_converting:
                return
                
            # Save SQL file
            self.sql_status_var.set("Saving SQL file...")
            self.logger.info("Saving SQL statements to file...")
            
            try:
                with open(sql_output, 'w', encoding='utf-8') as f:
                    f.write("-- SQL INSERT statements for knowledge base\n")
                    f.write("-- Generated from chatbot data\n\n")
                    
                    for sql in sql_statements:
                        f.write(sql + "\n\n")
                
                self.sql_progress_var.set(100)
                self.sql_status_var.set("Conversion completed successfully!")
                
                self.logger.info("=" * 60)
                self.logger.info("SQL CONVERSION COMPLETED SUCCESSFULLY!")
                self.logger.info("=" * 60)
                self.logger.info(f"Generated {len(sql_statements)} SQL INSERT statements")
                self.logger.info(f"Output file: {sql_output}")
                self.logger.info("=" * 60)
                
                # Show completion message
                messagebox.showinfo("Success", 
                                  f"SQL conversion completed successfully!\n\n"
                                  f"Generated {len(sql_statements)} SQL INSERT statements\n"
                                  f"Output file: {sql_output}")
                
            except Exception as e:
                self.logger.error(f"Error saving SQL file: {e}")
                messagebox.showerror("Error", f"Error saving SQL file: {e}")
                
        except Exception as e:
            self.logger.error(f"An error occurred during SQL conversion: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"An error occurred during SQL conversion:\n{e}")
        finally:
            # Reset UI state
            self.is_converting = False
            self.convert_button.config(state=tk.NORMAL)
            self.stop_convert_button.config(state=tk.DISABLED)
            if self.sql_progress_var.get() < 100:
                self.sql_status_var.set("Ready to convert")
                
    def clear_sql_log(self):
        """Clear the SQL log display"""
        self.sql_log_text.delete(1.0, tk.END)
                
    def monitor_log_queue(self):
        """Monitor the log queue and update the log display"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                # Update both log displays
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.sql_log_text.insert(tk.END, message + "\n")
                self.sql_log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.monitor_log_queue)
        
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.sql_log_text.delete(1.0, tk.END)

def main():
    """Main function to run the GUI"""
    # Check dependencies
    try:
        import requests
        import bs4
        import google.generativeai
    except ImportError as e:
        messagebox.showerror("Missing Dependencies", 
                           f"Missing dependency: {e}\n\n"
                           "Please install dependencies with:\n"
                           "pip install -r requirements.txt")
        return
    
    # Create and run the GUI
    root = tk.Tk()
    
    # Set the theme (if available)
    try:
        style = ttk.Style()
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
    except:
        pass
    
    app = ScraperGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
