'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from '@/i18n/navigation';
import { CheckCircle, ArrowLeft } from 'lucide-react';

const SPECIALTY_OPTIONS = [
  { value: 'neurology', label_tr: 'Nöroloji', label_en: 'Neurology' },
  { value: 'ftr', label_tr: 'Fiziksel Tip ve Rehabilitasyon', label_en: 'Physical Medicine & Rehabilitation' },
  { value: 'neurosurgery', label_tr: 'Beyin ve Sinir Cerrahisi', label_en: 'Neurosurgery' },
  { value: 'physiology', label_tr: 'Fizyoloji', label_en: 'Physiology' },
  { value: 'geriatrics', label_tr: 'Geriatri', label_en: 'Geriatrics' },
  { value: 'psychiatry', label_tr: 'Psikiyatri', label_en: 'Psychiatry' },
  { value: 'sleep_medicine', label_tr: 'Uyku Bozuklukları', label_en: 'Sleep Medicine' },
  { value: 'clinical_psychology', label_tr: 'Klinik Psikoloji', label_en: 'Clinical Psychology' },
  { value: 'social_work', label_tr: 'Sosyal Hizmet', label_en: 'Social Work' },
];

export default function RegisterPage() {
  const t = useTranslations();
  const { register } = useAuth();
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    role: 'patient',
    phone: '',
    specialty: '',
    license_number: '',
  });
  const [consents, setConsents] = useState({
    kvkk: false,
    health_data: false,
    terms: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPendingScreen, setShowPendingScreen] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!consents.kvkk || !consents.terms) {
      setError(t('auth.consentRequired'));
      return;
    }
    if (formData.role === 'patient' && !consents.health_data) {
      setError(t('auth.healthConsentRequired'));
      return;
    }
    if (formData.password !== formData.password_confirm) {
      setError(t('auth.passwordMismatch'));
      return;
    }

    setLoading(true);
    try {
      const result = await register(formData);

      // Doctor registration: show pending approval screen
      if (result.status === 'pending_approval') {
        setShowPendingScreen(true);
        return;
      }

      // Normal registration: redirect to dashboard
      const dashboardPath =
        formData.role === 'doctor' ? '/doctor/dashboard' : '/patient/dashboard';
      router.push(dashboardPath);
    } catch {
      setError(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  // Pending approval screen for doctors
  if (showPendingScreen) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="mx-auto w-20 h-20 bg-teal-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-10 h-10 text-teal-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            {t('auth.applicationPending')}
          </h2>
          <p className="text-gray-600 leading-relaxed">
            {t('auth.applicationPendingDesc')}
          </p>
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-4 text-sm text-teal-700">
            {t('auth.applicationPendingNote')}
          </div>
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-teal-600 hover:text-teal-700 font-medium"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('auth.backToHome')}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            {t('auth.registerTitle')}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('common.firstName')}
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('common.lastName')}
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.email')}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder={t('auth.emailPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.phone')}
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.registerAs')}
              </label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              >
                <option value="patient">{t('auth.patient')}</option>
                <option value="doctor">{t('auth.doctor')}</option>
              </select>
            </div>

            {/* Doctor-specific fields */}
            {formData.role === 'doctor' && (
              <>
                <div className="bg-teal-50 border border-teal-200 rounded-lg p-3 text-sm text-teal-700">
                  {t('auth.doctorApplicationNote')}
                </div>
                <div>
                  <label htmlFor="specialty" className="block text-sm font-medium text-gray-700 mb-1">
                    {t('auth.specialty')} *
                  </label>
                  <select
                    id="specialty"
                    name="specialty"
                    required
                    value={formData.specialty}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  >
                    <option value="">{t('auth.selectSpecialty')}</option>
                    {SPECIALTY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label_tr}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="license_number" className="block text-sm font-medium text-gray-700 mb-1">
                    {t('auth.licenseNumber')} *
                  </label>
                  <input
                    id="license_number"
                    name="license_number"
                    type="text"
                    required
                    value={formData.license_number}
                    onChange={handleChange}
                    placeholder={t('auth.licenseNumberPlaceholder')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
              </>
            )}

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.password')}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                placeholder={t('auth.passwordPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.confirmPassword')}
              </label>
              <input
                id="password_confirm"
                name="password_confirm"
                type="password"
                required
                value={formData.password_confirm}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* KVKK Consents */}
          <div className="space-y-3 border-t pt-4">
            <label className="flex items-start gap-2">
              <input
                type="checkbox"
                checked={consents.kvkk}
                onChange={(e) =>
                  setConsents((prev) => ({ ...prev, kvkk: e.target.checked }))
                }
                className="mt-1"
              />
              <span className="text-sm text-gray-600">
                {t('auth.kvkkConsent')} *
              </span>
            </label>

            {formData.role === 'patient' && (
              <label className="flex items-start gap-2">
                <input
                  type="checkbox"
                  checked={consents.health_data}
                  onChange={(e) =>
                    setConsents((prev) => ({
                      ...prev,
                      health_data: e.target.checked,
                    }))
                  }
                  className="mt-1"
                />
                <span className="text-sm text-gray-600">
                  {t('auth.healthDataConsent')} *
                </span>
              </label>
            )}

            <label className="flex items-start gap-2">
              <input
                type="checkbox"
                checked={consents.terms}
                onChange={(e) =>
                  setConsents((prev) => ({ ...prev, terms: e.target.checked }))
                }
                className="mt-1"
              />
              <span className="text-sm text-gray-600">
                {t('auth.termsConsent')} *
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:opacity-50 transition-colors"
          >
            {loading
              ? t('common.loading')
              : formData.role === 'doctor'
              ? t('auth.submitApplication')
              : t('common.register')}
          </button>

          <p className="text-center text-sm text-gray-500">
            {t('auth.hasAccount')}{' '}
            <Link href="/auth/login" className="text-teal-600 hover:underline">
              {t('common.login')}
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
