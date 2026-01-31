'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from '@/i18n/navigation';

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
  });
  const [consents, setConsents] = useState({
    kvkk: false,
    health_data: false,
    terms: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!consents.kvkk || !consents.terms) {
      setError('Tum zorunlu onaylari vermelisiniz.');
      return;
    }
    if (formData.role === 'patient' && !consents.health_data) {
      setError('Saglik verisi isleme onayini vermelisiniz.');
      return;
    }
    if (formData.password !== formData.password_confirm) {
      setError('Sifreler eslesmedi.');
      return;
    }

    setLoading(true);
    try {
      await register(formData);
      const dashboardPath =
        formData.role === 'doctor' ? '/doctor/dashboard' : '/patient/dashboard';
      router.push(dashboardPath);
    } catch {
      setError(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

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
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="patient">{t('auth.patient')}</option>
                <option value="doctor">{t('auth.doctor')}</option>
              </select>
            </div>

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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? t('common.loading') : t('common.register')}
          </button>

          <p className="text-center text-sm text-gray-500">
            {t('auth.hasAccount')}{' '}
            <Link href="/auth/login" className="text-blue-600 hover:underline">
              {t('common.login')}
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
