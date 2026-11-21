import spotipy
from spotipy.oauth2 import SpotifyPKCE
from dotenv import load_dotenv
import os

load_dotenv()

SCOPES=[
    "user-read-playback-state",
    "user-modify-playback-state",
]

class SpotifyController:

    def __init__(self):

        auth_manager = SpotifyPKCE(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=" ".join(SCOPES),
        )

        self.sp=spotipy.Spotify(
            auth_manager=auth_manager
        )


    def get_playback(self):
        return self.sp.current_playback()

    def play_pause(self):

        playback=self.get_playback()

        if playback is None:
            print("No active Spotify playback device")

        if playback["is_playing"]:
            self.sp.pause_playback()
            print("Paused")
        else:
            self.sp.start_playback()
            print("Playing")

    def skip_track(self):
        self.sp.next_track()
        print("Skipped")

    def previous_track(self):
        self.sp.previous_track()
        print("Previous Track")
    
    def set_volume(self, volume):
        volume=max(0, min(100, int(volume)))

        self.sp.volume(volume)
        print(f"Volume: {volume}%")
                    