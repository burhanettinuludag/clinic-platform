'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useCaregiverPatients, useCaregiverAlerts } from '@/hooks/useCaregiverData';
import {
  Users, AlertTriangle, Activity, Brain, ChevronRight,
  TrendingUp, Calendar, Shield, Bell,
} from 'lucide-react';

export default function CaregiverDashboardPage() {
  const t = useTranslations();
  const { data: patients, isLoading: patientsLoading } = useCaregiverPatients();
  const { data: alerts, isLoading: alertsLoading } = useCaregiverAlerts();

  if (patientsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Yükleniyor...</div>
      </div>
    );
  }

  const activeAlerts = alerts?.filter((a) => a.severity >= 2) || [];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-teal-100 rounded-lg">
            <Shield className="w-6 h-6 text-teal-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Bakıcı Paneli</h1>
            <p className="text-sm text-gray-500">
              Hastalarınızın durumunu takip edin
            </p>
          </div>
        </div>
      </div>

      {/* Alerts Banner */}
      {activeAlerts.length > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center gap-2 mb-3">
            <Bell className="w-5 h-5 text-red-600" />
            <h2 className="font-semibold text-red-800">
              {activeAlerts.length} Aktif Uyarı
            </h2>
          </div>
          <div className="space-y-2">
            {activeAlerts.slice(0, 5).map((alert, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 p-3 bg-white rounded-lg border border-red-100"
              >
                <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                  alert.severity >= 3 ? 'text-red-500' : 'text-amber-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{alert.patient_name}</p>
                  <p className="text-sm text-gray-600">{alert.message}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(alert.timestamp).toLocaleDateString('tr-TR')}
                  </p>
                </div>
                <Link
                  href={`/caregiver/patients/${alert.patient_id}`}
                  className="text-xs text-teal-600 hover:text-teal-700 flex-shrink-0"
                >
                  Detay
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Patients Grid */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">
            Hastalarım ({patients?.length || 0})
          </h2>
        </div>

        {!patients || patients.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-xl">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              Henüz atanmış hasta yok
            </h3>
            <p className="text-sm text-gray-400">
              Doktorunuz size hasta atadıktan sonra burada görünecektir.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {patients.map((patient) => (
              <Link
                key={patient.id}
                href={`/caregiver/patients/${patient.id}`}
                className="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md hover:border-teal-200 transition-all group"
              >
                {/* Patient Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center">
                      <span className="text-teal-700 font-bold text-sm">
                        {patient.first_name[0]}{patient.last_name[0]}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {patient.first_name} {patient.last_name}
                      </h3>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {patient.has_alerts && (
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                    )}
                    <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-teal-600 transition" />
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="text-center p-2 bg-gray-50 rounded-lg">
                    <Brain className="w-4 h-4 text-purple-500 mx-auto mb-1" />
                    <p className="text-lg font-bold text-gray-900">
                      {patient.latest_score !== null
                        ? Math.round(Number(patient.latest_score))
                        : '-'}
                    </p>
                    <p className="text-[10px] text-gray-500">Skor</p>
                  </div>
                  <div className="text-center p-2 bg-gray-50 rounded-lg">
                    <Activity className="w-4 h-4 text-green-500 mx-auto mb-1" />
                    <p className="text-lg font-bold text-gray-900">
                      {patient.exercises_today}
                    </p>
                    <p className="text-[10px] text-gray-500">Bugün</p>
                  </div>
                  <div className="text-center p-2 bg-gray-50 rounded-lg">
                    <TrendingUp className="w-4 h-4 text-amber-500 mx-auto mb-1" />
                    <p className="text-lg font-bold text-gray-900">
                      {patient.streak_days}
                    </p>
                    <p className="text-[10px] text-gray-500">Seri</p>
                  </div>
                </div>

                {/* Last Activity */}
                {patient.last_activity && (
                  <div className="mt-3 flex items-center gap-1 text-xs text-gray-400">
                    <Calendar className="w-3 h-3" />
                    Son aktivite: {new Date(patient.last_activity).toLocaleDateString('tr-TR')}
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
