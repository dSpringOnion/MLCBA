from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import os
import uuid
from werkzeug.utils import secure_filename
import tempfile

from vehicle_detector import VehicleDetector
from behavior_analyzer import BehaviorAnalyzer
from ml_classifier import MLBehaviorClassifier

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
UPLOAD_FOLDER = 'uploads'
SAMPLE_VIDEOS_FOLDER = os.path.join(os.path.dirname(__file__), 'sample_videos')
PROCESSED_VIDEOS_FOLDER = 'processed_videos'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAMPLE_VIDEOS_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_VIDEOS_FOLDER, exist_ok=True)

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

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Vehicle Behavior Detector API is running'})

@app.route('/upload', methods=['POST'])
def upload_video():
    """Process uploaded video file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Please upload a video file.'}), 400
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            temp_path = temp_file.name
            file.save(temp_path)
        
        try:
            # Process video
            results = process_video(temp_path, save_processed=True)
            return jsonify(results)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process a single frame from webcam or video"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
            
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

@app.route('/sample_videos')
def get_sample_videos():
    """Get list of sample videos"""
    sample_videos = [
        {
            'id': 'highway_normal',
            'name': 'Highway Traffic - Normal',
            'description': 'Regular highway driving with normal traffic flow',
            'duration': '2:30',
            'vehicles': 8,
            'riskLevel': 'low'
        },
        {
            'id': 'city_intersection',
            'name': 'City Intersection - Moderate',
            'description': 'Urban intersection with lane changes and moderate traffic',
            'duration': '1:45',
            'vehicles': 12,
            'riskLevel': 'medium'
        },
        {
            'id': 'aggressive_driving',
            'name': 'Aggressive Driving - High Risk',
            'description': 'Footage containing aggressive and dangerous driving behaviors',
            'duration': '3:15',
            'vehicles': 6,
            'riskLevel': 'high'
        }
    ]
    return jsonify(sample_videos)

@app.route('/process_sample/<video_id>', methods=['POST'])
def process_sample_video(video_id):
    """Process a sample video"""
    try:
        # Map video IDs to actual file names
        video_files = {
            'highway_normal': 'approaching (2).MP4',
            'city_intersection': 'approaching (5).MP4', 
            'aggressive_driving': 'change_lane (1).MP4'
        }
        
        if video_id not in video_files:
            return jsonify({'error': 'Sample video not found'}), 404
        
        video_path = os.path.join(SAMPLE_VIDEOS_FOLDER, video_files[video_id])
        
        # Check if video file exists
        if not os.path.exists(video_path):
            return jsonify({'error': f'Video file not found: {video_files[video_id]}. Please add your dashcam videos to the sample_videos folder.'}), 404
        
        # Process the actual video
        results = process_video(video_path, save_processed=True)
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/processed_video/<video_id>')
def get_processed_video(video_id):
    """Serve processed video file"""
    try:
        video_path = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id}.mp4')
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Processed video not found'}), 404
            
        return send_file(video_path, mimetype='video/mp4')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/retrain_model', methods=['POST'])
def retrain_model():
    """Retrain the ML model with accumulated real data"""
    try:
        # Retrain with real data
        accuracy = classifier.train_model(use_real_data=True)
        
        # Save the updated model
        classifier.save_model()
        
        return jsonify({
            'message': 'Model retrained successfully',
            'accuracy': accuracy,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_video(video_path, save_processed=False):
    """Process entire video file"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")
            
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        all_results = []
        processed_video_path = None
        
        # Setup video writer if saving processed video
        if save_processed:
            video_id = str(uuid.uuid4())
            processed_video_path = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id}.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(processed_video_path, fourcc, fps, (width, height))
        
        frame_idx = 0
        processed_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 10th frame for performance
            annotated_frame = frame.copy()
            if frame_idx % 10 == 0:
                try:
                    detections = detector.detect_vehicles(frame)
                    behaviors = analyzer.analyze_behavior(detections, frame.shape)
                    ml_results = classifier.predict(behaviors)
                    
                    # Save behavior data for training
                    if behaviors:
                        classifier.save_training_data(behaviors)
                    
                    frame_results = []
                    for vehicle_id in behaviors.keys():
                        vehicle_data = behaviors[vehicle_id]
                        ml_data = ml_results.get(vehicle_id, {})
                        
                        frame_results.append({
                            'frame': frame_idx,
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
                    
                    # Draw annotations if we have detections
                    if detections:
                        annotated_frame = detector.draw_detections(frame, detections)
                        annotated_frame = draw_behavior_info(annotated_frame, frame_results)
                    
                    all_results.extend(frame_results)
                    processed_frames += 1
                except Exception as e:
                    print(f"Error processing frame {frame_idx}: {e}")
                    continue
            
            # Write frame to output video if saving
            if save_processed:
                out.write(annotated_frame)
            
            frame_idx += 1
        
        cap.release()
        if save_processed:
            out.release()
        
        result_data = {
            'total_frames': frame_count,
            'processed_frames': processed_frames,
            'results': all_results,
            'summary': generate_video_summary(all_results)
        }
        
        if save_processed and processed_video_path:
            result_data['processed_video_path'] = processed_video_path
            result_data['video_id'] = video_id
        
        return result_data
    
    except Exception as e:
        raise Exception(f"Video processing failed: {str(e)}")

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
        return {
            'total_vehicles': 0,
            'risk_distribution': {'SAFE': 0, 'RISKY': 0, 'DANGEROUS': 0},
            'average_score': 0,
            'alert_level': 'LOW'
        }
    
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
        return {
            'total_unique_vehicles': 0,
            'dangerous_vehicles': 0,
            'risky_vehicles': 0,
            'safe_vehicles': 0
        }
    
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
        max_risk = max(stats['risk_levels'], key=lambda x: ['SAFE', 'RISKY', 'DANGEROUS'].index(x))
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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)