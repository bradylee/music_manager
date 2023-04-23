import requests_mock

from musicmanager import core as dut
from musicmanager.item import Album, Artist
from musicmanager.spotify_interface import SpotifyInterface


def test_insertItemsFromPlaylist(tmp_path):
    """
    Test `insert_items_from_playlist` by mocking the requests and comparing table data.
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
    cur = app.db._con.cursor()

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
        "total": 3,
    }

    # Call the function under test with the mocked request.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=response_data, status_code=status_code)
        app.insert_items_from_playlist(playlist_id)

    # Get the track data.
    cmd = """
      SELECT id,
             name,
             album,
             rating
        FROM tracks
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the number of tracks.
    assert len(rows) == 3

    # Verify the track data.
    assert rows[0] == (
        "6bsxDgpU5nlcHNZYtsfZG8",
        "Bleeding Sun",
        "7hkhFnClNPmRXL20KqdzSO",
        0,
    )
    assert rows[1] == (
        "15eQh5ZLBoMReY20MDG37T",
        "Breathless",
        "1GLmxzF8g5p0fcdAatGq5Y",
        0,
    )
    assert rows[2] == ("2GDX9DpZgXsLAkXhHBQU1Q", "Choke", "0a40snAsSiU0fSBrba93YB", 0)

    # Get the album data.
    cmd = """
      SELECT id,
             name,
             artist
        FROM albums
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the number of albums.
    assert len(rows) == 3

    # Verify the album data.
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

    # Get the artist data.
    cmd = """
      SELECT id,
             name
        FROM artists
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the number of artists.
    assert len(rows) == 3

    # Verify the artist data.
    assert rows[0] == ("4UgQ3EFa8fEeaIEg54uV5b", "Chelsea Grin")
    assert rows[1] == ("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD")
    assert rows[2] == ("7bDLHytU8vohbiWbePGrRU", "Falsifier")


