import cv2
import mediapipe as mp
import numpy as np
import time
import os
import datetime
import logging
import threading
import numpy as np

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)  # Only log errors and above

#
FPS = 30

#rpicamera2 Variables

# --- Webcam Variables ---
webcam_frame = None
camera_lock = threading.Lock()

# --- Video Writer Variables ---
video_writer = None
is_recording = False
is_replaying = False
is_triggered = False
is_stopped = False
is_extended = False
RECORDING_DURATION = 20  # 10 seconds recording duration
HOLD_DURATION = 9
EXT_DURATION = 2
REPLAY_FOLDER = "/home/user/Bullseye/replay"
start_time = None
extended_time = None

class Detection():
    def __init__(self):
        # --- MediaPipe Initialization ---
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, smooth_landmarks=True)
        self.mp_drawing = mp.solutions.drawing_utils
        self.TOGGLE_DRAWING = False  # Toggle to enable/disable drawing of landmarks
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

    def pose_detection(self,image):
        global is_recording, is_triggered, is_stopped, is_extended
        global start_time, extended_time
        global video_writer
        height,width,channel = image.shape
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.pose_result = self.pose.process(image)
        if image is not None and self.pose_result.pose_landmarks:
            if self.TOGGLE_DRAWING:
                self.mp_drawing.draw_landmarks(
                    image,
                    self.pose_result.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                )   #랜드마크가 있는 프렝임을 보여준다.pygame 윈도우에 표시
            left_shoulder = self.pose_result.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.LEFT_SHOULDER
            ]
            left_elbow = self.pose_result.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.LEFT_ELBOW
            ]
            left_hip = self.pose_result.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.LEFT_HIP
            ]
            right_shoulder = self.pose_result.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.RIGHT_SHOULDER
            ]
            right_elbow = self.pose_result.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.RIGHT_ELBOW
            ]
            right_hip = self.pose_result.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.RIGHT_HIP
            ]

            left_angle = self.calculate_angle(left_elbow, left_shoulder, left_hip)
            right_angle = self.calculate_angle(right_elbow, right_shoulder, right_hip)

            if (left_angle > 70 or right_angle > 60):
                print("Bow pose detected!, start recording for", RECORDING_DURATION, "s")
                if not is_recording:
                    is_recording = True
                    start_time = datetime.datetime.now()
                    with camera_lock:
                        #self.initialize_video_writer(1920,1080)
                        self.initialize_video_writer(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
            elif is_recording and ((datetime.datetime.now() - start_time).total_seconds() > HOLD_DURATION):
                if not is_extended:
                    is_extended = True
                    extended_time = datetime.datetime.now()
                elif is_extended and ((datetime.datetime.now() - extended_time).total_seconds() > EXT_DURATION): 
                    if is_recording:
                        is_stopped = True
        if is_recording:
            if (datetime.datetime.now() - start_time).total_seconds() > RECORDING_DURATION:
                is_recording = False
                print("Recording stopped!")
                video_writer.release()
                video_writer = None
                is_triggered = True     #for starting replay
            elif is_stopped:
                is_recording = False
                print("Recording stopped!")
                video_writer.release()
                video_writer = None
                is_triggered = True     #for starting replay 
                is_stopped = False
                is_extended = False              
            else:
                with camera_lock:
                    try:
                        video_writer.write(image)
                        print("Frame written")
                    except Exception as e:
                        print(f"Error writing frame: {e}")
       # return image 
                        
    def initialize_video_writer(self,frame_width, frame_height):
        global video_writer
        filename = os.path.join(
        #    REPLAY_FOLDER, f"replay_{time.strftime('%Y%m%d_%H%M%S')}.avi"
            REPLAY_FOLDER, f"replay_video.avi"
        )  # .avi 확장자 사용
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # XVID 코덱 사용 (더 안정적)
        video_writer = cv2.VideoWriter(filename, fourcc, FPS, (frame_width, frame_height))


