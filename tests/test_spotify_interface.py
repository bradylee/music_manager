import requests_mock
from urllib.parse import urlparse, parse_qs

from src import spotify_interface as dut


def test_get_request_headers():
    """
    Test `get_request_headers` by calling with different token strings and checking the
    constructed value.
    """
    # Test a sample token.
    token = "sample"
    api = dut.SpotifyInterface(token)
    headers = api.get_request_headers()
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"
    assert headers["Authorization"] == "Bearer sample"

    # Test another sample.
    token = "another_sample"
    api = dut.SpotifyInterface(token)
    headers = api.get_request_headers()
    assert headers["Authorization"] == "Bearer another_sample"

def test_get_playlist_items():
    """
    Test `get_playlist_items` by mocking the request and checking the response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
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
        tracks = api.get_playlist_items(playlist_id)

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
        tracks = api.get_playlist_items(playlist_id, limit=1)

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

        assert api.get_playlist_items(playlist_id) is None
        assert mock.call_count == 1
