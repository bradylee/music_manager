import json
import logging
import requests

from src.item import Track, Album, Artist


class SpotifyInterface():
    """
    Class to interface with the Spotify API in Spotify Manager.
    """

    def __init__(self, token):
        self.token = token

    def get_request_headers(self):
        """
        Construct and return standard headers for Spotify requests.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        return headers

    def get_playlist_items(self, playlist_id, limit=50):
        """
        Request items from a Spotify playlist.
        Returns a list of Track objects.
        """
        tracks = []

        # API endpoint to get tracks from a playlist.
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        market = "US"
        fields = "items(track(name,id,album(name,id,artists(name,id)))),total"
        offset = 0

        # Iterate requests until we get all tracks.
        # We get the total number of tracks from the first response.
        total = None
        while total is None or offset < total:
            params = {
                "market": market,
                "fields": fields,
                "limit": limit,
                "offset": offset,
            }
            offset += limit

            # Execute the GET request.
            headers = self.get_request_headers()
            response = requests.get(
                endpoint,
                headers=headers,
                params=params
            )

            if response.status_code != 200:
                logging.error(f"Request responded with status {response.status_code}")
                return None

            data = response.json()

            if total is None:
                total = data["total"]
                logging.debug(f"Playlist has {total} tracks")

            # Parse the data to create a track list.
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
