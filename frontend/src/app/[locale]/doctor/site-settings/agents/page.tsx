'use client';

import { useState } from 'react';
import {
  useAgentList,
  useTriggerAgent,
  useAgentTriggerHistory,
  useAgentStats,
} from '@/hooks/useSiteAdmin';
import type { AgentItem } from '@/hooks/useSiteAdmin';
import {
  Bot,
  Play,
  Clock,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Loader2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  BarChart3,
  History,
  Zap,
  Timer,
  Cpu,
  FileText,
  Bell,
  Wrench,
  Share2,
  TrendingUp,
} from 'lucide-react';

const CATEGORY_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  content: { label: 'Icerik', icon: <FileText className="h-4 w-4" />, color: 'bg-purple-100 text-purple-700' },
  report: { label: 'Rapor', icon: <BarChart3 className="h-4 w-4" />, color: 'bg-blue-100 text-blue-700' },
  notification: { label: 'Bildirim', icon: <Bell className="h-4 w-4" />, color: 'bg-amber-100 text-amber-700' },
  maintenance: { label: 'Bakim', icon: <Wrench className="h-4 w-4" />, color: 'bg-gray-100 text-gray-700' },
  gamification: { label: 'Oyunlastirma', icon: <Zap className="h-4 w-4" />, color: 'bg-green-100 text-green-700' },
  analysis: { label: 'Analiz', icon: <TrendingUp className="h-4 w-4" />, color: 'bg-cyan-100 text-cyan-700' },
  social: { label: 'Sosyal Medya', icon: <Share2 className="h-4 w-4" />, color: 'bg-pink-100 text-pink-700' },
};

const RISK_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  low: { label: 'Dusuk', icon: <ShieldCheck className="h-3 w-3" />, color: 'text-green-600' },
  medium: { label: 'Orta', icon: <Shield className="h-3 w-3" />, color: 'text-amber-600' },
  high: { label: 'Yuksek', icon: <ShieldAlert className="h-3 w-3" />, color: 'text-red-600' },
};

