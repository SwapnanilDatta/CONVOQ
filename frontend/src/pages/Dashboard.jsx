import React, { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { ArrowLeft } from 'lucide-react';

import FileUpload from '../components/FileUpload';
import OverviewStats from '../components/OverviewStats';
import Participants from '../components/Participants';
import SentimentTimeline from '../components/SentimentTimeline';
import ReplyTimeStats from '../components/ReplyTimeStats';
import PeakHours from '../components/PeakHours';
import FeaturesScore from '../components/FeaturesScore';
import ErrorDisplay from '../components/ErrorDisplay';
import HistoryList from '../components/HistoryList';
import CoachSummary from '../components/CoachSummary';
import SemanticVibeCheck from '../components/SemanticVibeCheck';
import RelationshipHealthGrid from '../components/RelationshipHealthGrid';
import { getCompleteAnalysis, getHistory, getDeepAnalysis } from '../services/api';

const Dashboard = () => {
    const [analysisData, setAnalysisData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [, setHistory] = useState([]); // Used to trigger updates

    const [token, setToken] = useState(null);
    const [deepLoading, setDeepLoading] = useState(false);
    const [analysisKeys, setAnalysisKeys] = useState({ cacheKey: null, analysisId: null });

    const { user } = useUser();
    const { getToken } = useAuth();

    useEffect(() => {
        const initToken = async () => {
            const authToken = await getToken();
            setToken(authToken);
        };
        if (user) initToken();
    }, [user]);

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

    const handleFileUpload = async (file, dateFormat) => {
        setIsLoading(true);
        setError(null);
        try {
            const token = await getToken();
            const data = await getCompleteAnalysis(file, token, dateFormat);
            if (data.cache_key) {
                setAnalysisKeys({ cacheKey: data.cache_key, analysisId: data.analysis_id });
            }
            setAnalysisData(data);
            loadHistory();
        } catch (err) {
            setError(err.message || 'Something went wrong');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeepScan = async () => {
        if (!analysisKeys.cacheKey || !analysisKeys.analysisId) return;

        setDeepLoading(true);
        try {
            const token = await getToken();
            const deepData = await getDeepAnalysis(analysisKeys.cacheKey, analysisKeys.analysisId, token);

            // Merge deep data into current analysisData
            setAnalysisData(prev => ({
                ...prev,
                ...deepData,
                trend_analysis: deepData.trend_analysis || prev.trend_analysis,
                analysis_status: 'complete'
            }));

            // Clear keys to prevent re-triggering? optional.
            // setAnalysisKeys({ cacheKey: null, analysisId: null });

        } catch (err) {
            console.error(err);
            // Don't nuke the whole view, just alert
            alert("Deep scan failed: " + (err.response?.data?.detail || err.message));
        } finally {
            setDeepLoading(false);
        }
    };

    const handleSelectAnalysis = (item) => {
        const sourceData = item.full_data || item.analysis_results;

        if (!sourceData) {
            setError("Corrupt history data found.");
            return;
        }

        const formattedData = {
            ...sourceData,
            total_messages: item.total_messages,
            health_score: item.health_score,
            persona_tag: item.persona_tag,
            sentiment: sourceData.sentiment || { timeline: [] },
            coach_summary: sourceData.coach_summary || "",
            semantic_analysis: sourceData.semantic_analysis || { events: [] }
        };

        setAnalysisData(formattedData);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleReset = () => {
        setAnalysisData(null);
        setError(null);
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

                {/* Sidebar */}
                <div className="lg:col-span-1">
                    <div className="space-y-4">
                        {/* History */}
                        <div className="bg-slate-900/50 backdrop-blur-md rounded-2xl border border-white/10 p-4 sticky top-24 max-h-[calc(100vh-240px)] overflow-y-auto">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 px-2">History</h3>
                            <HistoryList onSelect={handleSelectAnalysis} />
                        </div>
                    </div>
                </div>

                {/* Main Content */}
                <div className="lg:col-span-3">

                    {/* Header Greeting */}
                    {!analysisData && !isLoading && (
                        <div className="mb-8 animate-fade-in">
                            <h2 className="text-3xl font-bold mb-2">Sup, {user?.firstName}? 👋</h2>
                            <p className="text-slate-400">Ready to expose some red flags? Upload your chat below.</p>
                        </div>
                    )}

                    {!analysisData && !isLoading && (
                        <div className="bg-slate-900/40 backdrop-blur-sm rounded-3xl border border-white/10 p-8 min-h-[400px] flex items-center justify-center">
                            <FileUpload onFileSelect={handleFileUpload} isLoading={isLoading} />
                        </div>
                    )}

                    {isLoading && (
                        <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
                            <div className="w-16 h-16 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin mb-4"></div>
                            <p className="text-xl font-medium animate-pulse">Reading the tea... ☕</p>
                            <p className="text-slate-500 text-sm mt-2">This might take a sec if you talk too much.</p>
                        </div>
                    )}

                    {error && (
                        <div className="mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-200">
                            <ErrorDisplay error={error} onReset={handleReset} />
                        </div>
                    )}

                    {analysisData && !isLoading && (
                        <div className="space-y-6 animate-fade-in-up">
                            <div className="flex items-center justify-between mb-6">
                                <button
                                    onClick={handleReset}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm font-medium transition-colors"
                                >
                                    <ArrowLeft size={16} /> Analyze Another
                                </button>
                                <span className="text-xs font-mono text-slate-500">ID: {new Date().getTime().toString().slice(-6)}</span>
                            </div>

                            {/* 1. High Level Stats */}
                            <OverviewStats data={analysisData} />

                            {/* 1.5 Decision & Trends */}
                            <RelationshipHealthGrid
                                trendData={analysisData.trend_analysis}
                                adviceData={analysisData.decision_advice}
                                onDeepScan={handleDeepScan}
                                isDeepLoading={deepLoading}
                                status={analysisData.analysis_status}
                            />

                            {/* 2. The Coach's Roast */}
                            <div className="grid gap-6">
                                <CoachSummary summary={analysisData.coach_summary} />
                                <SemanticVibeCheck semanticData={analysisData.semantic_analysis} />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Participants
                                    participants={analysisData.participants}
                                    initiations={analysisData.initiations}
                                />
                                <FeaturesScore features={analysisData.features} />
                            </div>

                            <SentimentTimeline timeline={analysisData.sentiment.timeline} />

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
        </div>
    );
};

export default Dashboard;
