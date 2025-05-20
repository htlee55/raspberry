import cv2
import mediapipe as mp
import numpy as np

class Detection():
    def __init__(self):
        # --- MediaPipe Initialization ---
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, smooth_landmarks=True)
        self.mp_drawing = mp.solutions.drawing_utils
        self.TOGGLE_DRAWING = True  # Toggle to enable/disable drawing of landmarks
        self.pose_result = None

    # --- Angle Calculation Function ---
    def calculate_angle(self, a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
            a[1] - b[1], a[0] - b[0]
        )
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def pose_detection(self, image):
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.pose_result = self.pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if self.pose_result.pose_landmarks:
            if self.TOGGLE_DRAWING:
                self.mp_drawing.draw_landmarks(
                    image,
                    self.pose_result.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                )

            landmarks = self.pose_result.pose_landmarks.landmark
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]

            left_angle = self.calculate_angle(left_elbow, left_shoulder, left_hip)
            right_angle = self.calculate_angle(right_elbow, right_shoulder, right_hip)

            print(f"Left angle: {left_angle:.2f}, Right angle: {right_angle:.2f}")
            if left_angle > 70 or right_angle > 60:
                print("Bow pose detected!")

        return image
