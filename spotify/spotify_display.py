import cv2
import numpy as np
import requests
import threading
import time

'''
This was AI because less important. Except the thread locks
'''


class SpotifyDisplay:
    def __init__(self, spotify_controller):
        self.spotify = spotify_controller

        self.playback = None
        self.album_art = None
        self.volume = None

        self.lock = threading.Lock()
        self.running = False
        self.thread = None

        self.last_track_id = None
        self.last_progress_update = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(
            target=self._update_loop,
            daemon=True
        )
        self.thread.start()

    def stop(self):
        self.running = False

        if self.thread is not None:
            self.thread.join(timeout=2)

    def _update_loop(self):
        while self.running:
            try:
                playback = self.spotify.get_playback()

                if playback and playback.get("item"):
                    track = playback["item"]
                    track_id = track["id"]

                    # Only download artwork when the track changes
                    if track_id != self.last_track_id:
                        images = track["album"]["images"]
                        artwork = None

                        if images:
                            artwork = self._download_artwork(
                                images[0]["url"]
                            )

                        with self.lock:
                            self.album_art = artwork

                        self.last_track_id = track_id

                    with self.lock:
                        self.playback = playback
                        self.last_progress_update = time.monotonic()

                else:
                    with self.lock:
                        self.playback = None
                        self.album_art = None

                    self.last_track_id = None

            except Exception as e:
                print(f"Spotify display update error: {e}")

            time.sleep(1)

    def _download_artwork(self, url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            image_array = np.frombuffer(
                response.content,
                dtype=np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            return image

        except Exception as e:
            print(f"Artwork download error: {e}")
            return None

        
    def draw(self, frame):
        with self.lock:
            playback = self.playback
            artwork = (
                self.album_art.copy()
                if self.album_art is not None
                else None
            )
            progress_update = self.last_progress_update

        frame_height, frame_width = frame.shape[:2]

        if playback is None:
            cv2.putText(
                frame,
                "Spotify: No active playback",
                (20, frame_height - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            return frame

        track = playback["item"]

        title = track["name"]
        artists = ", ".join(
            artist["name"] for artist in track["artists"]
        )
        album = track["album"]["name"]
        is_playing = playback["is_playing"]

        progress = playback["progress_ms"] or 0
        duration = track["duration_ms"]

        if is_playing:
            elapsed = time.monotonic() - progress_update
            progress += int(elapsed * 1000)

        progress = min(progress, duration)

        # Calculate panel dimensions relative to frame
        margin = int(frame_width * 0.02)
        panel_width = int(frame_width * 0.38)
        panel_height = int(frame_height * 0.24)

        panel_x = frame_width - panel_width - margin
        panel_y = margin

        # Calculate internal spacing
        padding = int(panel_width * 0.05)
        art_size = panel_height - 2 * padding

        text_x = panel_x + padding + art_size + padding
        text_width = panel_x + panel_width - padding - text_x

        # Draw translucent background
        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (panel_x, panel_y),
            (panel_x + panel_width, panel_y + panel_height),
            (20, 20, 20),
            -1
        )

        cv2.addWeighted(
            overlay, 0.85,
            frame, 0.15,
            0, frame
        )

        # Draw album artwork
        if artwork is not None:
            artwork_resized = cv2.resize(
                artwork,
                (art_size, art_size)
            )

            art_x = panel_x + padding
            art_y = panel_y + padding

            frame[
                art_y:art_y + art_size,
                art_x:art_x + art_size
            ] = artwork_resized

        # Helper: fit text inside available width
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = panel_height / 230
        font_scale = max(0.35, min(font_scale, 0.75))

        def fit_text(text, scale):
            while text:
                width = cv2.getTextSize(
                    text, font, scale, 1
                )[0][0]

                if width <= text_width:
                    return text

                text = text[:-1]

            return ""

        def draw_text(text, y, scale, color=(255, 255, 255)):
            text = fit_text(text, scale)

            cv2.putText(
                frame,
                text,
                (text_x, y),
                font,
                scale,
                color,
                1,
                cv2.LINE_AA
            )

        # Calculate text positions relative to panel
        text_top = panel_y + int(panel_height * 0.25)

        draw_text(
            title,
            text_top,
            font_scale,
        )

        draw_text(
            artists,
            text_top + int(panel_height * 0.19),
            font_scale * 0.75,
            (210, 210, 210)
        )

        draw_text(
            album,
            text_top + int(panel_height * 0.36),
            font_scale * 0.65,
            (160, 160, 160)
        )

        status = "PLAYING" if is_playing else "PAUSED"

        draw_text(
            status,
            text_top + int(panel_height * 0.55),
            font_scale * 0.7,
            (30, 220, 30)
        )

        # Progress bar
        bar_x = text_x
        bar_y = panel_y + panel_height - padding
        bar_width = text_width
        bar_height = max(3, int(panel_height * 0.035))

        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (100, 100, 100),
            -1
        )

        if duration > 0:
            progress_width = int(
                bar_width * progress / duration
            )

            cv2.rectangle(
                frame,
                (bar_x, bar_y),
                (bar_x + progress_width, bar_y + bar_height),
                (30, 220, 30),
                -1
            )

        return frame

