import requests_mock

from src import database_interface
from src.item import Track, Album, Artist
from src.spotify_interface import SpotifyInterface

from src import spotify_manager as dut


def test_insert_items_from_playlist(tmp_path):
    """
    Test `insert_items_from_playlist` by mocking requests and selecting data.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    playlist_id = "example"
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Create a new temporary database.
    database_path = tmp_path / "test.db"
    app = dut.SpotifyManager(database_path)
    app.api = SpotifyInterface(token)
    app.db.create_tables()
    cur = app.db.con.cursor()

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
        app.insert_items_from_playlist(playlist_id)

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
