import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Shield, Zap, Search, ArrowRight, Github } from 'lucide-react';
import heroVisual from '../assets/hero-visual.png';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const token = useAuthStore((state) => state.token);

  const handleCTA = () => {
    if (token) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg text-slate-200 selection:bg-primary/30 overflow-x-hidden">
      {/* Animated Background Mesh */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-[10%] -left-[10%] w-[60%] h-[60%] bg-primary/20 rounded-full blur-[160px] animate-pulse-slow" />
        <div className="absolute top-[20%] -right-[10%] w-[40%] h-[40%] bg-accent-indigo/10 rounded-full blur-[140px] animate-float" />
        <div className="absolute bottom-[0%] left-[20%] w-[30%] h-[30%] bg-accent-emerald/5 rounded-full blur-[100px]" />
      </div>

      {/* Navbar */}
      <nav className="relative z-50 backdrop-blur-md border-b border-white/5 sticky top-0">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3 group cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent-indigo rounded-xl flex items-center justify-center font-bold text-white shadow-lg shadow-primary/30 group-hover:rotate-12 transition-transform duration-500">
              <Shield className="w-6 h-6" />
            </div>
            <span className="text-2xl font-black tracking-tighter text-white">TRUST<span className="text-primary">LENS</span></span>
          </div>
          <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-400">
            <button onClick={() => navigate('/how-it-works')} className="hover:text-primary transition-colors">Technology</button>
            <a href="https://github.com/Thanvik931/TrustLens" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-2">
              <Github className="w-4 h-4" /> Open Source
            </a>
          </div>
          <button 
            onClick={handleCTA}
            className="px-6 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary/50 transition-all text-sm font-bold text-white"
          >
            {token ? 'Go to Dashboard' : 'Sign In'}
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 container mx-auto px-6 pt-24 pb-40">
        <div className="flex flex-col items-center text-center">
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-300 text-[10px] font-black mb-10 uppercase tracking-[0.2em] shadow-inner backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse" />
            <span>AI Governance Platform v2.0 Live</span>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-black text-white mb-8 leading-[0.9] tracking-tighter max-w-5xl">
            AUDIT THE <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent-indigo to-accent-emerald">
              AI BLACK BOX.
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mb-14 leading-relaxed font-medium">
            The first cognitive digital twin architecture for real-time AI oversight. 
            Extract reasoning, verify ethics, and ensure compliance with zero latency.
          </p>

          <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-8">
            <button 
              onClick={handleCTA}
              className="group px-10 py-5 bg-primary hover:bg-primary-hover text-white rounded-2xl font-black text-lg shadow-2xl shadow-primary/40 transition-all hover:-translate-y-1 flex items-center"
            >
              {token ? 'Access Dashboard' : 'Launch CDT Monitor'}
              <ArrowRight className="ml-3 w-6 h-6 group-hover:translate-x-2 transition-transform" />
            </button>
            <button 
              onClick={() => navigate('/how-it-works')}
              className="px-10 py-5 text-slate-400 hover:text-white font-bold text-lg transition-colors flex items-center"
            >
              Technical Specs
            </button>
          </div>
        </div>

        {/* Hero Visual Mockup */}
        <div className="mt-32 relative max-w-6xl mx-auto group">
          <div className="absolute -inset-1 bg-gradient-to-r from-primary/50 to-accent-emerald/50 rounded-[2.5rem] blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
          <div className="relative glass-panel p-3 rounded-[2rem] border-white/10 shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)] overflow-hidden">
             <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-b from-white/10 to-transparent z-20 pointer-events-none" />
             <div className="relative z-10 rounded-[1.5rem] overflow-hidden border border-white/5">
                <img 
                  src={heroVisual} 
                  alt="TrustLens Dashboard" 
                  className="w-full object-cover transform hover:scale-[1.02] transition-transform duration-1000"
                />
             </div>
             {/* Floating UI Elements */}
             <div className="hidden lg:block absolute -right-12 top-1/4 w-64 glass-panel p-4 border-white/10 animate-float shadow-2xl z-30">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 rounded-full bg-accent-rose/20 flex items-center justify-center">
                    <Zap className="w-4 h-4 text-accent-rose" />
                  </div>
                  <span className="text-xs font-bold text-white">Live Anomaly Detected</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-accent-rose w-3/4 animate-pulse" />
                </div>
             </div>
          </div>
        </div>
      </main>

      {/* The 3 Pillars */}
      <section className="relative z-10 container mx-auto px-6 py-40">
        <div className="grid md:grid-cols-3 gap-16">
          <div className="flex flex-col group">
            <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center mb-8 group-hover:bg-primary/20 group-hover:border-primary/50 transition-all duration-500 shadow-xl">
              <Shield className="w-10 h-10 text-primary" />
            </div>
            <h3 className="text-2xl font-black text-white mb-4 tracking-tight">Perceptual Audit</h3>
            <p className="text-slate-400 leading-relaxed text-lg">
              Capture every multi-layer inference step in real-time. We convert mathematical neural weights into human-readable logic.
            </p>
          </div>

          <div className="flex flex-col group">
            <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center mb-8 group-hover:bg-accent-indigo/20 group-hover:border-accent-indigo/50 transition-all duration-500 shadow-xl">
              <Zap className="w-10 h-10 text-accent-indigo" />
            </div>
            <h3 className="text-2xl font-black text-white mb-4 tracking-tight">Bias Auto-Repair</h3>
            <p className="text-slate-400 leading-relaxed text-lg">
              Our Meta-Cognitive Observer detects demographic drift and applies self-repair coefficients before decisions are finalized.
            </p>
          </div>

          <div className="flex flex-col group">
            <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center mb-8 group-hover:bg-accent-emerald/20 group-hover:border-accent-emerald/50 transition-all duration-500 shadow-xl">
              <Search className="w-10 h-10 text-accent-emerald" />
            </div>
            <h3 className="text-2xl font-black text-white mb-4 tracking-tight">Atlas Visibility</h3>
            <p className="text-slate-400 leading-relaxed text-lg">
              Enterprise-grade reporting powered by MongoDB Atlas. Interactive heatmaps and ethical compliance tracking for regulators.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-24 bg-black/20 backdrop-blur-3xl">
        <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-slate-500">
          <div className="flex items-center space-x-3 mb-8 md:mb-0">
            <div className="w-8 h-8 bg-white/5 rounded-lg flex items-center justify-center font-bold text-slate-400 text-sm border border-white/10">
              T
            </div>
            <span className="font-bold text-white tracking-widest text-xs uppercase">TrustLens © 2026</span>
          </div>
          <div className="flex space-x-12 text-[10px] font-black uppercase tracking-widest">
            <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-primary transition-colors">Governance API</a>
            <a href="https://github.com/Thanvik931/TrustLens" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">Open Source</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
