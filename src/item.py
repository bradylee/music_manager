class Item:
    """
    Generic class to represent a Spotify item.
    """
    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def __repr__(self):
        return f"Item({repr(self.id)}, {repr(self.name)})"


class Track(Item):
    """
    Represents a track.
    """
    def __init__(self, _id, name, album=None):
        super().__init__(_id, name)
        self.album = album

    def __repr__(self):
        return f"Track({repr(self.id)}, {repr(self.name)}, album={self.album})"


class Album(Item):
    """
    Represents an album.
    """
    def __init__(self, _id, name, artist=None):
        super().__init__(_id, name)
        self.artist = artist

    def __repr__(self):
        return f"Album({repr(self.id)}, {repr(self.name)}, artist={self.artist})"


class Artist(Item):
    """
    Represents an artist.
    """
    def __init__(self, _id, name):
        super().__init__(_id, name)

    def __repr__(self):
        return f"Artist({repr(self.id)}, {repr(self.name)})"


def get_album_list(tracks):
    """
    Get a list of unique albums from a list of tracks.
    """
    albums = []
    lookup_table = set()
    for track in tracks:
        if track.album.id not in lookup_table:
            lookup_table.add(track.album.id)
            albums.append(track.album)
    return albums


def get_artist_list(albums):
    """
    Get a list of unique artists from a list of albums.
    """
    artists = []
    lookup_table = set()
    for album in albums:
        if album.artist.id not in lookup_table:
            lookup_table.add(album.artist.id)
            artists.append(album.artist)
    return artists
