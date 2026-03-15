'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from '@/i18n/navigation';

export default function LoginPage() {
  const t = useTranslations();
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(email, password);
      // Role-based redirect
      const roleRedirects: Record<string, string> = {
        doctor: '/doctor/dashboard',
        admin: '/doctor/dashboard',
        caregiver: '/caregiver/dashboard',
        relative: '/relative/dashboard',
        patient: '/patient/dashboard',
      };
      router.push(roleRedirects[user.role] || '/patient/dashboard');
    } catch (err: any) {
      const errorData = err?.response?.data;
      if (errorData?.approval_status === 'pending_approval') {
        setError(t('auth.pendingDoctorLogin'));
      } else if (errorData?.approval_status === 'rejected') {
        setError(t('auth.rejectedDoctorLogin'));
      } else if (errorData?.non_field_errors?.[0]) {
        setError(errorData.non_field_errors[0]);
      } else {
        setError(t('auth.invalidCredentials'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            {t('auth.loginTitle')}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.email')}
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('auth.emailPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.password')}
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t('auth.passwordPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? t('common.loading') : t('common.login')}
          </button>

          <p className="text-center text-sm text-gray-500">
            {t('auth.noAccount')}{' '}
            <Link href="/auth/register" className="text-blue-600 hover:underline">
              {t('common.register')}
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
