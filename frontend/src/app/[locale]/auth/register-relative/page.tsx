'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useRouter } from '@/i18n/navigation';
import api from '@/lib/api';
import Cookies from 'js-cookie';
import {
  Shield,
  Eye,
  CheckCircle,
  AlertTriangle,
  Clock,
  UserPlus,
  Loader2,
} from 'lucide-react';

interface InvitationInfo {
  status: 'valid';
  invited_email: string;
  invited_name: string;
  patient_first_name: string;
  relationship_type: string;
  invited_by_name: string;
  expires_at: string;
}

const RELATIONSHIP_LABELS: Record<string, string> = {
  child: 'Çocuk',
  spouse: 'Eş',
  sibling: 'Kardeş',
  grandchild: 'Torun',
  other: 'Yakın',
};

export default function RegisterRelativePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get('token');

  const [inviteInfo, setInviteInfo] = useState<InvitationInfo | null>(null);
  const [verifying, setVerifying] = useState(true);
  const [verifyError, setVerifyError] = useState('');

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [phone, setPhone] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [success, setSuccess] = useState(false);

  // Verify token on mount
  useEffect(() => {
    if (!token) {
      setVerifyError('Davet tokeni bulunamadı. Lütfen davet linkini kontrol edin.');
      setVerifying(false);
      return;
    }

    api
      .get(`/auth/relative/invite/verify/${token}/`)
      .then((res) => {
        setInviteInfo(res.data);
        // Pre-fill name if available
        if (res.data.invited_name) {
          const parts = res.data.invited_name.split(' ');
          if (parts.length >= 2) {
            setFirstName(parts[0]);
            setLastName(parts.slice(1).join(' '));
          } else {
            setFirstName(res.data.invited_name);
          }
        }
      })
      .catch((err) => {
        const msg = err?.response?.data?.error || 'Davet doğrulanamadı.';
        setVerifyError(msg);
      })
      .finally(() => setVerifying(false));
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');

    if (password !== passwordConfirm) {
      setSubmitError('Şifreler eşleşmiyor.');
      return;
    }

    if (password.length < 8) {
      setSubmitError('Şifre en az 8 karakter olmalıdır.');
      return;
    }

    setSubmitting(true);

    try {
      const { data } = await api.post('/auth/relative/register/', {
        token,
        first_name: firstName,
        last_name: lastName,
        password,
        password_confirm: passwordConfirm,
        phone,
      });

      // Set tokens
      Cookies.set('access_token', data.tokens.access);
      Cookies.set('refresh_token', data.tokens.refresh);
      Cookies.set('user_role', data.user.role);

      setSuccess(true);

      // Redirect to relative dashboard after short delay
      setTimeout(() => {
        router.push('/relative/dashboard');
      }, 2000);
    } catch (err: any) {
      const errors = err?.response?.data;
      if (errors) {
        const msg =
          errors.token?.[0] ||
          errors.password?.[0] ||
          errors.password_confirm?.[0] ||
          errors.error ||
          errors.detail ||
          JSON.stringify(errors);
        setSubmitError(msg);
      } else {
        setSubmitError('Kayıt sırasında bir hata oluştu.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (verifying) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 text-teal-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Davet doğrulanıyor...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (verifyError) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-red-50 border border-red-200 rounded-xl p-8">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Davet Geçersiz</h2>
            <p className="text-gray-600 mb-4">{verifyError}</p>
            <p className="text-sm text-gray-500">
              Lütfen doktorunuzdan veya bakıcınızdan yeni bir davet linki isteyiniz.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-green-50 border border-green-200 rounded-xl p-8">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Kayıt Başarılı!</h2>
            <p className="text-gray-600 mb-4">
              Hesabınız oluşturuldu. Hasta takip panelinize yönlendiriliyorsunuz...
            </p>
            <Loader2 className="h-5 w-5 text-green-500 animate-spin mx-auto" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4">
      <div className="max-w-lg w-full space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-100 rounded-full mb-4">
            <UserPlus className="h-8 w-8 text-teal-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Hasta Yakını Kaydı</h2>
          <p className="text-gray-500 mt-2">
            Hastanızın durumunu uzaktan güvenle takip edin
          </p>
        </div>

        {/* Invitation Info Card */}
        {inviteInfo && (
          <div className="bg-teal-50 border border-teal-200 rounded-xl p-5">
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-teal-600" />
                <span className="text-teal-800 font-medium">Güvenli Davet</span>
              </div>
              <p className="text-teal-700">
                <strong>{inviteInfo.invited_by_name}</strong> tarafından{' '}
                <strong>{inviteInfo.patient_first_name}</strong> hastasının{' '}
                {RELATIONSHIP_LABELS[inviteInfo.relationship_type] || 'yakını'} olarak
                davet edildiniz.
              </p>
              <div className="flex items-center gap-2 text-teal-600">
                <Eye className="h-4 w-4" />
                <span className="text-xs">Salt okunur erişim - yalnızca izleme verileri</span>
              </div>
              <div className="flex items-center gap-2 text-teal-600">
                <Clock className="h-4 w-4" />
                <span className="text-xs">
                  Davet süresi:{' '}
                  {new Date(inviteInfo.expires_at).toLocaleDateString('tr-TR', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5">
          {submitError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {submitError}
            </div>
          )}

          {/* Email display (readonly) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">E-posta</label>
            <input
              type="email"
              disabled
              value={inviteInfo?.invited_email || ''}
              className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed"
            />
            <p className="text-xs text-gray-400 mt-1">E-posta adresi davet ile belirlenmiştir</p>
          </div>

          {/* Name fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ad *</label>
              <input
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="Adınız"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Soyad *</label>
              <input
                type="text"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Soyadınız"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="05XX XXX XX XX (opsiyonel)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>

          {/* Password fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Şifre *</label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="En az 8 karakter"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Şifre Tekrar *</label>
              <input
                type="password"
                required
                minLength={8}
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                placeholder="Şifrenizi tekrar girin"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting || !firstName || !lastName || !password || !passwordConfirm}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Kayıt yapılıyor...
              </>
            ) : (
              <>
                <UserPlus className="h-4 w-4" />
                Kayıt Ol ve Panele Git
              </>
            )}
          </button>
        </form>

        {/* Security Notice */}
        <div className="text-center text-xs text-gray-400 space-y-1">
          <p>Bu sayfa yalnızca davet linki ile erişilebilir.</p>
          <p>Verileriniz KVKK kapsamında korunmaktadır.</p>
        </div>
      </div>
    </div>
  );
}
