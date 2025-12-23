import React from 'react';
import { AlertCircle } from 'lucide-react';


const ErrorDisplay = ({ error, onReset }) => {
  return (
    <div className="error-container">
      <AlertCircle className="error-icon" size={48} />
      <h3 className="error-title">Analysis Failed</h3>
      <p className="error-message">{error}</p>
      <button onClick={onReset} className="error-button">
        Try Again
      </button>
    </div>
  );
};

export default ErrorDisplay;