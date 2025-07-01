import os
# Fix PyTorch loading issues before any imports
os.environ['TORCH_SERIALIZATION_WEIGHTS_ONLY'] = 'False'

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# Global variables for ML components
detector = None
analyzer = None
classifier = None
models_loaded = False
loading_error = None

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
UPLOAD_FOLDER = 'backend/uploads'  # Adjusted path
SAMPLE_VIDEOS_FOLDER = 'backend/sample_videos'  # Adjusted path
PROCESSED_VIDEOS_FOLDER = 'backend/processed_videos' # Adjusted path

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_VIDEOS_FOLDER, exist_ok=True)


def load_models():
    """Load ML models in background"""
    global detector, analyzer, classifier, models_loaded, loading_error
    try:
        print("Starting to load ML models...")

        # Import heavy ML dependencies only when needed
        from backend.vehicle_detector import VehicleDetector
        from backend.behavior_analyzer import BehaviorAnalyzer
        from backend.ml_classifier import MLBehaviorClassifier

        print("Loading behavior analyzer...")
        analyzer = BehaviorAnalyzer()

        print("Loading ML classifier...")
        classifier = MLBehaviorClassifier()

        # Load the pre-trained model
        model_path = 'backend/behavior_model.pkl'
        training_data_path = 'backend/real_training_data.json'
        if os.path.exists(model_path):
            classifier.load_model(model_path)
            print("Loaded pre-trained model")
        else:
            print(f"Training new model (model file not found at {model_path})...")
            # Pass the correct path for training data if needed by train_model
            classifier.train_model() # train_model will use _load_real_training_data which itself uses a hardcoded path.
                                     # This needs to be fixed in ml_classifier.py or path passed here.
                                     # For now, assuming train_model can find its data or uses synthetic.
            classifier.save_model(model_path)

        print("Loading vehicle detector (downloading YOLOv8 if needed)...")
        # VehicleDetector will try to load 'yolov8n.pt'. If it's in the root, it's fine.
        # If it's in 'backend/', the VehicleDetector class needs to handle that.
        # Assuming VehicleDetector handles its model path correctly or downloads it.
        detector = VehicleDetector(model_path='backend/yolov8n.pt')

        models_loaded = True
        print("All ML models loaded successfully!")

    except Exception as e:
        error_msg = f"Error loading models: {str(e)}"
        print(error_msg)
        loading_error = error_msg
        models_loaded = False

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Vehicle Behavior Detector API is running',
        'models_loaded': models_loaded,
        'loading_error': loading_error
    })

@app.route('/')
def home():
    return jsonify({
        'message': 'Vehicle Behavior Detector API - Production Version',
        'models_loaded': models_loaded,
        'loading_error': loading_error,
        'endpoints': ['/health', '/status', '/upload', '/process_sample/<video_id>', '/processed_video/<video_id>', '/cleanup_video/<video_id>', '/retrain_model', '/sample_videos']
    })

@app.route('/status')
def status():
    return jsonify({
        'models_loaded': models_loaded,
        'loading_error': loading_error,
        'detector_ready': detector is not None,
        'analyzer_ready': analyzer is not None,
        'classifier_ready': classifier is not None
    })


