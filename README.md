# 🎵 Spotify vs Local Music Library Comparator

Compare your **Spotify playlists** against your **local music files** and automatically create a new playlist with the songs you’re missing.

Built with [Spotipy](https://spotipy.readthedocs.io/), [Mutagen](https://mutagen.readthedocs.io/), and [RapidFuzz](https://maxbachmann.github.io/RapidFuzz/).

## 🚀 Features
- Fetch all tracks from a Spotify playlist  
- Scan your local music folder (`.mp3`, `.flac`, `.wav`)  
- Compare songs using fuzzy matching (handles small naming differences)  
- Create a new Spotify playlist with the **missing tracks**  

## ⚙️ Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/spotify-local-compare.git
   cd spotify-local-compare
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   # macOS/Linux
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (you can copy from `.env.example`) and fill in your values:
   ```ini
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/
   LOCAL_MUSIC_DIR=C:\Users\YourName\Music
   SPOTIFY_PLAYLIST_ID=your_playlist_id
   ```

5. Run the script:
   ```bash
   python spotify_compare.py
   ```

## 📸 Example Output
```
INFO - Fetched 124 tracks from Spotify playlist.
INFO - Found 98 local tracks.
INFO - Identified 26 missing tracks.
INFO - Created new playlist with 24 missing tracks!
```

## 📂 Project Structure
```
├── spotify_compare.py   # main script
├── requirements.txt     # dependencies
├── .env.example         # sample environment variables
├── .gitignore           # ignore venv & secrets
├── LICENSE              # MIT license
└── README.md            # this file
```

## 🛠️ Tech Stack
- Python  
- Spotipy – Spotify Web API wrapper  
- Mutagen – MP3/FLAC/WAV metadata parser  
- RapidFuzz – fast fuzzy string matching  

## 📌 Future Improvements
- GUI interface for easier use  
- Docker image for one-command setup  
- Support for Apple Music or YouTube Music  

## 📄 License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
