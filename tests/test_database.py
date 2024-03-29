import pytest

from musicmanager import database as dut
from musicmanager.item import Album, Artist, Track


def test_transaction(tmp_path):
    """
    Test `transaction` by checking that changes are committed when no exception is thrown.
    """
    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")

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
    db = dut.Database(tmp_path / "test.db")

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
    Test `create_tables` by checking the list of tables.
    """
    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")

    # Function under test.
    db.create_tables()

    # Verify that all tables were created.
    tables = db.get_tables()
    assert "tracks" in tables
    assert "albums" in tables
    assert "artists" in tables


def test_createTables_force(tmp_path):
    """
    Test `create_tables` by confirming data is cleared on force.
    """
    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")
    cur = db._con.cursor()

    # Create the initial tables.
    db.create_tables()

    # Insert sample data into the tables.
    cmd = """
    INSERT INTO tracks(id, name, album_id)
         VALUES ('2GDX9DpZgXsLAkXhHBQU1Q', 'Choke', '0a40snAsSiU0fSBrba93YB');

    INSERT INTO albums(id, name, artist_id)
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
            "7hkhFnClNPmRXL20KqdzSO",
        ),
        Track(
            "15eQh5ZLBoMReY20MDG37T",
            "Breathless",
            "1GLmxzF8g5p0fcdAatGq5Y",
        ),
        Track(
            "2GDX9DpZgXsLAkXhHBQU1Q",
            "Choke",
            "0a40snAsSiU0fSBrba93YB",
        ),
    ]

    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    with db.transaction():
        db.insert_tracks(tracks)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name,
             album_id,
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
        None,
    )
    assert rows[1] == (
        "15eQh5ZLBoMReY20MDG37T",
        "Breathless",
        "1GLmxzF8g5p0fcdAatGq5Y",
        None,
    )
    assert rows[2] == (
        "2GDX9DpZgXsLAkXhHBQU1Q",
        "Choke",
        "0a40snAsSiU0fSBrba93YB",
        None,
    )


def test_insertTracks_rated(tmp_path):
    """
    Test `insert_tracks` can optionally set the rating.
    """
    # Input data.
    tracks = [
        Track(
            "6bsxDgpU5nlcHNZYtsfZG8",
            "Bleeding Sun",
            "7hkhFnClNPmRXL20KqdzSO",
        ),
        Track(
            "15eQh5ZLBoMReY20MDG37T",
            "Breathless",
            "1GLmxzF8g5p0fcdAatGq5Y",
        ),
        Track(
            "2GDX9DpZgXsLAkXhHBQU1Q",
            "Choke",
            "0a40snAsSiU0fSBrba93YB",
        ),
    ]

    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    with db.transaction():
        db.insert_tracks(tracks, rating=1)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name,
             album_id,
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
             album_id,
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
            "4UgQ3EFa8fEeaIEg54uV5b",
        ),
        Album(
            "1GLmxzF8g5p0fcdAatGq5Y",
            "Fractured",
            "7z9n8Q0icbgvXqx1RWoGrd",
        ),
        Album(
            "0a40snAsSiU0fSBrba93YB",
            "World Demise",
            "7bDLHytU8vohbiWbePGrRU",
        ),
    ]

    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")
    db.create_tables()
    cur = db._con.cursor()

    # Function under test.
    with db.transaction():
        db.insert_albums(albums)

    # Select data from the database to read it back.
    cmd = """
      SELECT id,
             name,
             artist_id
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
    db = dut.Database(tmp_path / "test.db")
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


def test_createTableFromSchema(tmp_path):
    """
    Test `create_table_from_schema` using a simplified schema.
    """
    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")
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


def test_printSummary(tmp_path, capsys):
    """
    Test `print_summary` by inserting different numbers of tracks, albums, and artists.
    """
    # Create a new temporary database.
    db = dut.Database(tmp_path / "test.db")
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
    cur.executemany("INSERT INTO albums(id, name, artist_id) VALUES (?, ?, ?)", albums)

    # Unique tracks with different ratings.
    tracks = [
        ("15eQh5ZLBoMReY20MDG37T", "Breathless", "1GLmxzF8g5p0fcdAatGq5Y", 1),
        ("15eQh5ZLBoMReY20MDG37T2", "Breathless 2", "1GLmxzF8g5p0fcdAatGq5Y", 1),
        ("15eQh5ZLBoMReY20MDG37T3", "Breathless 3", "1GLmxzF8g5p0fcdAatGq5Y2", 1),
        ("15eQh5ZLBoMReY20MDG37T4", "Breathless 4", "1GLmxzF8g5p0fcdAatGq5Y2", 1),
        ("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", None),
        ("2GDX9DpZgXsLAkXhHBQU1Q2", "Choke 2", "0a40snAsSiU0fSBrba93YB", 0),
        ("2GDX9DpZgXsLAkXhHBQU1Q3", "Choke 3", "0a40snAsSiU0fSBrba93YB2", 0),
        ("2GDX9DpZgXsLAkXhHBQU1Q4", "Choke 4", "0a40snAsSiU0fSBrba93YB2", 0),
        ("2GDX9DpZgXsLAkXhHBQU1Q5", "Choke 5", "0a40snAsSiU0fSBrba93YB2", -1),
        ("2GDX9DpZgXsLAkXhHBQU1Q6", "Choke 6", "0a40snAsSiU0fSBrba93YB2", -1),
    ]
    cur.executemany(
        "INSERT INTO tracks(id, name, album_id, rating) VALUES (?, ?, ?, ?)",
        tracks,
    )

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
