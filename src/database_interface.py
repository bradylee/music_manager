import logging
from pathlib import Path
import sqlite3

from src import schema
from src.item import Track, Album, Artist


class DatabaseInterface():
    """
    Class to interface with the database in Spotify Manager.
    """

    def __init__(self, database_path=None):
        """
        Initialize by opening a database connection.
        """
        # Use the default path if one is not given.
        if database_path is None:
            database_path = "~/.spotify_manager.db"

        # Open the connection.
        self.database_path = Path(database_path).expanduser().resolve()
        self._con = sqlite3.connect(self.database_path)

    def get_tables(self):
        """
        Returns a list of existing tables in the database.
        """
        cmd = """
        SELECT name
          FROM sqlite_master
         WHERE type='table'
        """
        rows = self._con.execute(cmd).fetchall()
        tables = [row[0] for row in rows]
        return tables

    def drop_table(self, name):
        """
        Drop a table if it exists.
        """
        if name in self.get_tables():
            cur = self._con.cursor()
            cur.execute(f"DROP TABLE {name}")
            self._con.commit()

    def create_tables(self, version=None, force=False):
        """
        Create tables for storing item information using the latest schema.
        """
        cur = self._con.cursor()

        # Default to latest version if one is not given.
        if version is None:
            version = DatabaseInterface.get_latest_schema_version()
        schema = DatabaseInterface.get_schema(version)

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
            cur.execute(cmd)

            # Set the version.
            cmd = """
            INSERT INTO version (major, minor, patch)
                 VALUES (?, ?, ?)
            """
            cur.execute(cmd, version)

        self._con.commit()

    def insert_tracks(self, tracks):
        """
        Insert data into the tracks table from a list of Track objects.
        """
        cur = self._con.cursor()

        cmd = """
        INSERT INTO tracks (id, name, album)
             VALUES (?, ?, ?)
        ON CONFLICT (id)
                 DO NOTHING
        """
        data = [(track.id, track.name, track.album.id) for track in tracks]
        cur.executemany(cmd, data)

        self._con.commit()

    def insert_albums(self, albums):
        """
        Insert data into the albums table from a list of Album objects.
        """
        cur = self._con.cursor()

        cmd = """
        INSERT INTO albums (id, name, artist)
             VALUES (?, ?, ?)
        ON CONFLICT (id)
                 DO NOTHING
        """
        data = [(album.id, album.name, album.artist.id) for album in albums]
        cur.executemany(cmd, data)

        self._con.commit()

    def insert_artists(self, artists):
        """
        Insert data into the artists table from a list of Artist objects.
        """
        cur = self._con.cursor()

        cmd = """
        INSERT INTO artists (id, name)
             VALUES (?, ?)
        ON CONFLICT (id)
                 DO NOTHING
        """
        data = [(artist.id, artist.name) for artist in artists]
        cur.executemany(cmd, data)

        self._con.commit()

    @staticmethod
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

    @staticmethod
    def tuple_to_semantic_version(version):
        """
        Convert a tuple of three integers to a semantic version string.
        """
        # Convert each part of the tuple to a string.
        parts = [str(part) for part in version]
        return '.'.join(parts)

    @staticmethod
    def get_latest_schema_version(schemas=None):
        """
        Return the latest version from the schemas lookup.
        """
        if schemas is None:
            schemas = schema.schemas

        # We use semantic versioning with no extensions, so we can simply sort after parsing to get
        # the latest version.
        versions = [DatabaseInterface.semantic_version_to_tuple(key) for key in schemas.keys()]
        return sorted(versions)[-1]

    @staticmethod
    def get_schema(version):
        """
        Return the schema associated with the given version or None if the version does not exist.
        """
        semantic_version = DatabaseInterface.tuple_to_semantic_version(version)
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
        self._con.execute(cmd)

    def upgrade_tables(self, new_version=None):
        """
        Update tables to the given schema version.
        """
        existing_tables = self.get_tables()
        item_tables = ["tracks", "albums", "artists"]

        # Make sure the tables to be updated exist.
        for table in item_tables:
            if table not in existing_tables:
                logging.error(f"Cannot update tables because {table} does not exist")
                return

        # Default to the latest version.
        if new_version is None:
            new_version = DatabaseInterface.get_latest_schema_version()

        # Get current schema version.
        cur = self._con.cursor()
        if "version" in existing_tables:
            current_version = cur.execute("SELECT * FROM version").fetchone()
        else:
            # Assume the oldest version if the version table does not exist.
            current_version = (1,0,0)

        # Quit if there is nothing to update.
        if new_version == current_version:
            return

        # Add new columns to the item tables.
        current_schema = DatabaseInterface.get_schema(current_version)
        new_schema = DatabaseInterface.get_schema(new_version)
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

        self._con.commit()

    def print_summary(self):
        """
        Print database summary information.
        """
        # Print summary information.
        cur = self._con.cursor()

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
