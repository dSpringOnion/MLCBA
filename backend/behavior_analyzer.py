import numpy as np
import math
from collections import deque, defaultdict

class BehaviorAnalyzer:
    def __init__(self, frame_rate=30):
        self.frame_rate = frame_rate
        self.vehicle_data = defaultdict(lambda: {
            'positions': deque(maxlen=30),
            'speeds': deque(maxlen=10),
            'accelerations': deque(maxlen=5),
            'lane_changes': 0,
            'erratic_movements': 0,
            'last_lane': None
        })
        
    def analyze_behavior(self, detections, frame_shape):
        behaviors = {}
        
        for detection in detections:
            vehicle_id = detection['id']
            center = detection['center']
            
            # Update position history
            self.vehicle_data[vehicle_id]['positions'].append(center)
            
            # Calculate metrics
            speed = self._calculate_speed(vehicle_id)
            acceleration = self._calculate_acceleration(vehicle_id)
            lane_change = self._detect_lane_change(vehicle_id, frame_shape)
            erratic = self._detect_erratic_movement(vehicle_id)
            
            # Update vehicle data
            if speed > 0:
                self.vehicle_data[vehicle_id]['speeds'].append(speed)
            if acceleration is not None:
                self.vehicle_data[vehicle_id]['accelerations'].append(acceleration)
            if lane_change:
                self.vehicle_data[vehicle_id]['lane_changes'] += 1
            if erratic:
                self.vehicle_data[vehicle_id]['erratic_movements'] += 1
            
            # Analyze behavior
            behavior_score = self._calculate_behavior_score(vehicle_id)
            risk_level = self._classify_risk(behavior_score)
            
            behaviors[vehicle_id] = {
                'speed': speed,
                'acceleration': acceleration,
                'lane_changes': self.vehicle_data[vehicle_id]['lane_changes'],
                'erratic_movements': self.vehicle_data[vehicle_id]['erratic_movements'],
                'behavior_score': behavior_score,
                'risk_level': risk_level,
                'center': center
            }
        
        return behaviors
    
    def _calculate_speed(self, vehicle_id):
        positions = self.vehicle_data[vehicle_id]['positions']
        if len(positions) < 2:
            return 0
        
        # Calculate distance between last two positions
        p1, p2 = positions[-2], positions[-1]
        distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        # Convert to speed (pixels per second)
        speed = distance * self.frame_rate
        return speed
    
    def _calculate_acceleration(self, vehicle_id):
        speeds = self.vehicle_data[vehicle_id]['speeds']
        if len(speeds) < 2:
            return None
        
        # Calculate acceleration from speed difference
        acceleration = (speeds[-1] - speeds[-2]) * self.frame_rate
        return acceleration
    
    def _detect_lane_change(self, vehicle_id, frame_shape):
        positions = self.vehicle_data[vehicle_id]['positions']
        if len(positions) < 10:
            return False
        
        # Simple lane change detection based on lateral movement
        recent_positions = list(positions)[-10:]
        y_positions = [pos[1] for pos in recent_positions]
        
        # Check for significant vertical movement (lane change)
        y_variance = np.var(y_positions)
        threshold = (frame_shape[0] / 10) ** 2  # Threshold based on frame height
        
        return y_variance > threshold
    
    def _detect_erratic_movement(self, vehicle_id):
        positions = self.vehicle_data[vehicle_id]['positions']
        if len(positions) < 5:
            return False
        
        # Calculate direction changes
        recent_positions = list(positions)[-5:]
        direction_changes = 0
        
        for i in range(len(recent_positions) - 2):
            p1, p2, p3 = recent_positions[i:i+3]
            
            # Calculate vectors
            v1 = (p2[0] - p1[0], p2[1] - p1[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            
            # Calculate angle between vectors
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                angle = math.acos(np.clip(cos_angle, -1, 1))
                
                if angle > math.pi / 4:  # 45-degree threshold
                    direction_changes += 1
        
        return direction_changes >= 2
    
    def _calculate_behavior_score(self, vehicle_id):
        data = self.vehicle_data[vehicle_id]
        score = 0
        
        # Speed factor
        if data['speeds']:
            avg_speed = np.mean(data['speeds'])
            if avg_speed > 100:  # High speed threshold
                score += 30
            elif avg_speed > 50:
                score += 15
        
        # Acceleration factor
        if data['accelerations']:
            max_accel = max(abs(a) for a in data['accelerations'])
            if max_accel > 50:  # High acceleration threshold
                score += 25
        
        # Lane changes
        score += data['lane_changes'] * 20
        
        # Erratic movements
        score += data['erratic_movements'] * 15
        
        return min(score, 100)  # Cap at 100
    
    def _classify_risk(self, behavior_score):
        if behavior_score >= 70:
            return 'DANGEROUS'
        elif behavior_score >= 40:
            return 'RISKY'
        else:
            return 'SAFE'