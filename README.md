# El País Opinion Section Scraper

Selenium-based web scraper for El País Opinion section with BrowserStack cross-browser testing.

## Features

- Scrapes first 5 articles from El País Opinion section
- Extracts Spanish titles and content
- Translates titles to English using Google Translate API
- Downloads article cover images
- Analyzes word frequency in translated titles
- Runs parallel tests across 5 different browsers using BrowserStack

## Requirements

- Python 3.8+
- BrowserStack account (free trial available)
- Chrome browser (for local testing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/elpais-scraper.git
cd elpais-scraper
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure BrowserStack credentials in `main.py`:
```python
BS_USERNAME = "your_browserstack_username"
BS_KEY = "your_browserstack_access_key"
```

## Usage

### Local Testing
Run local test first to verify setup:
```bash
python local_test.py
```

### BrowserStack Parallel Testing
Run across 5 browsers simultaneously:
```bash
python main.py
```

## Output

- `output_*.txt` - Scraped content and analysis for each browser
- `images/browser_*/` - Downloaded article images organized by browser

## Browser Configurations

- Chrome on Windows 10
- Safari on macOS Big Sur
- Firefox on Windows 11
- Chrome on Samsung Galaxy S22
- Safari on iPhone 13

## Assignment Details

This project was created as part of a technical assessment for the Customer Engineering Team position. It demonstrates:

- Web scraping with Selenium
- API integration (Google Translate)
- Cross-browser testing
- Parallel execution
- Data analysis and text processing

## License

MIT