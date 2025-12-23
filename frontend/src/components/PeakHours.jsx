import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PeakHours = ({ peakHours }) => {
  const chartData = peakHours.map(item => ({
    hour: `${item.hour}:00`,
    messages: item.count
  }));

  return (
    <div className="chart-card">
      <h2 className="chart-title">Peak Activity Hours</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="messages" fill="#06b6d4" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PeakHours;