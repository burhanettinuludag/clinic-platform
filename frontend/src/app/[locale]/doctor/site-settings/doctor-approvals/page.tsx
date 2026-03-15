'use client';

import { useState } from 'react';
import { useDoctorApplications, useApproveDoctorApplication, useRejectDoctorApplication, DoctorApplication } from '@/hooks/useSiteAdmin';
import { CheckCircle, XCircle, Clock, Users, Search, ArrowLeft } from 'lucide-react';
import { Link } from '@/i18n/navigation';

const STATUS_TABS = [
  { key: '', label: 'Tumu', icon: Users },
  { key: 'pending', label: 'Bekleyen', icon: Clock },
  { key: 'approved', label: 'Onaylanan', icon: CheckCircle },
  { key: 'rejected', label: 'Reddedilen', icon: XCircle },
];

const SPECIALTY_LABELS: Record<string, string> = {
  neurology: 'Noroloji',
  ftr: 'Fiziksel Tip ve Rehabilitasyon',
  neurosurgery: 'Beyin ve Sinir Cerrahisi',
  physiology: 'Fizyoloji',
  geriatrics: 'Geriatri',
  psychiatry: 'Psikiyatri',
  sleep_medicine: 'Uyku Bozukluklari',
  clinical_psychology: 'Klinik Psikoloji',
  social_work: 'Sosyal Hizmet',
};

export default function DoctorApprovalsPage() {
  const [activeTab, setActiveTab] = useState('');
  const [search, setSearch] = useState('');
  const [rejectModal, setRejectModal] = useState<{ id: string; name: string } | null>(null);
  const [rejectReason, setRejectReason] = useState('');

  const { data: applications, isLoading } = useDoctorApplications(activeTab || undefined);
  const approveMutation = useApproveDoctorApplication();
  const rejectMutation = useRejectDoctorApplication();

  const filtered = (applications || []).filter((app) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      app.user.first_name.toLowerCase().includes(q) ||
      app.user.last_name.toLowerCase().includes(q) ||
      app.user.email.toLowerCase().includes(q) ||
      app.license_number.toLowerCase().includes(q)
    );
  });

  const handleApprove = async (app: DoctorApplication) => {
    if (confirm(`Dr. ${app.user.first_name} ${app.user.last_name} onaylansin mi?`)) {
      await approveMutation.mutateAsync(app.id);
    }
  };

  const handleReject = async () => {
    if (!rejectModal) return;
    await rejectMutation.mutateAsync({ id: rejectModal.id, reason: rejectReason });
    setRejectModal(null);
    setRejectReason('');
  };

  const statusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: 'bg-amber-100 text-amber-700',
      approved: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700',
    };
    const labels: Record<string, string> = {
      pending: 'Bekliyor',
      approved: 'Onaylandi',
      rejected: 'Reddedildi',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
        {labels[status] || status}
      </span>
    );
  };

  const pendingCount = (applications || []).filter((a) => a.approval_status === 'pending').length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/doctor/site-settings" className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Doktor Basvurulari</h1>
          <p className="text-slate-500 mt-1">Doktor basvurularini incele, onayla veya reddet</p>
        </div>
        {pendingCount > 0 && (
          <span className="ml-auto bg-amber-500 text-white px-3 py-1 rounded-full text-sm font-medium">
            {pendingCount} bekleyen
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-2">
        {STATUS_TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-teal-50 text-teal-700 border border-teal-200'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Ad, e-posta veya sicil no ile ara..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-sm"
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="text-center py-12 text-slate-500">Yukleniyor...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          {search ? 'Arama sonucu bulunamadi.' : 'Basvuru bulunamadi.'}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Doktor</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Uzmanlik</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Sicil No</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Basvuru Tarihi</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Durum</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Aksiyonlar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((app) => (
                <tr key={app.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-slate-900">
                        Dr. {app.user.first_name} {app.user.last_name}
                      </p>
                      <p className="text-sm text-slate-500">{app.user.email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-700">
                    {SPECIALTY_LABELS[app.specialty] || app.specialty || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-700 font-mono">
                    {app.license_number || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">
                    {new Date(app.created_at).toLocaleDateString('tr-TR')}
                  </td>
                  <td className="px-4 py-3">{statusBadge(app.approval_status)}</td>
                  <td className="px-4 py-3 text-right">
                    {app.approval_status === 'pending' && (
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleApprove(app)}
                          disabled={approveMutation.isPending}
                          className="px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
                        >
                          Onayla
                        </button>
                        <button
                          onClick={() =>
                            setRejectModal({
                              id: app.id,
                              name: `${app.user.first_name} ${app.user.last_name}`,
                            })
                          }
                          className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
                        >
                          Reddet
                        </button>
                      </div>
                    )}
                    {app.approval_status === 'approved' && app.approved_at && (
                      <span className="text-xs text-slate-400">
                        {new Date(app.approved_at).toLocaleDateString('tr-TR')}
                      </span>
                    )}
                    {app.approval_status === 'rejected' && app.rejection_reason && (
                      <span className="text-xs text-red-400" title={app.rejection_reason}>
                        Sebep: {app.rejection_reason.substring(0, 30)}...
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Reject Modal */}
      {rejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Basvuru Reddi</h3>
            <p className="text-sm text-slate-600">
              Dr. {rejectModal.name} basvurusunu reddetmek istediginize emin misiniz?
            </p>
            <textarea
              placeholder="Red sebebi (opsiyonel)"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setRejectModal(null);
                  setRejectReason('');
                }}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Iptal
              </button>
              <button
                onClick={handleReject}
                disabled={rejectMutation.isPending}
                className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
              >
                {rejectMutation.isPending ? 'Isleniyor...' : 'Reddet'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
