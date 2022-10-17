import argparse
import logging

from src.database_interface import DatabaseInterface
from src import item
from src.item import Track, Album, Artist
from src.spotify_interface import SpotifyInterface


def insert_items_from_playlist(db, api, playlist_id):
    """
    Get tracks from a playlist and insert data from tracks, albums, and artists into the
    respective tables.
    """
    tracks = api.get_playlist_items(playlist_id)

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

    # Create the Spotify interface.
    api = SpotifyInterface(args.token)

    # Execute the parsed command.
    if args.subparser == "init":
        db.create_tables()
        db.update_tables((1,1,0))
    elif args.subparser == "add":
        insert_items_from_playlist(db, api, args.playlist_id)
    elif args.subparser == "show":
        print_summary(db)
    else:
        # Default to print help.
        parser.print_help()
