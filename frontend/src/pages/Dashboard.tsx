import { useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import MetricCard from '../components/dashboard/MetricCard';
import RecentDecisionsTable from '../components/dashboard/RecentDecisionsTable';
import EmbeddedChart from '../components/dashboard/EmbeddedChart';
import AnomalyPanel from '../components/dashboard/AnomalyPanel';
import { Activity, ShieldCheck, Zap } from 'lucide-react';

export default function Dashboard() {
  const { data: summary, isLoading: isSummaryLoading } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => apiClient('/analytics/summary')
  });

  const { data: metricsData } = useQuery({
    queryKey: ['analytics-metrics'],
    queryFn: () => apiClient('/analytics/metrics')
  });

  const { data: biasData } = useQuery({
    queryKey: ['analytics-bias-types'],
    queryFn: () => apiClient('/analytics/bias-types')
  });

  const { data: decisionsData, isLoading: isDecisionsLoading } = useQuery({
    queryKey: ['recent-decisions'],
    queryFn: () => apiClient('/decisions?limit=10')
  });

  const avgHealthScore = useMemo(() => {
    if (!summary) return undefined;
    const score = (summary.avgComplianceRate * 40) + (summary.avgTransparencyIndex * 30) + (summary.activeFlags === 0 ? 30 : 0);
    return `${score.toFixed(1)}/100`;
  }, [summary?.avgComplianceRate, summary?.avgTransparencyIndex, summary?.activeFlags]);

  const formatPercentage = useCallback((val: number | undefined) => {
    if (val === undefined) return undefined;
    return `${(val * 100).toFixed(1)}%`;
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12 px-2">
      
      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard 
          title="Total Decisions" 
          value={summary ? summary.totalDecisions : undefined} 
          isLoading={isSummaryLoading}
          icon={Activity} 
          trend="+12% daily"
          tooltip="Total number of automated decisions processed by internal AI monitors."
        />
        <MetricCard 
          title="Avg Compliance" 
          value={formatPercentage(summary?.avgComplianceRate)} 
          isLoading={isSummaryLoading}
          icon={ShieldCheck} 
          tooltip="Average rate of decisions passing all ethical and safety governance rules."
        />
        <MetricCard 
          title="Avg Transparency" 
          value={formatPercentage(summary?.avgTransparencyIndex)} 
          isLoading={isSummaryLoading}
          icon={Zap} 
          tooltip="Ratio of internally interpretable reasoning steps to total steps taking place."
        />
        <MetricCard 
          title="Cognitive Health" 
          value={avgHealthScore} 
          isLoading={isSummaryLoading}
          icon={Activity} 
          trend="Optimized"
          tooltip="Unified weighted health score of the monitored AI systems combining compliance, transparency, and bias alerts."
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 group">
          <div className="relative">
             <div className="absolute -inset-1 bg-primary/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500"></div>
             <EmbeddedChart 
               baseUrl="https://charts.mongodb.com/charts-project-0-hdpyqif"
               chartId="39f78fc4-994c-48d4-895f-cd300f276115"
               height="420px"
               title="Ethical Compliance Rate (30 Days)"
             />
          </div>
        </div>
        <div className="group">
           <div className="relative">
              <div className="absolute -inset-1 bg-accent-indigo/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500"></div>
              <EmbeddedChart 
                baseUrl="https://charts.mongodb.com/charts-project-0-hdpyqif"
                chartId="b5c92381-0433-400a-a359-84017dfdb66c"
                height="420px"
                title="Bias Distribution"
              />
           </div>
        </div>
      </div>

      {/* Anomaly Alerts Row */}
      <AnomalyPanel />

      {/* Table Row */}
      <div className="glass-panel overflow-hidden shadow-2xl mt-10 border-white/5 bg-white/2">
        <div className="p-8 border-b border-white/5 bg-white/5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-xl font-black text-white tracking-tight">Recent Decisions Live Feed</h2>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1">Real-time audit log of global model reasoning</p>
          </div>
          <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-accent-emerald/10 border border-accent-emerald/20">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-emerald opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-accent-emerald"></span>
            </span>
            <span className="text-[10px] font-black text-accent-emerald uppercase tracking-[0.2em]">System Live</span>
          </div>
        </div>
        <div className="p-2">
           <RecentDecisionsTable decisions={decisionsData?.data || []} />
        </div>
      </div>
      
    </div>
  );
}
