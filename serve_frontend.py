import os
# Fix PyTorch loading issues before any imports
os.environ['TORCH_SERIALIZATION_WEIGHTS_ONLY'] = 'False'

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import threading
import time

# Import the production app logic
from app_production import load_models, detector, analyzer, classifier, models_loaded, loading_error

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# Serve React App
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return send_from_directory(app.static_folder, 'index.html')

# API Routes (same as production app)
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Vehicle Behavior Detector API is running',
        'models_loaded': models_loaded,
        'loading_error': loading_error
    })

@app.route('/api/status')
def status():
    return jsonify({
        'models_loaded': models_loaded,
        'loading_error': loading_error,
        'detector_ready': detector is not None,
        'analyzer_ready': analyzer is not None,
        'classifier_ready': classifier is not None
    })

@app.route('/api/sample_videos')
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

if __name__ == '__main__':
    print("Note: This serves a simple demo message. For full UI, deploy frontend separately.")
    
    # Start loading models in background
    model_thread = threading.Thread(target=load_models)
    model_thread.daemon = True
    model_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)