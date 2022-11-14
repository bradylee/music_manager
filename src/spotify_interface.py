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

    def fetch_artist_albums(self, artist_id, limit=50):
        """
        Request all albums for a Spotify artist.
        Returns a list of Album objects.
        """
        albums = []

        # API endpoint to get albums from an artist.
        endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums"

        market = "US"
        offset = 0

        # TODO: Include all groups. This requires re-checking the artist on each album due to
        # features and compilations.
        include_groups = "album,single"

        # We get the total number of albums and the artist name from the first response.
        total = None
        artist_name = None

        # Iterate requests until we get all albums.
        while total is None or offset < total:
            params = {
                "market": market,
                "limit": limit,
                "offset": offset,
                "include_groups": include_groups,
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
                logging.debug(f"Artist has {total} albums")

            # Parse the data to create a track list.
            for item in data["items"]:
                album_id = item["id"]
                album_name = item["name"]

                # Get the artist name.
                if artist_name is None:
                    for artist in item["artists"]:
                        if artist["id"] == artist_id:
                            artist_name = artist["name"]

                # Create objects.
                artist = Artist(artist_id, artist_name)
                album = Album(album_id, album_name, artist=artist)
                albums.append(album)

        return albums
