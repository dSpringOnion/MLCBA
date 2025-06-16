from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Simple test app running'})

@app.route('/')
def home():
    return jsonify({'message': 'Test app - no ML dependencies'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting test app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)