import json
import logging
from pathlib import Path
import requests
import sqlite3
import sys

from src import schema


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
    Create tables for storing item information using the latest schema.
    """
    cur = con.cursor()

    # Get the latest schema.
    version = get_latest_schema_version()
    schema = get_schema(version)

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
        if "version" in tables:
            cur.execute("DROP TABLE version")

    # Create the tracks table.
    if "tracks" not in tables or force:
        create_table_from_schema(con, "tracks", schema["tracks"])

    # Create the albums table.
    if "albums" not in tables or force:
        create_table_from_schema(con, "albums", schema["albums"])

    # Create the artists table.
    if "artists" not in tables or force:
        create_table_from_schema(con, "artists", schema["artists"])

    # Create a table to track the schema version.
    if "version" not in tables or force:
        cmd = """
        CREATE TABLE version (
            major int NOT NULL PRIMARY KEY CHECK (major >= 0),
            minor int NOT NULL CHECK (minor >= 0),
            patch int NOT NULL CHECK (patch >= 0)
        )
        """
        cur.execute(cmd)

        # Set the version.
        cmd = """
        INSERT INTO version (major, minor, patch)
             VALUES (?, ?, ?)
        """
        cur.execute(cmd, version)

    con.commit()


def insert_tracks(con, tracks):
    """
    Insert data into the tracks table from a list of Track objects.
    """
    cur = con.cursor()

    cmd = """
    INSERT INTO tracks (id, name, album)
         VALUES (?, ?, ?)
    ON CONFLICT (id)
             DO NOTHING
    """
    data = [(track.id, track.name, track.album.id) for track in tracks]
    cur.executemany(cmd, data)

    con.commit()


def insert_albums(con, albums):
    """
    Insert data into the albums table from a list of Album objects.
    """
    cur = con.cursor()

    cmd = """
    INSERT INTO albums (id, name, artist)
         VALUES (?, ?, ?)
    ON CONFLICT (id)
             DO NOTHING
    """
    data = [(album.id, album.name, album.artist.id) for album in albums]
    cur.executemany(cmd, data)

    con.commit()


def insert_artists(con, artists):
    """
    Insert data into the artists table from a list of Artist objects.
    """
    cur = con.cursor()

    cmd = """
    INSERT INTO artists (id, name)
         VALUES (?, ?)
    ON CONFLICT (id)
             DO NOTHING
    """
    data = [(artist.id, artist.name) for artist in artists]
    cur.executemany(cmd, data)

    con.commit()


def get_album_list(tracks):
    """
    Get a list of unique albums from a list of tracks.
    """
    albums = []
    lookup_table = set()
    for track in tracks:
        if track.album.id not in lookup_table:
            lookup_table.add(track.album.id)
            albums.append(track.album)
    return albums


def get_artist_list(albums):
    """
    Get a list of unique artists from a list of albums.
    """
    artists = []
    lookup_table = set()
    for album in albums:
        if album.artist.id not in lookup_table:
            lookup_table.add(album.artist.id)
            artists.append(album.artist)
    return artists


def insert_items_from_playlist(con, token, playlist_id):
    """
    Get tracks from a playlist and insert data from tracks, albums, and artists into the
    respective tables.
    """
    tracks = get_spotify_playlist_items(token, playlist_id)

    if tracks is None:
        return

    albums = get_album_list(tracks)
    artists = get_artist_list(albums)

    insert_tracks(con, tracks)
    insert_albums(con, albums)
    insert_artists(con, artists)


def semantic_version_to_tuple(string):
    """
    Convert a semantic version string to a tuple.
    This is useful for sorting versions by a numeric value.
    This assumes a string of the format "MAJOR.MINOR.PATCH".
    Semantic version extensions are not supported.
    """
    parts = string.split('.')
    # Convert each part to an integer.
    version = [int(part) for part in parts]
    return tuple(version)


def tuple_to_semantic_version(version):
    """
    Convert a tuple of three integers to a semantic version string.
    """
    # Convert each part of the tuple to a string.
    parts = [str(part) for part in version]
    return '.'.join(parts)


def get_latest_schema_version(schemas=None):
    """
    Return the latest version from the schemas lookup.
    """
    if schemas is None:
        schemas = schema.schemas

    # We use semantic versioning with no extensions, so we can simply sort after parsing to get
    # the latest version.
    versions = [semantic_version_to_tuple(key) for key in schemas.keys()]
    return sorted(versions)[-1]


def get_schema(version):
    """
    Return the schema associated with the given version or None if the version does not exist.
    """
    semantic_version = tuple_to_semantic_version(version)
    return schema.schemas.get(semantic_version, None)


def create_table_from_schema(con, name, schema):
    """
    Create a table from the given schema. This assumes the table does not exist.
    """
    # Get the parameters from the schema.
    parameters = [f"{column} {datatype}" for column, datatype in schema.items()]

    # Create the table.
    cmd = f"""
    CREATE TABLE {name} (
        {','.join(parameters)}
    )
    """
    con.execute(cmd)


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

    # Create and populate tables.
    create_tables(con)
    insert_items_from_playlist(con, token, playlist_id)

    # Print summary information.
    cur = con.cursor()

    cmd = """
    SELECT COUNT()
      FROM tracks
    """
    print(cur.execute(cmd).fetchone()[0], "tracks")

    cmd = """
    SELECT COUNT()
      FROM albums
    """
    print(cur.execute(cmd).fetchone()[0], "albums")

    cmd = """
    SELECT COUNT()
      FROM artists
    """
    print(cur.execute(cmd).fetchone()[0], "artists")

    # Close the database connection.
    con.close()
