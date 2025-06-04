# personDetector.py
from ultralytics import YOLO
import numpy as np

class PersonDetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)

    def detect_person_roi(self, image):
        # YOLO는 BGR을 RGB로 자동 변환하므로 그냥 넣음
        results = self.model.predict(source=image, conf=0.4, classes=[0], verbose=False)  # class 0 = person
        if not results or len(results[0].boxes) == 0:
            return None
        
        # 중심에서 가까운 사람 하나 선택
        h, w, _ = image.shape
        center_x, center_y = w // 2, h // 2

        min_dist = float('inf')
        best_box = None
        for box in results[0].boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            box_center_x = (x1 + x2) // 2
            box_center_y = (y1 + y2) // 2
            dist = (box_center_x - center_x) ** 2 + (box_center_y - center_y) ** 2
            if dist < min_dist:
                min_dist = dist
                best_box = (x1, y1, x2 - x1, y2 - y1)  # (x, y, w, h)

        return best_box  # ROI 박스 반환
