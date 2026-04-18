import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BrainCircuit, Activity, Database, BarChart3, HelpCircle, Github, Shield } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export default function Sidebar() {
  const { user } = useAuthStore();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Simulation', path: '/simulate', icon: Activity },
    { name: 'Audit Log', path: '/decisions', icon: BrainCircuit },
    { name: 'AI Systems', path: '/systems', icon: Database },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'How It Works', path: '/how-it-works', icon: HelpCircle },
  ];

  return (
    <div className="w-72 bg-dark-sidebar border-r border-white/5 h-full flex flex-col transition-all duration-300 z-50">
      <div className="h-20 flex items-center px-8 border-b border-white/5 shrink-0">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center mr-3 shadow-lg shadow-primary/20">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <span className="font-black text-xl text-white tracking-tighter uppercase">NEURO<span className="text-primary">CLOAK</span></span>
      </div>

      <nav className="flex-1 px-4 py-8 space-y-1.5 overflow-y-auto scrollbar-none">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-4 py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${
                isActive 
                  ? 'bg-primary/10 text-primary shadow-inner border border-primary/20' 
                  : 'text-slate-500 hover:bg-white/5 hover:text-slate-200'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={`w-5 h-5 mr-4 shrink-0 transition-colors ${isActive ? 'text-primary' : 'text-slate-500'}`} />
                {item.name}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-6 border-t border-white/5 space-y-6">
        <a href="https://github.com/Thanvik931/NeuroCloak" target="_blank" rel="noreferrer" className="flex items-center px-4 py-2 text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-white hover:bg-white/5 rounded-xl transition-all">
          <Github className="w-4 h-4 mr-3 shrink-0" />
          Project Repository
        </a>
        <div className="flex items-center space-x-4 bg-white/2 hover:bg-white/5 transition-colors p-4 rounded-2xl border border-white/5 cursor-default group shadow-inner">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent-indigo flex items-center justify-center shrink-0 border border-white/10 group-hover:rotate-6 transition-transform">
            <span className="text-white font-black text-sm text-center leading-none">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-black text-white truncate tracking-tight">{user?.email || 'Unknown User'}</p>
            <p className="text-[9px] text-primary font-black uppercase tracking-[0.2em] truncate mt-1">
              {user?.role || 'VIEWER'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
