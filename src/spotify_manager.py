import argparse
import logging

from src.database_interface import DatabaseInterface
from src import item
from src.item import Track, Album, Artist
from src.spotify_interface import SpotifyInterface


class SpotifyManager():
    """
    Application class for the Spotify Manager.
    """
    def __init__(self, database_path=None):
        """
        Initialize the application.
        """
        # Configure logger.
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Open the database connection.
        self.db = DatabaseInterface(database_path)

        # The Spotify interface depends on parsing arguments for the token.
        self.api = None

        # Command line arguments.
        parser = argparse.ArgumentParser(description="Spotify Manager")
        parser.add_argument("--token", type=str, help="Spotify access token")
        parser.add_argument("--playlist-id", type=str, help="Spotify ID of the playlist from which to fetch tracks")
        subparsers = parser.add_subparsers(help="sub-command help", dest="subparser")
        subparsers.add_parser("init", help="Initialize the database")
        subparsers.add_parser("upgrade", help="Upgrade the database schema to the latest version")
        subparsers.add_parser("add", help="Add items to the database")
        subparsers.add_parser("show", help="Print database summary information")
        self.parser = parser

    def run(self, argv=None):
        args = self.parser.parse_args(argv)

        # Initialize the Spotify interface if we have a token.
        if args.token is not None:
            self.api = SpotifyInterface(args.token)

        # Execute the parsed command.
        if args.subparser == "init":
            self.db.create_tables()
        elif args.subparser == "upgrade":
            self.db.upgrade_tables()
        elif args.subparser == "add":
            self.insert_items_from_playlist(args.playlist_id)
        elif args.subparser == "show":
            self.db.print_summary()
        else:
            # Default to print help.
            parser.print_help()

    def insert_items_from_playlist(self, playlist_id):
        """
        Get tracks from a playlist and insert data from tracks, albums, and artists into the
        respective tables.
        """
        if self.api is None:
            logging.error("Spotify interface is not initialized")
            return

        tracks = self.api.get_playlist_items(playlist_id)

        if tracks is None:
            return

        albums = item.get_album_list(tracks)
        artists = item.get_artist_list(albums)

        self.db.insert_tracks(tracks)
        self.db.insert_albums(albums)
        self.db.insert_artists(artists)


if __name__ == "__main__":
    app = SpotifyManager()
    app.run()
