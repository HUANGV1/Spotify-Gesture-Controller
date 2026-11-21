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
            self.draw_landmarks(frame, landmarks)
            label=results.handedness[i][0].category_name
            if label=="Right":
                self.draw_pinch_line(frame, landmarks)
            hands[label]=landmarks

        return hands, frame

    def draw_landmarks(self, frame, landmarks):
        height, width, _ = frame.shape

        points = [
            (int(landmark.x * width), int(landmark.y * height))
            for landmark in landmarks
        ]

        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

        for start, end in connections:
            cv2.line(frame, points[start], points[end], (0, 255, 0), 2)

        for point in points:
            cv2.circle(frame, point, 5, (0, 0, 255), -1)

    def draw_pinch_line(self, frame, landmarks):
        height, width, _ = frame.shape

        thumb = (int(landmarks[4].x * width),
                int(landmarks[4].y * height))

        index = (int(landmarks[8].x * width),
                int(landmarks[8].y * height))

        cv2.line(frame, thumb, index, (255, 0, 0), 2)


    def close(self):
        self.cap.release()
        self.landmarker.close()
        cv2.destroyAllWindows()