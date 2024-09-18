import requests
import json

api_key = 'API_KEY' # Replace with your actual API key
url = f"https://tile.googleapis.com/v1/createSession?key={api_key}"

body = {
    "mapType": "terrain",
    "language": "en-US",
    "region": "US",
    "layerTypes": ["layerRoadmap"]
}

response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(body))

if response.status_code == 200:

    data = response.json()
    print("Session Token:", data.get('sessionToken'))
else:
    print(f"Failed to fetch session token. Status Code: {response.status_code}")
    print("Response:", response.text)

print(response)