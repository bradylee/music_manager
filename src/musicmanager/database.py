import sqlite3
from contextlib import contextmanager
from pathlib import Path

from musicmanager import schema
from musicmanager.item import Album, Artist, Track


class Database:
    """
    Interface to the database.
    """

    def __init__(self, database_path=None):
        """
        Initialize by opening a database connection.
        """
        # Use the default path if one is not given.
        if database_path is None:
            database_path = "~/.music_manager.db"

        # Open the connection.
        self.database_path = Path(database_path).expanduser().resolve()
        self._con = sqlite3.connect(self.database_path, isolation_level=None)

        # Cursor for interacting with the database.
        # This is controlled by the `transaction` context.
        self._active_cursor = None

    def _execute(self, *args, **kwargs):
        """
        Execute a command with the active cursor.
        """
        # Make sure the cursor is set.
        if self._active_cursor is None:
            raise RuntimeError("Cannot execute a command outside of a transaction")

        return self._active_cursor.execute(*args, **kwargs)

    def _executemany(self, *args, **kwargs):
        """
        Execute a parameterized command with the active cursor.
        """
        # Make sure the cursor is set.
        if self._active_cursor is None:
            raise RuntimeError(
                "Cannot execute a parameterized command outside of a transaction"
            )

        return self._active_cursor.executemany(*args, **kwargs)

    @contextmanager
    def transaction(self):
        """
        Context to create explicit transactions. This helps keep the database in a known state in
        the case of exceptions, since some actions are otherwise automatically committed.
        """
        self._active_cursor = self._con.cursor()
        try:
            # Start a transaction.
            self._execute("BEGIN")
            yield
            # Complete the transaction.
            self._execute("COMMIT")
        except Exception as ex:
            # Undo the changes on failure.
            self._execute("ROLLBACK")
            raise ex
        finally:
            self._active_cursor.close()
            self._active_cursor = None

    def get_tables(self):
        """
        Returns a list of existing tables in the database sorted by name.
        """
        # Allow an on-demand cursor as needed, since this logic is read only.
        if self._active_cursor is not None:
            cur = self._active_cursor
        else:
            cur = self._con.cursor()

        # Select the data.
        cmd = """
          SELECT name
            FROM sqlite_master
           WHERE type='table'
        ORDER BY name
        """
        rows = cur.execute(cmd).fetchall()
        tables = [row[0] for row in rows]
        return tables

    def drop_table(self, name):
        """
        Drop a table if it exists.
        """
        if name in self.get_tables():
            self._execute(f"DROP TABLE {name}")

    def create_tables(self, version=None, force=False):
        """
        Create tables for storing item information using the latest schema.
        """
        with self.transaction():
            # Default to latest version if one is not given.
            if version is None:
                version = Database.get_latest_schema_version()
            schema = Database.get_schema(version)

            # Get a list of existing tables.
            tables = self.get_tables()

            # Drop tables to recreate on force.
            if force:
                self.drop_table("tracks")
                self.drop_table("albums")
                self.drop_table("artists")
                self.drop_table("version")

            # Create the tracks table.
            if "tracks" not in tables or force:
                self.create_table_from_schema("tracks", schema["tracks"])

            # Create the albums table.
            if "albums" not in tables or force:
                self.create_table_from_schema("albums", schema["albums"])

            # Create the artists table.
            if "artists" not in tables or force:
                self.create_table_from_schema("artists", schema["artists"])

            # Create a table to track the schema version.
            if "version" not in tables or force:
                cmd = """
                CREATE TABLE version (
                    major int NOT NULL PRIMARY KEY CHECK (major >= 0),
                    minor int NOT NULL CHECK (minor >= 0),
                    patch int NOT NULL CHECK (patch >= 0)
                )
                """
                self._execute(cmd)

                # Set the version.
                cmd = """
                INSERT INTO version (major, minor, patch)
                     VALUES (?, ?, ?)
                """
                self._execute(cmd, version)

    def insert_tracks(self, tracks, rating=None):
        """
        Insert data into the tracks table from a list of Track objects.
        """
        if rating is None:
            # Insert the track without setting the rating.
            cmd = """
            INSERT INTO tracks (id, name, album)
                 VALUES (?, ?, ?)
            ON CONFLICT (id)
                     DO NOTHING
            """
            data = [(track.id, track.name, track.album.id) for track in tracks]
        else:
            # Insert the track and set the rating.
            cmd = """
            INSERT INTO tracks (id, name, album, rating, num_times_rated)
                 VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (id)
                     DO UPDATE
                    SET rating = excluded.rating,
                        num_times_rated = num_times_rated + 1
            """
            data = [
                (track.id, track.name, track.album.id, rating, 1) for track in tracks
            ]
        self._executemany(cmd, data)

    def insert_albums(self, albums):
        """
        Insert data into the albums table from a list of Album objects.
        """
        cmd = """
        INSERT INTO albums (id, name, artist)
             VALUES (?, ?, ?)
        ON CONFLICT (id)
                 DO NOTHING
        """
        data = [(album.id, album.name, album.artist.id) for album in albums]
        self._executemany(cmd, data)

    def insert_artists(self, artists):
        """
        Insert data into the artists table from a list of Artist objects.
        """
        cmd = """
        INSERT INTO artists (id, name)
             VALUES (?, ?)
        ON CONFLICT (id)
                 DO NOTHING
        """
        data = [(artist.id, artist.name) for artist in artists]
        self._executemany(cmd, data)

    def get_tracks(self):
        """
        Get a list of all tracks in the database.
        """
        tracks = []

        cmd = """
        SELECT tracks.id,
               tracks.name,
               albums.id,
               albums.name,
               artists.id,
               artists.name
          FROM tracks
          JOIN albums
            ON tracks.album = albums.id
          JOIN artists
            ON albums.artist = artists.id
        """
        for (
            track_id,
            track_name,
            album_id,
            album_name,
            artist_id,
            artist_name,
        ) in self._con.execute(cmd):
            artist = Artist(artist_id, artist_name)
            album = Album(album_id, album_name, artist=artist)
            track = Track(track_id, track_name, album=album)
            tracks.append(track)

        return tracks

    def get_albums(self):
        """
        Get a list of all albums in the database.
        """
        albums = []

        cmd = """
        SELECT albums.id,
               albums.name,
               artists.id,
               artists.name
          FROM albums
          JOIN artists
            ON albums.artist = artists.id
        """
        for album_id, album_name, artist_id, artist_name in self._con.execute(cmd):
            artist = Artist(artist_id, artist_name)
            album = Album(album_id, album_name, artist=artist)
            albums.append(album)

        return albums

    def get_artists(self):
        """
        Get a list of all artists in the database.
        """
        artists = []

        cmd = """
        SELECT id,
               name
          FROM artists
        """
        for id_, name in self._con.execute(cmd):
            artist = Artist(id_, name)
            artists.append(artist)

        return artists

    @staticmethod
    def semantic_version_to_tuple(string):
        """
        Convert a semantic version string to a tuple.
        This is useful for sorting versions by a numeric value.
        This assumes a string of the format "MAJOR.MINOR.PATCH".
        Semantic version extensions are not supported.
        """
        parts = string.split(".")
        # Convert each part to an integer.
        version = [int(part) for part in parts]
        return tuple(version)

    @staticmethod
    def tuple_to_semantic_version(version):
        """
        Convert a tuple of three integers to a semantic version string.
        """
        # Convert each part of the tuple to a string.
        parts = [str(part) for part in version]
        return ".".join(parts)

    @staticmethod
    def get_latest_schema_version(schemas=None):
        """
        Return the latest version from the schemas lookup.
        """
        if schemas is None:
            schemas = schema.schemas

        # We use semantic versioning with no extensions, so we can simply sort after parsing to get
        # the latest version.
        versions = [Database.semantic_version_to_tuple(key) for key in schemas.keys()]
        return sorted(versions)[-1]

    @staticmethod
    def get_schema(version):
        """
        Return the schema associated with the given version or None if the version does not exist.
        """
        semantic_version = Database.tuple_to_semantic_version(version)
        return schema.schemas.get(semantic_version, None)

    def create_table_from_schema(self, name, schema):
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
        self._execute(cmd)

    def print_summary(self):
        """
        Print database summary information.
        """
        cmd = """
        SELECT COUNT()
          FROM tracks
        """
        num_tracks = self._con.execute(cmd).fetchone()[0]

        cmd = """
        SELECT COUNT()
          FROM tracks
         WHERE num_times_rated > 0
        """
        num_rated_tracks = self._con.execute(cmd).fetchone()[0]

        cmd = """
        SELECT COUNT()
          FROM tracks
         WHERE num_times_rated = 0
        """
        num_unrated_tracks = self._con.execute(cmd).fetchone()[0]

        cmd = """
        SELECT COUNT()
          FROM tracks
         WHERE rating > 0
        """
        num_liked_tracks = self._con.execute(cmd).fetchone()[0]

        cmd = """
        SELECT COUNT()
          FROM tracks
         WHERE rating = 0
           AND num_times_rated > 0
        """
        num_neutral_tracks = self._con.execute(cmd).fetchone()[0]

        cmd = """
        SELECT COUNT()
          FROM tracks
         WHERE rating < 0
        """
        num_disliked_tracks = self._con.execute(cmd).fetchone()[0]

        cmd = """
        SELECT COUNT()
          FROM albums
        """
        num_albums = self._con.execute(cmd).fetchone()[0]

        cmd = """
        SELECT COUNT()
          FROM artists
        """
        num_artists = self._con.execute(cmd).fetchone()[0]

        summary = (
            f"{num_tracks} tracks\n"
            f"    {num_rated_tracks} rated\n"
            f"        {num_liked_tracks} liked\n"
            f"        {num_neutral_tracks} neutral\n"
            f"        {num_disliked_tracks} disliked\n"
            f"    {num_unrated_tracks} unrated\n"
            f"{num_albums} albums\n"
            f"{num_artists} artists\n"
        )
        print(summary, end="")

        # Check accuracy by summing up each value.
        assert num_tracks == num_rated_tracks + num_unrated_tracks
        assert (
            num_rated_tracks
            == num_liked_tracks + num_neutral_tracks + num_disliked_tracks
        )
