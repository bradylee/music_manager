import pytest

from src import database_interface as dut
from src.item import Album, Artist, Track


def test_transaction(tmp_path):
    """
    Test `transaction` by checking that changes are committed when no exception is thrown.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")

    # Create a basic table and insert an arbitrary value.
    with db.transaction():
        db._execute("CREATE TABLE example (a int)")
        db._execute("INSERT INTO example (a) VALUES (1)")

    # Verify the example table was created and data was inserted.
    cur = db._con.cursor()
    rows = cur.execute("SELECT * FROM example").fetchall()
    assert rows == [(1,)]


def test_transaction_exception(tmp_path):
    """
    Test `transaction` by checking that changes are not committed when an exception is thrown.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")

    # Throw an exception during a transaction to demonstrate rollback.
    with pytest.raises(RuntimeError):
        with db.transaction():
            db._execute("CREATE TABLE example (a int)")
            db._execute("INSERT INTO example (a) VALUES (1)")
            # Normally create adds an implicit COMMIT, so create another table to show that is no
            # longer the case.
            db._execute("CREATE TABLE sample (b text)")
            raise RuntimeError

    # Verify that no tables were created.
    assert db.get_tables() == []


def test_createTables(tmp_path):
    """
    Test `create_tables` by checking the list of tables and the version number.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    cur = db._con.cursor()

    # Function under test.
    db.create_tables()

    # Verify that all tables were created.
    tables = db.get_tables()
    assert "tracks" in tables
    assert "albums" in tables
    assert "artists" in tables
    assert "version" in tables

    # Verify the version table includes the latest version.
    rows = cur.execute("SELECT * FROM version").fetchall()
    version = dut.DatabaseInterface.get_latest_schema_version()
    assert rows == [version]


def test_createTables_force(tmp_path):
    """
    Test `create_tables` by confirming data is cleared on force.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    cur = db._con.cursor()

    # Create the initial tables.
    db.create_tables()

    # Insert sample data into the tables.
    cmd = """
    INSERT INTO tracks(id, name, album)
         VALUES ('2GDX9DpZgXsLAkXhHBQU1Q', 'Choke', '0a40snAsSiU0fSBrba93YB');

    INSERT INTO albums(id, name, artist)
         VALUES ('0a40snAsSiU0fSBrba93YB', 'World Demise', '7bDLHytU8vohbiWbePGrRU');

    INSERT INTO artists(id, name)
         VALUES ('7bDLHytU8vohbiWbePGrRU', 'Falsifier');
    """
    cur.executescript(cmd)

    # Verify the tables have some data.
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert len(rows) == 1
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert len(rows) == 1
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert len(rows) == 1

    # Recreate the tables with force.
    db.create_tables(force=True)

    # Verify the tables are now empty
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert len(rows) == 0
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert len(rows) == 0
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert len(rows) == 0


