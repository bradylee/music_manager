schemas = {}

# Original schema.
schemas["1.0.0"] = {
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

# Add rating and num_times_rated columns to tracks.
schemas["1.1.0"] = {
    "tracks": {
        "id": "text NOT NULL PRIMARY KEY",
        "name": "text NOT NULL",
        "album": "text NOT NULL",
        "rating": "int NOT NULL DEFAULT 0 CHECK (rating >= -1 AND rating <= 1)",
        "num_times_rated": "int NOT NULL DEFAULT 0 CHECK (num_times_rated >= 0)",
    },
    "albums": schemas["1.0.0"]["albums"],
    "artists": schemas["1.0.0"]["artists"],
}
