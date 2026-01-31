'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useDoctorPatients } from '@/hooks/useDoctorData';
import { Link } from '@/i18n/navigation';
import { Search, AlertTriangle, Clock, User } from 'lucide-react';

export default function DoctorPatientsPage() {
  const t = useTranslations();
  const [search, setSearch] = useState('');
  const [hasAlerts, setHasAlerts] = useState(false);

  const { data: patients, isLoading } = useDoctorPatients({
    search: search || undefined,
    has_alerts: hasAlerts ? 'true' : undefined,
  });

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Hastalar</h1>

      {/* Search */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Hasta ara..."
            value={search}
            onChange={handleSearchChange}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setHasAlerts(false)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            !hasAlerts
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Tumunu Goster
        </button>
        <button
          onClick={() => setHasAlerts(true)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1 ${
            hasAlerts
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <AlertTriangle className="h-4 w-4" />
          Uyarili Hastalar
        </button>
      </div>

      {/* Patient List */}
      {!patients || patients.length === 0 ? (
        <div className="text-center py-12">
          <User className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Hasta bulunamadi.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hasta
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  E-posta
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Moduller
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Son Aktivite
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uyarilar
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {patients.map((patient: any) => (
                <tr key={patient.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/doctor/patients/${patient.id}`}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {patient.full_name}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {patient.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {patient.enrolled_modules?.map((mod: string, idx: number) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {mod}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" />
                      {patient.last_active
                        ? new Date(patient.last_active).toLocaleDateString('tr-TR')
                        : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap gap-1">
                      {patient.alert_flags?.map((flag: any, idx: number) => (
                        <span
                          key={idx}
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${
                            flag.severity === 'critical'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          <AlertTriangle className="h-3 w-3" />
                          {flag.message || flag.type}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
