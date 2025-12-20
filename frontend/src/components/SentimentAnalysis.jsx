function SentimentAnalyzer({ timeline }) {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div>
      <h2>Sentiment Analysis</h2>
      <ul>
        {timeline.map((day, idx) => (
          <li key={idx}>
            <strong>{day.date}</strong> → {day.avg_sentiment.toFixed(3)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SentimentAnalyzer;