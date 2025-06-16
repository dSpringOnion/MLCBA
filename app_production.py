from flask import Flask, request, jsonify
from flask_cors import CORS
import os
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
        if os.path.exists('backend/behavior_model.pkl'):
            classifier.load_model('backend/behavior_model.pkl')
            print("Loaded pre-trained model")
        else:
            print("Training new model...")
            classifier.train_model()
            classifier.save_model('backend/behavior_model.pkl')
        
        print("Loading vehicle detector (downloading YOLOv8 if needed)...")
        detector = VehicleDetector()
        
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
        'endpoints': ['/health', '/status', '/upload', '/process_frame', '/sample_videos']
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
        
        # Mock response for now (since we know models are loading)
        return jsonify({
            'message': 'Video upload endpoint ready',
            'filename': file.filename,
            'note': 'Full processing will be available once models finish loading'
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