'use client';

import { useTranslations } from 'next-intl';
import { useDoctorAlerts } from '@/hooks/useDoctorData';
import { Link } from '@/i18n/navigation';
import { AlertTriangle, Clock, User } from 'lucide-react';

export default function DoctorAlertsPage() {
  const t = useTranslations();
  const { data: alerts, isLoading } = useDoctorAlerts();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  const sortedAlerts = alerts
    ? [...alerts].sort((a: any, b: any) => {
        const severityOrder: Record<string, number> = { critical: 0, warning: 1 };
        const aSev = severityOrder[a.severity] ?? 2;
        const bSev = severityOrder[b.severity] ?? 2;
        if (aSev !== bSev) return aSev - bSev;
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      })
    : [];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Uyarilar</h1>

      {sortedAlerts.length === 0 ? (
        <div className="text-center py-12">
          <AlertTriangle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Aktif uyari yok</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedAlerts.map((alert: any, idx: number) => {
            const isCritical = alert.severity === 'critical';

            return (
              <div
                key={idx}
                className={`bg-white rounded-lg shadow p-4 border-l-4 ${
                  isCritical ? 'border-l-red-500' : 'border-l-yellow-500'
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Severity Icon */}
                  <div
                    className={`flex-shrink-0 mt-0.5 ${
                      isCritical ? 'text-red-500' : 'text-yellow-500'
                    }`}
                  >
                    <AlertTriangle className="h-5 w-5" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {/* Severity Badge */}
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
                          isCritical
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {isCritical ? 'Kritik' : 'Uyari'}
                      </span>

                      {/* Alert Type */}
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                        {alert.alert_type}
                      </span>
                    </div>

                    {/* Patient Name */}
                    <div className="flex items-center gap-1 mb-1">
                      <User className="h-3.5 w-3.5 text-gray-400" />
                      <Link
                        href={`/doctor/patients/${alert.patient_id}`}
                        className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {alert.patient_name}
                      </Link>
                    </div>

                    {/* Alert Message */}
                    <p className="text-sm text-gray-700">{alert.message}</p>

                    {/* Time */}
                    <div className="flex items-center gap-1 mt-2 text-xs text-gray-400">
                      <Clock className="h-3 w-3" />
                      {alert.created_at
                        ? new Date(alert.created_at).toLocaleDateString('tr-TR', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        : '-'}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
