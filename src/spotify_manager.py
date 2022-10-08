import json
import requests
import sys


def get_spotify_request_headers(token):
    """
    Construct and return standard headers for Spotify requests.
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    return headers


if __name__ == "__main__":
    # Get command line arguments.
    token = sys.argv[1]
    playlist_id = sys.argv[2]

    # API endpoint to get tracks from a playlist.
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Execute the GET request.
    headers = get_spotify_request_headers(token)
    response = requests.get(endpoint, headers=headers)
    print(response.status_code)

    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4))
