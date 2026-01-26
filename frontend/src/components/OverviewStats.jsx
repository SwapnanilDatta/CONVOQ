import React from 'react';
import { MessageCircle, Heart, Zap, Ghost, Flame } from 'lucide-react';

const OverviewStats = ({ data }) => {
  const totalMessages = data.total_messages;

  const toxicityVal = data.toxicity?.toxicity_rate || 0;
  const isToxicLocked = data.toxicity?.status === 'locked';
  const isToxic = toxicityVal > 0.15;

  const colorConfig = {
    purple: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    green: 'bg-green-500/20 text-green-400 border-green-500/30',
    red: 'bg-red-500/20 text-red-400 border-red-500/30',
    pink: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
    cyan: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    gray: 'bg-slate-700/20 text-slate-400 border-slate-700/30',
  };

  const getHealthColor = (score) => {
    if (score > 70) return 'green';
    if (score < 50) return 'red';
    return 'pink';
  };

  const stats = [
    {
      icon: MessageCircle,
      label: 'Yap Level',
      subLabel: 'Total Messages',
      value: totalMessages.toLocaleString(),
      color: 'purple'
    },
    {
      icon: Heart,
      label: 'Vibe Score',
      subLabel: 'Health Score',
      value: isToxicLocked ? "Locked 🔒" : `${data.health_score.toFixed(0)}/100`,
      color: isToxicLocked ? 'gray' : getHealthColor(data.health_score)
    },
    {
      icon: Zap,
      label: 'Aura / Persona',
      subLabel: 'Relationship Tag',
      value: data.persona_tag || "Loading...",
      color: 'cyan'
    },
    {
      icon: isToxic ? Flame : Ghost,
      label: isToxic ? 'Cooked' : 'Chill',
      subLabel: 'Toxicity Rate',
      value: isToxicLocked ? "Locked 🔒" : `${(toxicityVal).toFixed(1)}%`,
      color: isToxic && !isToxicLocked ? 'red' : 'green'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, idx) => (
        <div key={idx} className="bg-slate-900/40 backdrop-blur-md rounded-2xl p-5 border border-white/5 hover:border-white/10 transition-all group">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 border ${colorConfig[stat.color]}`}>
            <stat.icon size={24} />
          </div>
          <div className="space-y-1">
            <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wide">{stat.label}</h3>
            <p className="text-2xl font-bold font-['Space_Grotesk'] text-white">{stat.value}</p>
            <span className="text-xs text-slate-500">{stat.subLabel}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default OverviewStats;