import cv2
from hand_tracking import HandTracker
from gesture_recognition import GestureRecognizer

# orchestrates hand_tracking and gesture_recognition 

tracker = HandTracker()
recognizer = GestureRecognizer()

try:

    # display on screen
    while True:
        hands, frame=tracker.get_hands()

        if frame is None: break

        for hand_lable, landmarks in hands.items():
            gesture=recognizer.recognize_gesture(landmarks)
            pinch_distance=recognizer.get_normalized_pinch_distance(landmarks)

            # display recognized gesture
            text=f"{hand_lable}: {gesture}"

            cv2.putText(
                frame,
                text,
                (20, 40 if hand_lable == "Left" else 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # display pinch distance
            pinch_text = f"{hand_lable} Pinch: {pinch_distance:.2f}"

            cv2.putText(
                frame,
                pinch_text,
                (20, 120 if hand_lable == "Left" else 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )

        cv2.imshow("Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    tracker.close()