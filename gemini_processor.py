import google.generativeai as genai
import json
import time
from typing import List, Dict, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class GeminiProcessor:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
    def process_content_for_knowledge_base(self, content: str, url: str, title: str) -> Dict:
        """Process content using Gemini to create structured knowledge base entries"""
        try:
            prompt = f"""
            Analyze the following web page content and create a structured knowledge base entry for an automated chatbot.
            
            URL: {url}
            Title: {title}
            Content: {content[:Config.MAX_CONTENT_LENGTH]}
            
            Please provide a JSON response with the following structure:
            {{
                "summary": "A concise summary of the page content (2-3 sentences)",
                "key_topics": ["topic1", "topic2", "topic3"],
                "faq_questions": [
                    {{
                        "question": "A potential FAQ question based on the content",
                        "answer": "A direct answer from the content"
                    }}
                ],
                "important_facts": ["fact1", "fact2", "fact3"],
                "keywords": ["keyword1", "keyword2", "keyword3"],
                "content_type": "article|product|service|help|about|contact|other",
                "relevance_score": 0.8
            }}
            
            Focus on creating useful FAQ questions and answers that would help users find information quickly.
            Make sure all answers are directly derived from the provided content.
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse the JSON response
            try:
                # Extract JSON from the response text
                response_text = response.text
                
                # Find JSON in the response (sometimes it's wrapped in markdown)
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif '{' in response_text and '}' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
                
                processed_data = json.loads(json_text)
                
                # Add metadata
                processed_data['url'] = url
                processed_data['title'] = title
                processed_data['processed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                
                return processed_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response text: {response.text}")
                
                # Fallback: create a basic structure
                return self._create_fallback_entry(content, url, title)
                
        except Exception as e:
            logger.error(f"Error processing content with Gemini: {e}")
            return self._create_fallback_entry(content, url, title)
    
    def _create_fallback_entry(self, content: str, url: str, title: str) -> Dict:
        """Create a fallback knowledge base entry when Gemini processing fails"""
        # Simple keyword extraction
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3 and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [word for word, freq in keywords]
        
        return {
            'url': url,
            'title': title,
            'summary': f"Content from {title} - {content[:200]}...",
            'key_topics': keywords[:5],
            'faq_questions': [
                {
                    'question': f"What is {title}?",
                    'answer': content[:300] + "..." if len(content) > 300 else content
                }
            ],
            'important_facts': [content[:200] + "..." if len(content) > 200 else content],
            'keywords': keywords,
            'content_type': 'other',
            'relevance_score': 0.5,
            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'processing_method': 'fallback'
        }
    
    def batch_process_pages(self, scraped_data: List[Dict]) -> List[Dict]:
        """Process multiple pages in batch"""
        processed_data = []
        
        logger.info(f"Processing {len(scraped_data)} pages with Gemini...")
        
        for i, page_data in enumerate(scraped_data):
            try:
                logger.info(f"Processing page {i+1}/{len(scraped_data)}: {page_data['title']}")
                
                # Combine different content elements
                content_parts = []
                
                if page_data.get('main_heading'):
                    content_parts.append(f"Main Heading: {page_data['main_heading']}")
                
                if page_data.get('meta_description'):
                    content_parts.append(f"Description: {page_data['meta_description']}")
                
                # Add headings
                for heading in page_data.get('headings', []):
                    content_parts.append(f"{'#' * heading['level']} {heading['text']}")
                
                # Add paragraphs
                for paragraph in page_data.get('paragraphs', []):
                    content_parts.append(paragraph)
                
                # Add list items
                for item in page_data.get('list_items', []):
                    content_parts.append(f"• {item}")
                
                combined_content = "\n\n".join(content_parts)
                
                # Process with Gemini
                processed_entry = self.process_content_for_knowledge_base(
                    combined_content,
                    page_data['url'],
                    page_data['title']
                )
                
                processed_data.append(processed_entry)
                
                # Add delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing page {page_data['url']}: {e}")
                # Add fallback entry
                fallback_entry = self._create_fallback_entry(
                    page_data.get('content', ''),
                    page_data['url'],
                    page_data['title']
                )
                processed_data.append(fallback_entry)
        
        logger.info(f"Completed processing {len(processed_data)} pages")
        return processed_data
