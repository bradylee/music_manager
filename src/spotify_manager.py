import argparse
import json
import logging
import requests

from src.database_interface import DatabaseInterface
from src import item
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


def insert_items_from_playlist(db, token, playlist_id):
    """
    Get tracks from a playlist and insert data from tracks, albums, and artists into the
    respective tables.
    """
    tracks = get_spotify_playlist_items(token, playlist_id)

    if tracks is None:
        return

    albums = item.get_album_list(tracks)
    artists = item.get_artist_list(albums)

    db.insert_tracks(tracks)
    db.insert_albums(albums)
    db.insert_artists(artists)


def configure_logger():
    """
    Configure the application logger.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def print_summary(db):
    """
    Print database summary information.
    """
    # Print summary information.
    cur = db.con.cursor()

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
    db = DatabaseInterface()

    # Execute the parsed command.
    if args.subparser == "init":
        db.create_tables()
        db.update_tables((1,1,0))
    elif args.subparser == "add":
        insert_items_from_playlist(db, args.token, args.playlist_id)
    elif args.subparser == "show":
        print_summary(db)
    else:
        # Default to print help.
        parser.print_help()
