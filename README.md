# 🚗 Vision-Based Vehicle Behavior Detector

An AI-powered system for detecting dangerous and unpredictable driving behaviors in real-time using computer vision and machine learning.

## 🌟 Features

- **Real-time Vehicle Detection**: Advanced YOLOv8-based vehicle tracking
- **Behavior Analysis**: Comprehensive analysis of speed, lane changes, and erratic movements
- **ML Classification**: Machine learning model classifies driving behavior as safe, risky, or dangerous
- **Modern Web Interface**: Professional React + TypeScript frontend with Tailwind CSS
- **File Upload Support**: Upload video files for analysis with progress tracking
- **Sample Videos**: Pre-loaded demo content with different risk scenarios

## 🏗️ Architecture

### Backend (Python)
- **Flask API** with CORS support
- **Computer Vision**: OpenCV + YOLOv8 for vehicle detection
- **ML Pipeline**: Scikit-learn for behavior classification
- **Real-time Processing**: Frame-by-frame analysis with performance optimization

### Frontend (React + TypeScript)
- **Modern UI**: Senior-level design with Tailwind CSS
- **Responsive Design**: Mobile-first approach with glass morphism effects
- **Interactive Components**: Drag & drop file upload, progress indicators
- **Real-time Results**: Live analysis display with comprehensive insights

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📊 How It Works

1. **Video Upload**: Users upload traffic footage through the web interface
2. **Vehicle Detection**: YOLOv8 identifies and tracks vehicles in each frame
3. **Behavior Analysis**: Algorithm analyzes movement patterns, speed changes, and lane behavior
4. **ML Classification**: Random Forest model classifies each vehicle's behavior
5. **Results Display**: Interactive dashboard shows analysis results with risk assessment

## 🎯 Detection Capabilities

- **Speed Analysis**: Identifies vehicles exceeding safe speed thresholds
- **Lane Change Detection**: Monitors frequent or abrupt lane changes
- **Erratic Movement**: Detects sudden direction changes and unpredictable behavior
- **Following Distance**: Analyzes spacing between vehicles
- **Acceleration Patterns**: Identifies aggressive acceleration/deceleration

## 🛠️ Technical Stack

### Backend
- **Framework**: Flask
- **Computer Vision**: OpenCV, YOLOv8 (Ultralytics)
- **Machine Learning**: Scikit-learn, NumPy, Pandas
- **Image Processing**: Pillow, imutils

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS with custom components
- **Animations**: Framer Motion
- **File Upload**: React Dropzone
- **HTTP Client**: Axios
- **Icons**: Lucide React

## 📁 Project Structure

```
visionBasedVehicleBehavior/
├── backend/
│   ├── vehicle_detector.py      # YOLO-based vehicle detection
│   ├── behavior_analyzer.py     # Behavioral analysis algorithms
│   ├── ml_classifier.py         # ML model for risk classification
│   ├── app.py                   # Flask API server
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/              # Reusable UI components
│   │   │   ├── features/        # Feature-specific components
│   │   │   └── layout/          # Layout components
│   │   ├── types/               # TypeScript type definitions
│   │   ├── utils/               # Utility functions
│   │   └── App.tsx              # Main application component
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🎨 UI/UX Features

- **Glass Morphism Design**: Modern translucent interfaces
- **Smooth Animations**: Framer Motion for engaging interactions
- **Progress Tracking**: Real-time upload and processing feedback
- **Risk Visualization**: Color-coded risk levels with clear indicators
- **Responsive Layout**: Works seamlessly on desktop and mobile
- **Accessibility**: WCAG-compliant design patterns

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload and process video file
- `POST /process_frame` - Process single frame (webcam/real-time)
- `GET /sample_videos` - Get list of sample videos
- `POST /process_sample/<video_id>` - Process sample video

## 📈 Sample Analysis Results

The system provides comprehensive analysis including:
- Total vehicles detected
- Risk distribution (Safe/Risky/Dangerous)
- Average behavior scores
- Frame-by-frame detection timeline
- Key insights and recommendations

## 🎯 Use Cases

- **Traffic Safety Monitoring**: Analyze intersection and highway safety
- **Insurance Claims**: Automated accident analysis
- **Fleet Management**: Monitor driver behavior in commercial fleets
- **Research**: Traffic pattern analysis for urban planning
- **Law Enforcement**: Identify dangerous driving incidents

## 🚧 Future Enhancements

- Real-time webcam processing
- Multi-camera support
- Advanced behavior patterns (road rage, distracted driving)
- Integration with traffic management systems
- Mobile app development
- Cloud deployment with scalable processing

## 👨‍💻 Developer

**Daniel Park**
- Portfolio: [Your Portfolio URL]
- GitHub: [@danielpark](https://github.com/danielpark)
- LinkedIn: [Your LinkedIn]

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for traffic safety and AI innovation**