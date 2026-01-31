'use client';

import { useTranslations } from 'next-intl';
import { useDashboardStats, useDoctorAlerts } from '@/hooks/useDoctorData';
import { Link } from '@/i18n/navigation';
import { Users, AlertTriangle, Activity, Brain, TrendingUp, Clock } from 'lucide-react';

const statCards = [
  {
    labelKey: 'doctor.dashboard.totalPatients',
    fallback: 'Toplam Hasta',
    field: 'total_patients',
    icon: Users,
    color: 'blue',
  },
  {
    labelKey: 'doctor.dashboard.activePatients',
    fallback: 'Aktif (7 gun)',
    field: 'active_patients_7d',
    icon: Activity,
    color: 'green',
  },
  {
    labelKey: 'doctor.dashboard.criticalAlerts',
    fallback: 'Kritik Uyari',
    field: 'critical_alerts',
    icon: AlertTriangle,
    color: 'red',
  },
  {
    labelKey: 'doctor.dashboard.warnings',
    fallback: 'Uyari',
    field: 'warning_alerts',
    icon: AlertTriangle,
    color: 'yellow',
  },
  {
    labelKey: 'doctor.dashboard.taskCompletion',
    fallback: 'Gorev Tamamlama',
    field: 'avg_task_completion_rate',
    icon: TrendingUp,
    color: 'purple',
    suffix: '%',
  },
  {
    labelKey: 'doctor.dashboard.attacks30d',
    fallback: 'Atak (30 gun)',
    field: 'total_attacks_30d',
    icon: Brain,
    color: 'orange',
  },
];

const colorMap: Record<string, { bg: string; iconBg: string; text: string }> = {
  blue: { bg: 'bg-blue-50', iconBg: 'bg-blue-100', text: 'text-blue-600' },
  green: { bg: 'bg-green-50', iconBg: 'bg-green-100', text: 'text-green-600' },
  red: { bg: 'bg-red-50', iconBg: 'bg-red-100', text: 'text-red-600' },
  yellow: { bg: 'bg-yellow-50', iconBg: 'bg-yellow-100', text: 'text-yellow-600' },
  purple: { bg: 'bg-purple-50', iconBg: 'bg-purple-100', text: 'text-purple-600' },
  orange: { bg: 'bg-orange-50', iconBg: 'bg-orange-100', text: 'text-orange-600' },
};

export default function DoctorDashboardPage() {
  const t = useTranslations();
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: alerts, isLoading: alertsLoading } = useDoctorAlerts();

  if (statsLoading || alertsLoading) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <p className="text-gray-500">Yukleniyor...</p>
      </div>
    );
  }

  const recentAlerts = alerts?.slice(0, 5) ?? [];

  const getLabel = (labelKey: string, fallback: string) => {
    try {
      const translated = t(labelKey);
      return translated === labelKey ? fallback : translated;
    } catch {
      return fallback;
    }
  };

  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">
        {getLabel('doctor.dashboard.title', 'Doktor Paneli')}
      </h1>

      {/* Stats Grid */}
      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-3">
        {statCards.map((card) => {
          const Icon = card.icon;
          const colors = colorMap[card.color];
          const value = stats?.[card.field as keyof typeof stats];
          return (
            <div
              key={card.field}
              className="rounded-xl border bg-white p-4 shadow-sm"
            >
              <div className="flex items-center gap-3">
                <div className={`rounded-lg p-2 ${colors.iconBg}`}>
                  <Icon className={`h-5 w-5 ${colors.text}`} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">
                    {getLabel(card.labelKey, card.fallback)}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {value != null ? `${value}${card.suffix ?? ''}` : '-'}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Alerts */}
      <div className="rounded-xl border bg-white shadow-sm">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {getLabel('doctor.dashboard.recentAlerts', 'Son Uyarilar')}
          </h2>
          <Link
            href="/doctor/alerts"
            className="text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            {getLabel('doctor.dashboard.viewAll', 'Tumunu Gor')}
          </Link>
        </div>

        {recentAlerts.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            {getLabel('doctor.dashboard.noAlerts', 'Uyari bulunmuyor.')}
          </div>
        ) : (
          <ul className="divide-y">
            {recentAlerts.map((alert: any, index: number) => (
              <li key={alert.id ?? index}>
                <Link
                  href={`/doctor/patients/${alert.patient_id}`}
                  className="flex items-center justify-between px-6 py-4 transition-colors hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {alert.patient_name}
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                      {alert.message}
                    </p>
                  </div>
                  <span
                    className={`ml-4 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      alert.severity === 'critical'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {alert.severity === 'critical' ? 'Kritik' : 'Uyari'}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
