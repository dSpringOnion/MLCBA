import React from 'react';
import { motion } from 'framer-motion';

interface ProgressBarProps {
  progress: number;
  className?: string;
  showPercentage?: boolean;
  color?: 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  className = '',
  showPercentage = true,
  color = 'primary',
  size = 'md'
}) => {
  const colors = {
    primary: 'bg-primary-600',
    success: 'bg-success-600',
    warning: 'bg-warning-600',
    danger: 'bg-danger-600',
  };
  
  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };
  
  return (
    <div className={`w-full ${className}`}>
      {showPercentage && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm font-medium text-gray-700">{Math.round(progress)}%</span>
        </div>
      )}
      <div className={`w-full bg-gray-200 rounded-full ${sizes[size]}`}>
        <motion.div
          className={`${colors[color]} ${sizes[size]} rounded-full transition-all duration-300`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;