import argparse
import json
import logging
from pathlib import Path
import requests
import sqlite3
import sys

from src import schema
from src.item import Track, Album, Artist


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


def get_tables(con):
    """
    Returns a list of existing tables in the database.
    """
    cmd = """
    SELECT name
      FROM sqlite_master
     WHERE type='table'
    """
    rows = con.execute(cmd).fetchall()
    tables = [row[0] for row in rows]
    return tables


def drop_table(con, name):
    """
    Drop a table if it exists.
    """
    if name in get_tables(con):
        cur = con.cursor()
        cur.execute(f"DROP TABLE {name}")
        con.commit()


def create_tables(con, version=None, force=False):
    """
    Create tables for storing item information using the latest schema.
    """
    cur = con.cursor()

    # Default to latest version if one is not given.
    if version is None:
        version = get_latest_schema_version()
    schema = get_schema(version)

    # Get a list of existing tables.
    tables = get_tables(con)

    # Drop tables to recreate on force.
    if force:
        drop_table(con, "tracks")
        drop_table(con, "albums")
        drop_table(con, "artists")
        drop_table(con, "version")

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


def update_tables(con, new_version):
    """
    Update tables to the given schema version.
    """
    existing_tables = get_tables(con)
    item_tables = ["tracks", "albums", "artists"]

    # Make sure the tables to be updated exist.
    for table in item_tables:
        if table not in existing_tables:
            logging.error(f"Cannot update tables because {table} does not exist")
            return

    # Get current schema version.
    cur = con.cursor()
    if "version" in existing_tables:
        current_version = cur.execute("SELECT * FROM version").fetchone()
    else:
        # Assume the oldest version if the version table does not exist.
        current_version = (1,0,0)

    # Quit if there is nothing to update.
    if new_version == current_version:
        return

    # Add new columns to the item tables.
    current_schema = get_schema(current_version)
    new_schema = get_schema(new_version)
    for table in item_tables:
        for column in new_schema[table].keys():
            if column in current_schema[table]:
                continue
            definition = new_schema[table][column]
            cmd = f"""
            ALTER TABLE {table}
                    ADD {column} {definition}
            """
            cur.execute(cmd)

    # Update the version.
    cmd = """
    UPDATE version
       SET major = ?,
           minor = ?,
           patch = ?
    """
    cur.execute(cmd, new_version)

    con.commit()


def open_database(path=None):
    """
    Open and return a database connection.
    """
    if path is None:
        # Default path if none is given.
        path = "~/.spotify_manager.db"
    database_path = Path(path).expanduser().resolve()
    con = sqlite3.connect(database_path)
    return con


def configure_logger():
    """
    Configure the application logger.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def print_summary(con):
    """
    Print database summary information.
    """
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


if __name__ == "__main__":
    # Command line arguments.
    parser = argparse.ArgumentParser(description="Spotify Manager")
    parser.add_argument("--token", type=str, help="Spotify access token")
    parser.add_argument("--playlist-id", type=str, help="Spotify ID of the playlist from which to fetch tracks")
    subparsers = parser.add_subparsers(help="sub-command help", dest="subparser")
    subparsers.add_parser("init", help="Initialize the database")
    subparsers.add_parser("add", help="Add items to the database")
    subparsers.add_parser("show", help="Print database summary information")
    args = parser.parse_args()

    # Configure logger.
    configure_logger()

    # Open the database connection.
    con = open_database()

    # Execute the parsed command.
    if args.subparser == "init":
        create_tables(con)
        update_tables(con, (1,1,0))
    elif args.subparser == "add":
        insert_items_from_playlist(con, args.token, args.playlist_id)
    elif args.subparser == "show":
        print_summary(con)
    else:
        # Default to print help.
        parser.print_help()

    # Close the database connection.
    con.close()
