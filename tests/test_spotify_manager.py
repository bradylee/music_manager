from src.spotify_manager import *


def test_get_spotify_request_headers():
    """
    Test `get_spotify_request_headers` by calling with different token strings and verifying the constructed value.
    """
    # Test a sample token.
    token = 'sample'
    headers = get_spotify_request_headers(token)
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"
    assert headers["Authorization"] == "Bearer sample"

    # Test another sample.
    token = 'another_sample'
    headers = get_spotify_request_headers(token)
    assert headers["Authorization"] == "Bearer another_sample"
