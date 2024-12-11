import shodan
import json
from datetime import datetime

# Replace with your Shodan API Key
SHODAN_API_KEY = "your_shodan_api_key"

# File where incidents are stored
FEED_FILE = "cyber_incident_feed.json"

def fetch_shodan_data(query, limit=100):
    """
    Fetch data from Shodan API for a specific query.

    Args:
        query (str): The search query for Shodan.
        limit (int): Maximum number of results to fetch.

    Returns:
        list: A list of incident dictionaries.
    """
    api = shodan.Shodan(SHODAN_API_KEY)
    incidents = []
    try:
        results = api.search(query, limit=limit)
        for result in results.get('matches', []):
            incident = {
                "source": "Shodan",
                "title": f"Service Detected on {result['ip_str']}",
                "link": f"https://www.shodan.io/host/{result['ip_str']}",  # Link to Shodan details
                "published": datetime.utcnow().isoformat(),
                "summary": f"Detected service on IP {result['ip_str']} using port {result.get('port', 'Unknown')}.",
                "ip": result['ip_str'],
                "port": result.get('port', "Unknown"),
                "vulnerability": result.get('data', "No specific details")
            }
            incidents.append(incident)
    except shodan.APIError as e:
        print(f"Error fetching data for query '{query}': {e}")
    return incidents

def load_existing_feed(filename):
    """
    Load existing cyber incident feed from JSON file.

    Args:
        filename (str): JSON file containing the feed.

    Returns:
        list: List of incidents.
    """
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_feed_to_file(incidents, filename):
    """
    Save incidents to a JSON file.

    Args:
        incidents (list): List of incidents to save.
        filename (str): Output JSON file name.
    """
    with open(filename, "w") as file:
        json.dump(incidents, file, indent=4)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # List of Shodan queries
    queries = [
        "port:22 country:IN",  # SSH services in India
        "port:80 country:IN",  # HTTP Servers in India
        "port:443 country:US",  # HTTPS Servers in the United States
        "port:3306 product:MySQL",  # MySQL Databases globally
        "port:27017 country:CN",  # MongoDB Databases in China
        "port:9200 product:ElasticSearch country:DE",  # ElasticSearch instances in Germany
        "port:3389 country:IN has_screenshot:true",  # RDP Servers in India with screenshots
        "default-password country:US",  # Devices with default passwords in the United States
        "product:Docker",  # Exposed Docker APIs globally
        "ssl:'example.com'",  # Devices with SSL certificates for example.com
        "product:Apache version:2.2 country:IN"  # Outdated Apache servers in India
    ]

    # Initialize an empty list to store incidents
    all_incidents = []

    for query in queries:
        print(f"Fetching data for query: {query}")
        incidents = fetch_shodan_data(query, limit=50)
        all_incidents.extend(incidents)

    # Load existing feed
    existing_feed = load_existing_feed(FEED_FILE)

    # Merge new incidents with existing feed
    updated_feed = existing_feed + all_incidents

    # Save updated feed to file
    save_feed_to_file(updated_feed, FEED_FILE)
