'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTodayAssessment, useCreateAssessment, useUpdateAssessment } from '@/hooks/useDementiaData';
import { ArrowLeft, Save, CheckCircle, AlertCircle, Moon, Heart, Brain, User } from 'lucide-react';
import Link from 'next/link';

interface AssessmentFormData {
  mood_score: number | null;
  confusion_level: number | null;
  agitation_level: number | null;
  anxiety_level: number | null;
  sleep_quality: number | null;
  sleep_hours: number | null;
  night_wandering: boolean | null;
  eating_independence: number | null;
  dressing_independence: number | null;
  hygiene_independence: number | null;
  mobility_independence: number | null;
  verbal_communication: number | null;
  recognition_family: boolean | null;
  fall_occurred: boolean;
  wandering_occurred: boolean;
  medication_missed: boolean;
  notes: string;
  concerns: string;
}

const INITIAL_FORM: AssessmentFormData = {
  mood_score: null,
  confusion_level: null,
  agitation_level: null,
  anxiety_level: null,
  sleep_quality: null,
  sleep_hours: null,
  night_wandering: null,
  eating_independence: null,
  dressing_independence: null,
  hygiene_independence: null,
  mobility_independence: null,
  verbal_communication: null,
  recognition_family: null,
  fall_occurred: false,
  wandering_occurred: false,
  medication_missed: false,
  notes: '',
  concerns: '',
};

