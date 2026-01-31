'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  useSymptomDefinitions,
  useTodaySymptoms,
  useLogSymptom,
} from '@/hooks/usePatientData';
import { Activity, Check } from 'lucide-react';
import type { SymptomDefinition } from '@/lib/types/patient';

function SymptomInput({
  definition,
  value,
  onChange,
}: {
  definition: SymptomDefinition;
  value: unknown;
  onChange: (val: unknown) => void;
}) {
  switch (definition.input_type) {
    case 'slider': {
      const config = definition.config as { min?: number; max?: number; step?: number };
      const min = config.min ?? 0;
      const max = config.max ?? 10;
      return (
        <div>
          <input
            type="range"
            min={min}
            max={max}
            step={config.step ?? 1}
            value={(value as number) ?? min}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-full accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>{min}</span>
            <span className="text-lg font-bold text-gray-900">{(value as number) ?? min}</span>
            <span>{max}</span>
          </div>
        </div>
      );
    }
    case 'boolean':
      return (
        <div className="flex gap-3">
          {[true, false].map((opt) => (
            <button
              key={String(opt)}
              onClick={() => onChange(opt)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium border transition ${
                value === opt
                  ? opt
                    ? 'bg-green-50 border-green-300 text-green-700'
                    : 'bg-red-50 border-red-300 text-red-700'
                  : 'border-gray-200 text-gray-500 hover:bg-gray-50'
              }`}
            >
              {opt ? 'Evet' : 'Hayir'}
            </button>
          ))}
        </div>
      );
    case 'choice': {
      const config = definition.config as { choices_tr?: string[]; choices_en?: string[] };
      const choices = config.choices_tr ?? config.choices_en ?? [];
      return (
        <div className="flex flex-wrap gap-2">
          {choices.map((choice) => (
            <button
              key={choice}
              onClick={() => onChange(choice)}
              className={`px-3 py-1.5 rounded-lg text-sm border transition ${
                value === choice
                  ? 'bg-blue-50 border-blue-300 text-blue-700'
                  : 'border-gray-200 text-gray-500 hover:bg-gray-50'
              }`}
            >
              {choice}
            </button>
          ))}
        </div>
      );
    }
    case 'number': {
      const config = definition.config as { min?: number; max?: number };
      return (
        <input
          type="number"
          min={config.min}
          max={config.max}
          value={(value as number) ?? ''}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      );
    }
    case 'text':
      return (
        <textarea
          value={(value as string) ?? ''}
          onChange={(e) => onChange(e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      );
    default:
      return null;
  }
}

export default function SymptomsPage() {
  const t = useTranslations();
  const { data: definitions, isLoading } = useSymptomDefinitions();
  const { data: todayEntries } = useTodaySymptoms();
  const logMutation = useLogSymptom();
  const [values, setValues] = useState<Record<string, unknown>>({});
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());

  const today = new Date().toISOString().split('T')[0];

  const alreadyLogged = new Set(
    todayEntries?.map((e) => e.symptom_definition) ?? []
  );

  const handleSave = (defId: string) => {
    const value = values[defId];
    if (value === undefined) return;
    logMutation.mutate(
      {
        symptom_definition: defId,
        recorded_date: today,
        value,
      },
      {
        onSuccess: () => {
          setSavedIds((prev) => new Set([...prev, defId]));
        },
      }
    );
  };

  if (isLoading) {
    return <div className="text-center py-12 text-gray-500">{t('common.loading')}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">{t('patient.symptoms.title')}</h1>
      </div>

      <p className="text-sm text-gray-500 mb-6">
        {t('patient.symptoms.todaysEntries')} ({todayEntries?.length ?? 0}/{definitions?.length ?? 0})
      </p>

      <div className="space-y-4">
        {definitions?.map((def) => {
          const isAlreadyLogged = alreadyLogged.has(def.id) || savedIds.has(def.id);
          return (
            <div
              key={def.id}
              className={`bg-white rounded-xl border p-5 ${
                isAlreadyLogged ? 'border-green-200 bg-green-50/20' : 'border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium text-gray-900">{def.label}</label>
                {isAlreadyLogged && (
                  <span className="flex items-center gap-1 text-xs text-green-600">
                    <Check className="w-3.5 h-3.5" /> {t('common.completed')}
                  </span>
                )}
              </div>

              {!isAlreadyLogged && (
                <>
                  <SymptomInput
                    definition={def}
                    value={values[def.id]}
                    onChange={(val) => setValues((prev) => ({ ...prev, [def.id]: val }))}
                  />
                  <button
                    onClick={() => handleSave(def.id)}
                    disabled={values[def.id] === undefined || logMutation.isPending}
                    className="mt-3 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {t('common.save')}
                  </button>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
