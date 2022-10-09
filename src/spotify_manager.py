import json
import requests
import sys


class Item:
    """
    Generic class to represent a Spotify item.
    """
    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def __repr__(self):
        return f"Item('{self.id}', '{self.name}')"


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

    data = response.json()

    # Parse the data to create a track list.
    tracks = []
    for item in data["items"]:
        track_data = item["track"]
        track = Item(track_data["id"], track_data["name"])
        tracks.append(track)

    return tracks


if __name__ == "__main__":
    # Get command line arguments.
    token = sys.argv[1]
    playlist_id = sys.argv[2]

    tracks = get_spotify_playlist_items(token, playlist_id)
    for track in tracks:
        print(track)
