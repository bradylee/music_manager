import requests_mock
import sqlite3
from urllib.parse import urlparse, parse_qs

from src.spotify_manager import *


def test_get_spotify_request_headers():
    """
    Test `get_spotify_request_headers` by calling with different token strings and checking the
    constructed value.
    """
    # Test a sample token.
    token = "sample"
    headers = get_spotify_request_headers(token)
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"
    assert headers["Authorization"] == "Bearer sample"

    # Test another sample.
    token = "another_sample"
    headers = get_spotify_request_headers(token)
    assert headers["Authorization"] == "Bearer another_sample"


def test_get_spotify_playlist_items():
    """
    Test `get_spotify_playlist_items` by mocking the request and checking the response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    playlist_id = "example"
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Trimmed down response data.
    def get_response(request, context):
        """
        Callback to dynamically determine the response, since the function under test may make
        multiple requests with one call.
        """
        # Parse parameters out of request URL.
        # All of the param values are returned as a list of strings.
        query = urlparse(request.url).query
        params = parse_qs(query)
        limit = int(params["limit"][0])
        offset = int(params["offset"][0])

        # Full response by default.
        response_data = {
            "items": [
                {
                    "track": {
                        "album": {
                            "artists": [
                                {
                                    "id": "4UgQ3EFa8fEeaIEg54uV5b",
                                    "name": "Chelsea Grin",
                                }
                            ],
                            "id": "7hkhFnClNPmRXL20KqdzSO",
                            "name": "Bleeding Sun",
                        },
                        "id": "6bsxDgpU5nlcHNZYtsfZG8",
                        "name": "Bleeding Sun",
                    },
                },
                {
                    "track": {
                        "album": {
                            "artists": [
                                {
                                    "id": "7z9n8Q0icbgvXqx1RWoGrd",
                                    "name": "FRCTRD",
                                }
                            ],
                            "id": "1GLmxzF8g5p0fcdAatGq5Y",
                            "name": "Fractured",
                        },
                        "id": "15eQh5ZLBoMReY20MDG37T",
                        "name": "Breathless",
                    },
                },
                {
                    "track": {
                        "album": {
                            "artists": [
                                {
                                    "id": "7bDLHytU8vohbiWbePGrRU",
                                    "name": "Falsifier",
                                }
                            ],
                            "id": "0a40snAsSiU0fSBrba93YB",
                            "name": "World Demise",
                        },
                        "id": "2GDX9DpZgXsLAkXhHBQU1Q",
                        "name": "Choke",
                    },
                },
            ],
            "total": 3
        }

        # Slice the items based on the given offset and limit.
        response_data["items"] = response_data["items"][offset:offset+limit]
        return response_data

    # Test that a good response results in a list of tracks.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=get_response, status_code=status_code)
        tracks = get_spotify_playlist_items(token, playlist_id)

        assert len(tracks) == 3
        assert mock.call_count == 1

        assert tracks[0].id == "6bsxDgpU5nlcHNZYtsfZG8"
        assert tracks[0].name == "Bleeding Sun"
        assert tracks[0].album.id == "7hkhFnClNPmRXL20KqdzSO"
        assert tracks[0].album.name == "Bleeding Sun"
        assert tracks[0].album.artist.id == "4UgQ3EFa8fEeaIEg54uV5b"
        assert tracks[0].album.artist.name == "Chelsea Grin"

        assert tracks[1].id == "15eQh5ZLBoMReY20MDG37T"
        assert tracks[1].name == "Breathless"
        assert tracks[1].album.id == "1GLmxzF8g5p0fcdAatGq5Y"
        assert tracks[1].album.name == "Fractured"
        assert tracks[1].album.artist.id == "7z9n8Q0icbgvXqx1RWoGrd"
        assert tracks[1].album.artist.name == "FRCTRD"

        assert tracks[2].id == "2GDX9DpZgXsLAkXhHBQU1Q"
        assert tracks[2].name == "Choke"
        assert tracks[2].album.id == "0a40snAsSiU0fSBrba93YB"
        assert tracks[2].album.name == "World Demise"
        assert tracks[2].album.artist.id == "7bDLHytU8vohbiWbePGrRU"
        assert tracks[2].album.artist.name == "Falsifier"

    # Test that multiple requests are made if the total is greater than the limit.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=get_response, status_code=status_code)
        tracks = get_spotify_playlist_items(token, playlist_id, limit=1)

        assert len(tracks) == 3
        assert mock.call_count == 3

        assert tracks[0].id == "6bsxDgpU5nlcHNZYtsfZG8"
        assert tracks[0].name == "Bleeding Sun"
        assert tracks[0].album.id == "7hkhFnClNPmRXL20KqdzSO"
        assert tracks[0].album.name == "Bleeding Sun"
        assert tracks[0].album.artist.id == "4UgQ3EFa8fEeaIEg54uV5b"
        assert tracks[0].album.artist.name == "Chelsea Grin"

        assert tracks[1].id == "15eQh5ZLBoMReY20MDG37T"
        assert tracks[1].name == "Breathless"
        assert tracks[1].album.id == "1GLmxzF8g5p0fcdAatGq5Y"
        assert tracks[1].album.name == "Fractured"
        assert tracks[1].album.artist.id == "7z9n8Q0icbgvXqx1RWoGrd"
        assert tracks[1].album.artist.name == "FRCTRD"

        assert tracks[2].id == "2GDX9DpZgXsLAkXhHBQU1Q"
        assert tracks[2].name == "Choke"
        assert tracks[2].album.id == "0a40snAsSiU0fSBrba93YB"
        assert tracks[2].album.name == "World Demise"
        assert tracks[2].album.artist.id == "7bDLHytU8vohbiWbePGrRU"
        assert tracks[2].album.artist.name == "Falsifier"

    # Test that a bad response results in None.
    with requests_mock.mock() as mock:
        status_code = 400
        mock.get(endpoint, json=get_response, status_code=status_code)

        assert get_spotify_playlist_items(token, playlist_id) is None
        assert mock.call_count == 1

def test_create_tables(tmp_path):
    """
    Test `create_tables` by inserting and selecting data.
    """
    # Create a new temporary database.
    con = sqlite3.connect(tmp_path / "test.db")
    cur = con.cursor()

    # Function under test.
    create_tables(con)

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
    create_tables(con, force=True)

    # Check the tables are now empty
    rows = cur.execute("SELECT * FROM tracks").fetchall()
    assert len(rows) == 0
    rows = cur.execute("SELECT * FROM albums").fetchall()
    assert len(rows) == 0
    rows = cur.execute("SELECT * FROM artists").fetchall()
    assert len(rows) == 0

    # Check the version table includes the latest version.
    rows = cur.execute("SELECT * FROM version").fetchall()
    version = get_latest_schema_version()
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
    con = sqlite3.connect(tmp_path / "test.db")
    cur = con.cursor()
    create_tables(con)

    # Function under test.
    insert_tracks(con, tracks)

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
    con = sqlite3.connect(tmp_path / "test.db")
    cur = con.cursor()
    create_tables(con)

    # Function under test.
    insert_albums(con, albums)

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
    con = sqlite3.connect(tmp_path / "test.db")
    cur = con.cursor()
    create_tables(con)

    # Function under test.
    insert_artists(con, artists)

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

def test_get_album_list():
    """
    Test `get_album_list` with sample data including duplicates.
    """
    # Input data that includes duplicate albums.
    tracks = [
        Track(
            "6bsxDgpU5nlcHNZYtsfZG8",
            "Bleeding Sun",
            album=Album("7hkhFnClNPmRXL20KqdzSO", "Bleeding Sun")
        ),
        Track(
            "6bsxDgpU5nlcHNZYtsfZG82",
            "Bleeding Sun 2",
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

    # Function under test.
    albums = get_album_list(tracks)

    # Check the duplicate album was removed.
    assert len(albums) == 3

    # Check the object member values.
    assert albums[0].id == "7hkhFnClNPmRXL20KqdzSO"
    assert albums[0].name == "Bleeding Sun"
    assert albums[1].id == "1GLmxzF8g5p0fcdAatGq5Y"
    assert albums[1].name == "Fractured"
    assert albums[2].id == "0a40snAsSiU0fSBrba93YB"
    assert albums[2].name == "World Demise"

def test_get_artist_list():
    """
    Test `get_artist_list` with sample data including duplicates.
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
            "1GLmxzF8g5p0fcdAatGq5Y2",
            "Fractured 2",
            artist=Artist("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD")
        ),
        Album(
            "0a40snAsSiU0fSBrba93YB",
            "World Demise",
            artist=Artist("7bDLHytU8vohbiWbePGrRU", "Falsifier")
        ),
    ]

    # Function under test.
    artists = get_artist_list(albums)

    # Check the duplicate artist was removed.
    assert len(artists) == 3

    # Check the object member values.
    assert artists[0].id == "4UgQ3EFa8fEeaIEg54uV5b"
    assert artists[0].name == "Chelsea Grin"
    assert artists[1].id == "7z9n8Q0icbgvXqx1RWoGrd"
    assert artists[1].name == "FRCTRD"
    assert artists[2].id == "7bDLHytU8vohbiWbePGrRU"
    assert artists[2].name == "Falsifier"

