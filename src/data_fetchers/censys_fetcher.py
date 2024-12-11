import json
import requests
from censys.search import CensysHosts
from config import config

def load_sources():
    with open("config/sources.json", "r") as f:
        sources = json.load(f)
    return sources
def fetch_censys_data(query, limit=50):
    api_id = config["censys"]["api_id"]
    api_secret = config["censys"]["api_secret"]
    
    censys = CensysHosts(api_id,api_secret)
    # Perform search query on Censys
    try:
        results = censys.search(query, per_page=limit)
        return results
    except Exception as e:
        print(f"Error fetching data from Censys: {e}")
        return None
def parse_censys_data(results):
    if not results:
        print("No results found.")
        return []
    
    parsed_data = []
    for result in results["matches"]:
        parsed_data.append({
            "ip": result.get("ip", ""),
            "protocols": result.get("protocols", []),
            "location": result.get("location", {}),
            "timestamp": result.get("timestamp", ""),
        })
    return parsed_data

# Save the fetched Censys data into a JSON file
def save_to_file(data, filename="censys_data.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

def main():
    sources = load_sources()

    # Search the "enabled" sources to fetch data
    for source in sources:
        if source["enabled"] and source["name"] == "Censys":
            query = source["query"]
            print(f"Fetching data from Censys using query: {query}")
            data = fetch_censys_data(query, source["limit"])
            if data:
                parsed_data = parse_censys_data(data)
                save_to_file(parsed_data)

if __name__ == "__main__":
    main()
