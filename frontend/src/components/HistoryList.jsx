import React, { useEffect, useState } from 'react';
import { getHistory } from '../services/api';
import { useAuth } from '@clerk/clerk-react';
import { Clock, MessageSquare, Activity } from 'lucide-react';

const HistoryList = ({ onSelect }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const { getToken } = useAuth();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = await getToken();
        const data = await getHistory(token);
        setHistory(data);
      } catch (err) {
        console.error("History fetch failed", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []); // Only fetch on mount

  // Let's stick to simple styling first. Using 'key={index}' is bad practice, prefer 'item.id' if available.

  if (loading) return (
    <div className="flex items-center justify-center py-8 text-slate-500 gap-2">
      <div className="w-4 h-4 rounded-full border-2 border-slate-500 border-t-transparent animate-spin"></div>
      Loading...
    </div>
  );

  return (
    <div className="space-y-3">
      {history.length === 0 ? (
        <p className="text-slate-500 text-sm text-center py-4">No history yet.</p>
      ) : (
        history.map((item, index) => (
          <div
            key={item.id || index}
            onClick={() => onSelect(item)}
            className="group p-3 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 border border-white/5 hover:border-purple-500/30 cursor-pointer transition-all hover:translate-x-1"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                <Clock size={10} /> {new Date(item.created_at).toLocaleDateString()}
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide 
                  ${item.health_score > 0.7 ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                {Math.round(item.health_score * 100)}% Health
              </span>
            </div>

            {item.persona_tag && (
              <div className="mb-2 text-sm font-semibold text-white group-hover:text-purple-300 transition-colors line-clamp-1">
                {item.persona_tag}
              </div>
            )}

            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1"><MessageSquare size={10} /> {item.total_messages}</span>
              {/* Add more stats if available */}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default HistoryList;
