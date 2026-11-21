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

        for hand_lable, landmarks in hands.items():
            fingers=recognizer.get_finger_states(landmarks)

            print(hand_lable, fingers)

        if frame is None: break

        # if "Left" in hands:
        #     print("Left Hand Detected")

        # if "Right" in hands:
        #     print("Right Hand Detected")

        cv2.imshow("Hand Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    tracker.close()