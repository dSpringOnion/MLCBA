import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'safe' | 'risky' | 'dangerous' | 'default';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'default', 
  size = 'md',
  className = '' 
}) => {
  const baseClasses = 'inline-flex items-center font-medium rounded-full';
  
  const variants = {
    safe: 'bg-success-100 text-success-800 border border-success-200',
    risky: 'bg-warning-100 text-warning-800 border border-warning-200',
    dangerous: 'bg-danger-100 text-danger-800 border border-danger-200',
    default: 'bg-gray-100 text-gray-800 border border-gray-200',
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };
  
  return (
    <span className={`
      ${baseClasses}
      ${variants[variant]}
      ${sizes[size]}
      ${className}
    `}>
      {children}
    </span>
  );
};

export default Badge;