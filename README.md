# Web Scraper Knowledge Base Generator

A powerful web scraper that extracts data from websites and creates structured knowledge bases in JSON format, optimized for automated chatbots. Uses Google's Gemini AI for intelligent content processing.

## Features

- **Comprehensive Web Scraping**: Extracts text, headings, links, and structured content
- **AI-Powered Processing**: Uses Gemini AI to create FAQ questions, summaries, and structured data
- **Chatbot-Ready Output**: Generates JSON knowledge bases optimized for chatbot training
- **Configurable**: Customizable scraping parameters and output formats
- **Robust Error Handling**: Graceful handling of network issues and parsing errors
- **Search Indexes**: Creates multiple indexes for efficient content retrieval

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key**:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Basic Usage

```bash
python main.py https://example.com
```

### Advanced Usage

```bash
# Scrape with custom parameters
python main.py https://example.com --max-pages 20 --delay 2.0 --output my_kb.json

# Skip Gemini processing for faster scraping
python main.py https://example.com --no-gemini

# Enable verbose logging
python main.py https://example.com --verbose
```

### Command Line Options

- `--max-pages`: Maximum number of pages to scrape (default: 50)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--output`: Output JSON filename (default: knowledge_base.json)
- `--output-dir`: Output directory (default: knowledge_base)
- `--no-gemini`: Skip Gemini processing (faster but less structured)
- `--min-content`: Minimum content length to include (default: 100)
- `--verbose`: Enable verbose logging

## Output Structure

The scraper generates two main files:

### 1. Knowledge Base (`knowledge_base.json`)

```json
{
  "metadata": {
    "website_url": "https://example.com",
    "created_at": "2024-01-01T12:00:00",
    "total_pages": 25,
    "total_faqs": 150,
    "content_types": {"article": 10, "product": 5, "help": 10}
  },
  "pages": [...],
  "search_index": {...},
  "faq_section": [...],
  "topics_index": {...},
  "keywords_index": {...}
}
```

### 2. Chatbot Data (`chatbot_data.json`)

```json
{
  "intents": ["faq_1", "faq_2", "page_1"],
  "responses": {
    "faq_1": "Answer to FAQ question 1",
    "faq_2": "Answer to FAQ question 2"
  },
  "training_data": [
    {
      "intent": "faq_1",
      "text": "What is your return policy?",
      "response": "Our return policy allows..."
    }
  ]
}
```

## Configuration

Create a `.env` file to customize settings:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Scraping Configuration
MAX_PAGES=50
DELAY_BETWEEN_REQUESTS=1.0
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Output Configuration
OUTPUT_DIR=knowledge_base
JSON_FILENAME=knowledge_base.json

# Content Processing
MIN_CONTENT_LENGTH=100
MAX_CONTENT_LENGTH=5000

# Gemini Model Configuration
GEMINI_MODEL=gemini-1.5-flash
MAX_TOKENS=1000
```

## How It Works

1. **Web Scraping**: Uses BeautifulSoup to extract content from web pages
2. **Content Processing**: Gemini AI analyzes content and creates structured data
3. **Knowledge Base Creation**: Formats data into searchable knowledge base
4. **Chatbot Optimization**: Creates training data for chatbot systems

## Example Use Cases

- **E-commerce Sites**: Extract product information, FAQs, and policies
- **Documentation Sites**: Create searchable knowledge bases from docs
- **Support Sites**: Generate FAQ databases for customer service
- **Educational Sites**: Extract course content and create study materials

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Make sure you've created a `.env` file with your API key
   - Or use `--no-gemini` flag to skip AI processing

2. **"No data was scraped"**
   - Check if the URL is accessible
   - Some sites may block automated requests
   - Try increasing the delay with `--delay 2.0`

3. **Rate limiting errors**
   - Increase delay between requests
   - Reduce max pages if needed

### Logs

Check `scraper.log` for detailed logging information.

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: XML/HTML parser
- `google-generativeai`: Gemini AI integration
- `python-dotenv`: Environment variable management
- `tqdm`: Progress bars

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!
