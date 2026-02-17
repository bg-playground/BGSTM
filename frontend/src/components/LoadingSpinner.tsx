import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', className = '' }) => {
  const sizeClass = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-12 w-12' : 'h-8 w-8';

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div
        className={`${sizeClass} animate-spin rounded-full border-4 border-gray-200 border-t-primary-600`}
      ></div>
    </div>
  );
};
