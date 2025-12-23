import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import OverviewStats from './components/OverviewStats';
import Participants from './components/Participants';
import SentimentTimeline from './components/SentimentTimeline';
import ReplyTimeStats from './components/ReplyTimeStats';
import PeakHours from './components/PeakHours';
import FeaturesScore from './components/FeaturesScore';
import ErrorDisplay from './components/ErrorDisplay';
import { uploadFile, getCompleteAnalysis } from './services/api';
import './App.css';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

const handleFileUpload = async (file) => {
  setIsLoading(true);
  setError(null);

  try {
    const data = await getCompleteAnalysis(file); // ✅ pass file
    setAnalysisData(data);
  } catch (err) {
    setError(err.message || 'Something went wrong');
  } finally {
    setIsLoading(false);
  }
};


  const handleReset = () => {
    setAnalysisData(null);
    setError(null);
  };

  return (
    <div className="app">
      <div className="app-container">
        {/* Header */}
        <div className="app-header">
          <h1 className="app-title">Chat Relationship Analyzer</h1>
          <p className="app-subtitle">
            Discover the hidden patterns in your conversations
          </p>
        </div>

        {/* Upload Section */}
        {!analysisData && !isLoading && (
          <FileUpload onFileSelect={handleFileUpload} isLoading={isLoading} />
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p className="loading-text">Analyzing your chat...</p>
          </div>
        )}

        {/* Error State */}
        {error && <ErrorDisplay error={error} onReset={handleReset} />}

        {/* Results Section */}
        {analysisData && !isLoading && (
          <div className="results-container">
            <div className="reset-button-container">
              <button onClick={handleReset} className="reset-button">
                Analyze Another Chat
              </button>
            </div>

            <OverviewStats data={analysisData} />

            <div className="grid-2col">
              <Participants 
                participants={analysisData.participants} 
                initiations={analysisData.initiations}
              />
              <FeaturesScore features={analysisData.features} />
            </div>

            <SentimentTimeline timeline={analysisData.sentiment.timeline} />

            <div className="grid-2col">
              <ReplyTimeStats 
                replyTimes={analysisData.reply_times}
                participants={analysisData.participants}
              />
              <PeakHours peakHours={analysisData.reply_times.peak_hours} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;