def test_insertItemsFromPlaylist_rated(tmp_path):
    """
    Test `insert_items_from_playlist` can optionally set track rating.
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
    cur = app.db._con.cursor()

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
        "total": 3,
    }

    # Call the function under test with the mocked request.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(endpoint, json=response_data, status_code=status_code)
        app.insert_items_from_playlist(playlist_id, rating=1)

    # Get the track data.
    cmd = """
      SELECT id,
             name,
             album,
             rating
        FROM tracks
    ORDER BY name
    """
    rows = cur.execute(cmd).fetchall()

    # Verify the track data.
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


def test_fetchAlbums(tmp_path):
    """
    Test `fetch_albums` by mocking the request and selecting from the database.
    """
    # Create a new temporary database.
    database_path = tmp_path / "test.db"
    app = dut.SpotifyManager(database_path)
    app.api = SpotifyInterface("sample_token")
    app.db.create_tables()

    # Populate artists, so we can fetch albums for these.
    artists = [Artist("0gJ0dOw0r6d", "Abyss"), Artist("aBMmJr6ROvQ", "Walker")]
    with app.db.transaction():
        app.db.insert_artists(artists)

    # Limited response data for the first artist.
    response_data_1 = {
        "items": [
            {
                "artists": [{"id": "0gJ0dOw0r6d", "name": "Abyss"}],
                "id": "55Eath51v7Cj",
                "name": "Intergalactic",
            },
            {
                "artists": [{"id": "0gJ0dOw0r6d", "name": "Abyss"}],
                "id": "1PGRRV8bSTwi",
                "name": "Ruff",
            },
            {
                "artists": [{"id": "0gJ0dOw0r6d", "name": "Abyss"}],
                "id": "4vTvDu4oVQmg",
                "name": "Astronaut",
            },
        ],
        "total": 3,
    }

    # Limited response data for the second artist.
    response_data_2 = {
        "items": [
            {
                "artists": [{"id": "aBMmJr6ROvQ", "name": "Walker"}],
                "id": "jEI6Ca2Inev",
                "name": "Metal Version",
            },
            {
                "artists": [{"id": "aBMmJr6ROvQ", "name": "Walker"}],
                "id": "wiT66uIlJdQ3",
                "name": "Anthem",
            },
            {
                "artists": [{"id": "aBMmJr6ROvQ", "name": "Walker"}],
                "id": "gSTAa9W2y1Z",
                "name": "Ocean",
            },
        ],
        "total": 3,
    }

    # Mock the requests.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(
            "https://api.spotify.com/v1/artists/0gJ0dOw0r6d/albums",
            json=response_data_1,
            status_code=status_code,
        )
        mock.get(
            "https://api.spotify.com/v1/artists/aBMmJr6ROvQ/albums",
            json=response_data_2,
            status_code=status_code,
        )

        # Function under test.
        app.fetch_albums()

        # Get the album data.
        albums = app.db.get_albums()

        # Verify the number of albums.
        assert len(albums) == 6

        # Verify the album data.
        assert albums[0].id == "55Eath51v7Cj"
        assert albums[0].name == "Intergalactic"
        assert albums[0].artist.id == "0gJ0dOw0r6d"
        assert albums[0].artist.name == "Abyss"
        assert albums[1].id == "1PGRRV8bSTwi"
        assert albums[1].name == "Ruff"
        assert albums[1].artist.id == "0gJ0dOw0r6d"
        assert albums[1].artist.name == "Abyss"
        assert albums[2].id == "4vTvDu4oVQmg"
        assert albums[2].name == "Astronaut"
        assert albums[2].artist.id == "0gJ0dOw0r6d"
        assert albums[2].artist.name == "Abyss"
        assert albums[3].id == "jEI6Ca2Inev"
        assert albums[3].name == "Metal Version"
        assert albums[3].artist.id == "aBMmJr6ROvQ"
        assert albums[3].artist.name == "Walker"
        assert albums[4].id == "wiT66uIlJdQ3"
        assert albums[4].name == "Anthem"
        assert albums[4].artist.id == "aBMmJr6ROvQ"
        assert albums[4].artist.name == "Walker"
        assert albums[5].id == "gSTAa9W2y1Z"
        assert albums[5].name == "Ocean"
        assert albums[5].artist.id == "aBMmJr6ROvQ"
        assert albums[5].artist.name == "Walker"


def test_fetchTracks(tmp_path):
    """
    Test `fetch_tracks` by mocking the request and selecting from the database.
    """
    # Create a new temporary database.
    database_path = tmp_path / "test.db"
    app = dut.SpotifyManager(database_path)
    app.api = SpotifyInterface("sample_token")
    app.db.create_tables()

    # Populate the albums, so we can fetch tracks for these.
    # We also need to populate the artist so the join succeeds.
    artist = Artist("0gJ0dOw0r6d", "Acrania")
    albums = [
        Album("1B5sG6YCOqg", "The Beginning", artist=artist),
        Album("lv5djSYqp0X", "The End", artist=artist),
    ]
    with app.db.transaction():
        app.db.insert_artists([artist])
        app.db.insert_albums(albums)

    # Limited response data for the first album.
    response_data_1 = {
        "id": "1B5sG6YCOqg",
        "name": "The Beginning",
        "tracks": {
            "items": [
                {
                    "id": "55Ps7eQ0IpSy",
                    "name": "Beginning",
                },
                {
                    "id": "5xyv86cHra90",
                    "name": "Auctioneer",
                },
                {
                    "id": "4tiUaYEcc20f",
                    "name": "Depopulation",
                },
            ],
            "total": 3,
        },
    }

    # Limited response data for the second album.
    response_data_2 = {
        "id": "lv5djSYqp0X",
        "name": "The End",
        "tracks": {
            "items": [
                {
                    "id": "IpSypn32TH6uCi",
                    "name": "End",
                },
                {
                    "id": "a90CtItbROxdl",
                    "name": "Depravity",
                },
                {
                    "id": "c20fVSluB31T0y",
                    "name": "Programme",
                },
            ],
            "total": 3,
        },
    }

    # Mock the requests.
    with requests_mock.mock() as mock:
        status_code = 200
        mock.get(
            "https://api.spotify.com/v1/albums/1B5sG6YCOqg",
            json=response_data_1,
            status_code=status_code,
        )
        mock.get(
            "https://api.spotify.com/v1/albums/lv5djSYqp0X",
            json=response_data_2,
            status_code=status_code,
        )

        # Function under test.
        app.fetch_tracks()

        # Get the track data.
        tracks = app.db.get_tracks()

        # Verify the number of albums.
        assert len(tracks) == 6

        # Verify the track data.
        assert tracks[0].id == "55Ps7eQ0IpSy"
        assert tracks[0].name == "Beginning"
        assert tracks[0].album.id == "1B5sG6YCOqg"
        assert tracks[0].album.name == "The Beginning"
        assert tracks[0].album.artist.id == "0gJ0dOw0r6d"
        assert tracks[0].album.artist.name == "Acrania"
        assert tracks[1].id == "5xyv86cHra90"
        assert tracks[1].name == "Auctioneer"
        assert tracks[1].album.id == "1B5sG6YCOqg"
        assert tracks[1].album.name == "The Beginning"
        assert tracks[1].album.artist.id == "0gJ0dOw0r6d"
        assert tracks[1].album.artist.name == "Acrania"
        assert tracks[2].id == "4tiUaYEcc20f"
        assert tracks[2].name == "Depopulation"
        assert tracks[2].album.id == "1B5sG6YCOqg"
        assert tracks[2].album.name == "The Beginning"
        assert tracks[2].album.artist.id == "0gJ0dOw0r6d"
        assert tracks[2].album.artist.name == "Acrania"
        assert tracks[3].id == "IpSypn32TH6uCi"
        assert tracks[3].name == "End"
        assert tracks[3].album.id == "lv5djSYqp0X"
        assert tracks[3].album.name == "The End"
        assert tracks[3].album.artist.id == "0gJ0dOw0r6d"
        assert tracks[3].album.artist.name == "Acrania"
        assert tracks[4].id == "a90CtItbROxdl"
        assert tracks[4].name == "Depravity"
        assert tracks[4].album.id == "lv5djSYqp0X"
        assert tracks[4].album.name == "The End"
        assert tracks[4].album.artist.id == "0gJ0dOw0r6d"
        assert tracks[4].album.artist.name == "Acrania"
        assert tracks[5].id == "c20fVSluB31T0y"
        assert tracks[5].name == "Programme"
        assert tracks[5].album.id == "lv5djSYqp0X"
        assert tracks[5].album.name == "The End"
        assert tracks[5].album.artist.id == "0gJ0dOw0r6d"
        assert tracks[5].album.artist.name == "Acrania"
