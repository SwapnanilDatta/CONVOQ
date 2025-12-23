import React from 'react';


const FeaturesScore = ({ features }) => {
  const featureData = Object.entries(features).map(([key, value]) => ({
    name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    score: (value * 100).toFixed(1)
  }));

  return (
    <div className="chart-card">
      <h2 className="chart-title">Relationship Features</h2>
      <div className="features-list">
        {featureData.map((feature, idx) => (
          <div key={idx} className="feature-item">
            <div className="feature-header">
              <span className="feature-name">{feature.name}</span>
              <span className="feature-score">{feature.score}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${feature.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeaturesScore;