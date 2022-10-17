from src.item import Track, Album, Artist

from src import database_interface as dut


def test_create_tables(tmp_path):
    """
    Test `create_tables` by inserting and selecting data.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    cur = db._con.cursor()

    # Function under test.
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

    # Check the tables have data.
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert len(rows) == 1
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert len(rows) == 1
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert len(rows) == 1

    # Recreate the tables.
    db.create_tables(force=True)

    # Check the tables are now empty
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert len(rows) == 0
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert len(rows) == 0
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert len(rows) == 0

    # Check the version table includes the latest version.
    rows = cur.execute("SELECT * FROM version").fetchall()
    version = dut.DatabaseInterface.get_latest_schema_version()
    assert rows == [version]

def test_insert_tracks(tmp_path):
    """
    Test `insert_tracks` by selecting data and comparing it to the input.
    """
    # Input data.
    tracks = [
        Track(
            "6bsxDgpU5nlcHNZYtsfZG8",
            "Bleeding Sun",
            album=Album("7hkhFnClNPmRXL20KqdzSO", "Bleeding Sun")
        ),
        Track(
            "15eQh5ZLBoMReY20MDG37T",
            "Breathless",
            album=Album("1GLmxzF8g5p0fcdAatGq5Y", "Fractured")
        ),
        Track(
            "2GDX9DpZgXsLAkXhHBQU1Q",
            "Choke",
            album=Album("0a40snAsSiU0fSBrba93YB", "World Demise")
        ),
    ]

    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    db.insert_tracks(tracks)

    # Select data from the database to check it was inserted correctly.
    cmd = """
      SELECT id,
             name,
             album
        FROM tracks
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    assert len(rows) == 3

    assert rows[0] == ("6bsxDgpU5nlcHNZYtsfZG8", "Bleeding Sun", "7hkhFnClNPmRXL20KqdzSO")
    assert rows[1] == ("15eQh5ZLBoMReY20MDG37T", "Breathless", "1GLmxzF8g5p0fcdAatGq5Y")
    assert rows[2] == ("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB")

def test_insert_albums(tmp_path):
    """
    Test `insert_albums` by selecting data and comparing it to the input.
    """
    # Input data.
    albums = [
        Album(
            "7hkhFnClNPmRXL20KqdzSO",
            "Bleeding Sun",
            artist=Artist("4UgQ3EFa8fEeaIEg54uV5b", "Chelsea Grin")
        ),
        Album(
            "1GLmxzF8g5p0fcdAatGq5Y",
            "Fractured",
            artist=Artist("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD")
        ),
        Album(
            "0a40snAsSiU0fSBrba93YB",
            "World Demise",
            artist=Artist("7bDLHytU8vohbiWbePGrRU", "Falsifier")
        ),
    ]

    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    db.insert_albums(albums)

    # Select data from the database to check it was inserted correctly.
    cmd = """
      SELECT id,
             name,
             artist
        FROM albums
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    assert len(rows) == 3

    assert rows[0] == ("7hkhFnClNPmRXL20KqdzSO", "Bleeding Sun", "4UgQ3EFa8fEeaIEg54uV5b")
    assert rows[1] == ("1GLmxzF8g5p0fcdAatGq5Y", "Fractured", "7z9n8Q0icbgvXqx1RWoGrd")
    assert rows[2] == ("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU")

def test_insert_artists(tmp_path):
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
    db.insert_artists(artists)

    # Select data from the database to check it was inserted correctly.
    cmd = """
      SELECT id,
             name
        FROM artists
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    assert len(rows) == 3

    assert rows[0] == ("4UgQ3EFa8fEeaIEg54uV5b", "Chelsea Grin")
    assert rows[1] == ("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD")
    assert rows[2] == ("7bDLHytU8vohbiWbePGrRU", "Falsifier")

def test_semantic_version_to_tuple():
    """
    Test `semantic_version_to_tuple` with example data.
    """
    assert dut.DatabaseInterface.semantic_version_to_tuple("1.0.0") == (1, 0, 0)
    assert dut.DatabaseInterface.semantic_version_to_tuple("10.0.1") == (10, 0, 1)
    assert dut.DatabaseInterface.semantic_version_to_tuple("2.10.100") == (2, 10, 100)

def test_tuple_to_semantic_version():
    """
    Test `tuple_to_semantic_version` with example data.
    """
    assert dut.DatabaseInterface.tuple_to_semantic_version((1, 0, 0)) == "1.0.0"
    assert dut.DatabaseInterface.tuple_to_semantic_version((10, 0, 1)) == "10.0.1"
    assert dut.DatabaseInterface.tuple_to_semantic_version((2, 10, 100)) == "2.10.100"

def test_get_latest_schema_version():
    """
    Test `get_latest_schema_version` with a mock schemas lookup.
    """
    # Create versions to confirm that they are sorted numerically and not by ASCII.
    schemas = {
        "1.0.0": 'a',
        "10.10.0": 'b',
        "10.0.0": 'c',
        "2.0.10": 'd',
    }

    assert dut.DatabaseInterface.get_latest_schema_version(schemas) == (10, 10, 0)

def test_get_schema():
    """
    Test `get_schema` by requesting valid and invalid versions.
    """

    # Check the value for a real version.
    assert dut.DatabaseInterface.get_schema((1,0,0)) == {
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

    # Check the value for a fake version.
    assert dut.DatabaseInterface.get_schema((0,0,0)) is None

def test_create_table_from_schema(tmp_path):
    """
    Test `create_table_from_schema` by creating an example table and inserting and selecting data.
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

    # Check the tables have data.
    rows = cur.execute("SELECT * FROM example").fetchall()
    assert len(rows) == 2

def test_upgrade_tables(tmp_path):
    """
    Test `upgrade_tables` by creating a 1.0.0 table and updating it to the 1.1.0 schema.
    """
    # Create a new temporary database.
    db = dut.DatabaseInterface(tmp_path / "test.db")
    cur = db._con.cursor()

    # Create tables with an older version.
    db.create_tables(version=(1,0,0))

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

    # Check the tables have only 1.0.0 columns.
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert rows == [("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB")]
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert rows == [("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU")]
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert rows == [("7bDLHytU8vohbiWbePGrRU", "Falsifier")]

    # Function under test.
    db.upgrade_tables((1,1,0))

    # Check the tables now include 1.1.0 columns with default values.
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert rows == [("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 0, 0)]
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert rows == [("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU")]
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert rows == [("7bDLHytU8vohbiWbePGrRU", "Falsifier")]

    # Check the version table shows the updated version.
    rows = cur.execute("SELECT * FROM version").fetchall()
    assert rows == [(1,1,0)]

    # Check that running again does nothing.
    db.upgrade_tables((1,1,0))
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert rows == [("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 0, 0)]
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert rows == [("0a40snAsSiU0fSBrba93YB", "World Demise", "7bDLHytU8vohbiWbePGrRU")]
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert rows == [("7bDLHytU8vohbiWbePGrRU", "Falsifier")]
    rows = cur.execute("SELECT * FROM version").fetchall()
    assert rows == [(1,1,0)]

def test_print_summary(tmp_path, capsys):
    """
    Test `print_summary` by inserting data into a new database.
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

    tracks = [
        ("15eQh5ZLBoMReY20MDG37T", "Breathless", "1GLmxzF8g5p0fcdAatGq5Y"),
        ("15eQh5ZLBoMReY20MDG37T2", "Breathless 2", "1GLmxzF8g5p0fcdAatGq5Y"),
        ("15eQh5ZLBoMReY20MDG37T3", "Breathless 3", "1GLmxzF8g5p0fcdAatGq5Y2"),
        ("15eQh5ZLBoMReY20MDG37T4", "Breathless 4", "1GLmxzF8g5p0fcdAatGq5Y2"),
        ("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB"),
        ("2GDX9DpZgXsLAkXhHBQU1Q2", "Choke 2", "0a40snAsSiU0fSBrba93YB"),
        ("2GDX9DpZgXsLAkXhHBQU1Q3", "Choke 3", "0a40snAsSiU0fSBrba93YB2"),
        ("2GDX9DpZgXsLAkXhHBQU1Q4", "Choke 4", "0a40snAsSiU0fSBrba93YB2"),
    ]
    cur.executemany("INSERT INTO tracks(id, name, album) VALUES (?, ?, ?)", tracks)

    # Function under test.
    db.print_summary()

    # Check the output.
    captured = capsys.readouterr()
    assert captured.out == "8 tracks\n4 albums\n2 artists\n"
