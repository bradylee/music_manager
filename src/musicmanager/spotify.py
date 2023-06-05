import logging

import requests

from musicmanager.item import Album, Artist, Playlist, Track


class Spotify:
    """
    Interface to the Spotify API.
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

    def get_playlist(self, id_, limit=50):
        """
        Fetch a Spotify playlist by id.
        Returns a Playlist object.
        """
        playlist = Playlist()

        # API endpoint to get tracks from a playlist.
        endpoint = f"https://api.spotify.com/v1/playlists/{id_}/tracks"

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
            response = requests.get(endpoint, headers=headers, params=params)

            if response.status_code != 200:
                logging.error(f"Request responded with status {response.status_code}")
                return None

            data = response.json()

            if total is None:
                total = data["total"]
                logging.debug(f"Playlist has {total} tracks")

            # Parse the response data.
            for item in data["items"]:
                track_data = item["track"]
                album_data = track_data["album"]
                # Assume the artist listed first is the main artist.
                artist_data = album_data["artists"][0]

                # Create items from the data.
                artist = Artist(artist_data["id"], artist_data["name"])
                album = Album(album_data["id"], album_data["name"], artist_data["id"])
                track = Track(track_data["id"], track_data["name"], album_data["id"])

                # Add the items to the playlist.
                playlist.add_artist(artist)
                playlist.add_album(album)
                playlist.add_track(track)

        return playlist

    def get_artist_albums(self, artist, limit=50):
        """
        Request all albums for a Spotify artist.
        Returns a list of Album objects.
        """
        albums = []

        # API endpoint to get albums from an artist.
        endpoint = f"https://api.spotify.com/v1/artists/{artist.id}/albums"

        market = "US"
        offset = 0

        # TODO: Include all groups. This requires re-checking the artist on each album due to
        # features and compilations.
        include_groups = "album,single"

        # We get the total number of albums and the artist name from the first response.
        total = None

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
            response = requests.get(endpoint, headers=headers, params=params)

            if response.status_code != 200:
                logging.error(f"Request responded with status {response.status_code}")
                return None

            data = response.json()

            if total is None:
                total = data["total"]
                logging.debug(f"Artist {repr(artist.name)} has {total} albums")

            # Parse the data to create an album list.
            for item in data["items"]:
                album_id = item["id"]
                album_name = item["name"]
                album = Album(album_id, album_name, artist.id)
                albums.append(album)

        return albums

    def get_album_tracks(self, album):
        """
        Request all tracks for a Spotify album.
        Returns a list of Track objects.
        """
        tracks = []

        # API endpoint to get tracks from an album.
        endpoint = f"https://api.spotify.com/v1/albums/{album.id}"

        market = "US"

        # We get the total number of tracks and the album name from the first response.
        total = None

        # This endpoint should return all tracks with a single request. It does not have inputs for
        # offset or limit.
        params = {
            "market": market,
        }

        # Execute the GET request.
        headers = self.get_request_headers()
        response = requests.get(endpoint, headers=headers, params=params)

        if response.status_code != 200:
            logging.error(f"Request responded with status {response.status_code}")
            return None

        data = response.json()

        # Parse album data.
        assert album.id == data["id"]

        # Parse track data.
        track_data = data["tracks"]

        total = track_data["total"]
        logging.debug(f"Album {repr(album.name)} has {total} tracks")

        # Create the track list.
        for track in track_data["items"]:
            track = Track(track["id"], track["name"], album.id)
            tracks.append(track)

        return tracks
