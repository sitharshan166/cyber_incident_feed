import feedparser
import logging
import time
from datetime import datetime
from tenacity import retry, wait_fixed, stop_after_attempt
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CACHE_FILE = "certin_cache.json"
CACHE_TIME = 3600  # Cache for 1 hour

# Retry logic with tenacity
@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def fetch_certin(feed_url):
    cached_data = get_cached_data()
    if cached_data:
        logging.info("Using cached CERT-In data")
        return cached_data

    feed = feedparser.parse(feed_url)
    if feed.bozo:
        raise ValueError("Malformed feed")

    incidents = []
    for entry in feed.entries:
        parsed_entry = parse_entry(entry)
        if parsed_entry:
            incidents.append(parsed_entry)
    
    save_to_cache(incidents)
    return incidents

def parse_entry(entry):
    try:
        # Parse date to datetime format
        published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
        
        # Return structured data
        return {
            'title': entry.title,
            'link': entry.link,
            'published': published_date,
            'summary': entry.summary if 'summary' in entry else ''
        }
    except Exception as e:
        logging.error(f"Error parsing entry: {str(e)}")
        return None

def get_cached_data():
    if os.path.exists(CACHE_FILE):
        file_time = os.path.getmtime(CACHE_FILE)
        if time.time() - file_time < CACHE_TIME:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    return None

def save_to_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

