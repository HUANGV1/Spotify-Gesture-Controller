import math

class GestureRecognizer:

    def calculate_angle(self, a, b, c):
        """
        Calculate angle ABC using three landmarks.
        """
        ba=(a.x-b.x, a.y-b.y, a.z-b.z)
        bc=(c.x-b.x, c.y-b.y, c.z-b.z)

        dot_product=sum(x*y for x,y in zip(ba,bc))

        magnitude_ba=math.sqrt(sum(x**2 for x in ba))
        magnitude_bc=math.sqrt(sum(x**2 for x in bc))

        if magnitude_ba==0 or magnitude_bc==0: return 0

        cosine = dot_product / (magnitude_ba * magnitude_bc)

        # avoid floating-point errors
        cosine = max(-1, min(1, cosine))

        return math.degrees(math.acos(cosine))

    # determine if finger is extended
    def is_finger_extended(self, landmarks, mcp, pip, tip):
        
        angle=self.calculate_angle(
            landmarks[mcp],
            landmarks[pip],
            landmarks[tip],
        )

        return angle>150

    def is_thumb_extended(self, landmarks):
        angle=self.calculate_angle(
            landmarks[1],
            landmarks[2],
            landmarks[4],
        )

        return angle>145

    # determines which fingers are extended
    def get_finger_states(self, landmarks):
        fingers={
            "thumb": self.is_thumb_extended(landmarks),
            "index": self.is_finger_extended(landmarks, 5, 6, 8),
            "middle": self.is_finger_extended(landmarks, 9, 10, 12),
            "ring": self.is_finger_extended(landmarks, 13, 14, 16),
            "pinky": self.is_finger_extended(landmarks, 17, 18, 20),
        }

        return fingers

    # calc distance between thumb and index
    def get_pinch_distance(self, landmarks):
        pass

    def recognize_gesture(self, landmarks):
        pass