export default function AssessmentPage() {
  const router = useRouter();
  const { data: todayAssessment, isLoading } = useTodayAssessment();
  const createAssessment = useCreateAssessment();
  const updateAssessment = useUpdateAssessment();

  const [formData, setFormData] = useState<AssessmentFormData>(() => {
    if (todayAssessment) {
      return {
        mood_score: todayAssessment.mood_score,
        confusion_level: todayAssessment.confusion_level,
        agitation_level: todayAssessment.agitation_level,
        anxiety_level: todayAssessment.anxiety_level,
        sleep_quality: todayAssessment.sleep_quality,
        sleep_hours: todayAssessment.sleep_hours,
        night_wandering: todayAssessment.night_wandering,
        eating_independence: todayAssessment.eating_independence,
        dressing_independence: todayAssessment.dressing_independence,
        hygiene_independence: todayAssessment.hygiene_independence,
        mobility_independence: todayAssessment.mobility_independence,
        verbal_communication: todayAssessment.verbal_communication,
        recognition_family: todayAssessment.recognition_family,
        fall_occurred: todayAssessment.fall_occurred,
        wandering_occurred: todayAssessment.wandering_occurred,
        medication_missed: todayAssessment.medication_missed,
        notes: todayAssessment.notes || '',
        concerns: todayAssessment.concerns || '',
      };
    }
    return INITIAL_FORM;
  });

  const [currentSection, setCurrentSection] = useState(0);
  const [saved, setSaved] = useState(false);

  const sections = [
    { id: 'mood', title: 'Ruh Hali', icon: Heart },
    { id: 'sleep', title: 'Uyku', icon: Moon },
    { id: 'cognition', title: 'Biliş', icon: Brain },
    { id: 'daily', title: 'Günlük Aktiviteler', icon: User },
    { id: 'safety', title: 'Güvenlik', icon: AlertCircle },
  ];

  const updateField = (field: keyof AssessmentFormData, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSubmit = async () => {
    try {
      if (todayAssessment?.id) {
        await updateAssessment.mutateAsync({
          id: todayAssessment.id,
          ...formData,
        });
      } else {
        await createAssessment.mutateAsync(formData);
      }
      setSaved(true);
      setTimeout(() => {
        router.push('/tr/patient/dementia?tab=progress');
      }, 1500);
    } catch (error) {
      console.error('Failed to save assessment:', error);
    }
  };

  const ScaleInput = ({
    label,
    value,
    onChange,
    min = 1,
    max = 5,
    lowLabel,
    highLabel,
  }: {
    label: string;
    value: number | null;
    onChange: (val: number) => void;
    min?: number;
    max?: number;
    lowLabel?: string;
    highLabel?: string;
  }) => (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 mb-3">{label}</label>
      <div className="flex gap-2 justify-center">
        {Array.from({ length: max - min + 1 }, (_, i) => min + i).map((num) => (
          <button
            key={num}
            type="button"
            onClick={() => onChange(num)}
            className={`w-12 h-12 rounded-full font-medium transition-all ${
              value === num
                ? 'bg-indigo-600 text-white scale-110'
                : 'bg-gray-100 text-gray-600 hover:bg-indigo-100'
            }`}
          >
            {num}
          </button>
        ))}
      </div>
      {(lowLabel || highLabel) && (
        <div className="flex justify-between text-xs text-gray-500 mt-2 px-4">
          <span>{lowLabel}</span>
          <span>{highLabel}</span>
        </div>
      )}
    </div>
  );

  const BooleanInput = ({
    label,
    value,
    onChange,
    yesLabel = 'Evet',
    noLabel = 'Hayır',
  }: {
    label: string;
    value: boolean | null;
    onChange: (val: boolean) => void;
    yesLabel?: string;
    noLabel?: string;
  }) => (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 mb-3">{label}</label>
      <div className="flex gap-3 justify-center">
        <button
          type="button"
          onClick={() => onChange(true)}
          className={`px-6 py-2 rounded-lg font-medium transition-all ${
            value === true
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-indigo-100'
          }`}
        >
          {yesLabel}
        </button>
        <button
          type="button"
          onClick={() => onChange(false)}
          className={`px-6 py-2 rounded-lg font-medium transition-all ${
            value === false
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-indigo-100'
          }`}
        >
          {noLabel}
        </button>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Yükleniyor...</div>
      </div>
    );
  }

  if (saved) {
    return (
      <div className="max-w-lg mx-auto text-center py-12">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Değerlendirme Kaydedildi!</h2>
        <p className="text-gray-600">Günlük değerlendirmeniz başarıyla kaydedildi.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/tr/patient/dementia"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Günlük Değerlendirme</h1>
          <p className="text-sm text-gray-500">
            {new Date().toLocaleDateString('tr-TR', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {sections.map((section, index) => {
          const Icon = section.icon;
          return (
            <button
              key={section.id}
              onClick={() => setCurrentSection(index)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                currentSection === index
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              {section.title}
            </button>
          );
        })}
      </div>

      {/* Form Sections */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {/* Mood Section */}
        {currentSection === 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Ruh Hali Değerlendirmesi</h3>
            <ScaleInput
              label="Bugünkü genel ruh hali nasıldı?"
              value={formData.mood_score}
              onChange={(val) => updateField('mood_score', val)}
              lowLabel="Çok kötü"
              highLabel="Çok iyi"
            />
            <ScaleInput
              label="Kaygı düzeyi nasıldı?"
              value={formData.anxiety_level}
              onChange={(val) => updateField('anxiety_level', val)}
              lowLabel="Hiç kaygı yok"
              highLabel="Çok kaygılı"
            />
            <ScaleInput
              label="Ajitasyon/huzursuzluk düzeyi nasıldı?"
              value={formData.agitation_level}
              onChange={(val) => updateField('agitation_level', val)}
              lowLabel="Hiç yok"
              highLabel="Çok yoğun"
            />
          </div>
        )}

        {/* Sleep Section */}
        {currentSection === 1 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Uyku Değerlendirmesi</h3>
            <ScaleInput
              label="Uyku kalitesi nasıldı?"
              value={formData.sleep_quality}
              onChange={(val) => updateField('sleep_quality', val)}
              lowLabel="Çok kötü"
              highLabel="Çok iyi"
            />
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Yaklaşık kaç saat uyudu?
              </label>
              <div className="flex gap-2 flex-wrap justify-center">
                {[4, 5, 6, 7, 8, 9, 10, 11, 12].map((hours) => (
                  <button
                    key={hours}
                    type="button"
                    onClick={() => updateField('sleep_hours', hours)}
                    className={`px-4 py-2 rounded-lg font-medium transition-all ${
                      formData.sleep_hours === hours
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-indigo-100'
                    }`}
                  >
                    {hours}s
                  </button>
                ))}
              </div>
            </div>
            <BooleanInput
              label="Gece dolaşması oldu mu?"
              value={formData.night_wandering}
              onChange={(val) => updateField('night_wandering', val)}
            />
          </div>
        )}

        {/* Cognition Section */}
        {currentSection === 2 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Bilişsel Değerlendirme</h3>
            <ScaleInput
              label="Konfüzyon (karışıklık) düzeyi nasıldı?"
              value={formData.confusion_level}
              onChange={(val) => updateField('confusion_level', val)}
              lowLabel="Hiç yok"
              highLabel="Çok yoğun"
            />
            <ScaleInput
              label="Sözel iletişim becerisi nasıldı?"
              value={formData.verbal_communication}
              onChange={(val) => updateField('verbal_communication', val)}
              lowLabel="Çok zor"
              highLabel="Normal"
            />
            <BooleanInput
              label="Aile bireylerini tanıdı mı?"
              value={formData.recognition_family}
              onChange={(val) => updateField('recognition_family', val)}
            />
          </div>
        )}

        {/* Daily Activities Section */}
        {currentSection === 3 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Günlük Aktiviteler</h3>
            <p className="text-sm text-gray-500 mb-6">
              1 = Tamamen yardıma ihtiyaç duyuyor, 5 = Tamamen bağımsız
            </p>
            <ScaleInput
              label="Yemek yeme"
              value={formData.eating_independence}
              onChange={(val) => updateField('eating_independence', val)}
              lowLabel="Yardımla"
              highLabel="Bağımsız"
            />
            <ScaleInput
              label="Giyinme"
              value={formData.dressing_independence}
              onChange={(val) => updateField('dressing_independence', val)}
              lowLabel="Yardımla"
              highLabel="Bağımsız"
            />
            <ScaleInput
              label="Kişisel hijyen"
              value={formData.hygiene_independence}
              onChange={(val) => updateField('hygiene_independence', val)}
              lowLabel="Yardımla"
              highLabel="Bağımsız"
            />
            <ScaleInput
              label="Hareket/mobilite"
              value={formData.mobility_independence}
              onChange={(val) => updateField('mobility_independence', val)}
              lowLabel="Yardımla"
              highLabel="Bağımsız"
            />
          </div>
        )}

        {/* Safety Section */}
        {currentSection === 4 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Güvenlik Değerlendirmesi</h3>
            <BooleanInput
              label="Bugün düşme oldu mu?"
              value={formData.fall_occurred}
              onChange={(val) => updateField('fall_occurred', val)}
            />
            <BooleanInput
              label="Bugün kaybolma/dolaşma olayı oldu mu?"
              value={formData.wandering_occurred}
              onChange={(val) => updateField('wandering_occurred', val)}
            />
            <BooleanInput
              label="Bugün ilaç atlama oldu mu?"
              value={formData.medication_missed}
              onChange={(val) => updateField('medication_missed', val)}
            />
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notlar (opsiyonel)
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => updateField('notes', e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Günle ilgili notlarınız..."
              />
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Endişeler (opsiyonel)
              </label>
              <textarea
                value={formData.concerns}
                onChange={(e) => updateField('concerns', e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Doktorunuzla paylaşmak istediğiniz endişeler..."
              />
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={() => setCurrentSection((prev) => Math.max(0, prev - 1))}
            disabled={currentSection === 0}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Önceki
          </button>

          {currentSection < sections.length - 1 ? (
            <button
              type="button"
              onClick={() => setCurrentSection((prev) => prev + 1)}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              Sonraki
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={createAssessment.isPending || updateAssessment.isPending}
              className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {createAssessment.isPending || updateAssessment.isPending ? 'Kaydediliyor...' : 'Kaydet'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
