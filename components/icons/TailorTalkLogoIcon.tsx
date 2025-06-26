
import React from 'react';

export const TailorTalkLogoIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg 
    viewBox="0 0 100 100" 
    xmlns="http://www.w3.org/2000/svg" 
    className={className}
  >
    <defs>
      <linearGradient id="logoGradientTailorTalk" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style={{stopColor: '#5A9BF3', stopOpacity: 1}} />
        <stop offset="100%" style={{stopColor: '#4380D3', stopOpacity: 1}} />
      </linearGradient>
    </defs>
    <path 
      d="M10 5 H90 Q95 5 95 10 V60 Q95 65 90 65 H55 L50 75 L45 65 H10 Q5 65 5 60 V10 Q5 5 10 5 Z" 
      fill="url(#logoGradientTailorTalk)" 
    />
    <text 
      x="50" 
      y="39"
      fontFamily="Arial, Helvetica, sans-serif" 
      fontSize="40" 
      fill="white" 
      textAnchor="middle" 
      dominantBaseline="central" 
      fontWeight="bold"
    >
      T
    </text>
  </svg>
);
