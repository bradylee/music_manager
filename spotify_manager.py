import json
import requests
import sys

# Get command line arguments.
token = sys.argv[1]
playlist_id = sys.argv[2]

# Standard headers for Spotify requests.
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}

# API endpoint to get tracks from a playlist.
endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

# Execute the GET request.
response = requests.get(endpoint, headers=headers)
print(response.status_code)

if response.status_code == 200:
    print(json.dumps(response.json(), indent=4))
