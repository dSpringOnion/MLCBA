import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glass?: boolean;
}

const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  hover = false,
  glass = false 
}) => {
  const baseClasses = 'rounded-xl overflow-hidden';
  const glassClasses = glass ? 'glass-card' : 'bg-white shadow-lg border border-gray-200';
  const hoverClasses = hover ? 'card-hover' : '';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`
        ${baseClasses}
        ${glassClasses}
        ${hoverClasses}
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
};

export default Card;