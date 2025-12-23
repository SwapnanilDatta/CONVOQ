import React from 'react';
import { MessageCircle, Heart, Zap, AlertCircle } from 'lucide-react';
import { COLOR_MAP } from '../utils/constants';


const OverviewStats = ({ data }) => {
  const stats = [
    {
      icon: MessageCircle,
      label: 'Total Messages',
      value: data.total_messages,
      color: 'purple'
    },
    {
      icon: Heart,
      label: 'Health Score',
      value: `${data.health_score.toFixed(1)}%`,
      color: 'pink'
    },
    {
      icon: Zap,
      label: 'Persona',
      value: data.persona_tag,
      color: 'cyan'
    },
    {
      icon: AlertCircle,
      label: 'Toxicity Rate',
      value: `${(data.toxicity.toxicity_rate * 100).toFixed(1)}%`,
      color: data.toxicity.toxicity_rate > 0.1 ? 'red' : 'green'
    }
  ];

  return (
    <div className="overview-stats-grid">
      {stats.map((stat, idx) => (
        <div key={idx} className="stat-card">
          <div className={`stat-icon ${COLOR_MAP[stat.color]}`}>
            <stat.icon size={24} />
          </div>
          <h3 className="stat-label">{stat.label}</h3>
          <p className="stat-value">{stat.value}</p>
        </div>
      ))}
    </div>
  );
};

export default OverviewStats;