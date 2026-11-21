import cv2
import mediapipe as mp
import time

# send hands mediapipe information
class HandTracker:
    def __init__(self):
        # Mediapipe tasks api
        BaseOptions=mp.tasks.BaseOptions
        HandLandMarker=mp.tasks.vision.HandLandmarker
        HandLandMarkerOptions=mp.tasks.vision.HandLandmarkerOptions
        RunningMode=mp.tasks.vision.RunningMode

        # Configure hand landmarker
        options = HandLandMarkerOptions(
            base_options=BaseOptions(
                model_asset_path="video_capture/hand_landmarker.task"
            ),
            running_mode=RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7,
        )

        self.landmarker=HandLandMarker.create_from_options(options)

        self.cap=cv2.VideoCapture(0)

        if not self.cap.isOpened(): raise RuntimeError("Could not open webcam")


    def get_hands(self):

        ret, frame=self.cap.read()

        if not ret: return None, None

        height, width, _ = frame.shape

        # convert BGR (openCV) to RGB (mediapipe)
        rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # convert mediapipe image
        mp_image=mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        # process frame with timestamp
        timestamp_ms=time.monotonic_ns() // 1_000_000

        results=self.landmarker.detect_for_video(
            mp_image,
            timestamp_ms,
        )

        # map handedness to landmarks
        hands={}

        for i, landmarks in enumerate(results.hand_landmarks):
            label=results.handedness[i][0].category_name
            hands[label]=landmarks

        return hands, frame


    def close(self):
        self.cap.release()
        self.landmarker.close()
        cv2.destroyAllWindows()