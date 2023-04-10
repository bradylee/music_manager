import copy

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
schemas["1.1.0"] = copy.deepcopy(schemas["1.0.0"])
schemas["1.1.0"]["tracks"].update({
    # Track rating. Ratings can be negative, positive, or neutral (zero).
    "rating": "int NOT NULL DEFAULT 0 CHECK (rating >= -1 AND rating <= 1)",
    # The number of times a track has been rated.
    "num_times_rated": "int NOT NULL DEFAULT 0 CHECK (num_times_rated >= 0)",
})

# Add is_fetched column to albums.
schemas["1.2.0"] = copy.deepcopy(schemas["1.1.0"])
schemas["1.2.0"]["albums"].update({
    # Set to True when all tracks from the album have been set. This is to prevent
    # needlessly fetching an album multiple times since albums will not have tracks
    # modified after the intial release.
    "is_fetched": "boolean NOT NULL DEFAULT 0",
})
