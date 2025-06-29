import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Shield, Eye, TrendingUp, Car, Video } from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import VideoPlayer from '../ui/VideoPlayer';
import VideoNotice from '../ui/VideoNotice';
import { VideoAnalysisResult } from '../../types';
import { cleanupVideo } from '../../utils/api';

interface ResultsDisplayProps {
  results: VideoAnalysisResult;
  className?: string;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, className = '' }) => {
  // Setup video cleanup on component unmount and page leave
  useEffect(() => {
    const videoId = results.video_id;
    
    if (!videoId) return;

    // Cleanup function for component unmount
    const handleCleanup = () => {
      cleanupVideo(videoId);
    };

    // Handle page refresh/close
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      // Trigger cleanup (fire-and-forget)
      cleanupVideo(videoId);
      
      // Show browser warning about leaving page
      event.preventDefault();
      event.returnValue = 'Your processed video will be deleted if you leave this page.';
      return event.returnValue;
    };

    // Add event listener
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup function
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      handleCleanup();
    };
  }, [results.video_id]);

  // Add null checks to prevent crashes
  if (!results || !results.summary) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <p className="text-gray-500">No analysis results available</p>
      </div>
    );
  }

  const { summary } = results;
  const totalVehicles = summary.total_unique_vehicles || 0;
  const dangerousCount = summary.dangerous_vehicles || 0;
  const riskyCount = summary.risky_vehicles || 0;
  const safeCount = summary.safe_vehicles || 0;

  const getRiskColor = (count: number, total: number) => {
    if (total === 0) return 'text-gray-600';
    const percentage = (count / total) * 100;
    if (percentage > 50) return 'text-danger-600';
    if (percentage > 25) return 'text-warning-600';
    return 'text-success-600';
  };

  const getRiskLevel = () => {
    if (dangerousCount > 0) return 'HIGH';
    if (riskyCount > totalVehicles * 0.3) return 'MEDIUM';
    return 'LOW';
  };

  const riskLevel = getRiskLevel();

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Processed Video Display */}
      {results.video_id ? (
        <Card className="overflow-hidden">
          <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Video className="w-5 h-5 mr-2 text-primary-600" />
              {results.video_id.startsWith('demo_') ? 'Sample Video' : 'Processed Video with Detections'}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {results.video_id.startsWith('demo_') ? 
                'Sample traffic footage showing the types of behaviors our system can detect' :
                'Watch the video with real-time vehicle behavior analysis and annotations'
              }
            </p>
          </div>
          <VideoPlayer
            videoUrl={`${process.env.REACT_APP_API_URL || 'https://mlcba-production.up.railway.app'}/processed_video/${results.video_id}`}
            title={results.video_id.startsWith('demo_') ? 'Sample Video' : 'Processed Video Analysis'}
          />
          <VideoNotice className="mt-3" />
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Video className="w-5 h-5 mr-2 text-amber-600" />
              Video Analysis Complete
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Your video has been analyzed successfully. The behavioral analysis results are shown below.
            </p>
            <p className="text-xs text-amber-700 mt-2 bg-amber-100 p-2 rounded">
              Note: Processed video with annotations is not available in the current deployment environment, 
              but all analysis data has been computed from your uploaded video.
            </p>
          </div>
        </Card>
      )}

      {/* Header with overall risk assessment */}
      <Card className="p-6 bg-gradient-to-r from-slate-50 to-blue-50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Analysis Complete</h3>
            <p className="text-gray-600">
              Processed {results.processed_frames} frames from {results.total_frames} total frames
            </p>
          </div>
          <div className="text-right">
            <div className={`
              inline-flex items-center px-4 py-2 rounded-full text-sm font-medium
              ${riskLevel === 'HIGH' ? 'bg-danger-100 text-danger-800' : 
                riskLevel === 'MEDIUM' ? 'bg-warning-100 text-warning-800' : 
                'bg-success-100 text-success-800'}
            `}>
              {riskLevel === 'HIGH' ? <AlertTriangle className="w-4 h-4 mr-2" /> :
                riskLevel === 'MEDIUM' ? <Eye className="w-4 h-4 mr-2" /> :
                <Shield className="w-4 h-4 mr-2" />}
              {riskLevel} RISK
            </div>
          </div>
        </div>
      </Card>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6 text-center hover" glass>
          <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-primary-100 rounded-full">
            <Car className="w-6 h-6 text-primary-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">{totalVehicles}</div>
          <div className="text-sm font-medium text-gray-600">Total Vehicles</div>
        </Card>

        <Card className="p-6 text-center hover" glass>
          <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-danger-100 rounded-full">
            <AlertTriangle className="w-6 h-6 text-danger-600" />
          </div>
          <div className={`text-3xl font-bold mb-2 ${getRiskColor(dangerousCount, totalVehicles)}`}>
            {dangerousCount}
          </div>
          <div className="text-sm font-medium text-gray-600">Dangerous</div>
        </Card>

        <Card className="p-6 text-center hover" glass>
          <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-warning-100 rounded-full">
            <Eye className="w-6 h-6 text-warning-600" />
          </div>
          <div className={`text-3xl font-bold mb-2 ${getRiskColor(riskyCount, totalVehicles)}`}>
            {riskyCount}
          </div>
          <div className="text-sm font-medium text-gray-600">Risky</div>
        </Card>

        <Card className="p-6 text-center hover" glass>
          <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-success-100 rounded-full">
            <Shield className="w-6 h-6 text-success-600" />
          </div>
          <div className={`text-3xl font-bold mb-2 ${getRiskColor(safeCount, totalVehicles)}`}>
            {safeCount}
          </div>
          <div className="text-sm font-medium text-gray-600">Safe</div>
        </Card>
      </div>

      {/* Risk Distribution Chart */}
      <Card className="p-6" glass>
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h4>
        <div className="space-y-4">
          {totalVehicles > 0 && (
            <>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-danger-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Dangerous</span>
                </div>
                <span className="text-sm text-gray-600">
                  {totalVehicles > 0 ? ((dangerousCount / totalVehicles) * 100).toFixed(1) : '0'}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-danger-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${totalVehicles > 0 ? (dangerousCount / totalVehicles) * 100 : 0}%` }}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Risky</span>
                </div>
                <span className="text-sm text-gray-600">
                  {totalVehicles > 0 ? ((riskyCount / totalVehicles) * 100).toFixed(1) : '0'}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-warning-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${totalVehicles > 0 ? (riskyCount / totalVehicles) * 100 : 0}%` }}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Safe</span>
                </div>
                <span className="text-sm text-gray-600">
                  {totalVehicles > 0 ? ((safeCount / totalVehicles) * 100).toFixed(1) : '0'}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-success-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${totalVehicles > 0 ? (safeCount / totalVehicles) * 100 : 0}%` }}
                />
              </div>
            </>
          )}
        </div>
      </Card>

      {/* Detailed Results */}
      {results.results && results.results.length > 0 && (
        <Card className="p-6" glass>
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Detection Timeline</h4>
          <div className="space-y-3 max-h-96 overflow-y-auto scrollbar-hide">
            {results.results.slice(0, 50).map((detection, index) => (
              <motion.div
                key={`${detection.frame}-${detection.id}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.02 }}
                className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100"
              >
                <div className="flex items-center space-x-3">
                  <div className="text-sm font-mono text-gray-500">
                    Frame {detection.frame}
                  </div>
                  <div className="text-sm font-medium text-gray-900">
                    Vehicle {detection.id}
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="text-sm text-gray-600">
                    Score: {detection.behavior_score.toFixed(1)}
                  </div>
                  <Badge 
                    variant={
                      detection.risk_level === 'DANGEROUS' ? 'dangerous' :
                      detection.risk_level === 'RISKY' ? 'risky' : 'safe'
                    }
                    size="sm"
                  >
                    {detection.risk_level}
                  </Badge>
                </div>
              </motion.div>
            ))}
            {results.results.length > 50 && (
              <div className="text-center text-sm text-gray-500 pt-4">
                ... and {results.results.length - 50} more detections
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Summary Insights */}
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50" glass>
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
          Key Insights
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h5 className="font-medium text-gray-800">Safety Assessment</h5>
            <p className="text-sm text-gray-600">
              {dangerousCount === 0 && riskyCount === 0 
                ? "All vehicles exhibited safe driving behavior throughout the analysis."
                : dangerousCount > 0
                ? `${dangerousCount} vehicle(s) showed dangerous behavior patterns that require immediate attention.`
                : `${riskyCount} vehicle(s) displayed risky behavior that should be monitored.`
              }
            </p>
          </div>
          <div className="space-y-2">
            <h5 className="font-medium text-gray-800">Recommendation</h5>
            <p className="text-sm text-gray-600">
              {riskLevel === 'HIGH' 
                ? "Consider implementing immediate safety measures and increased monitoring."
                : riskLevel === 'MEDIUM'
                ? "Monitor traffic patterns and consider preventive safety measures."
                : "Traffic behavior appears normal. Continue regular monitoring."
              }
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ResultsDisplay;