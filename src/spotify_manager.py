import json
import logging
from pathlib import Path
import requests
import sqlite3
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


def get_spotify_playlist_items(token, playlist_id, limit=50):
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
        headers = get_spotify_request_headers(token)
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


def create_tables(con, force=False):
    """
    Create tables for storing item information.
    """
    cur = con.cursor()

    # Get a list of existing tables.
    cmd = """
    SELECT name
      FROM sqlite_master
     WHERE type='table'
    """
    rows = cur.execute(cmd).fetchall()
    tables = [row[0] for row in rows]

    # Drop tables to recreate on force.
    if force:
        if "tracks" in tables:
            cur.execute("DROP TABLE tracks")
        if "albums" in tables:
            cur.execute("DROP TABLE albums")
        if "artists" in tables:
            cur.execute("DROP TABLE artists")

    # Create the tracks table.
    if "tracks" not in tables or force:
        cmd = """
        CREATE TABLE tracks (
            id text NOT NULL PRIMARY KEY,
            name text NOT NULL,
            album text NOT NULL
        )
        """
        cur.execute(cmd)

    # Create the albums table.
    if "albums" not in tables or force:
        cmd = """
        CREATE TABLE albums (
            id text NOT NULL PRIMARY KEY,
            name text NOT NULL,
            artist text NOT NULL
        )
        """
        cur.execute(cmd)

    # Create the artists table.
    if "artists" not in tables or force:
        cmd = """
        CREATE TABLE artists (
            id text NOT NULL PRIMARY KEY,
            name text NOT NULL
        )
        """
        cur.execute(cmd)

    con.commit()


if __name__ == "__main__":
    # Get command line arguments.
    token = sys.argv[1]
    playlist_id = sys.argv[2]

    # Configure logger.
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Connect to the database.
    # TODO: Make this path configurable.
    database_path = Path("~/.spotify_manager.db").expanduser().resolve()
    con = sqlite3.connect(database_path)

    create_tables(con)

    # Print playlist items.
    tracks = get_spotify_playlist_items(token, playlist_id)
    if tracks is not None:
        for track in tracks:
            print(track)
        print(len(tracks))

    # Close the database connection.
    con.close()
