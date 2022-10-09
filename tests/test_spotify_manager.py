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


def test_get_spotify_playlist_items(requests_mock):
    """
    Test `get_spotify_playlist_items` by mocking the request and checking the response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    playlist_id = "example"
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Trimmed down response data.
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
    }

    # Test that a good response results in a list of tracks.
    status_code = 200
    requests_mock.get(endpoint, json=response_data, status_code=status_code)
    tracks = get_spotify_playlist_items(token, playlist_id)

    assert len(tracks) == 3

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
    status_code = 400
    requests_mock.get(endpoint, json=response_data, status_code=status_code)
    assert get_spotify_playlist_items(token, playlist_id) == None
