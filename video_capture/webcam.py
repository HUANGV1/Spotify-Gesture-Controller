import cv2
import mediapipe as mp
import time

BaseOptions=mp.tasks.BaseOptions
HandLandMarker=mp.tasks.vision.HandLandmarker
HandLandMarkerOptions=mp.tasks.vision.HandLandmarkerOptions
RunningMode=mp.tasks.vision.RunningMode

# Hand skeleton connections (21 landmarks)
CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

# Configure hand landmarker
options = HandLandMarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7,
)

# Start webcap

print("Starting webcam...", flush=True)
cap=cv2.VideoCapture(0)

if not cap.isOpened(): raise RuntimeError("Could not open webcam")

print("Camera opened:", cap.isOpened(), flush=True)

# main loop
with HandLandMarker.create_from_options(options) as landmarker:

    print("Landmarker initialized", flush=True)

    while True:
        print("Reading frame...", flush=True)
        ret, frame=cap.read()

        if not ret: break

        print("Frame received:", ret, flush=True)

        # frame=cv2.flip(frame, 1)

        height, width, _ = frame.shape

        # convert BGR (openCV) to RGB (mediapipe)
        rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # convert mediapipe image
        mp_image=mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        print("Running inference...", flush=True)

        # process frame with timestamp
        timestamp_ms=time.monotonic_ns() // 1_000_000

        results=landmarker.detect_for_video(
            mp_image,
            timestamp_ms,
        )

        # draw detected hands
        for hand_index, hand_landmarks in enumerate(results.hand_landmarks):
            # get handedness
            hand_label=results.handedness[hand_index][0].category_name

            # convert normalized coordinates to pixels
            points=[]

            for landmark in hand_landmarks:
                x=int(landmark.x*width)
                y=int(landmark.y*height)
                points.append((x,y))

            # draw connections
            for start, end in CONNECTIONS:
                cv2.line(
                    frame,
                    points[start],
                    points[end],
                    (0, 255, 0),
                    2
                )

            # draw landmarks
            for point in points:
                cv2.circle(
                    frame,
                    point,
                    5,
                    (0,0,255),
                    -1
                )

            # display hand label
            cv2.putText(
                frame,
                hand_label,
                points[0],
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,0,0),
                2
            )

        print("Inference complete", flush=True)

        cv2.imshow("Mediapipe Hand Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()