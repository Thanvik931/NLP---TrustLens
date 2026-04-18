import { Eye, Brain, Shield, Activity, RefreshCw, ShieldCheck, Zap, Wrench, PlusCircle, TrendingUp, ArrowRight, Database } from 'lucide-react';
import { Link } from 'react-router-dom';

const HowItWorks = () => {
  return (
    <div className="max-w-7xl mx-auto py-24 px-6 space-y-40">
      
      {/* SECTION 1 — Hero */}
      <section className="text-center space-y-8 animate-in fade-in slide-in-from-top-10 duration-1000">
        <div className="inline-flex items-center space-x-2 px-4 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-[10px] font-black uppercase tracking-widest mx-auto">
           <span>The Architecture of Trust</span>
        </div>
        <h1 className="text-6xl md:text-8xl font-black text-white tracking-tighter leading-none">
          HOW NEURO<span className="text-primary">CLOAK</span> <br /> 
          AUDITS THE FUTURE.
        </h1>
        <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto leading-relaxed font-medium">
          Our Cognitive Digital Twin (CDT) doesn't just watch AI — it understands it. 
          By mirroring internal reasoning layers, we bring transparency to the black box.
        </p>
      </section>

      {/* SECTION 2 — The Problem (Redesigned) */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
        <div className="space-y-8">
          <h2 className="text-4xl font-black text-white tracking-tight">The Problem: <br /><span className="text-accent-rose">Hidden Reasoning</span></h2>
          <p className="text-lg text-slate-400 leading-relaxed font-medium">
            Standard AI models output decisions based on millions of mathematical weights. To a human, this is a "Black Box". When a loan is denied or a medical triage fails, the logic is buried in high-dimensional space. 
          </p>
          <div className="space-y-4">
             <div className="flex items-center gap-4 text-slate-300 font-bold">
                <div className="w-6 h-6 rounded-full bg-accent-rose/20 flex items-center justify-center text-accent-rose">✕</div>
                No Regulatory Audit Trail
             </div>
             <div className="flex items-center gap-4 text-slate-300 font-bold">
                <div className="w-6 h-6 rounded-full bg-accent-rose/20 flex items-center justify-center text-accent-rose">✕</div>
                Invisible Demographic Biases
             </div>
             <div className="flex items-center gap-4 text-slate-300 font-bold">
                <div className="w-6 h-6 rounded-full bg-accent-rose/20 flex items-center justify-center text-accent-rose">✕</div>
                Lack of Medical/Legal Explanation
             </div>
          </div>
        </div>
        <div className="relative group">
          <div className="absolute -inset-4 bg-accent-rose/20 rounded-[2rem] blur-2xl opacity-20 group-hover:opacity-40 transition duration-1000"></div>
          <div className="glass-panel p-12 rounded-[2rem] border-white/5 bg-white/2 flex flex-col items-center justify-center space-y-10 relative overflow-hidden">
            <div className="w-56 h-36 bg-slate-900/80 rounded-2xl border border-white/10 flex items-center justify-center relative z-10 shadow-2xl backdrop-blur-xl">
              <span className="text-white font-black text-xs tracking-widest flex items-center gap-3 uppercase"><Brain className="w-5 h-5 text-slate-500" /> Standard AI</span>
            </div>
            <div className="flex gap-16 w-full justify-center relative z-10 items-center">
              <div className="flex flex-col items-center">
                <ArrowRight className="text-slate-700 w-10 h-10 rotate-180" />
              </div>
              <div className="flex flex-col items-center text-center">
                <div className="w-3 h-3 rounded-full bg-accent-rose animate-ping mb-4" />
                <span className="text-white font-black text-[10px] uppercase tracking-widest px-3 py-1 bg-accent-rose/20 rounded-full">Decision Reached</span>
              </div>
              <div className="flex flex-col items-center">
                <ArrowRight className="text-slate-700 w-10 h-10" />
              </div>
            </div>
            <div className="bg-white/5 text-slate-500 px-6 py-3 rounded-xl text-xs font-black border border-white/5 tracking-[0.2em] uppercase">
              "Reasoning: Undetermined"
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 3 — The Architecture (Step-by-Step) */}
      <section className="space-y-20 relative">
        <div className="text-center space-y-4">
          <h2 className="text-4xl font-black text-white tracking-tight">The Cognitive Oversight Stack</h2>
          <p className="text-slate-400 text-lg font-medium">Four integrated layers of trust and transparency.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[
            { icon: Eye, color: 'text-primary', bg: 'bg-primary/10', title: '01. PERCEPTION', desc: 'Converts raw vector inputs into semantic features. The system identifies what it is "looking at" in human terms.' },
            { icon: Brain, color: 'text-accent-indigo', bg: 'bg-accent-indigo/10', title: '02. REASONING', bgBorder: 'border-accent-indigo/20', desc: 'Maps neural activations to symbolic logic gates. Records the exact decision pathway through the neural net.' },
            { icon: Shield, color: 'text-accent-emerald', bg: 'bg-accent-emerald/10', title: '03. VERIFICATION', desc: 'Cross-checks logic against the Governance Knowledge Base (GKB) to ensure legal and ethical safety.' },
            { icon: Activity, color: 'text-accent-rose', bg: 'bg-accent-rose/10', title: '04. MONITORING', desc: 'The Meta-Observer detects cognitive drift and applies real-time repair coefficients to prevent errors.' }
          ].map((step, i) => (
            <div key={i} className="relative group cursor-default">
              <div className={`absolute -inset-2 bg-gradient-to-b from-white/10 to-transparent rounded-[2rem] opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
              <div className="glass-panel p-8 rounded-[2rem] border-white/5 bg-white/2 h-full flex flex-col hover:border-white/10 transition-all duration-500">
                <div className={`w-14 h-14 rounded-2xl ${step.bg} flex items-center justify-center mb-8 border border-white/5`}>
                  <step.icon className={`w-7 h-7 ${step.color}`} />
                </div>
                <h3 className={`text-sm font-black tracking-widest mb-4 uppercase ${step.color}`}>{step.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed font-medium">{step.desc}</p>
              </div>
              {i < 3 && (
                 <div className="hidden lg:block absolute top-1/2 -right-4 translate-y-[-50%] z-20">
                    <ArrowRight className="w-8 h-8 text-white/10" />
                 </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 4 — The Metrics (Premium Cards) */}
      <section className="space-y-16">
        <div className="flex flex-col md:flex-row justify-between items-end gap-8 border-b border-white/5 pb-12">
           <div className="space-y-4">
              <h2 className="text-4xl font-black text-white tracking-tight">Governance Metrics</h2>
              <p className="text-slate-400 text-lg font-medium max-w-xl">We measure what matters most to regulators and enterprise stakeholders.</p>
           </div>
           <Link to="/analytics" className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-xs font-black uppercase tracking-widest text-slate-300 hover:text-white hover:bg-white/10 transition-all">View Live Analytics</Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            { icon: RefreshCw, title: 'Cognitive Consistency', color: 'text-primary', desc: "The mathematical correlation between the AI's internal state and the CDT's explanation." },
            { icon: Eye, title: 'Transparency Index', color: 'text-accent-indigo', desc: "Percentage of reasoning steps fully resolvable to human-readable symbolic logic." },
            { icon: ShieldCheck, title: 'Ethical Compliance', color: 'text-accent-emerald', desc: "Pass/Fail rate against specific ethical constraints like Fair Lending or HIPAA." },
            { icon: Zap, title: 'Adaptation Speed', color: 'text-accent-rose', desc: "System responsiveness to environmental distribution shifts, measured in microseconds." },
            { icon: Wrench, title: 'Self-Repair Efficiency', color: 'text-yellow-400', desc: "Success rate of automated bias mitigation performed by the Meta-Observer." }
          ].map((metric, i) => (
            <div key={i} className="glass-panel p-8 rounded-[1.5rem] border-white/5 flex gap-6 hover:bg-white/5 transition-colors group">
              <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center shrink-0 border border-white/10 group-hover:border-primary/50 transition-colors">
                <metric.icon className={`w-6 h-6 ${metric.color}`} />
              </div>
              <div>
                <h3 className="text-lg font-black text-white mb-2 tracking-tight">{metric.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed font-medium">{metric.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 5 — Data & Training (Technical Card) */}
      <section className="relative">
        <div className="absolute -inset-10 bg-primary/5 rounded-[4rem] blur-[100px] z-0" />
        <div className="relative z-10 glass-panel p-12 md:p-20 rounded-[3rem] border-white/10 bg-white/2 max-w-5xl mx-auto space-y-12 overflow-hidden shadow-2xl">
          <div className="flex flex-col md:flex-row items-center gap-12">
             <div className="space-y-6 flex-1">
                <h2 className="text-4xl font-black text-white tracking-tight leading-none">MASTER-MODE <br /><span className="text-primary">TRAINING</span></h2>
                <p className="text-slate-300 leading-relaxed text-lg font-medium">
                  NeuroCloak isn't just a dashboard; it's an observer for high-performance ML models trained on proprietary datasets.
                </p>
                <div className="grid grid-cols-2 gap-4 pt-4">
                   <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                      <div className="text-2xl font-black text-white">99.8%</div>
                      <div className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Model Precision</div>
                   </div>
                   <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                      <div className="text-2xl font-black text-white">4.5ms</div>
                      <div className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Audit Latency</div>
                   </div>
                </div>
             </div>
             <div className="flex-1 w-full bg-black/40 rounded-3xl p-8 border border-white/5 font-mono text-xs space-y-4 shadow-inner">
                <div className="text-primary opacity-60 flex justify-between">
                   <span>// Neural Topology Initialization</span>
                   <span className="text-[8px] px-2 py-0.5 rounded bg-primary/20">READY</span>
                </div>
                <div className="text-slate-400">
                   <span className="text-accent-indigo">import</span> scikit_learn <span className="text-accent-indigo">as</span> skl <br />
                   <span className="text-slate-500"># Training Random Forest Ensemble...</span> <br />
                   clf = skl.ensemble.RandomForest(n_estimators=500) <br />
                   clf.fit(X_train, y_train) <br />
                   <br />
                   <span className="text-slate-500"># Initializing CDT Observer...</span> <br />
                   cdt = NeuroCloak.Observer(model=clf) <br />
                   cdt.attach_governance_rules('finance_v4')
                </div>
                <div className="pt-4 border-t border-white/5 flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-accent-emerald" />
                   <span className="text-accent-emerald font-bold">Training Complete: 0.1ms drift detected.</span>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* SECTION 7 — Call to action (Upgraded) */}
      <section className="py-24 text-center space-y-12">
        <h2 className="text-4xl font-black text-white tracking-tight">Step Into the Future of Governance.</h2>
        <div className="flex flex-col sm:flex-row gap-6 justify-center">
          <Link to="/simulate" className="px-10 py-5 bg-primary hover:bg-primary-hover text-white font-black text-lg rounded-2xl transition-all shadow-xl shadow-primary/30 hover:-translate-y-1 flex items-center justify-center gap-3">
            <Zap className="w-6 h-6" /> Start Live Simulation
          </Link>
          <Link to="/dashboard" className="px-10 py-5 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-black text-lg rounded-2xl transition-all flex items-center justify-center gap-3">
            Enter Dashboard
          </Link>
        </div>
      </section>
      
    </div>
  );
};

export default HowItWorks;
