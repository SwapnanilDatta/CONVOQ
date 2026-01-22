import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
import { MessageSquare, Home, Info, Sparkles } from 'lucide-react';

const RootLayout = () => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <div className="min-h-screen bg-slate-950 text-white font-['Outfit'] selection:bg-purple-500/30 selection:text-purple-200 overflow-x-hidden relative">
            {/* Ambient Background Glow */}
            <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/20 rounded-full blur-[120px] mix-blend-screen animate-pulse"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/20 rounded-full blur-[120px] mix-blend-screen animate-pulse" style={{ animationDelay: '2s' }}></div>
            </div>

            {/* Navbar */}
            <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-slate-950/70 backdrop-blur-xl supports-[backdrop-filter]:bg-slate-950/40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center gap-1">
                            <Link to="/" className="flex items-center gap-2 group">
                                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center shadow-lg group-hover:shadow-purple-500/25 transition-all">
                                    <MessageSquare className="w-5 h-5 text-white" />
                                </div>
                                <span className="text-xl font-bold font-['Space_Grotesk'] tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                                    CONVOQ
                                </span>
                            </Link>
                        </div>

                        <div className="hidden md:block">
                            <div className="flex items-baseline space-x-4">
                                <NavLink to="/" icon={<Home size={16} />} active={isActive('/')}>Home</NavLink>
                                <NavLink to="/dashboard" icon={<Sparkles size={16} />} active={isActive('/dashboard')}>Dashboard</NavLink>
                                <NavLink to="/about" icon={<Info size={16} />} active={isActive('/about')}>About</NavLink>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <SignedIn>
                                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                                    <UserButton
                                        appearance={{
                                            elements: {
                                                avatarBox: "w-8 h-8 ring-2 ring-purple-500/20"
                                            }
                                        }}
                                    />
                                </div>
                            </SignedIn>
                            <SignedOut>
                                <SignInButton mode="modal">
                                    <button className="px-5 py-2 rounded-full bg-white text-slate-950 font-semibold text-sm hover:bg-slate-200 transition-all shadow-lg hover:shadow-white/10">
                                        Sign In
                                    </button>
                                </SignInButton>
                            </SignedOut>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="pt-20 pb-10 min-h-[calc(100vh-80px)]">
                <Outlet />
            </main>

            <footer className="border-t border-white/5 py-8 mt-auto">
                <div className="max-w-7xl mx-auto px-4 text-center">
                    <p className="text-slate-500 text-sm font-['Space_Grotesk']">
                        Developed by <span className="text-slate-300 font-semibold">Swapnanil Datta</span> • GenZ Chat Analyzer
                    </p>
                </div>
            </footer>
        </div>
    );
};

const NavLink = ({ to, children, icon, active }) => (
    <Link
        to={to}
        className={`
      flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
      ${active
                ? 'bg-purple-500/10 text-purple-300 border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.15)]'
                : 'text-slate-400 hover:text-white hover:bg-white/5'}
    `}
    >
        {icon}
        {children}
    </Link>
);

export default RootLayout;
