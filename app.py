from flask import Flask, jsonify, request
import requests
import os
import json

# Base API URL
BASE_URL = "https://rickandmortyapi.com/api"

# Directory to save data
OUTPUT_DIR = "rick_and_morty_data"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)

def fetch_all_pages(endpoint):
    """
    Fetch all pages of data from the given API endpoint.
    """
    url = f"{BASE_URL}/{endpoint}"
    results = []
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data from {url}: {response.status_code}")
            break
        data = response.json()
        results.extend(data['results'])
        url = data.get('info', {}).get('next')  # Next page URL
    return results

def save_to_json(filename, data):
    """
    Save the filtered data to a JSON file.
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"Saved {len(data)} records to {filepath}")

def collect_and_filter_data():
    """
    Collect and filter data from the API and save to JSON.
    """
    # Fetch and filter characters data
    print("Fetching characters...")
    characters = fetch_all_pages("character")

    # Prepare data for JSON (Character Name, Location Name, Avatar Image URL)
    filtered_data = []
    for character in characters:
        character_name = character.get("name")
        location_name = character.get("location", {}).get("name")
        avatar_url = character.get("image")

        # If all required fields are present, append to data list
        if character_name and location_name and avatar_url:
            filtered_data.append({
                "Character Name": character_name,
                "Location Name": location_name,
                "Avatar URL": avatar_url
            })

    # Save to JSON
    save_to_json("filtered_characters.json", filtered_data)
    print("Data collection complete!")
    return filtered_data

@app.route('/rickandmorty', methods=['GET'])
def rick_and_morty_data():
    """
    Collect data if not already collected and return the data.
    """
    filepath = os.path.join(OUTPUT_DIR, "filtered_characters.json")

    # Check if data already exists
    if os.path.exists(filepath):
        print("Data already exists. Reading from file.")
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        print("Data not found. Collecting new data.")
        data = collect_and_filter_data()

    return jsonify(data), 200

# Healthcheck endpoint
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def home():
    return "Welcome to the Rick and Morty API Service!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
