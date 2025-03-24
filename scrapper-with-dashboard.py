import streamlit as st
import pandas as pd
import os
import time
import random
from datetime import datetime, timedelta
import re
import feedparser
import requests
from bs4 import BeautifulSoup
import logging
import html
import plotly.express as px
import plotly.graph_objects as go
import json
import warnings

# Suppress the ScriptRunContext warnings
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

class RSSNewsScraperMultiSource:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        self.all_articles = []
        
        # Create output directory if it doesn't exist
        self.output_dir = 'news_data'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up logging
        self.setup_logging()
        
        # RSS feeds by category
        self.rss_feeds = {
            'US Politics': [
                {
                    'url': 'https://www.cnbc.com/id/10000113/device/rss/rss.html',
                    'source': 'CNBC Politics'
                },
                {
                    'url': 'http://feeds.washingtonpost.com/rss/politics',
                    'source': 'Washington Post Politics'
                },
                {
                    'url': 'https://feeds.npr.org/1014/rss.xml',
                    'source': 'NPR Politics'
                },
                {
                    'url': 'https://www.politico.com/rss/politicopicks.xml',
                    'source': 'Politico'
                },
                {
                    'url': 'https://thehill.com/rss/syndicator/19109',
                    'source': 'The Hill'
                }
            ],
            'Brazil Politics': [
                {
                    'url': 'https://feeds.folha.uol.com.br/poder/rss091.xml',
                    'source': 'Folha - Poder'
                },
                {
                    'url': 'https://g1.globo.com/rss/g1/politica/',
                    'source': 'G1 Política'
                },
                {
                    'url': 'https://www.poder360.com.br/feed/',
                    'source': 'Poder360'
                }
            ],
            'LATAM Politics': [
                {
                    'url': 'https://news.google.com/rss/search?q=latin+america+politics+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - LATAM Politics'
                },
                {
                    'url': 'https://www.reuters.com/arc/outboundfeeds/v3/category/latin-america/?outputType=xml',
                    'source': 'Reuters LATAM'
                }
            ],
            'Global Politics': [
                {
                    'url': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
                    'source': 'WSJ World'
                },
                {
                    'url': 'http://feeds.bbci.co.uk/news/world/rss.xml',
                    'source': 'BBC World'
                },
                {
                    'url': 'https://news.un.org/feed/subscribe/en/news/all/rss.xml',
                    'source': 'UN News'
                }
            ],
            'US Finance': [
                {
                    'url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
                    'source': 'CNBC Finance'
                },
                {
                    'url': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml',
                    'source': 'Wall Street Journal'
                },
                {
                    'url': 'http://feeds.marketwatch.com/marketwatch/topstories/',
                    'source': 'MarketWatch'
                },
                {
                    'url': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258',
                    'source': 'CNBC Markets'
                }
            ],
            'Europe Finance': [
                {
                    'url': 'https://www.ft.com/rss/home',
                    'source': 'Financial Times'
                },
                {
                    'url': 'http://feeds.bbci.co.uk/news/business/rss.xml',
                    'source': 'BBC Business'
                },
                {
                    'url': 'https://news.google.com/rss/search?q=europe+finance+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - Europe Finance'
                }
            ],
            'LATAM Finance': [
                {
                    'url': 'https://news.google.com/rss/search?q=latin+america+finance+economy+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - LATAM Finance'
                }
            ],
            'Brazil Finance': [
                {
                    'url': 'https://www.infomoney.com.br/feed/',
                    'source': 'InfoMoney'
                },
                {
                    'url': 'https://g1.globo.com/rss/g1/economia/',
                    'source': 'G1 Economia'
                },
                {
                    'url': 'https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml',
                    'source': 'Agência Brasil'
                }
            ],
            'Global Finance': [
                {
                    'url': 'https://news.google.com/rss/search?q=global+financial+markets+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - Global Markets'
                },
                {
                    'url': 'https://www.imf.org/en/News/Rss',
                    'source': 'IMF'
                },
                {
                    'url': 'https://www.bloomberg.com/feed/markets/sitemap_index.xml',
                    'source': 'Bloomberg Markets'
                }
            ],
            'China Finance': [
                {
                    'url': 'https://news.google.com/rss/search?q=china+economy+finance+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - China Finance'
                },
                {
                    'url': 'https://www.scmp.com/rss/4/feed',
                    'source': 'South China Morning Post - Economy'
                }
            ],
            'Canada Finance': [
                {
                    'url': 'https://news.google.com/rss/search?q=canada+economy+finance+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - Canada Finance'
                }
            ],
            'Business': [
                {
                    'url': 'https://www.cnbc.com/id/10001147/device/rss/rss.html',
                    'source': 'CNBC Business'
                },
                {
                    'url': 'https://www.ft.com/companies/rss',
                    'source': 'Financial Times - Companies'
                }
            ],
            'M&A': [
                {
                    'url': 'https://news.google.com/rss/search?q=merger+acquisition+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - M&A'
                },
                {
                    'url': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100345817',
                    'source': 'CNBC Deals and IPOs'
                }
            ],
            'Macroeconomics': [
                {
                    'url': 'https://news.google.com/rss/search?q=macroeconomics+inflation+rates+gdp+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - Macroeconomics'
                }
            ],
            'Microeconomics': [
                {
                    'url': 'https://news.google.com/rss/search?q=microeconomics+consumer+behavior+market+structure+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - Microeconomics'
                }
            ],
            'Trade War': [
                {
                    'url': 'https://news.google.com/rss/search?q=trade+war+tariffs+when:2d&hl=en-US&gl=US&ceid=US:en',
                    'source': 'Google News - Trade War'
                }
            ]
        }
    
    def setup_logging(self):
        """Set up basic logging to a file"""
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'rss_scraper_log.txt')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('RSSNewsScraperLogger')
        # Also log to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        
        self.logger.info("RSS Scraper initialized")
    
    def log(self, message, level='info'):
        """Wrapper for logging with fallback to print"""
        try:
            if level == 'info':
                self.logger.info(message)
            elif level == 'error':
                self.logger.error(message)
            elif level == 'warning':
                self.logger.warning(message)
        except:
            # Fallback to print if logging fails
            print(f"{level.upper()}: {message}")
    
    def clean_text(self, text):
        """Clean up text by removing HTML tags, decoding HTML entities, and normalizing whitespace"""
        if text is None:
            return ''
        
        # Convert to string if not already
        text = str(text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:!?\'"-]', '', text)
        
        return text.strip()
    
    def create_simple_summary(self, text, max_length=200):
        """Create a simple summary by truncating text to specified length"""
        if not text:
            return ""
        
        clean_text = self.clean_text(text)
        
        # If text is already short, return it as is
        if len(clean_text) <= max_length:
            return clean_text
        
        # Find the last period, question mark, or exclamation point within the max_length
        last_sentence_end = max(
            clean_text[:max_length].rfind('.'),
            clean_text[:max_length].rfind('?'),
            clean_text[:max_length].rfind('!')
        )
        
        # If found a sentence end, return up to that point
        if last_sentence_end > 0:
            return clean_text[:last_sentence_end + 1]
        
        # If no sentence end found, find the last space before max_length
        last_space = clean_text[:max_length].rfind(' ')
        if last_space > 0:
            return clean_text[:last_space] + '...'
        
        # If no space found, just truncate and add ellipsis
        return clean_text[:max_length] + '...'
    
    def is_recent_entry(self, entry, days=2):
        """Check if an entry is within the specified number of days"""
        # Try different date fields
        pub_date = None
        if hasattr(entry, 'published'):
            pub_date = entry.published
        elif hasattr(entry, 'pubDate'):
            pub_date = entry.pubDate
        elif hasattr(entry, 'updated'):
            pub_date = entry.updated
        
        if not pub_date:
            # If no date found, assume it's recent
            return True
        
        try:
            # Try to parse the date
            date_obj = None
            
            # Try different date formats
            formats_to_try = [
                '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
                '%a, %d %b %Y %H:%M:%S %Z',  # RFC 822 with timezone name
                '%Y-%m-%dT%H:%M:%S%z',      # ISO 8601
                '%Y-%m-%dT%H:%M:%SZ',       # ISO 8601 UTC
                '%Y-%m-%d %H:%M:%S',        # Basic format
                '%a %b %d %H:%M:%S %z %Y'   # Twitter format
            ]
            
            for fmt in formats_to_try:
                try:
                    date_obj = datetime.strptime(pub_date, fmt)
                    break
                except:
                    continue
            
            # If no format worked, try email utils
            if not date_obj:
                try:
                    from email.utils import parsedate_to_datetime
                    date_obj = parsedate_to_datetime(pub_date)
                except:
                    # If all parsing fails, return True (assume it's recent)
                    return True
            
            # Check if the entry is within the specified number of days
            cutoff_date = datetime.now() - timedelta(days=days)
            return date_obj >= cutoff_date
            
        except Exception as e:
            self.log(f"Error parsing date: {pub_date} - {str(e)}", 'warning')
            # If there's an error, return True (assume it's recent)
            return True
    
    def get_feed_data(self, feed_url, source_name, category):
        """Parse RSS feed and extract article information"""
        self.log(f"Fetching RSS feed: {feed_url} for {source_name}")
        
        try:
            # Add a small random delay to avoid too many simultaneous requests
            time.sleep(random.uniform(0.5, 2))
            
            # Parse the feed
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                self.log(f"No entries found in feed for {source_name}", 'warning')
                return []
            
            self.log(f"Found {len(feed.entries)} entries in feed for {source_name}")
            
            # Process entries (only those from the past 2 days)
            articles = []
            for entry in feed.entries:
                try:
                    # Skip if not recent
                    if not self.is_recent_entry(entry, days=2):
                        continue
                    
                    # Extract data from entry
                    title = entry.title if hasattr(entry, 'title') else "No title"
                    link = entry.link if hasattr(entry, 'link') else ""
                    
                    # Try different fields for summary/description
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = entry.summary
                    elif hasattr(entry, 'description'):
                        summary = entry.description
                    elif hasattr(entry, 'content'):
                        # Some feeds use content instead of summary
                        summary = entry.content[0].value if entry.content else ""
                    
                    # Clean the summary text
                    summary = self.clean_text(summary)
                    
                    # Get publication date
                    pub_date = None
                    if hasattr(entry, 'published'):
                        pub_date = entry.published
                    elif hasattr(entry, 'pubDate'):
                        pub_date = entry.pubDate
                    elif hasattr(entry, 'updated'):
                        pub_date = entry.updated
                    
                    # Format date or use current date
                    if pub_date:
                        try:
                            # Try to parse the date, but use current date as fallback
                            date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                            pub_date = date_obj.strftime("%Y-%m-%d")
                        except:
                            try:
                                # Try alternative format
                                from email.utils import parsedate_to_datetime
                                date_obj = parsedate_to_datetime(pub_date)
                                pub_date = date_obj.strftime("%Y-%m-%d")
                            except:
                                # If parsing fails, use the original string
                                pass
                    else:
                        pub_date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Add to articles list
                    articles.append({
                        'headline': self.clean_text(title),
                        'summary': summary,
                        'url': link,
                        'source': source_name,
                        'category': category,
                        'timestamp': pub_date
                    })
                    
                except Exception as e:
                    self.log(f"Error processing entry for {source_name}: {str(e)}", 'error')
            
            self.log(f"Successfully processed {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            self.log(f"Error fetching feed {feed_url} for {source_name}: {str(e)}", 'error')
            return []
    
    def scrape_category(self, category):
        """Scrape all feeds for a specific category"""
        self.log(f"Scraping category: {category}")
        
        if category not in self.rss_feeds:
            self.log(f"Unknown category: {category}", 'error')
            return
        
        for feed in self.rss_feeds[category]:
            try:
                feed_url = feed['url']
                source_name = feed['source']
                
                # Get articles from this feed
                articles = self.get_feed_data(feed_url, source_name, category)
                
                # Add to master list
                self.all_articles.extend(articles)
                
            except Exception as e:
                self.log(f"Error processing feed {feed} for category {category}: {str(e)}", 'error')
    
    def scrape_all_categories(self):
        """Scrape all categories defined in rss_feeds with no article limit"""
        self.log(f"Starting to scrape all categories for past 2 days")
        
        for category in self.rss_feeds.keys():
            try:
                self.scrape_category(category)
            except Exception as e:
                self.log(f"Error scraping category {category}: {str(e)}", 'error')
        
        self.log(f"Completed scraping all categories. Collected {len(self.all_articles)} articles total.")
    
    def save_results(self):
        """Save scraped articles to CSV files with error handling"""
        if not self.all_articles:
            self.log("No articles to save.", 'warning')
            return
        
        try:
            # Create a timestamp for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save all articles to one file
            df_all = pd.DataFrame(self.all_articles)
            all_file = os.path.join(self.output_dir, f"all_news_{timestamp}.csv")
            df_all.to_csv(all_file, index=False, encoding='utf-8-sig')
            self.log(f"Saved all {len(self.all_articles)} articles to {all_file}")
            
            # Save separate files by category
            categories = df_all['category'].unique()
            for category in categories:
                try:
                    df_category = df_all[df_all['category'] == category]
                    category_file = os.path.join(self.output_dir, f"{category.replace(' ', '_').lower()}_{timestamp}.csv")
                    df_category.to_csv(category_file, index=False, encoding='utf-8-sig')
                    self.log(f"Saved {len(df_category)} {category} articles to {category_file}")
                except Exception as e:
                    self.log(f"Error saving category {category}: {str(e)}", 'error')
        
        except Exception as e:
            self.log(f"Error saving results: {str(e)}", 'error')
            # Try a simplified approach as fallback
            try:
                simple_file = os.path.join(self.output_dir, "news_backup.csv")
                pd.DataFrame(self.all_articles).to_csv(simple_file, index=False)
                self.log(f"Saved backup file to {simple_file}")
            except:
                self.log("Critical failure: Could not save any results", 'error')
    
    def remove_duplicates(self):
        """Remove duplicate articles based on URL and headline"""
        if not self.all_articles:
            return
        
        self.log(f"Removing duplicates from {len(self.all_articles)} articles")
        
        # Convert to DataFrame for easier deduplication
        df = pd.DataFrame(self.all_articles)
        
        # Drop duplicates based on URL (most reliable method)
        df_no_url_dupes = df.drop_duplicates(subset=['url'])
        
        # Also check for duplicates in headlines (different URLs might have same content)
        df_no_dupes = df_no_url_dupes.drop_duplicates(subset=['headline'])
        
        # Convert back to list of dictionaries
        self.all_articles = df_no_dupes.to_dict('records')
        
        self.log(f"After removing duplicates: {len(self.all_articles)} articles remain")


# Function to generate sample data if scraper isn't available
def generate_sample_data():
    """Create sample news data for testing when scraper is unavailable"""
    sources = [
        'CNBC Finance', 'Wall Street Journal', 'Financial Times', 'BBC Business',
        'Politico', 'The Hill', 'InfoMoney', 'Folha - Poder', 'Google News - M&A'
    ]
    
    categories = [
        'US Finance', 'Global Finance', 'US Politics', 'Brazilian Politics', 
        'LATAM Politics', 'M&A', 'Macroeconomics', 'Trade War'
    ]
    
    headlines = [
        "Central Bank Raises Interest Rates Amid Inflation Concerns",
        "Government Announces New Infrastructure Package",
        "Tech Giants Face Antitrust Scrutiny",
        "Global Markets React to Trade Tensions",
        "Oil Prices Surge on Supply Concerns",
        "Election Results Impact Market Sentiment",
        "New Regulations for Banking Sector Announced",
        "Retail Sales Data Shows Economic Recovery",
        "Major Merger Announced Between Tech Companies",
        "Brazilian Currency Gains Against Dollar"
    ]
    
    summaries = [
        "The decision comes as inflation reached its highest level in a decade, prompting monetary policy tightening.",
        "The $2 trillion package aims to rebuild aging infrastructure and create millions of jobs over the next decade.",
        "Regulators are investigating potential anticompetitive practices among major technology companies.",
        "Global markets experienced volatility as trade negotiations between major economies stalled.",
        "Crude oil prices increased by 5% following production cuts and geopolitical tensions.",
        "Markets responded positively to the election outcome, with banking and healthcare sectors seeing gains.",
        "New regulatory framework aims to increase capital requirements and enhance consumer protections.",
        "Consumer spending rose 2.4% month-over-month, indicating economic resilience despite challenges.",
        "The merger will create a new entity valued at over $50 billion, pending regulatory approval.",
        "The Brazilian real strengthened against the U.S. dollar following positive economic data."
    ]
    
    data = []
    
    # Create sample articles
    for i in range(100):
        source_index = i % len(sources)
        source = sources[source_index]
        
        # Assign category based on source
        if source in ['CNBC Finance', 'Wall Street Journal']:
            category = 'US Finance'
        elif source in ['Financial Times', 'BBC Business']:
            category = 'Global Finance'
        elif source in ['Politico', 'The Hill']:
            category = 'US Politics'
        elif source in ['InfoMoney']:
            category = 'Brazil Finance'
        elif source in ['Folha - Poder']:
            category = 'Brazilian Politics'
        elif source in ['Google News - M&A']:
            category = 'M&A'
        else:
            category = categories[i % len(categories)]
        
        # Create a date within the past two weeks
        days_ago = i % 14
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Select headline and summary
        headline_index = i % len(headlines)
        headline = f"{headlines[headline_index]} - {i+1}"
        summary = summaries[headline_index]
        
        data.append({
            'headline': headline,
            'summary': summary,
            'url': f"https://example.com/{source.lower().replace(' ', '')}/article{i+1}",
            'source': source,
            'category': category,
            'timestamp': date
        })
    
    return data

# Function to get a list of saved news files
def get_saved_news_files():
    """Get a list of all saved news CSV files"""
    if not os.path.exists('news_data'):
        return []
    
    files = [f for f in os.listdir('news_data') if f.startswith("all_news_") and f.endswith(".csv")]
    return sorted(files, reverse=True)

# Function to load a specific news file
def load_news_file(filename):
    """Load a specific news CSV file"""
    filepath = os.path.join('news_data', filename)
    try:
        df = pd.read_csv(filepath)
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading file {filename}: {str(e)}")
        return []

# Set up the Streamlit page
st.set_page_config(
    page_title="News Repository Dashboard",
    page_icon="📰",
    layout="wide"
)

# Create data directory if it doesn't exist
DATA_DIR = "news_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Create session state to store data
if 'news_data' not in st.session_state:
    st.session_state.news_data = None
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# Header
st.title("News Repository Dashboard")
st.markdown("### Politics, Finance, Business & Economics News Repository")

# Sidebar controls
st.sidebar.header("Controls")

# Status indicators
st.sidebar.subheader("System Status")
st.sidebar.markdown("RSS Scraper: ✅ Available")

# Data loading options
st.sidebar.subheader("Data Sources")
sample_data_button = st.sidebar.button("Load Sample Data")
rss_fetch_button = st.sidebar.button("Fetch RSS News")

# Load previous data
st.sidebar.subheader("Load Previous Data")
saved_files = get_saved_news_files()
if saved_files:
    selected_file = st.sidebar.selectbox("Select saved data file", saved_files)
    load_file_button = st.sidebar.button("Load Selected File")
    
    if load_file_button:
        with st.spinner(f"Loading data from {selected_file}..."):
            st.session_state.news_data = load_news_file(selected_file)
            st.session_state.current_file = selected_file
            st.session_state.last_updated = datetime.now()
            st.success(f"Loaded {len(st.session_state.news_data)} news items from {selected_file}")
            st.rerun()
else:
    st.sidebar.info("No saved data files found")

# Button handlers
if sample_data_button:
    with st.spinner("Generating sample data..."):
        st.session_state.news_data = generate_sample_data()
        st.session_state.current_file = "sample_data"
        st.session_state.last_updated = datetime.now()
    st.success(f"Loaded {len(st.session_state.news_data)} sample news items")
    st.rerun()

if rss_fetch_button:
    with st.spinner("Fetching RSS news feeds..."):
        try:
            # Create RSS scraper and fetch data
            scraper = RSSNewsScraperMultiSource()
            st.info("Scraper created successfully. Fetching RSS feeds...")
            
            # Scrape all categories (now with no limit per feed)
            scraper.scrape_all_categories() 
            
            # Log the results
            st.info(f"Scraping completed. Found {len(scraper.all_articles)} articles.")
            
            # Remove duplicates
            scraper.remove_duplicates()
            st.info(f"After removing duplicates: {len(scraper.all_articles)} articles.")
            
            if scraper.all_articles:
                st.session_state.news_data = scraper.all_articles
                st.session_state.last_updated = datetime.now()
                
                # Save the data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"all_news_{timestamp}.csv"
                filepath = os.path.join(DATA_DIR, filename)
                
                df = pd.DataFrame(scraper.all_articles)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                
                st.session_state.current_file = filename
                st.success(f"Successfully fetched {len(scraper.all_articles)} articles from RSS feeds")
            else:
                st.error("RSS fetch completed but no articles found")
                if st.session_state.news_data is None:
                    st.session_state.news_data = generate_sample_data()
                    st.session_state.current_file = "sample_data"
        except Exception as e:
            st.error(f"Error during RSS fetch: {str(e)}")
            import traceback
            st.code(traceback.format_exc(), language="python")
            if st.session_state.news_data is None:
                st.session_state.news_data = generate_sample_data()
                st.session_state.current_file = "sample_data"
    st.rerun()

# Main dashboard content
if st.session_state.news_data is None or len(st.session_state.news_data) == 0:
    st.info("No data loaded. Please load sample data, fetch RSS news, or select a saved file.")
else:
    # Convert to DataFrame for processing
    df = pd.DataFrame(st.session_state.news_data)
    
    # Display current dataset info
    st.markdown(f"**Current dataset:** {st.session_state.current_file or 'None'}")
    if st.session_state.last_updated:
        st.markdown(f"**Last updated:** {st.session_state.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Articles", len(df))
    with col2:
        st.metric("News Categories", df['category'].nunique())
    with col3:
        st.metric("News Sources", df['source'].nunique())
    
    # Filters
    st.subheader("Filter News Articles")
    
    # Create columns for filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Date filter
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        min_date = df['date'].min()
        max_date = df['date'].max()
        selected_date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
    with col2:
        # Category filter
        categories = sorted(df['category'].unique())
        selected_categories = st.multiselect("Categories", categories)
    
    with col3:
        # Source filter
        sources = sorted(df['source'].unique())
        selected_sources = st.multiselect("Sources", sources)
    
    with col4:
        # Search filter
        search_query = st.text_input("Search headlines or summaries")
    
    # Apply filters
    filtered_df = df.copy()
    
    # Date filter
    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
    
    # Category filter
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    
    # Source filter
    if selected_sources:
        filtered_df = filtered_df[filtered_df['source'].isin(selected_sources)]
    
    # Search filter
    if search_query:
        search_query = search_query.lower()
        filtered_df = filtered_df[
            filtered_df['headline'].str.lower().str.contains(search_query) | 
            filtered_df['summary'].str.lower().str.contains(search_query)
        ]
    
    # Sort by date (newest first)
    filtered_df = filtered_df.sort_values('timestamp', ascending=False)
    
    # Show the filtered dataframe
    st.subheader(f"News Articles ({len(filtered_df)} results)")
    
    # Display the table
    st.dataframe(
        filtered_df[['timestamp', 'category', 'source', 'headline', 'summary', 'url']],
        column_config={
            "timestamp": "Date",
            "category": "Category",
            "source": "Source",
            "headline": "Headline",
            "summary": "Summary",
            "url": st.column_config.LinkColumn("Link")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Download button for filtered data
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name=f"filtered_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

# Run the app
if __name__ == "__main__":
    # This code runs when the script is executed directly
    pass
