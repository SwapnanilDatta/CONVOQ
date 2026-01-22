import React from 'react';
import { Link } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton } from '@clerk/clerk-react';
import { ArrowRight, Upload, Zap, Lock, BarChart3 } from 'lucide-react';

const LandingPage = () => {
    return (
        <div className="relative">
            {/* Hero Section */}
            <section className="relative pt-20 pb-32 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col items-center text-center">

                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm font-medium mb-8 animate-fade-in-up">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
                    </span>
                    v2.0 is live • Pure Vibes
                </div>

                <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-slate-500 font-['Space_Grotesk']">
                    Decode Your <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Digital Chemistry</span>
                </h1>

                <p className="text-xl md:text-2xl text-slate-400 max-w-2xl mb-10 leading-relaxed font-['Outfit']">
                    Stop guessing if they like you. Upload your chat export and let our AI roast your reply times, sentiment, and vibe.
                </p>

                <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
                    <SignedIn>
                        <Link
                            to="/dashboard"
                            className="w-full sm:w-auto px-8 py-4 rounded-xl bg-white text-slate-950 font-bold text-lg hover:bg-slate-200 transition-all shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] flex items-center justify-center gap-2"
                        >
                            Go to Dashboard <ArrowRight size={20} />
                        </Link>
                    </SignedIn>
                    <SignedOut>
                        <SignInButton mode="modal">
                            <button className="w-full sm:w-auto px-8 py-4 rounded-xl bg-white text-slate-950 font-bold text-lg hover:bg-slate-200 transition-all shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] flex items-center justify-center gap-2">
                                Analyze My Chat <ArrowRight size={20} />
                            </button>
                        </SignInButton>
                    </SignedOut>
                    <a href="#features" className="w-full sm:w-auto px-8 py-4 rounded-xl bg-white/5 text-white font-semibold text-lg border border-white/10 hover:bg-white/10 transition-all flex items-center justify-center">
                        How it works
                    </a>
                </div>

                {/* Floating cards animation placeholder */}
                <div className="mt-20 relative w-full max-w-5xl aspect-video rounded-3xl border border-white/10 bg-gradient-to-b from-slate-900/50 to-slate-950/50 backdrop-blur-xl overflow-hidden shadow-2xl group">
                    <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:32px_32px]"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                            <div className="w-24 h-24 bg-purple-500/20 rounded-2xl mx-auto mb-4 flex items-center justify-center border border-purple-500/30 group-hover:scale-110 transition-transform duration-500">
                                <Upload className="w-10 h-10 text-purple-400" />
                            </div>
                            <h3 className="text-2xl font-bold">Drag & Drop Chat Export</h3>
                            <p className="text-slate-400 mt-2">WhatsApp or Instagram supported</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-white/5">
                <div className="grid md:grid-cols-3 gap-8">
                    <FeatureCard
                        icon={<Zap className="text-yellow-400" />}
                        title="Instant Roast"
                        desc="Our AI Coach analyzes your texting patterns and gives you brutally honest feedback."
                    />
                    <FeatureCard
                        icon={<BarChart3 className="text-blue-400" />}
                        title="Deep Analytics"
                        desc="See who texts first, reply time gaps, and sentiment trends over time."
                    />
                    <FeatureCard
                        icon={<Lock className="text-green-400" />}
                        title="100% Private"
                        desc="Your chats are analyzed locally or securely in memory. We don't store your secrets."
                    />
                </div>
            </section>
        </div>
    );
};

const FeatureCard = ({ icon, title, desc }) => (
    <div className="p-8 rounded-3xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all hover:-translate-y-1 duration-300 group">
        <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-white/10 flex items-center justify-center mb-6 group-hover:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-shadow">
            {icon}
        </div>
        <h3 className="text-xl font-bold mb-3 font-['Space_Grotesk']">{title}</h3>
        <p className="text-slate-400 leading-relaxed">
            {desc}
        </p>
    </div>
);

export default LandingPage;
