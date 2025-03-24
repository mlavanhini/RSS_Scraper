import feedparser
import pandas as pd
import time
import random
import os
from datetime import datetime, timedelta
import re
import requests
from bs4 import BeautifulSoup
import logging
import html
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


# Run the scraper if executed directly
if __name__ == "__main__":
    # Create scraper instance
    scraper = RSSNewsScraperMultiSource()
    
    # Scrape all categories
    scraper.scrape_all_categories()
    
    # Remove duplicate articles
    scraper.remove_duplicates()
    
    # Save results
    scraper.save_results()
    
    print(f"Scraping completed! Found {len(scraper.all_articles)} articles total.")