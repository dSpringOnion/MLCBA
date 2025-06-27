import React from 'react';
import { AlertTriangle, Info, Clock } from 'lucide-react';
import Card from './Card';

interface VideoNoticeProps {
  className?: string;
}

const VideoNotice: React.FC<VideoNoticeProps> = ({ className = '' }) => {
  return (
    <Card className={`p-4 bg-amber-50 border-amber-200 ${className}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <Info className="w-5 h-5 text-amber-600 mt-0.5" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-medium text-amber-800 mb-1">
            Temporary Video Storage
          </h4>
          <p className="text-sm text-amber-700 mb-2">
            Your processed video is temporarily stored for this session only.
          </p>
          <div className="flex items-start space-x-4 text-xs text-amber-600">
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>Auto-deleted when you leave this page</span>
            </div>
            <div className="flex items-center space-x-1">
              <AlertTriangle className="w-3 h-3" />
              <span>Refreshing will remove the video</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default VideoNotice;