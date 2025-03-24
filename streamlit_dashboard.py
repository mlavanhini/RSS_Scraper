import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import time
import random
import warnings

# Suppress the ScriptRunContext warnings
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

# Import the RSS-based news scraper
try:
    from rss_scraper import RSSNewsScraperMultiSource
    RSS_SCRAPER_AVAILABLE = True
    print("RSS Scraper module loaded successfully")
except ImportError as e:
    RSS_SCRAPER_AVAILABLE = False
    print(f"RSS Scraper import error: {str(e)}")

# Set up the Streamlit page
st.set_page_config(
    page_title="News Repository Dashboard",
    page_icon="📰",
    layout="wide"
)

# Create data directory if it doesn't exist
DATA_DIR = "news_data"
os.makedirs(DATA_DIR, exist_ok=True)

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
    if not os.path.exists(DATA_DIR):
        return []
    
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("all_news_") and f.endswith(".csv")]
    return sorted(files, reverse=True)

# Function to load a specific news file
def load_news_file(filename):
    """Load a specific news CSV file"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        df = pd.read_csv(filepath)
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading file {filename}: {str(e)}")
        return []

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
st.sidebar.markdown(f"RSS Scraper: {'✅ Available' if RSS_SCRAPER_AVAILABLE else '❌ Not Available'}")

# Data loading options
st.sidebar.subheader("Data Sources")
sample_data_button = st.sidebar.button("Load Sample Data")
rss_fetch_button = st.sidebar.button("Fetch RSS News", disabled=not RSS_SCRAPER_AVAILABLE)

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

if rss_fetch_button and RSS_SCRAPER_AVAILABLE:
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
