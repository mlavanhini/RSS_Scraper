# News Repository Dashboard

A Streamlit-based dashboard for collecting, storing, and browsing news articles from various sources.

## Overview

This application scrapes news articles from multiple RSS feeds covering various categories including:

- Politics (US, Brazil, LATAM, Global)
- Finance (US, Europe, LATAM, Brazil, Global, China, Canada)
- Business
- M&A
- Economics (Macro and Micro)
- Trade War

Articles are stored in CSV files and can be browsed, filtered, and searched through a user-friendly Streamlit interface.

## Features

- **Data Collection**: Fetch news articles from RSS feeds across multiple categories
- **Automatic Storage**: Save data to CSV files for later retrieval
- **Historical Access**: Load and browse previously collected news data
- **Advanced Filtering**: Filter articles by date, category, source, and text search
- **Responsive UI**: Clean table-based interface showing news article details
- **Export Capability**: Download filtered data as CSV

## Getting Started

### Prerequisites

- Python 3.7+
- Required Python packages (install via `pip install -r requirements.txt`):
  - streamlit
  - pandas
  - feedparser
  - plotly
  - beautifulsoup4
  - requests

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/news-repository-dashboard.git
   cd news-repository-dashboard
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

Run the Streamlit app:

```
streamlit run streamlit_dashboard.py
```

The application will open in your default web browser.

## Usage

1. **Fetch News**: Click "Fetch RSS News" to collect the latest articles from the past two days
2. **Browse Data**: View the articles in the data table
3. **Filter Results**: Use the filter controls to narrow down articles by date, category, source, or keyword
4. **Load Previous Data**: Select a previously saved data file from the dropdown to view historical data
5. **Export Data**: Download your filtered results using the "Download" button

## Project Structure

- `streamlit_dashboard.py`: Main Streamlit application code
- `rss_scraper.py`: RSS feed scraper implementation
- `news_data/`: Directory where news data is stored as CSV files
- `logs/`: Directory for log files

## Maintenance

- The application automatically keeps a record of all fetched data in the `news_data` directory
- Each data collection run creates a new timestamped CSV file
- No manual maintenance is required

## Troubleshooting

- If RSS feeds fail to load, check your internet connection
- If specific feeds consistently fail, they may have changed their URL or format
- Check the logs directory for detailed error information

## License

This project is licensed under the MIT License - see the LICENSE file for details.
