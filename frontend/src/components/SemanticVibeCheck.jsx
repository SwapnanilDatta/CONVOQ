import React from 'react';
import { AlertTriangle, Skull, Heart, Frown, Zap } from 'lucide-react';

const SemanticVibeCheck = ({ semanticData }) => {
  // Guard clause if data is missing or empty
  if (!semanticData || !semanticData.events || semanticData.events.length === 0) {
    return (
      <div className="chart-card flex flex-col items-center justify-center p-12 text-center border-green-500/20 bg-green-900/5">
        <div className="mb-4 p-4 rounded-full bg-green-500/10 text-green-400 animate-bounce">
          <Heart size={32} />
        </div>
        <h2 className="text-2xl font-bold text-green-400 mb-2 font-display">Vibe Check: Immaculate</h2>
        <p className="text-slate-400 max-w-sm">
          No toxic arguments or quarrels detected. You two are chilling. 🍦
        </p>
      </div>
    );
  }

  // Helper to style events based on type
  const getEventStyle = (type) => {
    switch (type?.toLowerCase()) {
      case 'quarrel':
      case 'conflict':
        return {
          icon: <AlertTriangle size={20} />,
          bg: 'bg-red-500/10',
          border: 'border-red-500/20',
          text: 'text-red-400',
          label: 'Possible Beef 🥩'
        };
      case 'banter':
      case 'joking':
        return {
          icon: <Skull size={20} />,
          bg: 'bg-purple-500/10',
          border: 'border-purple-500/20',
          text: 'text-purple-400',
          label: 'Playful Roasting 💀'
        };
      case 'vent':
        return {
          icon: <Frown size={20} />,
          bg: 'bg-blue-500/10',
          border: 'border-blue-500/20',
          text: 'text-blue-400',
          label: 'Venting / Emotional 🌧️'
        };
      default:
        return {
          icon: <Zap size={20} />,
          bg: 'bg-slate-700/30',
          border: 'border-slate-700/50',
          text: 'text-yellow-400',
          label: 'Intense Moment'
        };
    }
  };

  return (
    <div className="chart-card">
      <h2 className="chart-title">⚠️ Tension Timeline</h2>
      <p className="chart-subtitle">Moments where the AI detected high intensity.</p>

      <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
        {semanticData.events.map((event, idx) => {
          const style = getEventStyle(event.type);
          const date = new Date(event.timestamp).toLocaleDateString();
          const time = new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          return (
            <div key={idx} className={`relative p-4 rounded-2xl border ${style.bg} ${style.border} transition-all hover:scale-[1.01]`}>
              <div className="flex gap-4">
                <div className={`mt-1 p-2 rounded-xl ${style.bg} ${style.text} h-fit`}>
                  {style.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <span className={`font-bold text-sm uppercase tracking-wider ${style.text}`}>{style.label}</span>
                    <span className="text-xs font-mono text-slate-500">{date} • {time}</span>
                  </div>
                  <p className="text-slate-200 text-sm leading-relaxed mb-3">
                    "{event.summary}"
                  </p>

                  {/* Sentiment bar */}
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${event.sentiment_score < 0 ? 'bg-red-500' : 'bg-green-500'}`}
                      style={{ width: `${Math.abs(event.sentiment_score * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SemanticVibeCheck;