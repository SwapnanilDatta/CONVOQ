import React, { useState, useEffect } from 'react';
import { 
  SignedIn, 
  SignedOut, 
  SignInButton, 
  UserButton, 
  useUser,
  useAuth
} from '@clerk/clerk-react';

import FileUpload from './components/FileUpload';
import OverviewStats from './components/OverviewStats';
import Participants from './components/Participants';
import SentimentTimeline from './components/SentimentTimeline';
import ReplyTimeStats from './components/ReplyTimeStats';
import PeakHours from './components/PeakHours';
import FeaturesScore from './components/FeaturesScore';
import ErrorDisplay from './components/ErrorDisplay';
import HistoryList from './components/HistoryList'; // Updated from Sidebar to HistoryList per your comment
import { getCompleteAnalysis, getHistory } from './services/api';
import './App.css';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  
  const { user } = useUser();
  const { getToken } = useAuth();

  const loadHistory = async () => {
    try {
      const token = await getToken();
      const data = await getHistory(token);
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  useEffect(() => {
    if (user) loadHistory();
  }, [user]);

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setError(null);
    try {
      const token = await getToken();
      const data = await getCompleteAnalysis(file, token);
      setAnalysisData(data);
      loadHistory(); // Refresh history list after saving new analysis
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectAnalysis = (item) => {
    // Mapping Supabase JSONB back to the format components expect
    const formattedData = {
      ...item.analysis_results,
      total_messages: item.total_messages,
      health_score: item.health_score,
      persona_tag: item.persona_tag,
      sentiment: {
        timeline: item.analysis_results.sentiment // Mapping nested timeline
      }
    };
    setAnalysisData(formattedData);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleReset = () => {
    setAnalysisData(null);
    setError(null);
  };

  return (
    <div className="app">
      <div className="app-container">
        <div className="app-header">
          <div className="auth-header-row">
            <h1 className="app-title">Chat Relationship Analyzer</h1>
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
          <p className="app-subtitle">
            {user ? `Welcome, ${user.firstName}! ` : ""}
            Discover the hidden patterns in your conversations
          </p>
        </div>

        <SignedIn>
          <div className="app-main-layout">
            {/* Sidebar / History Section */}
            <aside className="app-sidebar">
              <HistoryList onSelect={handleSelectAnalysis} />
            </aside>

            <main className="main-content">
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
                      ← Analyze Another Chat
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
            </main>
          </div>
        </SignedIn>

        <SignedOut>
          <div className="welcome-card">
            <h2>Please sign in to analyze your chats</h2>
            <p>Your data is processed securely and privately.</p>
            <div className="signin-btn-wrapper">
              <SignInButton mode="modal">
                <button className="auth-button">Sign In to Start</button>
              </SignInButton>
            </div>
          </div>
        </SignedOut>
      </div>
    </div>
  );
}

export default App;