def test_insertTracks(tmp_path):
    """
    Test `insert_tracks` by selecting data and comparing it to the input.
    """
    # Input data.
    tracks = [
        Track(
            "6bsxDgpU5nlcHNZYtsfZG8",
            "Bleeding Sun",
            album=Album("7hkhFnClNPmRXL20KqdzSO", "Bleeding Sun"),
        ),
        Track(
            "15eQh5ZLBoMReY20MDG37T",
            "Breathless",
            album=Album("1GLmxzF8g5p0fcdAatGq5Y", "Fractured"),
        ),
        Track(
            "2GDX9DpZgXsLAkXhHBQU1Q",
            "Choke",
            album=Album("0a40snAsSiU0fSBrba93YB", "World Demise"),
        ),
    ]

    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    with db.transaction():
        db.insert_tracks(tracks)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name,
             album,
             rating
        FROM tracks
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the number of tracks.
    assert len(rows) == 3

    # Verify the selected data matches the input.
    assert rows[0] == (
        "6bsxDgpU5nlcHNZYtsfZG8",
        "Bleeding Sun",
        "7hkhFnClNPmRXL20KqdzSO",
        0,
    )
    assert rows[1] == (
        "15eQh5ZLBoMReY20MDG37T",
        "Breathless",
        "1GLmxzF8g5p0fcdAatGq5Y",
        0,
    )
    assert rows[2] == ("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 0)


def test_insertTracks_rated(tmp_path):
    """
    Test `insert_tracks` can optionally set the rating.
    """
    # Input data.
    tracks = [
        Track(
            "6bsxDgpU5nlcHNZYtsfZG8",
            "Bleeding Sun",
            album=Album("7hkhFnClNPmRXL20KqdzSO", "Bleeding Sun"),
        ),
        Track(
            "15eQh5ZLBoMReY20MDG37T",
            "Breathless",
            album=Album("1GLmxzF8g5p0fcdAatGq5Y", "Fractured"),
        ),
        Track(
            "2GDX9DpZgXsLAkXhHBQU1Q",
            "Choke",
            album=Album("0a40snAsSiU0fSBrba93YB", "World Demise"),
        ),
    ]

    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    with db.transaction():
        db.insert_tracks(tracks, rating=1)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name,
             album,
             rating
        FROM tracks
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the number of tracks.
    assert len(rows) == 3

    # Verify the selected data matches the input.
    assert rows[0] == (
        "6bsxDgpU5nlcHNZYtsfZG8",
        "Bleeding Sun",
        "7hkhFnClNPmRXL20KqdzSO",
        1,
    )
    assert rows[1] == (
        "15eQh5ZLBoMReY20MDG37T",
        "Breathless",
        "1GLmxzF8g5p0fcdAatGq5Y",
        1,
    )
    assert rows[2] == ("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 1)

    # Change the rating.
    with db.transaction():
        db.insert_tracks(tracks, rating=-1)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name,
             album,
             rating
        FROM tracks
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the selected data matches the input.
    # Verify the rating was updated.
    assert rows[0][-1] == -1
    assert rows[1][-1] == -1
    assert rows[2][-1] == -1


def test_insertAlbums(tmp_path):
    """
    Test `insert_albums` by selecting data and comparing it to the input.
    """
    # Input data.
    albums = [
        Album(
            "7hkhFnClNPmRXL20KqdzSO",
            "Bleeding Sun",
            artist=Artist("4UgQ3EFa8fEeaIEg54uV5b", "Chelsea Grin"),
        ),
        Album(
            "1GLmxzF8g5p0fcdAatGq5Y",
            "Fractured",
            artist=Artist("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD"),
        ),
        Album(
            "0a40snAsSiU0fSBrba93YB",
            "World Demise",
            artist=Artist("7bDLHytU8vohbiWbePGrRU", "Falsifier"),
        ),
    ]

    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    with db.transaction():
        db.insert_albums(albums)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name,
             artist
        FROM albums
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the number of albums.
    assert len(rows) == 3

    # Verify the selected data matches the input.
    assert rows[0] == (
        "7hkhFnClNPmRXL20KqdzSO",
        "Bleeding Sun",
        "4UgQ3EFa8fEeaIEg54uV5b",
    )
    assert rows[1] == ("1GLmxzF8g5p0fcdAatGq5Y", "Fractured", "7z9n8Q0icbgvXqx1RWoGrd")
    assert rows[2] == (
        "0a40snAsSiU0fSBrba93YB",
        "World Demise",
        "7bDLHytU8vohbiWbePGrRU",
    )


def test_insertArtists(tmp_path):
    """
    Test `insert_artists` by selecting data and comparing it to the input.
    """
    # Input data.
    artists = [
        Artist("4UgQ3EFa8fEeaIEg54uV5b", "Chelsea Grin"),
        Artist("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD"),
        Artist("7bDLHytU8vohbiWbePGrRU", "Falsifier"),
    ]

    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    with db.transaction():
        db.insert_artists(artists)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name
        FROM artists
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the number of albums.
    assert len(rows) == 3

    # Verify the selected data matches the input.
    assert rows[0] == ("4UgQ3EFa8fEeaIEg54uV5b", "Chelsea Grin")
    assert rows[1] == ("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD")
    assert rows[2] == ("7bDLHytU8vohbiWbePGrRU", "Falsifier")


def test_semanticVersionToTuple():
    """
    Test `semantic_version_to_tuple` with example data.
    """
    assert dut.DatabaseInterface.semantic_version_to_tuple("1.0.0") == (1, 0, 0)
    assert dut.DatabaseInterface.semantic_version_to_tuple("10.0.1") == (10, 0, 1)
    assert dut.DatabaseInterface.semantic_version_to_tuple("2.10.100") == (2, 10, 100)


def test_tupleToSemanticVersion():
    """
    Test `tuple_to_semantic_version` with example data.
    """
    assert dut.DatabaseInterface.tuple_to_semantic_version((1, 0, 0)) == "1.0.0"
    assert dut.DatabaseInterface.tuple_to_semantic_version((10, 0, 1)) == "10.0.1"
    assert dut.DatabaseInterface.tuple_to_semantic_version((2, 10, 100)) == "2.10.100"


def test_getLatestSchemaVersion():
    """
    Test `get_latest_schema_version` with a mock schemas lookup.
    """
    # Create versions to confirm that they are sorted numerically and not by ASCII.
    schemas = {
        "1.0.0": "a",
        "10.10.0": "b",
        "10.0.0": "c",
        "2.0.10": "d",
    }

    # Verify the latest schema is the greatest version number.
    assert dut.DatabaseInterface.get_latest_schema_version(schemas) == (10, 10, 0)


def test_getSchema():
    """
    Test `get_schema` by requesting a valid version.
    """
    # Verify the value for a real version.
    assert dut.DatabaseInterface.get_schema((1, 0, 0)) == {
        "tracks": {
            "id": "text NOT NULL PRIMARY KEY",
            "name": "text NOT NULL",
            "album": "text NOT NULL",
        },
        "albums": {
            "id": "text NOT NULL PRIMARY KEY",
            "name": "text NOT NULL",
            "artist": "text NOT NULL",
        },
        "artists": {
            "id": "text NOT NULL PRIMARY KEY",
            "name": "text NOT NULL",
        },
    }


def test_getSchema_invalid():
    """
    Test `get_schema` by requesting an invalid version.
    """
    # Verify the value for a fake version.
    assert dut.DatabaseInterface.get_schema((0, 0, 0)) is None


def test_createTableFromSchema(tmp_path):
    """
    Test `create_table_from_schema` using a simplified schema.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    cur = db._con.cursor()

    # Example schema.
    schema = {
        "string": "text NOT NULL PRIMARY KEY",
        "number": "int NOT NULL",
    }

    # Function under test.
    with db.transaction():
        db.create_table_from_schema("example", schema)

    # Insert sample data into the tables.
    data = [
        ("hello", 1),
        ("goodbye", 2),
    ]
    cmd = """
    INSERT INTO example(string, number)
         VALUES (?, ?);
    """
    cur.executemany(cmd, data)

    # Verify the tables have data.
    rows = cur.execute("SELECT * FROM example").fetchall()
    assert len(rows) == 2


def test_upgradeTables(tmp_path):
    """
    Test `upgrade_tables` by creating a 1.0.0 table and upgrading it to the 1.1.0 schema.
    """
    # Create a new temporary database with an old schema.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables(version=(1, 0, 0))
    cur = db._con.cursor()

    # Insert sample data into the tables.
    cmd = """
    INSERT INTO tracks(id, name, album)
         VALUES ('2GDX9DpZgXsLAkXhHBQU1Q', 'Choke', '0a40snAsSiU0fSBrba93YB');

    INSERT INTO albums(id, name, artist)
         VALUES ('0a40snAsSiU0fSBrba93YB', 'World Demise', '7bDLHytU8vohbiWbePGrRU');

    INSERT INTO artists(id, name)
         VALUES ('7bDLHytU8vohbiWbePGrRU', 'Falsifier');
    """
    cur.executescript(cmd)

    # Verify the tables have only 1.0.0 columns.
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert rows == [("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB")]
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert rows == [
        ("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU")
    ]
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert rows == [("7bDLHytU8vohbiWbePGrRU", "Falsifier")]

    # Upgrade the table to the newer schema.
    db.upgrade_tables((1, 1, 0))

    # Verify the tables now include 1.1.0 columns with default values.
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert rows == [("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 0, 0)]
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert rows == [
        ("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU")
    ]
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert rows == [("7bDLHytU8vohbiWbePGrRU", "Falsifier")]

    # Verify the version table shows the updated version.
    rows = cur.execute("SELECT * FROM version").fetchall()
    assert rows == [(1, 1, 0)]

    # Verify that running again does nothing to show that upgrade is idempotent.
    db.upgrade_tables((1, 1, 0))
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert rows == [("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 0, 0)]
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert rows == [
        ("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU")
    ]
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert rows == [("7bDLHytU8vohbiWbePGrRU", "Falsifier")]
    rows = cur.execute("SELECT * FROM version").fetchall()
    assert rows == [(1, 1, 0)]


def test_printSummary(tmp_path, capsys):
    """
    Test `print_summary` by inserting different numbers of tracks, albums, and artists.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Create and insert example data.
    artists = [
        ("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD"),
        ("7bDLHytU8vohbiWbePGrRU", "Falsifier"),
    ]
    cur.executemany("INSERT INTO artists(id, name) VALUES (?, ?)", artists)

    albums = [
        ("1GLmxzF8g5p0fcdAatGq5Y", "Fractured", "7z9n8Q0icbgvXqx1RWoGrd"),
        ("1GLmxzF8g5p0fcdAatGq5Y2", "Fractured 2", "7z9n8Q0icbgvXqx1RWoGrd"),
        ("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU"),
        ("0a40snAsSiU0fSBrba93YB2", "World Demise 2", "7bDLHytU8vohbiWbePGrRU"),
    ]
    cur.executemany("INSERT INTO albums(id, name, artist) VALUES (?, ?, ?)", albums)

    # Unique tracks with different ratings and number of times rated.
    # Any rating counts as being rated, even if number of times rated is zero.
    tracks = [
        ("15eQh5ZLBoMReY20MDG37T", "Breathless", "1GLmxzF8g5p0fcdAatGq5Y", 1, 0),
        ("15eQh5ZLBoMReY20MDG37T2", "Breathless 2", "1GLmxzF8g5p0fcdAatGq5Y", 1, 1),
        ("15eQh5ZLBoMReY20MDG37T3", "Breathless 3", "1GLmxzF8g5p0fcdAatGq5Y2", 1, 10),
        ("15eQh5ZLBoMReY20MDG37T4", "Breathless 4", "1GLmxzF8g5p0fcdAatGq5Y2", 1, 100),
        ("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 0, 0),
        ("2GDX9DpZgXsLAkXhHBQU1Q2", "Choke 2", "0a40snAsSiU0fSBrba93YB", 0, 2),
        ("2GDX9DpZgXsLAkXhHBQU1Q3", "Choke 3", "0a40snAsSiU0fSBrba93YB2", 0, 4),
        ("2GDX9DpZgXsLAkXhHBQU1Q4", "Choke 4", "0a40snAsSiU0fSBrba93YB2", 0, 6),
        ("2GDX9DpZgXsLAkXhHBQU1Q5", "Choke 5", "0a40snAsSiU0fSBrba93YB2", -1, 0),
        ("2GDX9DpZgXsLAkXhHBQU1Q6", "Choke 6", "0a40snAsSiU0fSBrba93YB2", -1, 3),
    ]
    cur.executemany("INSERT INTO tracks(id, name, album, rating, num_times_rated) VALUES (?, ?, ?, ?, ?)", tracks)

    # Function under test.
    db.print_summary()

    # The expected output.
    expected = (
        "10 tracks\n"
        "    9 rated\n"
        "        4 liked\n"
        "        3 neutral\n"
        "        2 disliked\n"
        "    1 unrated\n"
        "4 albums\n"
        "2 artists\n"
    )

    # Verify the output.
    captured = capsys.readouterr()
    assert captured.out == expected
