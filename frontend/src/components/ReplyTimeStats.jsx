import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';


const ReplyTimeStats = ({ replyTimes, participants }) => {
  const avgReplyData = participants.map(p => ({
    name: p,
    avgMinutes: replyTimes.avg_reply_time[p]
  }));

  return (
    <div className="chart-card">
      <h2 className="chart-title">Average Reply Times</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={avgReplyData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Bar dataKey="avgMinutes" fill="#ec4899" />
        </BarChart>
      </ResponsiveContainer>
      <div className="reply-stats-grid">
        <div className="reply-stat-box fastest">
          <p className="reply-stat-label">Fastest Reply</p>
          <p className="reply-stat-value">{replyTimes.fastest_reply.minutes} min</p>
          <p className="reply-stat-subtitle">by {replyTimes.fastest_reply.from}</p>
        </div>
        <div className="reply-stat-box slowest">
          <p className="reply-stat-label">Longest Ghosting</p>
          <p className="reply-stat-value">{replyTimes.longest_ghosting.minutes} min</p>
          <p className="reply-stat-subtitle">by {replyTimes.longest_ghosting.from}</p>
        </div>
      </div>
    </div>
  );
};

export default ReplyTimeStats;