export default function AgentsPage() {
  const { data, isLoading } = useAgentList();
  const { data: statsData } = useAgentStats();
  const { data: historyData } = useAgentTriggerHistory();
  const triggerAgent = useTriggerAgent();
  const [triggeringKey, setTriggeringKey] = useState<string | null>(null);
  const [tab, setTab] = useState<'agents' | 'history' | 'stats'>('agents');

  const handleTrigger = (agent: AgentItem) => {
    const riskWarning = agent.risk_level === 'high'
      ? '\n\nDIKKAT: Bu islem AI kredisi tuketir!'
      : '';
    if (confirm(`"${agent.name_tr}" simdi calistirilsin mi?${riskWarning}`)) {
      setTriggeringKey(agent.key);
      triggerAgent.mutate(agent.key, {
        onSettled: () => setTriggeringKey(null),
      });
    }
  };

  const formatDuration = (ms: number | null) => {
    if (!ms) return '-';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatCooldown = (seconds: number) => {
    if (seconds <= 0) return null;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m > 0 ? `${m}dk ${s}sn` : `${s}sn`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Bot className="h-7 w-7 text-indigo-500" />
            Agent Yonetimi
          </h1>
          <p className="text-gray-500 mt-1">
            Zamanlanmis gorevleri izleyin ve ihtiyac halinde manuel tetikleyin.
          </p>
        </div>
        {data && (
          <div className="text-right">
            <p className="text-sm text-gray-500">Gunluk Tetikleme</p>
            <p className="text-lg font-bold text-gray-900">
              {data.daily_triggers_used} / {data.daily_trigger_limit}
            </p>
          </div>
        )}
      </div>

      {/* Success/Error */}
      {triggerAgent.isSuccess && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />
          {(triggerAgent.data as any)?.message || 'Agent basariyla tetiklendi!'}
        </div>
      )}
      {triggerAgent.isError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <XCircle className="h-4 w-4" />
          {(triggerAgent.error as any)?.response?.data?.error || 'Agent tetiklenemedi.'}
        </div>
      )}

      {/* Weekly Stats Summary */}
      {statsData && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <MiniStat label="Haftalik Gorev" value={statsData.weekly.total} icon={<Cpu className="h-4 w-4" />} />
          <MiniStat label="Basarili" value={statsData.weekly.completed} icon={<CheckCircle className="h-4 w-4 text-green-500" />} />
          <MiniStat label="Basarisiz" value={statsData.weekly.failed} icon={<XCircle className="h-4 w-4 text-red-500" />} />
          <MiniStat label="Calisiyor" value={statsData.weekly.running} icon={<Loader2 className="h-4 w-4 text-amber-500" />} />
          <MiniStat label="Token" value={statsData.weekly.total_tokens.toLocaleString('tr-TR')} icon={<Zap className="h-4 w-4 text-indigo-500" />} />
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-6">
          {[
            { key: 'agents' as const, label: 'Agent Listesi', icon: <Bot className="h-4 w-4" /> },
            { key: 'history' as const, label: 'Tetikleme Gecmisi', icon: <History className="h-4 w-4" /> },
            { key: 'stats' as const, label: 'Istatistikler', icon: <BarChart3 className="h-4 w-4" /> },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-2 pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {tab === 'agents' && (
        <div className="space-y-3">
          {isLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
            </div>
          ) : (
            data?.agents.map((agent) => (
              <AgentCard
                key={agent.key}
                agent={agent}
                isTriggering={triggeringKey === agent.key}
                onTrigger={() => handleTrigger(agent)}
                formatDuration={formatDuration}
                formatCooldown={formatCooldown}
              />
            ))
          )}
        </div>
      )}

      {tab === 'history' && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          {!historyData?.history.length ? (
            <div className="text-center py-12 text-gray-400">
              <History className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p>Henuz tetikleme gecmisi yok.</p>
            </div>
          ) : (
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tetikleyen</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {historyData.history.map((h) => (
                  <tr key={h.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{h.task_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{h.user_email}</td>
                    <td className="px-4 py-3 text-sm text-gray-400 font-mono">{h.ip_address}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(h.created_at).toLocaleString('tr-TR')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'stats' && statsData && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Haftalik Task Dagilimi</h3>
          {statsData.by_task.length === 0 ? (
            <p className="text-gray-400 text-center py-8">Bu hafta henuz gorev calismamis.</p>
          ) : (
            <div className="space-y-3">
              {statsData.by_task.map((t) => (
                <div key={t.task_type} className="flex items-center justify-between py-2 border-b border-gray-50">
                  <span className="text-sm font-medium text-gray-700">{t.task_type}</span>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-500">{t.count} çalışma</span>
                    <span className="text-green-600">{t.success} başarılı</span>
                    {t.fail > 0 && <span className="text-red-600">{t.fail} başarısız</span>}
                    <span className="text-indigo-600">{(t.tokens || 0).toLocaleString('tr-TR')} token</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ==================== SUB-COMPONENTS ====================

function MiniStat({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-3 flex items-center gap-3">
      <div className="p-2 bg-gray-50 rounded-lg">{icon}</div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-lg font-bold text-gray-900">{value}</p>
      </div>
    </div>
  );
}

function AgentCard({
  agent,
  isTriggering,
  onTrigger,
  formatDuration,
  formatCooldown,
}: {
  agent: AgentItem;
  isTriggering: boolean;
  onTrigger: () => void;
  formatDuration: (ms: number | null) => string;
  formatCooldown: (s: number) => string | null;
}) {
  const cat = CATEGORY_CONFIG[agent.category] || CATEGORY_CONFIG.maintenance;
  const risk = RISK_CONFIG[agent.risk_level] || RISK_CONFIG.low;
  const cooldownText = formatCooldown(agent.cooldown_remaining_seconds);
  const isCooldown = agent.cooldown_remaining_seconds > 0;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between">
        {/* Left: Info */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-semibold text-gray-900">{agent.name_tr}</h3>
            <span className={`px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1 ${cat.color}`}>
              {cat.icon} {cat.label}
            </span>
            <span className={`flex items-center gap-1 text-xs ${risk.color}`}>
              {risk.icon} {risk.label} Risk
            </span>
          </div>
          <p className="text-sm text-gray-500 mb-2">{agent.description_tr}</p>
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" /> {agent.schedule_info}
            </span>
            <span className="flex items-center gap-1">
              <Timer className="h-3 w-3" /> Cooldown: {agent.cooldown_minutes}dk
            </span>
            {agent.last_run && (
              <>
                <span className="flex items-center gap-1">
                  {agent.last_run.status === 'completed' ? (
                    <CheckCircle className="h-3 w-3 text-green-500" />
                  ) : agent.last_run.status === 'failed' ? (
                    <XCircle className="h-3 w-3 text-red-500" />
                  ) : (
                    <Loader2 className="h-3 w-3 text-amber-500 animate-spin" />
                  )}
                  Son: {agent.last_run.created_at ? new Date(agent.last_run.created_at).toLocaleString('tr-TR') : '-'}
                </span>
                {agent.last_run.tokens_used ? (
                  <span>{agent.last_run.tokens_used.toLocaleString('tr-TR')} token</span>
                ) : null}
              </>
            )}
          </div>
        </div>

        {/* Right: Trigger Button */}
        <div className="ml-4 flex flex-col items-end gap-1">
          <button
            onClick={onTrigger}
            disabled={isTriggering || isCooldown}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
              isCooldown
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50'
            }`}
          >
            {isTriggering ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            {isCooldown ? 'Bekleniyor' : 'Calistir'}
          </button>
          {cooldownText && (
            <span className="text-xs text-amber-600 flex items-center gap-1">
              <Timer className="h-3 w-3" /> {cooldownText}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
