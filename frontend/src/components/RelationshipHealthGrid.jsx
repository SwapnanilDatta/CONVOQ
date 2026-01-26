import React from 'react';
import { TrendingUp, AlertTriangle, CheckCircle, PauseCircle, Copy, Lock, Loader2 } from 'lucide-react';

const RelationshipHealthGrid = ({ trendData, adviceData, onDeepScan, isDeepLoading, status }) => {

    // Check for "Locked" State
    const isLocked = status === 'pending_deep' || (trendData && trendData.status === 'locked');

    if (isLocked) {
        return (
            <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-white/10 p-8 text-center relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-32 bg-purple-500/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

                <div className="relative z-10 flex flex-col items-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800/80 mb-4 border border-white/5">
                        <Lock className="text-purple-400" size={32} />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">Unlock Deep Insights</h3>
                    <p className="text-slate-400 max-w-lg mx-auto mb-6">
                        Reveal advanced toxicity checks, trend decision signals, and get Coach's specific advice.
                        This uses deeper AI analysis.
                    </p>

                    <button
                        onClick={onDeepScan}
                        disabled={isDeepLoading}
                        className="flex items-center gap-2 px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold transition-all shadow-lg hover:shadow-purple-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isDeepLoading ? (
                            <>
                                <Loader2 size={20} className="animate-spin" /> Analyzing...
                            </>
                        ) : (
                            <>
                                Unlock Metrics <TrendingUp size={18} />
                            </>
                        )}
                    </button>
                </div>
            </div>
        );
    }

    if (!trendData || trendData.decision === "Not Enough Data") {
        return (
            <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-white/10 p-8 text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-4">
                    <TrendingUp className="text-slate-400" size={32} />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Not Enough Data for Trends</h3>
                <p className="text-slate-400 max-w-md mx-auto">
                    Upload more chat logs over time to unlock longitudinal tracking.
                    We need at least 2 uploads to show you how this relationship is evolving.
                </p>
            </div>
        );
    }

    const { decision, decision_color, reasons } = trendData;
    const { advice = [], reply_suggestions = [] } = adviceData || {};

    const colorMap = {
        green: {
            bg: 'bg-green-500/10',
            border: 'border-green-500/20',
            text: 'text-green-400',
            icon: CheckCircle
        },
        yellow: {
            bg: 'bg-yellow-500/10',
            border: 'border-yellow-500/20',
            text: 'text-yellow-400',
            icon: AlertTriangle
        },
        red: {
            bg: 'bg-red-500/10',
            border: 'border-red-500/20',
            text: 'text-red-400',
            icon: PauseCircle
        }
    };

    const theme = colorMap[decision_color] || colorMap.green;
    const Icon = theme.icon;

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        // Could add toast here
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Col: Decision & Reasons */}
            <div className={`rounded-3xl border ${theme.border} ${theme.bg} p-8 relative overflow-hidden`}>
                <div className="absolute top-0 right-0 p-32 bg-white/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-6">
                        <Icon className={theme.text} size={32} />
                        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400">Decision Signal</h2>
                    </div>

                    <h1 className={`text-4xl font-black mb-6 ${theme.text} font-['Space_Grotesk']`}>
                        {decision}
                    </h1>

                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">Why?</h3>
                        <ul className="space-y-2">
                            {reasons.map((reason, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-slate-300">
                                    <span className={`mt-1.5 w-1.5 h-1.5 rounded-full ${theme.text.replace('text-', 'bg-')}`}></span>
                                    {reason}
                                </li>
                            ))}
                            {reasons.length === 0 && (
                                <li className="text-slate-400 italic">No major flags detected.</li>
                            )}
                        </ul>
                    </div>

                    {advice.length > 0 && (
                        <div className="mt-8 pt-6 border-t border-white/10">
                            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-3">Advice</h3>
                            <ul className="list-disc list-inside space-y-1 text-slate-300">
                                {advice.map((item, idx) => (
                                    <li key={idx}>{item}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>

            {/* Right Col: Reply Suggestions */}
            <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-white/10 p-8 flex flex-col">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white mb-2">What to Say Next</h2>
                    <p className="text-slate-400 text-sm">Drafts generated based on your current situation.</p>
                </div>

                <div className="space-y-4 flex-1">
                    {reply_suggestions.length > 0 ? (
                        reply_suggestions.map((reply, idx) => (
                            <div key={idx} className="group relative bg-slate-800/50 hover:bg-slate-800 border border-white/5 rounded-2xl p-4 transition-all">
                                <p className="text-slate-200 pr-8 font-medium">"{reply}"</p>
                                <button
                                    onClick={() => copyToClipboard(reply)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-white/5 text-slate-400 opacity-0 group-hover:opacity-100 transition-all hover:bg-white/10 hover:text-white"
                                    title="Copy text"
                                >
                                    <Copy size={16} />
                                </button>
                            </div>
                        ))
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-slate-500 py-12">
                            <p>No specific reply suggestions available.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RelationshipHealthGrid;
