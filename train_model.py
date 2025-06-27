#!/usr/bin/env python3
"""
Script to process dashcam videos and train the ML model with real data
"""
import os
import sys
sys.path.append('backend')

from backend.vehicle_detector import VehicleDetector
from backend.behavior_analyzer import BehaviorAnalyzer
from backend.ml_classifier import MLBehaviorClassifier
import cv2

def process_video_for_training(video_path, detector, analyzer, classifier):
    """Process a video and collect training data"""
    print(f"Processing {os.path.basename(video_path)}...")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return 0
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0
    training_samples = 0
    
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 10th frame for performance
        if frame_idx % 10 == 0:
            try:
                detections = detector.detect_vehicles(frame)
                behaviors = analyzer.analyze_behavior(detections, frame.shape)
                
                # Save behavior data for training
                if behaviors:
                    classifier.save_training_data(behaviors)
                    training_samples += len(behaviors)
                
                processed_frames += 1
                
                # Progress indicator
                if processed_frames % 50 == 0:
                    progress = (frame_idx / frame_count) * 100
                    print(f"  Progress: {progress:.1f}% - {training_samples} training samples collected")
                    
            except Exception as e:
                print(f"  Error processing frame {frame_idx}: {e}")
        
        frame_idx += 1
    
    cap.release()
    print(f"  Completed: {processed_frames} frames processed, {training_samples} training samples")
    return training_samples

def main():
    print("🚗 Vehicle Behavior Model Training")
    print("=" * 50)
    
    # Initialize components
    print("Initializing AI components...")
    detector = VehicleDetector()
    analyzer = BehaviorAnalyzer()
    classifier = MLBehaviorClassifier()
    
    # Find all video files in sample_videos directory
    video_dir = "backend/sample_videos"
    video_extensions = ('.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.MP4', '.AVI', '.MOV')
    
    video_files = []
    for file in os.listdir(video_dir):
        if file.endswith(video_extensions) and not file.startswith('.'):
            video_files.append(os.path.join(video_dir, file))
    
    if not video_files:
        print("❌ No video files found in backend/sample_videos/")
        return
    
    print(f"📹 Found {len(video_files)} video files:")
    for video in video_files:
        print(f"  - {os.path.basename(video)}")
    
    print("\n🔄 Processing videos to collect training data...")
    
    total_samples = 0
    for video_path in video_files:
        samples = process_video_for_training(video_path, detector, analyzer, classifier)
        total_samples += samples
    
    print(f"\n✅ Data collection complete!")
    print(f"📊 Total training samples collected: {total_samples}")
    
    if total_samples > 0:
        print("\n🤖 Training ML model with real data...")
        try:
            accuracy = classifier.train_model(use_real_data=True)
            classifier.save_model()
            print(f"✅ Model trained successfully!")
            print(f"📈 Training accuracy: {accuracy:.2%}")
            print("💾 Model saved to behavior_model.pkl")
        except Exception as e:
            print(f"❌ Error training model: {e}")
    else:
        print("⚠️  No training data collected. Check your videos and try again.")
    
    print("\n🎉 Training complete! Your model is ready to use.")

if __name__ == "__main__":
    main()