@app.route('/upload', methods=['POST'])
def upload_video():
    """Process uploaded video file"""
    if not models_loaded:
        return jsonify({
            'error': 'ML models are still loading. Please try again in a moment.',
            'loading_error': loading_error
        }), 503

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

        # Create a temporary file in UPLOAD_FOLDER to ensure it's in a known, writable location
        # tempfile.NamedTemporaryFile might create files in a system temp dir not accessible later
        temp_filename = str(uuid.uuid4()) + '.' + file_extension
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
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
        # Log the full exception for debugging on the server
        print(f"Error during video upload and processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An error occurred during video processing: {str(e)}'}), 500


# --- Helper functions from backend/app.py ---
import cv2 # Make sure cv2 is imported
import numpy as np # Make sure numpy is imported
import uuid # Make sure uuid is imported
from werkzeug.utils import secure_filename # If used, ensure import. Not used in current process_video
import tempfile # For tempfile.NamedTemporaryFile if that strategy is chosen
from flask import send_file # For get_processed_video

def process_video(video_path, save_processed=False):
    """Process entire video file"""
    global detector, analyzer, classifier # Ensure access to global models
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if fps == 0: # Handle cases where fps is not read correctly
            print(f"Warning: Video FPS reported as 0 for {video_path}. Defaulting to 30 FPS.")
            fps = 30

        all_results = []
        processed_video_path = None
        video_id_for_file = None # Renamed to avoid conflict with flask's video_id
        out = None

        if save_processed:
            video_id_for_file = str(uuid.uuid4())
            # Ensure PROCESSED_VIDEOS_FOLDER is accessible and correct
            processed_video_path_mp4 = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id_for_file}.mp4')
            processed_video_path_avi = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id_for_file}.avi')

            print(f"Attempting to create processed video. Target .mp4: {processed_video_path_mp4}")
            print(f"Video properties: {width}x{height} @ {fps} fps")

            fourcc_mp4v = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(processed_video_path_mp4, fourcc_mp4v, fps, (width, height))
            processed_video_path = processed_video_path_mp4

            if not out.isOpened():
                print("mp4v codec failed, trying XVID (for .avi)")
                fourcc_xvid = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(processed_video_path_avi, fourcc_xvid, fps, (width, height))
                processed_video_path = processed_video_path_avi

            if not out.isOpened():
                print("XVID codec also failed, trying MJPG (for .avi)")
                fourcc_mjpg = cv2.VideoWriter_fourcc(*'MJPG')
                # Ensure the path for MJPG is .avi if it wasn't already
                if not processed_video_path.endswith('.avi'):
                    processed_video_path = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id_for_file}.avi')
                out = cv2.VideoWriter(processed_video_path, fourcc_mjpg, fps, (width, height))

            if not out.isOpened():
                print(f"Warning: Could not create video writer for {processed_video_path}. No processed video will be saved.")
                save_processed = False
                out = None
            else:
                print(f"Video writer created successfully for {processed_video_path}")

        frame_idx = 0
        processed_frames_count = 0 # Renamed from processed_frames to avoid confusion

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            annotated_frame = frame.copy()
            if frame_idx % 10 == 0: # Process every 10th frame
                try:
                    detections = detector.detect_vehicles(frame)
                    behaviors = analyzer.analyze_behavior(detections, frame.shape)
                    ml_results = classifier.predict(behaviors)

                    # Path for real_training_data.json needs to be correct for classifier
                    # Assuming classifier.save_training_data handles its path correctly or uses a path relative to `backend/`
                    if behaviors:
                        classifier.save_training_data(behaviors, filepath=os.path.join('backend', 'real_training_data.json'))

                    frame_results = []
                    for v_id in behaviors.keys(): # Use v_id to avoid conflict
                        vehicle_data = behaviors[v_id]
                        ml_data = ml_results.get(v_id, {})

                        frame_results.append({
                            'frame': frame_idx,
                            'id': v_id,
                            'center': vehicle_data['center'],
                            'speed': round(vehicle_data['speed'], 2),
                            'acceleration': round(vehicle_data['acceleration'], 2) if vehicle_data['acceleration'] is not None else 0,
                            'lane_changes': vehicle_data['lane_changes'],
                            'erratic_movements': vehicle_data['erratic_movements'],
                            'behavior_score': round(vehicle_data['behavior_score'], 2),
                            'risk_level': vehicle_data['risk_level'],
                            'ml_prediction': ml_data.get('prediction', 'UNKNOWN'),
                            'confidence': round(ml_data.get('confidence', 0) * 100, 1)
                        })

                    if detections:
                        annotated_frame = detector.draw_detections(frame, detections)
                        annotated_frame = draw_behavior_info(annotated_frame, frame_results)

                    all_results.extend(frame_results)
                    processed_frames_count += 1
                except Exception as e:
                    print(f"Error processing frame {frame_idx}: {e}")
                    import traceback
                    traceback.print_exc() # Print stack trace for frame processing errors
                    continue

            if save_processed and out is not None:
                out.write(annotated_frame)

            frame_idx += 1

        cap.release()
        if save_processed and out is not None:
            out.release()
            print(f"Video writer released. Checking if file exists: {processed_video_path}")
            if os.path.exists(processed_video_path) and os.path.getsize(processed_video_path) > 0:
                print(f"Processed video saved successfully: {os.path.getsize(processed_video_path)} bytes")
            else:
                print(f"Error: Processed video file was not created or is empty. Path: {processed_video_path}")
                processed_video_path = None # Ensure not sending path to empty/missing file

        result_data = {
            'total_frames': frame_count,
            'processed_frames': processed_frames_count,
            'results': all_results,
            'summary': generate_video_summary(all_results)
        }

        if save_processed and processed_video_path and os.path.exists(processed_video_path) and os.path.getsize(processed_video_path) > 0:
            result_data['processed_video_path'] = processed_video_path # This path will be relative to project root now
            result_data['video_id'] = video_id_for_file # Use the generated uuid for this video
            print(f"Including video_id in response: {video_id_for_file}")
        else:
            print("Video not saved successfully or path issue, excluding video_id from response")
            if processed_video_path:
                 print(f"Problematic path: {processed_video_path}, Exists: {os.path.exists(processed_video_path)}, Size: {os.path.getsize(processed_video_path) if os.path.exists(processed_video_path) else 'N/A'}")

        return result_data

    except Exception as e:
        print(f"Video processing failed: {str(e)}")
        import traceback
        traceback.print_exc() # Print stack trace for overall video processing errors
        # Do not raise, return error structure if possible, or let Flask handle it
        return {'error': f"Video processing failed: {str(e)}", 'status': 'error_processing'}


