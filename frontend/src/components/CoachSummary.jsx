import React from 'react';
import { Sparkles } from 'lucide-react';

const CoachSummary = ({ summary }) => {
  if (!summary) return null;

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-900/20 to-slate-900/50 border border-purple-500/20 p-8 shadow-2xl">
      <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 blur-[50px] rounded-full pointer-events-none"></div>

      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
          <Sparkles className="text-white" size={20} />
        </div>
        <h3 className="text-xl font-bold font-['Space_Grotesk'] text-white">Coach's Vibe Check</h3>
      </div>

      <div className="bg-slate-900/40 rounded-2xl p-6 border border-white/5 backdrop-blur-sm">
        <div className="text-slate-300 leading-relaxed space-y-4 font-['Outfit']">
          {summary.split('\n').map((line, i) => {
            if (!line.trim()) return null;
            return <p key={i}>{line}</p>;
          })}
        </div>
      </div>
    </div>
  );
};

export default CoachSummary;
