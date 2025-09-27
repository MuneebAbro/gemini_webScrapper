# GUI Web Scraper Knowledge Base Generator

A graphical user interface for the Web Scraper Knowledge Base Generator that allows you to easily scrape websites and create knowledge bases for chatbots.

## Features

- **User-friendly GUI**: Simple interface with URL input and configuration options
- **Real-time Progress**: Progress bar and status updates during scraping
- **Live Logging**: Real-time log output showing scraping progress
- **Configurable Settings**: Adjust max pages, delay, content length, and more
- **Gemini AI Integration**: Optional AI processing for better content structuring
- **Output Management**: Choose output directory and filename
- **JSON to SQL Conversion**: Convert scraped data to SQL INSERT statements
- **Dual Converter Options**: Choose between AI-powered or simple keyword-based conversion
- **Auto-Conversion**: Automatically convert to SQL after scraping (saves time!)
- **Tabbed Interface**: Separate tabs for web scraping and SQL conversion

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Gemini API Key (Optional)
If you want to use Gemini AI processing, create a `.env` file in the project directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the GUI
```bash
python run_gui.py
```
or
```bash
python gui_scraper.py
```

## How to Use

### Web Scraping Tab

1. **Enter URL**: Type the website URL you want to scrape in the URL field
2. **Configure Settings**:
   - **Max Pages**: Maximum number of pages to scrape (1-1000)
   - **Delay**: Delay between requests in seconds (0.1-10.0)
   - **Min Content Length**: Minimum content length to include (10-1000 characters)
   - **Use Gemini AI**: Check to enable AI processing for better content structuring
   - **Auto-convert to SQL**: Check to automatically convert to SQL after scraping
   - **SQL Converter**: Choose between Simple or AI converter for auto-conversion
3. **Set Output**: Choose output directory and filename
4. **Business ID**: Enter business ID (required if auto-convert is enabled)
5. **Start Scraping**: Click "Start Scraping" to begin
6. **Monitor Progress**: Watch the progress bar and log output
7. **Stop if Needed**: Click "Stop" to interrupt the process

**Note**: When auto-convert is enabled, the scraper will automatically generate SQL INSERT statements after completing the scraping process, saving you time!

### JSON to SQL Tab

1. **Select JSON File**: Browse and select the chatbot data JSON file (usually `chatbot_data.json`)
2. **Enter Business ID**: Provide a unique business identifier for the SQL records
3. **Choose Converter Type**:
   - **Simple Converter**: Uses keyword-based category classification (faster, no API key needed)
   - **AI Converter**: Uses Gemini AI for intelligent category classification (requires API key)
4. **Set Output File**: Choose where to save the SQL file
5. **Start Conversion**: Click "Convert to SQL" to begin
6. **Monitor Progress**: Watch the progress bar and log output
7. **Stop if Needed**: Click "Stop" to interrupt the process

## GUI Components

### Tabbed Interface
The GUI now features two main tabs:

#### Web Scraping Tab
- **URL Input**: Enter the website URL to scrape
- **Configuration Panel**: Adjust scraping parameters
- **Auto-Convert Options**: Enable automatic SQL conversion with converter selection
- **Business ID Input**: Enter business identifier for SQL conversion
- **Output Settings**: Choose where to save results
- **Control Buttons**: Start/Stop scraping
- **Progress Bar**: Visual progress indicator
- **Status Label**: Current operation status
- **Log Output**: Real-time logging information

#### JSON to SQL Tab
- **File Browser**: Select JSON input file
- **Business ID Input**: Enter unique business identifier
- **Converter Selection**: Choose between AI or simple converter
- **Output Settings**: Choose SQL output file location
- **Control Buttons**: Start/Stop conversion
- **Progress Bar**: Visual progress indicator
- **Status Label**: Current operation status
- **Log Output**: Real-time logging information

### Configuration Options

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| Max Pages | Maximum pages to scrape | 50 | 1-1000 |
| Delay | Seconds between requests | 1.0 | 0.1-10.0 |
| Min Content Length | Minimum content to include | 100 | 10-1000 |
| Use Gemini AI | Enable AI processing | Auto-detect | Checkbox |
| Output Directory | Where to save files | knowledge_base | Browse |
| Output Filename | JSON output filename | knowledge_base.json | Text |

## Output Files

### Web Scraping Output
The scraper generates two main files:

1. **Knowledge Base JSON**: Structured data with all scraped content
2. **Chatbot Data JSON**: Formatted data ready for chatbot training

### Auto-Conversion Output
When auto-convert is enabled, the scraper also generates:

3. **SQL INSERT File**: Ready-to-use SQL INSERT statements (e.g., `knowledge_base_inserts_[business_id].sql`)

### SQL Conversion Output
The SQL converter generates:

1. **SQL INSERT File**: Ready-to-use SQL INSERT statements for database import
2. **Categorized Data**: Questions and answers automatically categorized into:
   - `services`: Questions about services/products offered
   - `pricing`: Questions about costs, prices, fees
   - `contact`: Questions about contact information, location, hours
   - `support`: Questions about help, troubleshooting, technical issues
   - `policies`: Questions about terms, conditions, policies, procedures
   - `general`: General information or other topics

## Tips for Best Results

### Web Scraping
1. **Start Small**: Begin with a low max pages count to test
2. **Respectful Scraping**: Use appropriate delays (1-2 seconds recommended)
3. **Check Logs**: Monitor the log output for any issues
4. **Use Gemini**: Enable Gemini AI for better content structuring
5. **Valid URLs**: Ensure URLs start with http:// or https://
6. **Auto-Convert**: Enable auto-conversion to save time and get SQL files immediately
7. **Business ID**: Always provide a meaningful business ID for SQL records

### SQL Conversion
1. **Use AI Converter**: For better category classification when API key is available
2. **Simple Converter**: Faster option when API key is not available
3. **Valid Business ID**: Use a unique identifier for your business/organization
4. **Check Output**: Review the generated SQL file before importing to database
5. **Backup Data**: Always backup your database before importing new data

## Troubleshooting

### Common Issues

#### Web Scraping Issues
1. **"Invalid URL" Error**: Make sure the URL starts with http:// or https://
2. **"Missing Dependencies" Error**: Run `pip install -r requirements.txt`
3. **"GEMINI_API_KEY not found"**: Either set the API key or uncheck "Use Gemini AI Processing"
4. **"Business ID required"**: Enter a business ID when auto-convert is enabled
5. **"GEMINI_API_KEY not found for AI SQL converter"**: Set API key or select Simple converter
6. **No Progress**: Check the log output for error messages
7. **Slow Scraping**: Increase the delay between requests

#### SQL Conversion Issues
1. **"File not found" Error**: Make sure the JSON file path is correct
2. **"No training data found"**: Ensure the JSON file contains chatbot training data
3. **"Invalid JSON" Error**: Check that the JSON file is properly formatted
4. **"Business ID required"**: Enter a valid business identifier
5. **"GEMINI_API_KEY not found"**: Set API key or use Simple Converter instead

### Getting Help

- Check the log output for detailed error messages
- Ensure all dependencies are installed
- Verify your internet connection
- Try with a different website URL

## Advanced Usage

### Command Line Alternative
If you prefer command line usage, you can still use the original `main.py`:
```bash
python main.py https://example.com --max-pages 20 --output my_kb.json
```

### Custom Configuration
You can modify the `config.py` file to change default settings, or use environment variables in a `.env` file.

## System Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux
- Internet connection
- Optional: Gemini API key for AI processing

## License

This project maintains the same license as the original web scraper.
