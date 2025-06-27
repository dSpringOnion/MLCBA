# Sample Videos Directory

Place your dashcam videos here for processing as sample videos.

## Expected Files:

- `highway_normal.mp4` - Normal highway driving footage
- `city_intersection.mp4` - Urban intersection with moderate traffic
- `aggressive_driving.mp4` - Footage containing aggressive/dangerous driving

## Supported Formats:
- MP4, AVI, MOV, WMV, FLV, WEBM

## How to Add Your Videos:

1. Download your dashcam videos from iCloud to your computer
2. Rename them to match the expected filenames above
3. Copy them to this directory: `backend/sample_videos/`
4. The system will automatically process them when you click "Watch Demo" samples

## Video Requirements:
- Recommended resolution: 720p or higher
- Duration: 30 seconds to 5 minutes optimal
- Clear view of multiple vehicles
- Good lighting conditions for best detection results

## Notes:
- Videos are processed every 10th frame for performance
- Processing time depends on video length and number of vehicles
- Larger files may take longer to process