def test_insert_items_from_playlist(tmp_path):
    """
    Test `insert_items_from_playlist` by mocking requests and selecting data.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    playlist_id = "example"
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Create a new temporary database.
    con = sqlite3.connect(tmp_path / "test.db")
    cur = con.cursor()

    # Function under test.
    create_tables(con)

    # Mock response data.
    response_data = {
        "items": [
            {
                "track": {
                    "album": {
                        "artists": [
                            {
                                "id": "4UgQ3EFa8fEeaIEg54uV5b",
                                "name": "Chelsea Grin",
                            }
                        ],
                        "id": "7hkhFnClNPmRXL20KqdzSO",
                        "name": "Bleeding Sun",
                    },
                    "id": "6bsxDgpU5nlcHNZYtsfZG8",
                    "name": "Bleeding Sun",
                },
            },
            {
                "track": {
                    "album": {
                        "artists": [
                            {
                                "id": "7z9n8Q0icbgvXqx1RWoGrd",
                                "name": "FRCTRD",
                            }
                        ],
                        "id": "1GLmxzF8g5p0fcdAatGq5Y",
                        "name": "Fractured",
                    },
                    "id": "15eQh5ZLBoMReY20MDG37T",
                    "name": "Breathless",
                },
            },
            {
                "track": {
                    "album": {
                        "artists": [
                            {
                                "id": "7bDLHytU8vohbiWbePGrRU",
                                "name": "Falsifier",
                            }
                        ],
                        "id": "0a40snAsSiU0fSBrba93YB",
                        "name": "World Demise",
                    },
                    "id": "2GDX9DpZgXsLAkXhHBQU1Q",
                    "name": "Choke",
                },
            },
        ],
        "total": 3
    }

    # Call the function under test with the mocked request.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=response_data, status_code=status_code)
        insert_items_from_playlist(con, token, playlist_id)

    # Select and check track data.
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

    # Select and check album data.
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

    # Select and check artist data.
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
    assert semantic_version_to_tuple("1.0.0") == (1, 0, 0)
    assert semantic_version_to_tuple("10.0.1") == (10, 0, 1)
    assert semantic_version_to_tuple("2.10.100") == (2, 10, 100)

def test_tuple_to_semantic_version():
    """
    Test `tuple_to_semantic_version` with example data.
    """
    assert tuple_to_semantic_version((1, 0, 0)) == "1.0.0"
    assert tuple_to_semantic_version((10, 0, 1)) == "10.0.1"
    assert tuple_to_semantic_version((2, 10, 100)) == "2.10.100"

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

    assert get_latest_schema_version(schemas) == (10, 10, 0)

def test_get_schema():
    """
    Test `get_schema` by requesting valid and invalid versions.
    """

    # Check the value for a real version.
    assert get_schema((1,0,0)) == {
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
    assert get_schema((0,0,0)) is None

def test_create_table_from_schema(tmp_path):
    """
    Test `create_table_from_schema` by creating an example table and inserting and selecting data.
    """
    # Create a new temporary database.
    con = sqlite3.connect(tmp_path / "test.db")
    cur = con.cursor()

    # Example schema.
    schema = {
        "string": "text NOT NULL PRIMARY KEY",
        "number": "int NOT NULL",
    }

    # Function under test.
    create_table_from_schema(con, "example", schema)

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
