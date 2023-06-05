from collections import OrderedDict


class Item:
    """
    Base interface for a Spotify item.
    """

    def __init__(self, id_, name):
        self.id = id_
        self.name = name

    def __repr__(self):
        return f"Item({repr(self.id)}, {repr(self.name)})"


class Track(Item):
    """
    Interface for a single track.
    """

    def __init__(self, id_, name, album_id, rating=None):
        super().__init__(id_, name)

        self.album_id = album_id
        self.rating = rating

    def __repr__(self):
        return f"Track({repr(self.id)}, {repr(self.name)}, {repr(self.album_id)}, rating={repr(self.rating)})"


class Album(Item):
    """
    Interface for a single album.
    """

    def __init__(self, id_, name, artist_id):
        super().__init__(id_, name)

        self.artist_id = artist_id

    def __repr__(self):
        return f"Album({repr(self.id)}, {repr(self.name)}, {repr(self.artist_id)})"


class Artist(Item):
    """
    Interface for a single artist.
    """

    def __init__(self, id_, name):
        super().__init__(id_, name)

    def __repr__(self):
        return f"Artist({repr(self.id)}, {repr(self.name)})"


class Playlist:
    """
    Interface for a playlist. Playlists contain lists for tracks, albums, and artists.
    The tracks are the tracks in the playlist. The albums are the albums those tracks
    are from. The artists are the artists that created those albums.
    """

    def __init__(self):
        # Store items internally as dictionaries to ensure duplicates are ignored.
        # The keys are the item ids, while the values are the actual items.
        self._tracks = OrderedDict()
        self._albums = OrderedDict()
        self._artists = OrderedDict()

    @property
    def tracks(self):
        """
        Returns a list of unique tracks in the playlist.
        """
        values = self._tracks.values()
        return list(values)

    @property
    def albums(self):
        """
        Returns a list of unique albums in the playlist.
        """
        values = self._albums.values()
        return list(values)

    @property
    def artists(self):
        """
        Returns a list of unique artists in the playlist.
        """
        values = self._artists.values()
        return list(values)

    def add_track(self, track):
        """
        Add a single track to the playlist.
        """
        self._tracks[track.id] = track

    def add_album(self, album):
        """
        Add a single album to the playlist.
        """
        self._albums[album.id] = album

    def add_artist(self, artist):
        """
        Add a single artist to the playlist.
        """
        self._artists[artist.id] = artist
