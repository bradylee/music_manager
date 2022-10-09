import json
import logging
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
        return f"Item({repr(self.id)}, {repr(self.name)})"


class Track(Item):
    """
    Represents a track.
    """
    def __init__(self, _id, name, album=None):
        super().__init__(_id, name)
        self.album = album

    def __repr__(self):
        return f"Track({repr(self.id)}, {repr(self.name)}, album={self.album})"


class Album(Item):
    """
    Represents an album.
    """
    def __init__(self, _id, name, artist=None):
        super().__init__(_id, name)
        self.artist = artist

    def __repr__(self):
        return f"Album({repr(self.id)}, {repr(self.name)}, artist={self.artist})"


class Artist(Item):
    """
    Represents an artist.
    """
    def __init__(self, _id, name):
        super().__init__(_id, name)

    def __repr__(self):
        return f"Artist({repr(self.id)}, {repr(self.name)})"


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
    Returns a list of Track objects.
    """
    # API endpoint to get tracks from a playlist.
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Execute the GET request.
    headers = get_spotify_request_headers(token)
    response = requests.get(endpoint, headers=headers)

    if response.status_code != 200:
        logging.error(f"Request responded with status {response.status_code}")
        return None

    data = response.json()

    # Parse the data to create a track list.
    tracks = []
    for item in data["items"]:
        track_data = item["track"]
        album_data = track_data["album"]
        # Assume the artist listed first is the main artist.
        artist_data = album_data["artists"][0]

        # Create objects.
        artist = Artist(artist_data["id"], artist_data["name"])
        album = Album(album_data["id"], album_data["name"], artist=artist)
        track = Track(track_data["id"], track_data["name"], album=album)
        tracks.append(track)

    return tracks


if __name__ == "__main__":
    # Get command line arguments.
    token = sys.argv[1]
    playlist_id = sys.argv[2]

    # Configure logger.
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Print playlist items.
    tracks = get_spotify_playlist_items(token, playlist_id)
    if tracks is not None:
        for track in tracks:
            print(track)
