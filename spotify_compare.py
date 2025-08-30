"""
Spotify vs Local Music Library Comparator

This script compares a Spotify playlist with your local music library.
It identifies tracks that are in your Spotify playlist but missing in your local files,
then creates a new Spotify playlist containing those missing tracks.

Author: Suyash Sapre
License: MIT
"""

import os
import sys
import logging
from typing import List, Optional

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from mutagen.easyid3 import EasyID3
from rapidfuzz import fuzz, process

# ==============================
# CONFIGURATION
# ==============================
load_dotenv()  # Load .env file if present

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/")
SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"

LOCAL_MUSIC_DIR = os.getenv("LOCAL_MUSIC_DIR", "")
SPOTIFY_PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID", "")

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def ensure_config() -> None:
    """Validate required environment variables and local paths."""
    missing = []
    for key, value in {
        "SPOTIPY_CLIENT_ID": SPOTIPY_CLIENT_ID,
        "SPOTIPY_CLIENT_SECRET": SPOTIPY_CLIENT_SECRET,
        "SPOTIPY_REDIRECT_URI": SPOTIPY_REDIRECT_URI,
        "LOCAL_MUSIC_DIR": LOCAL_MUSIC_DIR,
        "SPOTIFY_PLAYLIST_ID": SPOTIFY_PLAYLIST_ID,
    }.items():
        if not value:
            missing.append(key)

    if missing:
        logging.error("Missing required configuration: %s", ", ".join(missing))
        logging.info("Create a .env file (you can copy from .env.example) and set the values.")
        sys.exit(1)

    if not os.path.isdir(LOCAL_MUSIC_DIR):
        logging.error("LOCAL_MUSIC_DIR does not exist or is not a directory: %s", LOCAL_MUSIC_DIR)
        sys.exit(1)


def spotify_client() -> spotipy.Spotify:
    """Authenticate and return a Spotipy client."""
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as exc:
        logging.exception("Failed to authenticate with Spotify: %s", exc)
        sys.exit(1)


# ==============================
# STEP 1: GET SONGS FROM SPOTIFY PLAYLIST
# ==============================
def get_spotify_tracks(sp: spotipy.Spotify, playlist_id: str) -> List[str]:
    """Retrieve all track names from a Spotify playlist as 'Artist - Title'."""
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks: List[str] = []

    while results:
        for item in results.get('items', []):
            track = item.get('track')
            if track:
                name = track.get('name') or ""
                artists = track.get('artists') or []
                artist = artists[0]['name'] if artists else "Unknown"
                if name:
                    tracks.append(f"{artist} - {name}")
        results = sp.next(results) if results.get('next') else None

    logging.info("Fetched %d tracks from Spotify playlist.", len(tracks))
    return tracks


# ==============================
# STEP 2: GET SONGS FROM LOCAL FILES
# ==============================
def get_local_tracks(music_dir: str) -> List[str]:
    """Retrieve track metadata from local music files as 'Artist - Title'."""
    local_tracks: List[str] = []
    exts = ('.mp3', '.flac', '.wav')
    for root, _, files in os.walk(music_dir):
        for file in files:
            if file.lower().endswith(exts):
                filepath = os.path.join(root, file)
                try:
                    meta = EasyID3(filepath)
                    artist = meta.get("artist", ["Unknown"])[0]
                    title = meta.get("title", [os.path.splitext(file)[0]])[0]
                    local_tracks.append(f"{artist} - {title}")
                except Exception:
                    # Fallback to filename (without extension) if ID3 not available
                    local_tracks.append(os.path.splitext(file)[0])
    logging.info("Found %d local tracks.", len(local_tracks))
    return local_tracks


# ==============================
# STEP 3: COMPARE TRACK LISTS
# ==============================
def find_missing_tracks(spotify_tracks: List[str], local_tracks: List[str], threshold: int = 80) -> List[str]:
    """Find tracks from Spotify playlist that are missing in local library."""
    missing: List[str] = []
    for sp_song in spotify_tracks:
        match = process.extractOne(sp_song, local_tracks, scorer=fuzz.token_sort_ratio)
        if not match or (match[1] or 0) < threshold:
            missing.append(sp_song)

    logging.info("Identified %d missing tracks.", len(missing))
    return missing


# ==============================
# STEP 4: CREATE NEW SPOTIFY PLAYLIST
# ==============================
def create_missing_playlist(sp: spotipy.Spotify, missing_tracks: List[str], name: str = "Missing Songs") -> Optional[dict]:
    """Create a new Spotify playlist with missing songs and add found URIs."""
    if not missing_tracks:
        logging.info("No missing tracks to add.")
        return None

    user_id = sp.me()['id']
    new_playlist = sp.user_playlist_create(user_id, name, public=False)
    uris: List[str] = []

    for item in missing_tracks:
        results = sp.search(q=item, type="track", limit=1)
        tracks = results.get('tracks', {}).get('items', [])
        if tracks:
            uris.append(tracks[0]['uri'])

    if uris:
        sp.playlist_add_items(new_playlist['id'], uris)
        logging.info("Created new playlist '%s' with %d missing tracks!", name, len(uris))
    else:
        logging.warning("No track URIs found for missing items; playlist created empty.")

    return new_playlist


def main() -> None:
    ensure_config()
    sp = spotify_client()
    spotify_tracks = get_spotify_tracks(sp, SPOTIFY_PLAYLIST_ID)
    local_tracks = get_local_tracks(LOCAL_MUSIC_DIR)
    missing_tracks = find_missing_tracks(spotify_tracks, local_tracks, threshold=80)
    create_missing_playlist(sp, missing_tracks)


if __name__ == "__main__":
    main()
