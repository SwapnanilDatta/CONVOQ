import React from 'react';
import { Github, Twitter, Mail } from 'lucide-react';

const AboutPage = () => {
    return (
        <div className="max-w-4xl mx-auto px-4 py-20 text-center">
            <h1 className="text-5xl font-bold mb-8 font-['Space_Grotesk']">Behind the Code</h1>

            <div className="bg-slate-900/50 backdrop-blur-xl rounded-3xl p-10 border border-white/10 mb-12">
                <p className="text-xl text-slate-300 leading-relaxed mb-6">
                    CONVOQ was built to help you understand your digital relationships without the guesswork.
                    Using advanced NLP and sentiment analysis, we decode the subtext of your chats.
                </p>
                <p className="text-slate-400">
                    It's not just about who texts more. It's about who texts <i>better</i>.
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8 items-center text-left">
                <div className="bg-gradient-to-tr from-purple-900/20 to-blue-900/20 rounded-3xl p-8 border border-white/5">
                    <h2 className="text-2xl font-bold mb-4">Meet the Developer</h2>
                    <p className="text-lg font-semibold text-purple-400 mb-2">Swapnanil Datta</p>
                    <p className="text-slate-400 mb-6">
                        Full Stack Developer & AI Enthusiast. Building things that make sense of the chaos.
                    </p>
                    <div className="flex gap-4">
                        <SocialLink href="https://github.com/SwapnanilDatta" icon={<Github size={20} />} label="GitHub" />
                        <SocialLink href="https://twitter.com/SwapnanilDatta" icon={<Twitter size={20} />} label="Twitter" />
                        <SocialLink href="mailto:dattaswapnanil@gmail.com" icon={<Mail size={20} />} label="Email" />
                    </div>
                </div>

                <div className="space-y-6">
                    <h3 className="text-xl font-bold">Tech Stack</h3>
                    <ul className="space-y-3">
                        <TechItem name="React 19" />
                        <TechItem name="Tailwind CSS v4" />
                        <TechItem name="FastAPI" />
                        <TechItem name="Groq LLM" />
                    </ul>
                </div>
            </div>
        </div>
    );
};

const SocialLink = ({ href, icon, label }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="p-3 bg-white/5 rounded-full hover:bg-white/10 hover:scale-110 transition-all text-slate-300 hover:text-white" aria-label={label}>
        {icon}
    </a>
)

const TechItem = ({ name }) => (
    <li className="flex items-center gap-3 text-slate-400">
        <span className="w-2 h-2 rounded-full bg-purple-500"></span>
        {name}
    </li>
)

export default AboutPage;
