from src import item as dut
from src.item import Album, Artist, Track


def test_getAlbumList():
    """
    Test `get_album_list` with sample data including duplicates.
    """
    # Input data that includes duplicate albums.
    tracks = [
        Track(
            "6bsxDgpU5nlcHNZYtsfZG8",
            "Bleeding Sun",
            album=Album("7hkhFnClNPmRXL20KqdzSO", "Bleeding Sun"),
        ),
        Track(
            "6bsxDgpU5nlcHNZYtsfZG82",
            "Bleeding Sun 2",
            album=Album("7hkhFnClNPmRXL20KqdzSO", "Bleeding Sun"),
        ),
        Track(
            "15eQh5ZLBoMReY20MDG37T",
            "Breathless",
            album=Album("1GLmxzF8g5p0fcdAatGq5Y", "Fractured"),
        ),
        Track(
            "2GDX9DpZgXsLAkXhHBQU1Q",
            "Choke",
            album=Album("0a40snAsSiU0fSBrba93YB", "World Demise"),
        ),
    ]

    # Function under test.
    albums = dut.get_album_list(tracks)

    # Verify the duplicate album was removed.
    assert len(albums) == 3

    # Verify the object member values.
    assert albums[0].id == "7hkhFnClNPmRXL20KqdzSO"
    assert albums[0].name == "Bleeding Sun"
    assert albums[1].id == "1GLmxzF8g5p0fcdAatGq5Y"
    assert albums[1].name == "Fractured"
    assert albums[2].id == "0a40snAsSiU0fSBrba93YB"
    assert albums[2].name == "World Demise"


def test_getArtistList():
    """
    Test `get_artist_list` with sample data including duplicates.
    """
    # Input data.
    albums = [
        Album(
            "7hkhFnClNPmRXL20KqdzSO",
            "Bleeding Sun",
            artist=Artist("4UgQ3EFa8fEeaIEg54uV5b", "Chelsea Grin"),
        ),
        Album(
            "1GLmxzF8g5p0fcdAatGq5Y",
            "Fractured",
            artist=Artist("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD"),
        ),
        Album(
            "1GLmxzF8g5p0fcdAatGq5Y2",
            "Fractured 2",
            artist=Artist("7z9n8Q0icbgvXqx1RWoGrd", "FRCTRD"),
        ),
        Album(
            "0a40snAsSiU0fSBrba93YB",
            "World Demise",
            artist=Artist("7bDLHytU8vohbiWbePGrRU", "Falsifier"),
        ),
    ]

    # Function under test.
    artists = dut.get_artist_list(albums)

    # Verify the duplicate artist was removed.
    assert len(artists) == 3

    # Verify the object member values.
    assert artists[0].id == "4UgQ3EFa8fEeaIEg54uV5b"
    assert artists[0].name == "Chelsea Grin"
    assert artists[1].id == "7z9n8Q0icbgvXqx1RWoGrd"
    assert artists[1].name == "FRCTRD"
    assert artists[2].id == "7bDLHytU8vohbiWbePGrRU"
    assert artists[2].name == "Falsifier"
