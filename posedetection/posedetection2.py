import cv2
import mediapipe as mp
import numpy as np
import requests

class PoseDetection:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.server_url = "http://127.0.0.1:5000/upload" #자신의 환경으로 수정
    
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
    
    def is_special_pose(self, landmarks):
        #예: 양손이 머리 위로 올라간 포즈 (keypoint index는 Mediapipe 기준)
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]

        # 손목 y 좌표가 코보다 위에 있으면, 영상에서 y 좌표 값은 아래로 갈수록 커짐
        if left_wrist.y < nose.y and right_wrist.y < nose.y:
            return True
        return False

    def send_image_to_server(self, image):
        _, img_encoded = cv2.imencode('.jpg', image)
        files = {'image': ('capture.jpg', img_encoded.tobytes(), 'image/jpeg')}
        try:
            response = requests.post(self.server_url, files=files)
            print("서버 응답:", response.status_code, response.text)
        except Exception as e:
            print("이미지 전송 실패:", e)

    def process_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            # 이미지에 랜드마크를 그림
            if self.is_special_pose(results.pose_landmarks.landmark):
                print("특정 포즈가 감지되어 이미지 전송!")
                self.send_image_to_server(frame)

        return frame
