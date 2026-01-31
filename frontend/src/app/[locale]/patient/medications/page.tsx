'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  useActiveMedications,
  useCreateMedication,
  useLogMedication,
  useTodayMedicationLogs,
  useMedicationAdherence,
} from '@/hooks/usePatientData';
import { Pill, Plus, Check, X, TrendingUp } from 'lucide-react';

export default function MedicationsPage() {
  const t = useTranslations();
  const { data: medications, isLoading } = useActiveMedications();
  const { data: todayLogs } = useTodayMedicationLogs();
  const { data: adherence } = useMedicationAdherence();
  const createMed = useCreateMedication();
  const logMed = useLogMedication();

  const [showAddForm, setShowAddForm] = useState(false);
  const [newMed, setNewMed] = useState({ name: '', dosage: '', frequency: '' });

  const loggedMedIds = new Set(todayLogs?.map((l) => l.medication) ?? []);

  const handleAddMed = () => {
    if (!newMed.name) return;
    createMed.mutate(newMed, {
      onSuccess: () => {
        setShowAddForm(false);
        setNewMed({ name: '', dosage: '', frequency: '' });
      },
    });
  };

  const handleLog = (medId: string, wasTaken: boolean) => {
    logMed.mutate({
      medication: medId,
      taken_at: new Date().toISOString(),
      was_taken: wasTaken,
    });
  };

  if (isLoading) {
    return <div className="text-center py-12 text-gray-500">{t('common.loading')}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Pill className="w-6 h-6 text-purple-600" />
          <h1 className="text-2xl font-bold text-gray-900">{t('patient.medications.title')}</h1>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" /> {t('patient.medications.addMedication')}
        </button>
      </div>

      {/* Adherence Card */}
      {adherence && adherence.total_logs > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <h2 className="text-sm font-semibold">{t('patient.medications.adherence')}</h2>
          </div>
          <div className="flex items-end gap-6">
            <div>
              <div className="text-3xl font-bold text-gray-900">%{adherence.adherence_rate}</div>
              <div className="text-xs text-gray-400">{t('patient.medications.adherenceRate')}</div>
            </div>
            <div className="flex gap-4 text-sm">
              <div>
                <span className="text-green-600 font-medium">{adherence.taken}</span>
                <span className="text-gray-400 ml-1">{t('patient.medications.taken')}</span>
              </div>
              <div>
                <span className="text-red-500 font-medium">{adherence.missed}</span>
                <span className="text-gray-400 ml-1">{t('patient.medications.missed')}</span>
              </div>
            </div>
          </div>
          <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all"
              style={{ width: `${adherence.adherence_rate}%` }}
            />
          </div>
        </div>
      )}

      {/* Add Form */}
      {showAddForm && (
        <div className="bg-white rounded-xl border border-blue-200 p-5 mb-6">
          <h3 className="text-sm font-semibold mb-3">{t('patient.medications.addMedication')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
            <input
              type="text"
              placeholder={t('patient.medications.name')}
              value={newMed.name}
              onChange={(e) => setNewMed({ ...newMed, name: e.target.value })}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder={t('patient.medications.dosage')}
              value={newMed.dosage}
              onChange={(e) => setNewMed({ ...newMed, dosage: e.target.value })}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder={t('patient.medications.frequency')}
              value={newMed.frequency}
              onChange={(e) => setNewMed({ ...newMed, frequency: e.target.value })}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleAddMed}
              disabled={!newMed.name || createMed.isPending}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {t('common.save')}
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 text-gray-500 text-sm rounded-lg hover:bg-gray-100"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Medication List */}
      <h2 className="text-sm font-semibold text-gray-500 mb-3">{t('patient.medications.todaysLog')}</h2>
      <div className="space-y-3">
        {medications && medications.length > 0 ? (
          medications.map((med) => {
            const isLogged = loggedMedIds.has(med.id);
            return (
              <div
                key={med.id}
                className={`bg-white rounded-xl border p-4 ${
                  isLogged ? 'border-green-200' : 'border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{med.name}</h3>
                    <p className="text-xs text-gray-400">
                      {med.dosage && `${med.dosage} - `}{med.frequency}
                    </p>
                  </div>
                  {isLogged ? (
                    <span className="flex items-center gap-1 text-xs text-green-600">
                      <Check className="w-4 h-4" /> {t('patient.medications.taken')}
                    </span>
                  ) : (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleLog(med.id, true)}
                        disabled={logMed.isPending}
                        className="flex items-center gap-1 px-3 py-1.5 bg-green-50 text-green-700 text-xs rounded-lg hover:bg-green-100"
                      >
                        <Check className="w-3.5 h-3.5" /> {t('patient.medications.taken')}
                      </button>
                      <button
                        onClick={() => handleLog(med.id, false)}
                        disabled={logMed.isPending}
                        className="flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-600 text-xs rounded-lg hover:bg-red-100"
                      >
                        <X className="w-3.5 h-3.5" /> {t('patient.medications.missed')}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        ) : (
          <div className="text-center py-8 text-sm text-gray-500">
            {t('common.noResults')}
          </div>
        )}
      </div>
    </div>
  );
}
