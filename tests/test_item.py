from musicmanager.item import Album, Artist, Playlist, Track


def test_playlist_album_iterator():
    """
    Test that the album iterator in the Playlist object returns unique albums.
    """
    # Create two unique albums for tracks in the playlist to belong to.
    albums = [
        Album("album_id_0", "album_name_0"),
        Album("album_id_1", "album_name_1"),
    ]

    # Create a playlist with a couple tracks from each album to test that the iterator
    # ignores repeated albums.
    playlist = Playlist()
    playlist.add_track(Track("track_id_0", "track_name_0", albums[0]))
    playlist.add_track(Track("track_id_1", "track_name_1", albums[0]))
    playlist.add_track(Track("track_id_2", "track_name_2", albums[1]))
    playlist.add_track(Track("track_id_3", "track_name_3", albums[1]))

    # Iterate the albums and check only unique values are returned.
    i = 0
    for album in albums:
        assert album == albums[i]
        i += 1


def test_playlist_artist_iterator():
    """
    Test that the artist iterator in the Playlist object returns unique artists.
    """
    # Create two unique artists for tracks in the playlist to be created by.
    artists = [
        Artist("artist_id_0", "artist_name_0"),
        Artist("artist_id_1", "artist_name_1"),
    ]

    # Create a playlist with a couple tracks from each arist to test that the iterator
    # ignores repeated artists.
    playlist = Playlist()
    playlist.add_track(
        Track(
            "track_id_0",
            "track_name_0",
            Album("album_id_0", "album_name_0", artists[0]),
        )
    )
    playlist.add_track(
        Track(
            "track_id_1",
            "track_name_1",
            Album("album_id_1", "album_name_1", artists[0]),
        )
    )
    playlist.add_track(
        Track(
            "track_id_2",
            "track_name_2",
            Album("album_id_2", "album_name_2", artists[1]),
        )
    )
    playlist.add_track(
        Track(
            "track_id_3",
            "track_name_3",
            Album("album_id_3", "album_name_3", artists[1]),
        )
    )

    # Iterate the artists and check only unique values are returned.
    i = 0
    for artist in artists:
        assert artist == artists[i]
        i += 1
