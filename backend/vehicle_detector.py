import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict, deque
import math
import torch

class VehicleDetector:
    def __init__(self, model_path='yolov8n.pt'):
        # Fix PyTorch weights_only loading issue
        torch.serialization.add_safe_globals([])
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            # Try with older torch loading method
            import os
            os.environ['TORCH_SERIALIZATION_WEIGHTS_ONLY'] = 'False'
            self.model = YOLO(model_path)
        
        self.track_history = defaultdict(lambda: deque(maxlen=30))
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
    def detect_vehicles(self, frame):
        results = self.model.track(frame, persist=True, classes=self.vehicle_classes)
        detections = []
        
        if results[0].boxes is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confidences = results[0].boxes.conf.float().cpu().tolist()
            classes = results[0].boxes.cls.int().cpu().tolist()
            
            for box, track_id, conf, cls in zip(boxes, track_ids, confidences, classes):
                x, y, w, h = box
                detection = {
                    'id': track_id,
                    'bbox': (int(x-w/2), int(y-h/2), int(w), int(h)),
                    'center': (int(x), int(y)),
                    'confidence': conf,
                    'class': cls
                }
                detections.append(detection)
                
                # Store tracking history
                self.track_history[track_id].append((int(x), int(y)))
        
        return detections
    
    def get_track_history(self, track_id):
        return list(self.track_history[track_id])
    
    def draw_detections(self, frame, detections):
        annotated_frame = frame.copy()
        
        for detection in detections:
            x, y, w, h = detection['bbox']
            track_id = detection['id']
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw track ID
            cv2.putText(annotated_frame, f'ID: {track_id}', 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Draw tracking trail
            track = self.track_history[track_id]
            if len(track) > 1:
                points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], False, (255, 0, 0), 2)
        
        return annotated_frame