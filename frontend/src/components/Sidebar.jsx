import React from 'react';

const Sidebar = ({ history, onSelectAnalysis }) => {
  return (
    <div className="sidebar">
      <h3>Analysis History</h3>
      <ul>
        {history.map((item) => (
          <li key={item.id} onClick={() => onSelectAnalysis(item)}>
            {new Date(item.created_at).toLocaleString()} - {item.total_messages} messages
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;