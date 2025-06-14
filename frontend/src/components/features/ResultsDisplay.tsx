import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Shield, Eye, TrendingUp, Car, Zap } from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import { VideoAnalysisResult, VehicleDetection } from '../../types';

interface ResultsDisplayProps {
  results: VideoAnalysisResult;
  className?: string;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, className = '' }) => {
  const { summary } = results;
  const totalVehicles = summary.total_unique_vehicles;
  const dangerousCount = summary.dangerous_vehicles;
  const riskyCount = summary.risky_vehicles;
  const safeCount = summary.safe_vehicles;

  const getRiskColor = (count: number, total: number) => {
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
                  {((dangerousCount / totalVehicles) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-danger-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${(dangerousCount / totalVehicles) * 100}%` }}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Risky</span>
                </div>
                <span className="text-sm text-gray-600">
                  {((riskyCount / totalVehicles) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-warning-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${(riskyCount / totalVehicles) * 100}%` }}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Safe</span>
                </div>
                <span className="text-sm text-gray-600">
                  {((safeCount / totalVehicles) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-success-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${(safeCount / totalVehicles) * 100}%` }}
                />
              </div>
            </>
          )}
        </div>
      </Card>

      {/* Detailed Results */}
      {results.results.length > 0 && (
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