# Sample Videos Directory

Place your dashcam videos here for processing as sample videos.

## Expected Files:

- `highway_normal.mp4` - Normal highway driving footage
- `city_intersection.mp4` - Urban intersection with moderate traffic
- `aggressive_driving.mp4` - Footage containing aggressive/dangerous driving

## Supported Formats:
- MP4, AVI, MOV, WMV, FLV, WEBM

## How to Add Your Videos:

### Option 1: Download Demo Videos (Recommended)
Run the download script from the project root:
```bash
python3 download_demo_videos.py
```

### Option 2: Use Your Own Videos
1. Download your dashcam videos to your computer
2. Rename them to match the current expected filenames:
   - `approaching (2).MP4`
   - `approaching (5).MP4`  
   - `change_lane (1).MP4`
3. Copy them to this directory: `backend/sample_videos/`
4. The system will automatically process them when you click "Watch Demo" samples

### Option 3: Use Different Filenames
If you have different video files, update the filename mapping in `backend/app.py`:
```python
video_files = {
    'highway_normal': 'your-highway-video.mp4',
    'city_intersection': 'your-city-video.mp4', 
    'aggressive_driving': 'your-aggressive-video.mp4'
}
```

## Video Requirements:
- Recommended resolution: 720p or higher
- Duration: 30 seconds to 5 minutes optimal
- Clear view of multiple vehicles
- Good lighting conditions for best detection results

## Notes:
- Videos are processed every 10th frame for performance
- Processing time depends on video length and number of vehicles
- Larger files may take longer to process