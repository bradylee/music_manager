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

        assert get_spotify_playlist_items(token, playlist_id) == None
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
