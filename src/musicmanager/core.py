import argparse
import logging

from musicmanager.database import Database
from musicmanager.spotify import Spotify


class SpotifyManager:
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
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create the database interface. This opens a database connection automatically.
        self.db = Database(database_path)

        # The Spotify interface depends on parsing arguments for the token.
        self.api = None

        # Command line arguments.
        parser = argparse.ArgumentParser(description="Spotify Manager")
        subparsers = parser.add_subparsers(help="sub-command help", dest="subparser")
        self.parser = parser

        # Init command.
        subparser = subparsers.add_parser("init", help="Initialize the database")
        subparser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Set to drop and re-create any existing tables",
        )

        # Add command.
        subparser = subparsers.add_parser("add", help="Add items to the database")
        subparser.add_argument(
            "--token", type=str, required=True, help="Spotify access token"
        )
        subparser.add_argument(
            "--playlist-id",
            type=str,
            help="Spotify ID of the playlist from which to fetch tracks",
        )
        subparser.add_argument(
            "--rating",
            type=int,
            default=None,
            help="Rate each track with the given rating",
        )

        # Fetch command.
        subparser = subparsers.add_parser(
            "fetch",
            help="Fetch album data for known artists and track data for known albums",
        )
        subparser.add_argument(
            "--token", type=str, required=True, help="Spotify access token"
        )

        # Show command.
        subparsers.add_parser("show", help="Print database summary information")

    def run(self, argv=None):
        args = self.parser.parse_args(argv)

        # Execute the parsed command.
        if args.subparser == "init":
            self.db.create_tables(force=args.force)
        elif args.subparser == "add":
            self.api = Spotify(args.token)
            self.insert_items_from_playlist(args.playlist_id, rating=args.rating)
        elif args.subparser == "fetch":
            self.api = Spotify(args.token)
            self.fetch_albums()
            self.fetch_tracks()
        elif args.subparser == "show":
            self.db.print_summary()
        else:
            # Default to print help.
            self.parser.print_help()

    def insert_items_from_playlist(self, playlist_id, rating=None):
        """
        Get tracks from a playlist and insert data from tracks, albums, and artists into the
        respective tables.
        """
        if self.api is None:
            logging.error("Spotify interface is not initialized")
            return

        playlist = self.api.get_playlist(playlist_id)

        with self.db.transaction():
            self.db.insert_tracks(playlist.tracks, rating=rating)
            self.db.insert_albums(playlist.albums)
            self.db.insert_artists(playlist.artists)

    def fetch_albums(self):
        """
        Fetch all albums from known artists and insert into the database.
        """
        artists = self.db.get_artists()
        for artist in artists:
            albums = self.api.get_artist_albums(artist.id)
            with self.db.transaction():
                self.db.insert_albums(albums)

    def fetch_tracks(self):
        """
        Fetch all tracks from known albums and insert into the database.
        """
        albums = self.db.get_albums()
        for album in albums:
            tracks = self.api.get_album_tracks(album.id)
            with self.db.transaction():
                self.db.insert_tracks(tracks)


def main():
    app = SpotifyManager()
    app.run()


if __name__ == "__main__":
    main()
