#!/usr/bin/env python

# Get a Spotify access token using the use the Client Credentials Flow:
# https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow
# The client id and secret are read from environment variables.

import base64
import os

import requests

endpoint = "https://accounts.spotify.com/api/token"

client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

message = f"{client_id}:{client_secret}"
message_base64 = base64.b64encode(message.encode()).decode()

headers = {
    "Accept": "application/json",
    "Authorization": f"Basic {message_base64}",
}

data = {
    "grant_type": "client_credentials",
}

response = requests.post(endpoint, headers=headers, data=data)

# Print only the access token.
if response.status_code == 200:
    print(response.json()["access_token"])
