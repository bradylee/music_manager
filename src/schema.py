schemas = {
    "1.0.0": {
        "tracks": {
            "id": "text NOT NULL PRIMARY KEY",
            "name": "text NOT NULL",
            "album": "text NOT NULL",
        },
        "albums": {
            "id": "text NOT NULL PRIMARY KEY",
            "name": "text NOT NULL",
            "artist": "text NOT NULL",
        },
        "artists": {
            "id": "text NOT NULL PRIMARY KEY",
            "name": "text NOT NULL",
        },
    }
}
