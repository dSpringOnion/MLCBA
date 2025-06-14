from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import os

from vehicle_detector import VehicleDetector
from behavior_analyzer import BehaviorAnalyzer
from ml_classifier import MLBehaviorClassifier

app = Flask(__name__)
CORS(app)

# Initialize components
detector = VehicleDetector()
analyzer = BehaviorAnalyzer()
classifier = MLBehaviorClassifier()

# Train or load the model
if os.path.exists('behavior_model.pkl'):
    classifier.load_model()
else:
    classifier.train_model()
    classifier.save_model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    """Process uploaded video file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_path = 'temp_video.mp4'
        file.save(temp_path)
        
        # Process video
        results = process_video(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process a single frame from webcam or video"""
    try:
        data = request.json
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Detect vehicles
        detections = detector.detect_vehicles(frame)
        
        # Analyze behavior
        behaviors = analyzer.analyze_behavior(detections, frame.shape)
        
        # ML classification
        ml_results = classifier.predict(behaviors)
        
        # Combine results
        results = []
        for vehicle_id in behaviors.keys():
            vehicle_data = behaviors[vehicle_id]
            ml_data = ml_results.get(vehicle_id, {})
            
            results.append({
                'id': vehicle_id,
                'center': vehicle_data['center'],
                'speed': round(vehicle_data['speed'], 2),
                'acceleration': round(vehicle_data['acceleration'], 2) if vehicle_data['acceleration'] else 0,
                'lane_changes': vehicle_data['lane_changes'],
                'erratic_movements': vehicle_data['erratic_movements'],
                'behavior_score': round(vehicle_data['behavior_score'], 2),
                'risk_level': vehicle_data['risk_level'],
                'ml_prediction': ml_data.get('prediction', 'UNKNOWN'),
                'confidence': round(ml_data.get('confidence', 0) * 100, 1)
            })
        
        # Draw annotations on frame
        annotated_frame = detector.draw_detections(frame, detections)
        annotated_frame = draw_behavior_info(annotated_frame, results)
        
        # Convert back to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        annotated_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'annotated_image': f'data:image/jpeg;base64,{annotated_b64}',
            'detections': results,
            'summary': generate_summary(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_video(video_path):
    """Process entire video file"""
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    all_results = []
    
    while cap.read()[0]:
        frame_count += 1
    
    cap.release()
    cap = cv2.VideoCapture(video_path)
    
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 10th frame for performance
        if frame_idx % 10 == 0:
            detections = detector.detect_vehicles(frame)
            behaviors = analyzer.analyze_behavior(detections, frame.shape)
            ml_results = classifier.predict(behaviors)
            
            frame_results = []
            for vehicle_id in behaviors.keys():
                vehicle_data = behaviors[vehicle_id]
                ml_data = ml_results.get(vehicle_id, {})
                
                frame_results.append({
                    'frame': frame_idx,
                    'id': vehicle_id,
                    'risk_level': vehicle_data['risk_level'],
                    'behavior_score': vehicle_data['behavior_score'],
                    'ml_prediction': ml_data.get('prediction', 'UNKNOWN')
                })
            
            all_results.extend(frame_results)
        
        frame_idx += 1
    
    cap.release()
    
    return {
        'total_frames': frame_count,
        'processed_frames': frame_idx // 10,
        'results': all_results,
        'summary': generate_video_summary(all_results)
    }

def draw_behavior_info(frame, results):
    """Draw behavior information on frame"""
    for result in results:
        x, y = result['center']
        risk_level = result['risk_level']
        
        # Color based on risk level
        color = (0, 255, 0) if risk_level == 'SAFE' else (0, 165, 255) if risk_level == 'RISKY' else (0, 0, 255)
        
        # Draw risk level
        cv2.putText(frame, f"{risk_level} ({result['confidence']}%)", 
                   (x - 50, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw behavior score
        cv2.putText(frame, f"Score: {result['behavior_score']}", 
                   (x - 50, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return frame

def generate_summary(results):
    """Generate summary statistics"""
    if not results:
        return {'total_vehicles': 0}
    
    risk_counts = {'SAFE': 0, 'RISKY': 0, 'DANGEROUS': 0}
    total_score = 0
    
    for result in results:
        risk_counts[result['risk_level']] += 1
        total_score += result['behavior_score']
    
    return {
        'total_vehicles': len(results),
        'risk_distribution': risk_counts,
        'average_score': round(total_score / len(results), 2),
        'alert_level': 'HIGH' if risk_counts['DANGEROUS'] > 0 else 'MEDIUM' if risk_counts['RISKY'] > 0 else 'LOW'
    }

def generate_video_summary(results):
    """Generate summary for processed video"""
    if not results:
        return {'message': 'No vehicles detected'}
    
    # Aggregate by vehicle ID
    vehicle_stats = {}
    for result in results:
        vid = result['id']
        if vid not in vehicle_stats:
            vehicle_stats[vid] = {'scores': [], 'risk_levels': []}
        
        vehicle_stats[vid]['scores'].append(result['behavior_score'])
        vehicle_stats[vid]['risk_levels'].append(result['risk_level'])
    
    # Calculate statistics
    dangerous_vehicles = 0
    risky_vehicles = 0
    
    for vid, stats in vehicle_stats.items():
        max_risk = max(stats['risk_levels'], key=['SAFE', 'RISKY', 'DANGEROUS'].index)
        if max_risk == 'DANGEROUS':
            dangerous_vehicles += 1
        elif max_risk == 'RISKY':
            risky_vehicles += 1
    
    return {
        'total_unique_vehicles': len(vehicle_stats),
        'dangerous_vehicles': dangerous_vehicles,
        'risky_vehicles': risky_vehicles,
        'safe_vehicles': len(vehicle_stats) - dangerous_vehicles - risky_vehicles
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)