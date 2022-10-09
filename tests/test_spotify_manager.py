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
    response_data = {"hello": "world"}

    # Test JSON data is returned on a good response.
    status_code = 200
    requests_mock.get(endpoint, json=response_data, status_code=status_code)
    data = get_spotify_playlist_items(token, playlist_id)
    assert data == response_data

    # Test None is returned on a bad response.
    status_code = 400
    requests_mock.get(endpoint, json=response_data, status_code=status_code)
    data = get_spotify_playlist_items(token, playlist_id)
    assert data == None