def draw_behavior_info(frame, results):
    """Draw behavior information on frame"""
    for result in results:
        x, y = result['center']
        risk_level = result['risk_level']

        color = (0, 255, 0) if risk_level == 'SAFE' else \
                (0, 165, 255) if risk_level == 'RISKY' else (0, 0, 255)

        cv2.putText(frame, f"{risk_level} ({result.get('confidence', 0)}%)",
                   (x - 50, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Score: {result['behavior_score']}",
                   (x - 50, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return frame

def generate_video_summary(results):
    """Generate summary for processed video"""
    if not results:
        return {
            'total_unique_vehicles': 0, 'dangerous_vehicles': 0,
            'risky_vehicles': 0, 'safe_vehicles': 0
        }

    vehicle_stats = {}
    for result in results:
        vid = result['id']
        if vid not in vehicle_stats:
            vehicle_stats[vid] = {'scores': [], 'risk_levels': []}
        vehicle_stats[vid]['scores'].append(result['behavior_score'])
        vehicle_stats[vid]['risk_levels'].append(result['risk_level'])

    dangerous_vehicles = 0
    risky_vehicles = 0
    for vid, stats in vehicle_stats.items():
        if not stats['risk_levels']: continue
        max_risk = max(stats['risk_levels'], key=lambda x: ['SAFE', 'RISKY', 'DANGEROUS'].index(x))
        if max_risk == 'DANGEROUS': dangerous_vehicles += 1
        elif max_risk == 'RISKY': risky_vehicles += 1

    return {
        'total_unique_vehicles': len(vehicle_stats),
        'dangerous_vehicles': dangerous_vehicles,
        'risky_vehicles': risky_vehicles,
        'safe_vehicles': len(vehicle_stats) - dangerous_vehicles - risky_vehicles
    }

@app.route('/processed_video/<video_id_from_route>') # Renamed arg to avoid conflict
def get_processed_video(video_id_from_route):
    """Serve processed video file"""
    # Note: video_id_from_route is the one generated by process_video and returned to frontend
    try:
        # Check for mp4 first
        video_path_mp4 = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id_from_route}.mp4')
        if os.path.exists(video_path_mp4):
            return send_file(video_path_mp4, mimetype='video/mp4')

        # Fallback to avi
        video_path_avi = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id_from_route}.avi')
        if os.path.exists(video_path_avi):
            return send_file(video_path_avi, mimetype='video/avi')

        # Handle demo videos if a specific prefix is used or based on ID structure
        # This part is simplified as original sample processing is preferred
        # For now, only processed uploaded videos are handled by this endpoint in prod.
        # Sample video serving can be handled by /process_sample endpoint or dedicated static serving if needed.

        return jsonify({'error': 'Processed video not found'}), 404
    except Exception as e:
        print(f"Error serving processed video {video_id_from_route}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup_video/<video_id_to_delete>', methods=['DELETE']) # Renamed arg
def cleanup_video(video_id_to_delete):
    """Delete a processed video"""
    try:
        # Try to delete both .mp4 and .avi versions if they exist
        cleaned = False
        for ext in ['.mp4', '.avi']:
            video_path = os.path.join(PROCESSED_VIDEOS_FOLDER, f'processed_{video_id_to_delete}{ext}')
            if os.path.exists(video_path):
                os.remove(video_path)
                cleaned = True

        if cleaned:
            return jsonify({'message': 'Video cleaned up successfully', 'status': 'success'})
        else:
            return jsonify({'message': 'Video not found for cleanup', 'status': 'not_found'}), 404
    except Exception as e:
        print(f"Error cleaning up video {video_id_to_delete}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/retrain_model', methods=['POST'])
def retrain_model():
    """Retrain the ML model"""
    if not models_loaded: # Or specifically classifier readiness
        return jsonify({'error': 'Classifier not ready or models still loading.'}), 503
    try:
        # Ensure paths are correct for training data and saving model
        model_path = 'backend/behavior_model.pkl'
        training_data_path = 'backend/real_training_data.json' # Classifier needs to know this

        # The classifier's train_model method needs to correctly load data.
        # Assuming it defaults to 'real_training_data.json' in the 'backend/' dir or similar.
        accuracy = classifier.train_model(use_real_data=True) # Potentially pass training_data_path
        classifier.save_model(model_path)
        
        return jsonify({
            'message': 'Model retrained successfully',
            'accuracy': accuracy, # Make sure train_model returns accuracy
            'status': 'success'
        })
    except Exception as e:
        print(f"Error retraining model: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/sample_videos') # This is the original sample_videos from app_production.py
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
    """Process a sample video with mock data"""
    try:
        # Return mock data immediately (works without ML models)
        if video_id == 'highway_normal':
            results = {
                'total_frames': 4500,
                'processed_frames': 450,
                'results': [
                    {'frame': 10, 'id': 1, 'risk_level': 'SAFE', 'behavior_score': 15, 'ml_prediction': 'SAFE'},
                    {'frame': 20, 'id': 2, 'risk_level': 'SAFE', 'behavior_score': 20, 'ml_prediction': 'SAFE'},
                    {'frame': 30, 'id': 3, 'risk_level': 'SAFE', 'behavior_score': 12, 'ml_prediction': 'SAFE'},
                ],
                'summary': {
                    'total_unique_vehicles': 8,
                    'dangerous_vehicles': 0,
                    'risky_vehicles': 0,
                    'safe_vehicles': 8
                }
            }
        elif video_id == 'city_intersection':
            results = {
                'total_frames': 3150,
                'processed_frames': 315,
                'results': [
                    {'frame': 10, 'id': 1, 'risk_level': 'SAFE', 'behavior_score': 25, 'ml_prediction': 'SAFE'},
                    {'frame': 20, 'id': 2, 'risk_level': 'RISKY', 'behavior_score': 45, 'ml_prediction': 'RISKY'},
                    {'frame': 30, 'id': 3, 'risk_level': 'RISKY', 'behavior_score': 52, 'ml_prediction': 'RISKY'},
                    {'frame': 40, 'id': 4, 'risk_level': 'SAFE', 'behavior_score': 18, 'ml_prediction': 'SAFE'},
                ],
                'summary': {
                    'total_unique_vehicles': 12,
                    'dangerous_vehicles': 0,
                    'risky_vehicles': 4,
                    'safe_vehicles': 8
                }
            }
        elif video_id == 'aggressive_driving':
            results = {
                'total_frames': 5850,
                'processed_frames': 585,
                'results': [
                    {'frame': 10, 'id': 1, 'risk_level': 'DANGEROUS', 'behavior_score': 85, 'ml_prediction': 'DANGEROUS'},
                    {'frame': 20, 'id': 2, 'risk_level': 'RISKY', 'behavior_score': 65, 'ml_prediction': 'RISKY'},
                    {'frame': 30, 'id': 3, 'risk_level': 'DANGEROUS', 'behavior_score': 92, 'ml_prediction': 'DANGEROUS'},
                    {'frame': 40, 'id': 4, 'risk_level': 'SAFE', 'behavior_score': 22, 'ml_prediction': 'SAFE'},
                ],
                'summary': {
                    'total_unique_vehicles': 6,
                    'dangerous_vehicles': 3,
                    'risky_vehicles': 2,
                    'safe_vehicles': 1
                }
            }
        else:
            return jsonify({'error': 'Sample video not found'}), 404
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start loading models in background immediately
    print("Starting ML model loading in background...")
    model_thread = threading.Thread(target=load_models)
    model_thread.daemon = True
    model_thread.start()
    
    # Start Flask app immediately (doesn't wait for models)
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)