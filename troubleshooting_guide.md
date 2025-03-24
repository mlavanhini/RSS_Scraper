# Troubleshooting Guide

## Common Issues and Solutions

### "Missing ScriptRunContext" Warnings

**Problem:**
```
Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
```

**Solution:**
These warnings are harmless and can be safely ignored as they don't affect functionality. The application has been updated with warning filters to suppress these messages. If you're still seeing them, you can:

1. Run Streamlit with the `--logger.level=error` flag:
   ```
   streamlit run streamlit_dashboard.py --logger.level=error
   ```

2. Or set an environment variable before running:
   ```
   export STREAMLIT_LOGGER_LEVEL=error
   streamlit run streamlit_dashboard.py
   ```

### RSS Feed Connectivity Issues

**Problem:** The RSS feeds fail to load or return no results.

**Solutions:**
1. Check your internet connection
2. Verify the RSS feed URLs are still valid (RSS feeds can change without notice)
3. Try running with a longer timeout:
   ```python
   # In rss_scraper.py, increase the timeout in feedparser.parse:
   feed = feedparser.parse(feed_url, timeout=30)
   ```

### Date Parsing Errors

**Problem:** Errors related to parsing article dates.

**Solution:**
The scraper attempts to handle various date formats, but if you encounter specific feeds with unusual date formats, you may need to add additional date parsing formats in the `is_recent_entry` method in `rss_scraper.py`.

### Memory Issues with Large Datasets

**Problem:** The application crashes or becomes slow with large datasets.

**Solutions:**
1. Reduce the number of days to scrape (currently set to 2 days)
2. Add pagination to the table display:

   ```python
   # In streamlit_dashboard.py, add pagination:
   page_size = st.sidebar.slider("Articles per page", 10, 100, 25)
   page_number = st.sidebar.number_input("Page", min_value=1, value=1)
   
   start_idx = (page_number - 1) * page_size
   end_idx = start_idx + page_size
   
   display_df = filtered_df.iloc[start_idx:end_idx]
   ```

### GitHub/VSCode Deployment Issues

**Problem:** Deployment issues in GitHub Codespaces or VSCode.

**Solutions:**
1. Make sure all dependencies are correctly listed in requirements.txt
2. For GitHub Codespaces, ensure you're exposing the Streamlit port (typically 8501)
3. Use the following command to make Streamlit accessible from outside:
   ```
   streamlit run streamlit_dashboard.py --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
   ```

## Performance Optimization

If the dashboard becomes slow with large datasets:

1. **Implement caching:**
   ```python
   @st.cache_data(ttl=3600)  # Cache for 1 hour
   def load_news_file(filename):
       # Existing code...
   ```

2. **Reduce data loading:**
   - Load only the columns you need
   - Implement server-side pagination

3. **Optimize filters:**
   - Apply filters in a specific order (date first, then category, etc.)
   - Use more efficient string operations

## Getting Help

If you continue to experience issues:

1. Check the logs in the `logs/` directory
2. Create an issue on the GitHub repository with:
   - A description of the problem
   - Any error messages
   - Steps to reproduce the issue
