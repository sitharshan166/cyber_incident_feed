import shodan
import json
from datetime import datetime

# Replace with the path to your sources.json file
SOURCE_FILE = "sources.json"
FEED_FILE = "cyber_incident_feed.json"

def load_sources(filename):
    """
    Load sources from a JSON file.

    Args:
        filename (str): Path to the JSON file.

    Returns:
        list: List of source configurations.
    """
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Source file {filename} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}.")
        return []

def fetch_shodan_data(api_key, query, limit=100):
    """
    Fetch data from Shodan API for a specific query.

    Args:
        api_key (str): Shodan API key.
        query (str): The search query for Shodan.
        limit (int): Maximum number of results to fetch.

    Returns:
        list: A list of incident dictionaries.
    """
    api = shodan.Shodan(api_key)
    incidents = []
    try:
        results = api.search(query, limit=limit)
        for result in results.get('matches', []):
            incident = {
                "source": "Shodan",
                "title": f"Service Detected on {result['ip_str']}",
                "link": f"https://www.shodan.io/host/{result['ip_str']}",
                "published": datetime.utcnow().isoformat(),
                "summary": f"Detected service on IP {result['ip_str']} using port {result.get('port', 'Unknown')}.",
                "ip": result['ip_str'],
                "port": result.get('port', "Unknown"),
                "vulnerability": result.get('data', "No specific details")
            }
            incidents.append(incident)
    except shodan.APIError as e:
        print(f"Shodan API Error: {e}")
    return incidents

def save_feed_to_file(incidents, filename):
    """
    Save incidents to a JSON file.

    Args:
        incidents (list): List of incidents to save.
        filename (str): Output JSON file name.
    """
    try:
        with open(filename, "w") as file:
            json.dump(incidents, file, indent=4)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data: {e}")

if __name__ == "__main__":
    # Load sources from the sources.json file
    sources = load_sources(SOURCE_FILE)

    # Initialize a list to hold all fetched incidents
    all_incidents = []

    # Iterate through sources to fetch data
    for source in sources:
        if source.get("name") == "Shodan" and source.get("enabled", False):
            print(f"Fetching from Shodan with query: {source['query']}")
            shodan_incidents = fetch_shodan_data(
                api_key=source["api_key"],
                query=source["query"],
                limit=source.get("limit", 100)
            )
            all_incidents.extend(shodan_incidents)

    # Save the combined incidents to the feed file
    save_feed_to_file(all_incidents, FEED_FILE)
