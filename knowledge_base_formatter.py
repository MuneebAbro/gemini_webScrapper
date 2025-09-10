import json
import os
from typing import List, Dict
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class KnowledgeBaseFormatter:
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        self.json_filename = Config.JSON_FILENAME
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_knowledge_base_structure(self, processed_data: List[Dict], website_url: str) -> Dict:
        """Create a comprehensive knowledge base structure"""
        
        # Calculate statistics
        total_pages = len(processed_data)
        content_types = {}
        total_faqs = 0
        total_keywords = set()
        
        for entry in processed_data:
            content_type = entry.get('content_type', 'other')
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            total_faqs += len(entry.get('faq_questions', []))
            total_keywords.update(entry.get('keywords', []))
        
        # Create knowledge base structure
        knowledge_base = {
            'metadata': {
                'website_url': website_url,
                'created_at': datetime.now().isoformat(),
                'total_pages': total_pages,
                'total_faqs': total_faqs,
                'total_keywords': len(total_keywords),
                'content_types': content_types,
                'version': '1.0'
            },
            'pages': processed_data,
            'search_index': self._create_search_index(processed_data),
            'faq_section': self._create_faq_section(processed_data),
            'topics_index': self._create_topics_index(processed_data),
            'keywords_index': self._create_keywords_index(processed_data)
        }
        
        return knowledge_base
    
    def _create_search_index(self, processed_data: List[Dict]) -> Dict:
        """Create a search index for quick lookups"""
        search_index = {
            'by_url': {},
            'by_title': {},
            'by_content_type': {},
            'by_relevance': []
        }
        
        for entry in processed_data:
            url = entry.get('url', '')
            title = entry.get('title', '')
            content_type = entry.get('content_type', 'other')
            relevance = entry.get('relevance_score', 0.5)
            
            # Index by URL
            search_index['by_url'][url] = {
                'title': title,
                'content_type': content_type,
                'relevance_score': relevance,
                'summary': entry.get('summary', '')
            }
            
            # Index by title
            if title:
                search_index['by_title'][title.lower()] = url
            
            # Index by content type
            if content_type not in search_index['by_content_type']:
                search_index['by_content_type'][content_type] = []
            search_index['by_content_type'][content_type].append({
                'url': url,
                'title': title,
                'relevance_score': relevance
            })
            
            # Index by relevance
            search_index['by_relevance'].append({
                'url': url,
                'title': title,
                'relevance_score': relevance
            })
        
        # Sort by relevance
        search_index['by_relevance'].sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return search_index
    
    def _create_faq_section(self, processed_data: List[Dict]) -> List[Dict]:
        """Create a consolidated FAQ section"""
        all_faqs = []
        
        for entry in processed_data:
            faqs = entry.get('faq_questions', [])
            for faq in faqs:
                faq_entry = {
                    'question': faq.get('question', ''),
                    'answer': faq.get('answer', ''),
                    'source_url': entry.get('url', ''),
                    'source_title': entry.get('title', ''),
                    'relevance_score': entry.get('relevance_score', 0.5)
                }
                all_faqs.append(faq_entry)
        
        # Sort by relevance score
        all_faqs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return all_faqs
    
    def _create_topics_index(self, processed_data: List[Dict]) -> Dict:
        """Create an index of topics and related pages"""
        topics_index = {}
        
        for entry in processed_data:
            topics = entry.get('key_topics', [])
            url = entry.get('url', '')
            title = entry.get('title', '')
            relevance = entry.get('relevance_score', 0.5)
            
            for topic in topics:
                if topic not in topics_index:
                    topics_index[topic] = []
                
                topics_index[topic].append({
                    'url': url,
                    'title': title,
                    'relevance_score': relevance
                })
        
        # Sort each topic's pages by relevance
        for topic in topics_index:
            topics_index[topic].sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return topics_index
    
    def _create_keywords_index(self, processed_data: List[Dict]) -> Dict:
        """Create an index of keywords and related pages"""
        keywords_index = {}
        
        for entry in processed_data:
            keywords = entry.get('keywords', [])
            url = entry.get('url', '')
            title = entry.get('title', '')
            relevance = entry.get('relevance_score', 0.5)
            
            for keyword in keywords:
                if keyword not in keywords_index:
                    keywords_index[keyword] = []
                
                keywords_index[keyword].append({
                    'url': url,
                    'title': title,
                    'relevance_score': relevance
                })
        
        # Sort each keyword's pages by relevance
        for keyword in keywords_index:
            keywords_index[keyword].sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return keywords_index
    
    def save_knowledge_base(self, knowledge_base: Dict, filename: str = None) -> str:
        """Save the knowledge base to a JSON file"""
        if filename is None:
            filename = self.json_filename
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Knowledge base saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            raise
    
    def create_chatbot_ready_format(self, knowledge_base: Dict) -> Dict:
        """Create a chatbot-optimized format"""
        chatbot_data = {
            'intents': [],
            'responses': {},
            'contexts': {},
            'entities': {},
            'training_data': []
        }
        
        # Extract FAQ questions as intents
        faq_section = knowledge_base.get('faq_section', [])
        for i, faq in enumerate(faq_section):
            intent_name = f"faq_{i+1}"
            chatbot_data['intents'].append(intent_name)
            chatbot_data['responses'][intent_name] = faq['answer']
            chatbot_data['training_data'].append({
                'intent': intent_name,
                'text': faq['question'],
                'response': faq['answer']
            })
        
        # Add page summaries as additional intents
        pages = knowledge_base.get('pages', [])
        for page in pages:
            if page.get('summary'):
                intent_name = f"page_{page['url'].replace('/', '_').replace(':', '_')}"
                chatbot_data['intents'].append(intent_name)
                chatbot_data['responses'][intent_name] = page['summary']
                chatbot_data['training_data'].append({
                    'intent': intent_name,
                    'text': page['title'],
                    'response': page['summary']
                })
        
        return chatbot_data
    
    def save_chatbot_format(self, chatbot_data: Dict, filename: str = "chatbot_data.json") -> str:
        """Save chatbot-optimized format"""
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chatbot_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Chatbot data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving chatbot data: {e}")
            raise
