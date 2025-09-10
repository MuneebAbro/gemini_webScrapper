#!/usr/bin/env python3
"""
Convert chatbot data to SQL INSERT statements
"""

import json
import os
import sys
from typing import List, Dict
import google.generativeai as genai
from config import Config

class ChatbotToSQLConverter:
    def __init__(self):
        # Set up Gemini for category classification
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        else:
            self.model = None
            print("Warning: No Gemini API key found. Categories will be set to 'general'")
    
    def load_chatbot_data(self, filepath: str) -> Dict:
        """Load chatbot data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file '{filepath}': {e}")
            return None
    
    def classify_category_with_ai(self, question: str, answer: str) -> str:
        """Use Gemini AI to classify the category of a Q&A pair"""
        if not self.model:
            return 'general'
        
        try:
            prompt = f"""
            Analyze this question and answer pair and classify it into one of these categories:
            - services: Questions about what services/products are offered
            - pricing: Questions about costs, prices, fees
            - contact: Questions about how to contact, location, hours
            - support: Questions about help, troubleshooting, technical issues
            - policies: Questions about terms, conditions, policies, procedures
            - general: General information or other topics
            
            Question: {question}
            Answer: {answer}
            
            Return only the category name (e.g., "services", "pricing", "contact", "support", "policies", "general")
            """
            
            response = self.model.generate_content(prompt)
            category = response.text.strip().lower()
            
            # Validate category
            valid_categories = ['services', 'pricing', 'contact', 'support', 'policies', 'general']
            if category in valid_categories:
                return category
            else:
                return 'general'
                
        except Exception as e:
            print(f"Error classifying category: {e}")
            return 'general'
    
    def escape_sql_string(self, text: str) -> str:
        """Escape single quotes in SQL strings"""
        return text.replace("'", "''")
    
    def generate_sql_inserts(self, chatbot_data: Dict, business_id: str) -> List[str]:
        """Generate SQL INSERT statements from chatbot data"""
        sql_statements = []
        
        training_data = chatbot_data.get('training_data', [])
        
        if not training_data:
            print("No training data found in chatbot file")
            return sql_statements
        
        print(f"Processing {len(training_data)} Q&A pairs...")
        
        for i, item in enumerate(training_data):
            question = item.get('text', '').strip()
            answer = item.get('response', '').strip()
            
            if not question or not answer:
                print(f"Skipping item {i+1}: Missing question or answer")
                continue
            
            # Classify category using AI
            category = self.classify_category_with_ai(question, answer)
            
            # Escape SQL strings
            question_escaped = self.escape_sql_string(question)
            answer_escaped = self.escape_sql_string(answer)
            
            # Generate SQL INSERT statement
            sql = f"insert into knowledge_base (business_id, question, answer, category, priority)\nvalues\n('{business_id}', '{question_escaped}', '{answer_escaped}', '{category}', 1);"
            
            sql_statements.append(sql)
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(training_data)} items...")
        
        return sql_statements
    
    def save_sql_file(self, sql_statements: List[str], output_file: str):
        """Save SQL statements to a file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("-- SQL INSERT statements for knowledge base\n")
                f.write("-- Generated from chatbot data\n\n")
                
                for sql in sql_statements:
                    f.write(sql + "\n\n")
            
            print(f"SQL statements saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving SQL file: {e}")
    
    def convert(self, chatbot_file: str, business_id: str, output_file: str = None):
        """Main conversion function"""
        print("Chatbot Data to SQL Converter")
        print("=" * 40)
        
        # Load chatbot data
        chatbot_data = self.load_chatbot_data(chatbot_file)
        if not chatbot_data:
            return
        
        # Generate SQL statements
        sql_statements = self.generate_sql_inserts(chatbot_data, business_id)
        
        if not sql_statements:
            print("No SQL statements generated")
            return
        
        # Set default output file if not provided
        if not output_file:
            output_file = f"knowledge_base_inserts_{business_id}.sql"
        
        # Save to file
        self.save_sql_file(sql_statements, output_file)
        
        print(f"\nConversion completed!")
        print(f"Generated {len(sql_statements)} SQL INSERT statements")
        print(f"Output file: {output_file}")

def main():
    print("Chatbot Data to SQL Converter")
    print("=" * 40)
    
    # Get business ID from user
    business_id = input("Enter business ID: ").strip()
    if not business_id:
        print("Business ID is required")
        sys.exit(1)
    
    # Look for chatbot data file
    chatbot_files = [
        "chatbot_data.json",
        "knowledge_base/chatbot_data.json",
        "knowledge_base.json"
    ]
    
    chatbot_file = None
    for file in chatbot_files:
        if os.path.exists(file):
            chatbot_file = file
            break
    
    if not chatbot_file:
        print("Chatbot data file not found. Please specify the path:")
        chatbot_file = input("Enter path to chatbot data JSON file: ").strip()
        if not os.path.exists(chatbot_file):
            print(f"File not found: {chatbot_file}")
            sys.exit(1)
    
    print(f"Using chatbot data file: {chatbot_file}")
    
    # Ask for output file
    output_file = input("Enter output SQL file name (or press Enter for default): ").strip()
    if not output_file:
        output_file = None
    
    # Convert
    converter = ChatbotToSQLConverter()
    converter.convert(chatbot_file, business_id, output_file)

if __name__ == "__main__":
    main()
