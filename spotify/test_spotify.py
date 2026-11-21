from spotify_controller import SpotifyController

spotify = SpotifyController()

playback = spotify.get_playback()

if playback is None:
    print("No active Spotify device")

else:
    track = playback["item"]

    print("Connected to Spotify!")
    print("Track:", track["name"])
    print("Playing:", playback["is_playing"])
    print("Volume:", playback["device"]["volume_percent"])
