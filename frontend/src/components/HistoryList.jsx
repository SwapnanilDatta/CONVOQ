import React, { useEffect, useState } from 'react';
import { getHistory } from '../services/api';
import { useAuth } from '@clerk/clerk-react';

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
  }, []);

  if (loading) return <p>Loading history...</p>;

  return (
    <div className="history-list">
      <h3>Past Analyses</h3>
      {history.length === 0 ? <p>No history found.</p> : (
        history.map((item, index) => (
          <div key={index} className="history-item" onClick={() => onSelect(item)}>
            <div className="history-info">
              <span className="history-date">{new Date(item.created_at).toLocaleDateString()}</span>
              <span className="history-tag">{item.persona_tag}</span>
            </div>
            <div className="history-stats">
              <span>{item.total_messages} messages</span>
              <span className="history-score">Score: {Math.round(item.health_score * 100)}%</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default HistoryList;