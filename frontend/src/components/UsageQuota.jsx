import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Zap, Clock } from 'lucide-react';
import { API_BASE_URL } from '../utils/constants';

const UsageQuota = ({ token, refreshTrigger }) => {
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUsage();
    }, [refreshTrigger]);

    const fetchUsage = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch(`${API_BASE_URL}/usage`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch usage stats');
            }

            const data = await response.json();
            setUsage(data);
        } catch (err) {
            console.error('Error fetching usage:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-slate-900/50 backdrop-blur-md rounded-2xl border border-white/10 p-4 animate-pulse">
                <div className="h-4 bg-slate-700 rounded w-3/4 mb-3"></div>
                <div className="space-y-2">
                    <div className="h-3 bg-slate-700 rounded w-full"></div>
                    <div className="h-3 bg-slate-700 rounded w-5/6"></div>
                </div>
            </div>
        );
    }

    if (error || !usage) {
        return (
            <div className="bg-slate-900/50 backdrop-blur-md rounded-2xl border border-red-500/20 p-4">
                <p className="text-xs text-red-300">⚠️ Could not load quota info</p>
            </div>
        );
    }

    const rateLimit = usage.rate_limiting;
    const tokenUsage = usage.token_counting;

    // Status indicators
    const getRateLimitStatusColor = () => {
        if (rateLimit.requests_this_minute >= rateLimit.minute_limit) return 'from-red-500/30 to-red-500/10 border-red-500/30';
        if (rateLimit.requests_today >= rateLimit.daily_limit * 0.85) return 'from-yellow-500/30 to-yellow-500/10 border-yellow-500/30';
        return 'from-green-500/30 to-green-500/10 border-green-500/30';
    };

    const getTokenStatusColor = () => {
        if (tokenUsage.usage_percentage > 85) return 'from-red-500/30 to-red-500/10 border-red-500/30';
        if (tokenUsage.usage_percentage > 70) return 'from-yellow-500/30 to-yellow-500/10 border-yellow-500/30';
        return 'from-green-500/30 to-green-500/10 border-green-500/30';
    };

    return (
        <div className="space-y-3">
            {/* Rate Limiting */}
            <div className={`bg-gradient-to-br ${getRateLimitStatusColor()} backdrop-blur-md rounded-xl border p-4`}>
                <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <Clock size={16} className="text-blue-300" />
                        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wide">Requests</span>
                    </div>
                    <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                        rateLimit.requests_this_minute >= rateLimit.minute_limit 
                            ? 'bg-red-500/30 text-red-200' 
                            : rateLimit.requests_today >= rateLimit.daily_limit * 0.85 
                            ? 'bg-yellow-500/30 text-yellow-200' 
                            : 'bg-green-500/30 text-green-200'
                    }`}>
                        {rateLimit.status}
                    </span>
                </div>
                
                <div className="space-y-2 text-xs text-slate-300">
                    <div className="flex justify-between">
                        <span>This minute:</span>
                        <span className="font-mono font-semibold">{rateLimit.requests_this_minute}/{rateLimit.minute_limit}</span>
                    </div>
                    <div className="w-full bg-slate-700/50 rounded-full h-1.5 overflow-hidden">
                        <div 
                            className="bg-blue-400 h-full transition-all duration-300"
                            style={{ width: `${Math.min((rateLimit.requests_this_minute / rateLimit.minute_limit) * 100, 100)}%` }}
                        ></div>
                    </div>

                    <div className="flex justify-between pt-1">
                        <span>Today:</span>
                        <span className="font-mono font-semibold">{rateLimit.requests_today}/{rateLimit.daily_limit}</span>
                    </div>
                    <div className="w-full bg-slate-700/50 rounded-full h-1.5 overflow-hidden">
                        <div 
                            className="bg-blue-400 h-full transition-all duration-300"
                            style={{ width: `${Math.min((rateLimit.requests_today / rateLimit.daily_limit) * 100, 100)}%` }}
                        ></div>
                    </div>
                    <p className="text-slate-400 text-xs pt-1">📌 {rateLimit.remaining_requests_today} requests remaining today</p>
                </div>
            </div>

            {/* Token Usage */}
            <div className={`bg-gradient-to-br ${getTokenStatusColor()} backdrop-blur-md rounded-xl border p-4`}>
                <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <Zap size={16} className="text-amber-300" />
                        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wide">Token Budget</span>
                    </div>
                    <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                        tokenUsage.usage_percentage > 85
                            ? 'bg-red-500/30 text-red-200'
                            : tokenUsage.usage_percentage > 70
                            ? 'bg-yellow-500/30 text-yellow-200'
                            : 'bg-green-500/30 text-green-200'
                    }`}>
                        {tokenUsage.status}
                    </span>
                </div>

                <div className="space-y-2 text-xs text-slate-300">
                    <div className="flex justify-between">
                        <span>Used:</span>
                        <span className="font-mono font-semibold">{tokenUsage.tokens_used_today.toLocaleString()} / {tokenUsage.daily_limit.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-slate-700/50 rounded-full h-1.5 overflow-hidden">
                        <div 
                            className={`h-full transition-all duration-300 ${
                                tokenUsage.usage_percentage > 85 ? 'bg-red-400' : tokenUsage.usage_percentage > 70 ? 'bg-yellow-400' : 'bg-green-400'
                            }`}
                            style={{ width: `${Math.min(tokenUsage.usage_percentage, 100)}%` }}
                        ></div>
                    </div>
                    <p className="text-slate-400 text-xs pt-1">
                        🔋 {tokenUsage.tokens_remaining.toLocaleString()} tokens available • {tokenUsage.usage_percentage}% used
                    </p>
                </div>
            </div>

            {/* Reset Info */}
            <div className="text-xs text-slate-500 text-center bg-slate-900/30 rounded-lg p-2 border border-white/5">
                ⏰ Quotas reset daily at midnight UTC
            </div>
        </div>
    );
};

export default UsageQuota;
