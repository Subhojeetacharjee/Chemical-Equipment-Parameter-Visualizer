/**
 * Auth Card Component
 * 
 * A styled card wrapper for authentication pages.
 */
import React from 'react';

const AuthCard = ({ children, className = '' }) => {
  return (
    <div className={`
      bg-white dark:bg-gray-800
      rounded-3xl shadow-2xl
      p-8 sm:p-10
      w-full max-w-md
      animate-fade-in
      ${className}
    `}>
      {children}
    </div>
  );
};

export default AuthCard;
