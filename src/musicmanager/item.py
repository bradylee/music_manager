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

    def __init__(self, id_, name, album=None):
        super().__init__(id_, name)
        self.album = album

    def __repr__(self):
        return f"Track({repr(self.id)}, {repr(self.name)}, album={self.album})"


class Album(Item):
    """
    Interface for a single album.
    """

    def __init__(self, id_, name, artist=None):
        super().__init__(id_, name)
        self.artist = artist

    def __repr__(self):
        return f"Album({repr(self.id)}, {repr(self.name)}, artist={self.artist})"


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
    Interface for a playlist. Playlists contain a list of tracks.
    """

    def __init__(self):
        self._tracks = []

    @property
    def tracks(self):
        return self._tracks

    @property
    def albums(self):
        return list(self.iterate_albums())

    @property
    def artists(self):
        return list(self.iterate_artists())

    def add_track(self, track):
        """
        Add a single track to the playlist.
        """
        self._tracks.append(track)

    def iterate_albums(self):
        """
        Iterate over albums referenced by the playlist tracks and yield each album on
        the first occurrence.
        """
        lookup_table = set()
        for track in self.tracks:
            album = track.album
            if album is not None and album.id not in lookup_table:
                lookup_table.add(album.id)
                yield album

    def iterate_artists(self):
        """
        Iterate over artists referenced by the playlist tracks and yield each artist on
        the first occurrence.
        """
        lookup_table = set()
        for album in self.iterate_albums():
            artist = album.artist
            if artist is not None and artist.id not in lookup_table:
                lookup_table.add(artist.id)
                yield artist
