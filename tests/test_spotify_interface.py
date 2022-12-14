from urllib.parse import parse_qs, urlparse

import requests_mock

from src import spotify_interface as dut


def test_getRequestHeaders():
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


def test_getPlaylistItems():
    """
    Test `get_playlist_items` by mocking the request and checking the response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    playlist_id = "example"
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Limited response data.
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
        "total": 3,
    }

    # Test that a good response results in a list of tracks.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=response_data, status_code=status_code)
        tracks = api.get_playlist_items(playlist_id)

        # Verify there was only one request.
        assert mock.call_count == 1

        # Verify the number of tracks.
        assert len(tracks) == 3

        # Verify the track data.
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


def test_getPlaylistItems_multipleRequests():
    """
    Test `get_playlist_items` limit and offset logic by forcing multiple requests.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    playlist_id = "example"
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    def get_response(request, context):
        """
        Callback to dynamically determine the response, since the function under test
        will make multiple requests with one call.
        """
        # Parse parameters out of the request URL.
        # All of the param values are returned as a list of strings.
        query = urlparse(request.url).query
        params = parse_qs(query)
        limit = int(params["limit"][0])
        offset = int(params["offset"][0])

        assert limit == 1
        assert offset >= 0 and offset < 3

        if offset == 0:
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
                ],
                "total": 3,
            }
        elif offset == 1:
            response_data = {
                "items": [
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
                ],
                "total": 3,
            }
        elif offset == 2:
            response_data = {
                "items": [
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
                "total": 3,
            }

        return response_data

    # Test that multiple requests are made if the total is greater than the limit.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=get_response, status_code=status_code)
        tracks = api.get_playlist_items(playlist_id, limit=1)

        # Verify the number of requests made.
        assert mock.call_count == 3

        # Verify the number of tracks.
        assert len(tracks) == 3

        # Verify the track data.
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


def test_getPlaylistItems_badResponse():
    """
    Test `get_playlist_items` with a bad response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    playlist_id = "example"
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Test that a bad response results in None.
    with requests_mock.mock() as mock:
        status_code = 400
        mock.get(endpoint, json={"fake": "data"}, status_code=status_code)

        assert api.get_playlist_items(playlist_id) is None
        assert mock.call_count == 1


def test_getArtistAlbums():
    """
    Test `get_artist_albums` by mocking the request and checking the response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    artist_id = "0gJ0dOw0r6daBMmJr6ROvQ"
    endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums"

    # Limited response data.
    response_data = {
        "items": [
            {
                "artists": [{"id": "0gJ0dOw0r6daBMmJr6ROvQ", "name": "Abyss Walker"}],
                "album_type": "single",
                "id": "55Eath51v7CjEI6Ca2Inev",
                "name": "Intergalactic (Metal Version)",
                "release_date": "2022-05-06",
            },
            {
                "artists": [{"id": "0gJ0dOw0r6daBMmJr6ROvQ", "name": "Abyss Walker"}],
                "album_type": "single",
                "id": "1PGRRV8bSTwiT66uIlJdQ3",
                "name": "Ruff Ryder's Anthem (Metal Version)",
                "release_date": "2022-04-15",
            },
            {
                "artists": [{"id": "0gJ0dOw0r6daBMmJr6ROvQ", "name": "Abyss Walker"}],
                "album_type": "single",
                "id": "4vTvDu4oVQmgSTAa9W2y1Z",
                "name": "Astronaut In The Ocean",
                "release_date": "2021-07-15",
            },
        ],
        "total": 3,
    }

    # Test that a good response results in a list of albums.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=response_data, status_code=status_code)
        albums = api.get_artist_albums(artist_id)

        # Verify there was only one request.
        assert mock.call_count == 1

        # Verify the number of albums.
        assert len(albums) == 3

        # Verify the album data.
        assert albums[0].id == "55Eath51v7CjEI6Ca2Inev"
        assert albums[0].name == "Intergalactic (Metal Version)"
        assert albums[0].artist.id == "0gJ0dOw0r6daBMmJr6ROvQ"
        assert albums[0].artist.name == "Abyss Walker"
        assert albums[1].id == "1PGRRV8bSTwiT66uIlJdQ3"
        assert albums[1].name == "Ruff Ryder's Anthem (Metal Version)"
        assert albums[1].artist.id == "0gJ0dOw0r6daBMmJr6ROvQ"
        assert albums[1].artist.name == "Abyss Walker"
        assert albums[2].id == "4vTvDu4oVQmgSTAa9W2y1Z"
        assert albums[2].name == "Astronaut In The Ocean"
        assert albums[2].artist.id == "0gJ0dOw0r6daBMmJr6ROvQ"
        assert albums[2].artist.name == "Abyss Walker"


def test_getArtistAlbums_multipleRequests():
    """
    Test `get_artist_albums` limit and offset logic by forcing multiple requests.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    artist_id = "0gJ0dOw0r6daBMmJr6ROvQ"
    endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums"

    # Trimmed down response data.
    def get_response(request, context):
        """
        Callback to dynamically determine the response, since the function under test
        will make multiple requests with one call.
        """
        # Parse parameters out of the request URL.
        # All of the param values are returned as a list of strings.
        query = urlparse(request.url).query
        params = parse_qs(query)
        limit = int(params["limit"][0])
        offset = int(params["offset"][0])

        assert limit == 1
        assert offset >= 0 and offset < 3

        if offset == 0:
            response_data = {
                "items": [
                    {
                        "artists": [
                            {"id": "0gJ0dOw0r6daBMmJr6ROvQ", "name": "Abyss Walker"}
                        ],
                        "album_type": "single",
                        "id": "55Eath51v7CjEI6Ca2Inev",
                        "name": "Intergalactic (Metal Version)",
                        "release_date": "2022-05-06",
                    },
                ],
                "total": 3,
            }
        elif offset == 1:
            response_data = {
                "items": [
                    {
                        "artists": [
                            {"id": "0gJ0dOw0r6daBMmJr6ROvQ", "name": "Abyss Walker"}
                        ],
                        "album_type": "single",
                        "id": "1PGRRV8bSTwiT66uIlJdQ3",
                        "name": "Ruff Ryder's Anthem (Metal Version)",
                        "release_date": "2022-04-15",
                    },
                ],
                "total": 3,
            }
        elif offset == 2:
            response_data = {
                "items": [
                    {
                        "artists": [
                            {"id": "0gJ0dOw0r6daBMmJr6ROvQ", "name": "Abyss Walker"}
                        ],
                        "album_type": "single",
                        "id": "4vTvDu4oVQmgSTAa9W2y1Z",
                        "name": "Astronaut In The Ocean",
                        "release_date": "2021-07-15",
                    },
                ],
                "total": 3,
            }

        return response_data

    # Test that multiple requests are made if the total is greater than the limit.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=get_response, status_code=status_code)
        albums = api.get_artist_albums(artist_id, limit=1)

        # Verify the number of requests made.
        assert mock.call_count == 3

        # Verify the number of albums.
        assert len(albums) == 3

        # Verify the album data.
        assert albums[0].id == "55Eath51v7CjEI6Ca2Inev"
        assert albums[0].name == "Intergalactic (Metal Version)"
        assert albums[0].artist.id == "0gJ0dOw0r6daBMmJr6ROvQ"
        assert albums[0].artist.name == "Abyss Walker"
        assert albums[1].id == "1PGRRV8bSTwiT66uIlJdQ3"
        assert albums[1].name == "Ruff Ryder's Anthem (Metal Version)"
        assert albums[1].artist.id == "0gJ0dOw0r6daBMmJr6ROvQ"
        assert albums[1].artist.name == "Abyss Walker"
        assert albums[2].id == "4vTvDu4oVQmgSTAa9W2y1Z"
        assert albums[2].name == "Astronaut In The Ocean"
        assert albums[2].artist.id == "0gJ0dOw0r6daBMmJr6ROvQ"
        assert albums[2].artist.name == "Abyss Walker"


def test_getArtistAlbums_badResponse():
    """
    Test `get_artist_albums` with a bad response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    artist_id = "0gJ0dOw0r6daBMmJr6ROvQ"
    endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums"

    # Test that a bad response results in None.
    with requests_mock.mock() as mock:
        status_code = 400
        mock.get(endpoint, json={"fake": "data"}, status_code=status_code)

        assert api.get_artist_albums(artist_id) is None
        assert mock.call_count == 1


def test_getAlbumTracks():
    """
    Test `get_album_tracks` by mocking the request and checking the response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    album_id = "1B5sG6YCOqglv5djSYqp0X"
    endpoint = f"https://api.spotify.com/v1/albums/{album_id}"

    # Limited response data.
    response_data = {
        "id": "1B5sG6YCOqglv5djSYqp0X",
        "name": "The Beginning of the End",
        "tracks": {
            "items": [
                {
                    "explicit": False,
                    "id": "55Ps7eQ0IpSypn32TH6uCi",
                    "is_playable": True,
                    "name": "The Beginning",
                },
                {
                    "explicit": False,
                    "id": "5xyv86cHra90CtItbROxdl",
                    "is_playable": True,
                    "name": "Auctioneer of Depravity",
                },
                {
                    "explicit": False,
                    "id": "4tiUaYEcc20fVSluB31T0y",
                    "is_playable": True,
                    "name": "The Depopulation Programme",
                },
            ],
            "total": 3,
        },
    }

    # Test that a good response results in a list of tracks.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=response_data, status_code=status_code)
        tracks = api.get_album_tracks(album_id)

        # Verify there was only one request.
        assert mock.call_count == 1

        # Verify the number of tracks.
        assert len(tracks) == 3

        # Verify the track data.
        assert tracks[0].id == "55Ps7eQ0IpSypn32TH6uCi"
        assert tracks[0].name == "The Beginning"
        assert tracks[0].album.id == "1B5sG6YCOqglv5djSYqp0X"
        assert tracks[0].album.name == "The Beginning of the End"
        assert tracks[0].album.artist is None
        assert tracks[1].id == "5xyv86cHra90CtItbROxdl"
        assert tracks[1].name == "Auctioneer of Depravity"
        assert tracks[1].album.id == "1B5sG6YCOqglv5djSYqp0X"
        assert tracks[1].album.name == "The Beginning of the End"
        assert tracks[1].album.artist is None
        assert tracks[2].id == "4tiUaYEcc20fVSluB31T0y"
        assert tracks[2].name == "The Depopulation Programme"
        assert tracks[2].album.id == "1B5sG6YCOqglv5djSYqp0X"
        assert tracks[2].album.name == "The Beginning of the End"
        assert tracks[2].album.artist is None


def test_getAlbumTracks_badResponse():
    """
    Test `get_album_tracks` with a bad response.
    """
    # Set arbitrary values since the request is mocked.
    token = "sample"
    api = dut.SpotifyInterface(token)
    album_id = "1B5sG6YCOqglv5djSYqp0X"
    endpoint = f"https://api.spotify.com/v1/albums/{album_id}"

    # Test that a bad response results in None.
    with requests_mock.mock() as mock:
        status_code = 400
        mock.get(endpoint, json={"fake": "data"}, status_code=status_code)

        assert api.get_album_tracks(album_id) is None
        assert mock.call_count == 1
