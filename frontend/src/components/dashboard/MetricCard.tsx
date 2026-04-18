import React from 'react';
import { Skeleton } from '../ui/Skeleton';

interface MetricCardProps {
  title: string;
  value: string | number | undefined;
  icon: React.ElementType;
  trend?: string;
  tooltip?: string;
  isLoading?: boolean;
}

export default function MetricCard({ title, value, icon: Icon, trend, tooltip, isLoading }: MetricCardProps) {
  if (isLoading) {
    return (
      <div className="glass-panel p-6 border-white/5 bg-white/2">
        <Skeleton className="h-4 w-24 mb-4" />
        <Skeleton className="h-10 w-32" />
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 relative group overflow-hidden transition-all duration-500 hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] hover:-translate-y-1.5 border-white/5 bg-white/2">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase">{title}</p>
          <div className="mt-3 flex items-baseline gap-2">
            <h3 className="text-4xl font-black text-white tracking-tighter">{value ?? '---'}</h3>
            {trend && <span className="text-[10px] text-accent-emerald font-black bg-accent-emerald/10 px-2 py-1 rounded-lg uppercase tracking-wider">{trend}</span>}
          </div>
        </div>
        <div className="w-14 h-14 bg-primary/10 rounded-2xl border border-primary/20 flex items-center justify-center shadow-inner group-hover:bg-primary/20 group-hover:rotate-6 transition-all duration-500">
          <Icon className="w-7 h-7 text-primary" />
        </div>
      </div>
      
      {/* Tooltip on hover */}
      {tooltip && (
        <div className="absolute inset-0 bg-dark-sidebar/95 flex items-center justify-center p-6 opacity-0 group-hover:opacity-100 transition-all duration-500 text-sm text-slate-300 text-center backdrop-blur-xl font-bold leading-relaxed z-10 rounded-2xl cursor-default translate-y-2 group-hover:translate-y-0">
          {tooltip}
        </div>
      )}
    </div>
  );
}
