#!/usr/bin/env python3
"""
Download script for demo videos
Upload your videos to cloud storage and update the URLs below
"""

import os
import requests
from pathlib import Path

# Demo video URLs (replace with your cloud storage URLs)
DEMO_VIDEOS = {
    'approaching (2).MP4': 'https://your-cloud-storage.com/approaching-2.MP4',
    'approaching (5).MP4': 'https://your-cloud-storage.com/approaching-5.MP4', 
    'change_lane (1).MP4': 'https://your-cloud-storage.com/change-lane-1.MP4'
}

def download_file(url, filename):
    """Download a file from URL"""
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Downloaded {filename}")

def main():
    """Download all demo videos"""
    videos_dir = Path(__file__).parent / 'backend' / 'sample_videos'
    videos_dir.mkdir(exist_ok=True)
    
    print("🎥 Downloading demo videos...")
    
    for filename, url in DEMO_VIDEOS.items():
        filepath = videos_dir / filename
        
        if filepath.exists():
            print(f"⏭️  {filename} already exists, skipping")
            continue
            
        try:
            download_file(url, filepath)
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            print(f"   Please manually download from: {url}")
    
    print("\n🎉 Demo video setup complete!")
    print("📁 Videos are now available in backend/sample_videos/")

if __name__ == "__main__":
    main()