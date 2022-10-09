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


def get_spotify_playlist_items(token, playlist_id):
    """
    Request items from a Spotify playlist.
    """
    # API endpoint to get tracks from a playlist.
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Execute the GET request.
    headers = get_spotify_request_headers(token)
    response = requests.get(endpoint, headers=headers)

    if response.status_code != 200:
        return None

    return response.json()


if __name__ == "__main__":
    # Get command line arguments.
    token = sys.argv[1]
    playlist_id = sys.argv[2]

    data = get_spotify_playlist_items(token, playlist_id)
    print(json.dumps(data, indent=4))
