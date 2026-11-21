import cv2
import time
from video_capture.hand_tracking import HandTracker
from video_capture.gesture_recognition import GestureRecognizer
from spotify.spotify_controller import SpotifyController
from spotify.spotify_display import SpotifyDisplay

# for cooldown
COOLDOWN=1.0 # sec
last_command_time=0
previous_gesture=None

MIN_VOL=0
MAX_VOL=100
MIN_PINCH_DIST=0.25
MAX_PINCH_DIST=1.2
VOLUME_UPDATE_INTERVAL=0.15
last_volume_update_time=0

# orchestrates hand_tracking and gesture_recognition 

tracker = HandTracker()
recognizer = GestureRecognizer()
spotify = SpotifyController()
display = SpotifyDisplay(spotify)
display.start()

try:

    # display on screen
    while True:
        hands, frame=tracker.get_hands()

        if frame is None: break

        current_time=time.monotonic()

        left_gesture=None
        right_gesture=None

        if "Left" in hands:
            left_gesture=recognizer.recognize_gesture(hands["Left"])

        if "Right" in hands:
            right_gesture=recognizer.recognize_gesture(hands["Right"])

        # mode1: spotify playback (left open palm)
        if left_gesture=="OPEN_PALM" and "Right" in hands:
            gesture = recognizer.recognize_gesture(hands["Right"])

            if gesture=="UNKNOWN": previous_gesture=None

            elif (gesture!=previous_gesture and current_time-last_command_time>=COOLDOWN):

                if gesture == "OPEN_PALM":
                    spotify.play_pause()
                elif gesture == "ONE":
                    spotify.skip_track()
                elif gesture == "TWO":
                    spotify.previous_track()

                previous_gesture=gesture
                last_command_time=current_time
    

        # mode2: volume control (Left fist)
        elif left_gesture=="FIST" and "Right" in hands:
            previous_gesture=None

            # Continuous volume control
            pinch_distance = recognizer.get_normalized_pinch_distance(hands["Right"])

            if current_time - last_volume_update_time >= VOLUME_UPDATE_INTERVAL:
                volume_ratio = (
                    (pinch_distance - MIN_PINCH_DIST) / (MAX_PINCH_DIST - MIN_PINCH_DIST)
                )

                volume_ratio = max(0, min(1, volume_ratio))
                volume = int(volume_ratio * 100)

                spotify.set_volume(volume)
                last_volume_update = current_time
        else:
            previous_gesture=None

        cv2.putText(
            frame,
            f"Left hand mode: {left_gesture}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        cv2.putText(
                frame,
                f"Right hand gesture: {right_gesture}",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        if "Right" in hands:
            pinch_distance = recognizer.get_normalized_pinch_distance(
                hands["Right"]
            )
            cv2.putText(
                frame,
                f"Pinch distance: {pinch_distance:.3f}",
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        display.draw(frame)
        cv2.imshow("Spotify Gesture Controller", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    display.stop()
    tracker.close()