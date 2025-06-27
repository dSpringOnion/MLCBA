#!/usr/bin/env python3
"""
Simple training script - processes videos via the Flask app API
"""
import requests
import json
import os
import time

def train_model_with_videos():
    base_url = "http://localhost:5000"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print("❌ Backend server not running. Please start it first:")
            print("cd backend && python3 app.py")
            return
    except requests.ConnectionError:
        print("❌ Backend server not running. Please start it first:")
        print("cd backend && python3 app.py")
        return
    
    print("🚗 Training model with your dashcam videos")
    print("=" * 50)
    
    # Get sample videos
    try:
        response = requests.get(f"{base_url}/sample_videos")
        videos = response.json()
        print(f"📹 Found {len(videos)} sample videos")
    except Exception as e:
        print(f"❌ Error getting sample videos: {e}")
        return
    
    # Process each video
    total_processed = 0
    for video in videos:
        print(f"\n🔄 Processing {video['name']}...")
        try:
            response = requests.post(f"{base_url}/process_sample/{video['id']}")
            if response.status_code == 200:
                result = response.json()
                processed = result.get('processed_frames', 0)
                total_processed += processed
                print(f"✅ Processed {processed} frames")
                
                # Print summary
                summary = result.get('summary', {})
                print(f"   Vehicles: {summary.get('total_unique_vehicles', 0)}")
                print(f"   Safe: {summary.get('safe_vehicles', 0)}")
                print(f"   Risky: {summary.get('risky_vehicles', 0)}")
                print(f"   Dangerous: {summary.get('dangerous_vehicles', 0)}")
            else:
                print(f"❌ Error processing {video['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error processing {video['name']}: {e}")
        
        time.sleep(1)  # Brief pause between videos
    
    if total_processed > 0:
        print(f"\n🤖 Retraining model with collected data...")
        try:
            response = requests.post(f"{base_url}/retrain_model")
            if response.status_code == 200:
                result = response.json()
                print("✅ Model retrained successfully!")
                print(f"📈 Accuracy: {result.get('accuracy', 0):.2%}")
            else:
                print(f"❌ Error retraining model: {response.text}")
        except Exception as e:
            print(f"❌ Error retraining model: {e}")
    
    print(f"\n🎉 Training complete! Processed {total_processed} frames total.")

if __name__ == "__main__":
    train_model_with_videos()