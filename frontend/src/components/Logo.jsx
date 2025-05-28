import React from 'react';

const Logo = ({ size = 'lg', animated = true, className = '' }) => {
  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32',
    xl: 'w-48 h-48',
  };

  return (
    <div className={`relative ${sizeClasses[size]} ${className}`}>
      <div 
        className={`
          w-full h-full relative cursor-pointer
          ${animated ? 'transition-transform duration-300 hover:scale-105' : ''}
        `}
      >
        {/* Main circle with gradient */}
        <div className="absolute inset-2 rounded-full bg-gradient-to-br from-primary-500 to-success-500 shadow-lg" />
        
        {/* Arrow shape */}
        <div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-white"
          style={{
            width: '40%',
            height: '50%',
            clipPath: 'polygon(50% 0%, 0% 100%, 50% 85%, 100% 100%)',
            backgroundColor: 'white',
          }}
        />
        
        {/* Animated pulse ring */}
        {animated && (
          <div className="absolute inset-0 rounded-full border-2 border-primary-300 animate-pulse-ring opacity-60" />
        )}
      </div>
    </div>
  );
};

export default Logo; 