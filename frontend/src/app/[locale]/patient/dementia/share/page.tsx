'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import {
  useReportRecipients,
  useCreateReportRecipient,
  useDeleteReportRecipient,
  useShareReport,
  useShareHistory,
} from '@/hooks/useDementiaData';
import {
  ArrowLeft,
  Plus,
  Send,
  Mail,
  MessageCircle,
  UserPlus,
  History,
  CheckCircle,
  XCircle,
  Trash2,
  Shield,
} from 'lucide-react';

type Tab = 'recipients' | 'share' | 'history';

const RELATIONSHIP_OPTIONS = [
  { value: 'spouse', label_tr: 'Es', label_en: 'Spouse' },
  { value: 'child', label_tr: 'Cocuk', label_en: 'Child' },
  { value: 'sibling', label_tr: 'Kardes', label_en: 'Sibling' },
  { value: 'parent', label_tr: 'Ebeveyn', label_en: 'Parent' },
  { value: 'doctor', label_tr: 'Doktor', label_en: 'Doctor' },
  { value: 'other', label_tr: 'Diger', label_en: 'Other' },
];

const NOTIFY_VIA_OPTIONS = [
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'telegram', label: 'Telegram', icon: MessageCircle },
  { value: 'both', label: 'Her ikisi', icon: Send },
];

export default function SharePage() {
  const t = useTranslations('share');
  const [activeTab, setActiveTab] = useState<Tab>('recipients');
  const [showAddForm, setShowAddForm] = useState(false);
  const [shareRecipientId, setShareRecipientId] = useState('');
  const [shareStartDate, setShareStartDate] = useState('');
  const [shareEndDate, setShareEndDate] = useState('');
  const [shareResult, setShareResult] = useState<{ success: boolean; message: string } | null>(null);

  // Form state
  const [formName, setFormName] = useState('');
  const [formEmail, setFormEmail] = useState('');
  const [formPhone, setFormPhone] = useState('');
  const [formRelationship, setFormRelationship] = useState('other');
  const [formNotifyVia, setFormNotifyVia] = useState('email');
  const [formTelegramChatId, setFormTelegramChatId] = useState('');
  const [formConsent, setFormConsent] = useState(false);

  const { data: recipients, isLoading: loadingRecipients } = useReportRecipients();
  const { data: shareHistory, isLoading: loadingHistory } = useShareHistory();
  const createRecipient = useCreateReportRecipient();
  const deleteRecipient = useDeleteReportRecipient();
  const shareReport = useShareReport();

  const activeRecipients = recipients?.filter((r) => r.is_active) || [];

  const resetForm = () => {
    setFormName('');
    setFormEmail('');
    setFormPhone('');
    setFormRelationship('other');
    setFormNotifyVia('email');
    setFormTelegramChatId('');
    setFormConsent(false);
    setShowAddForm(false);
  };

  const handleAddRecipient = () => {
    if (!formName || !formConsent) return;
    if (formNotifyVia !== 'telegram' && !formEmail) return;

    createRecipient.mutate(
      {
        name: formName,
        email: formEmail,
        phone: formPhone,
        relationship: formRelationship,
        notify_via: formNotifyVia,
        telegram_chat_id: formTelegramChatId,
        kvkk_consent: formConsent,
      },
      {
        onSuccess: () => resetForm(),
      }
    );
  };

  const handleShare = () => {
    if (!shareRecipientId || !shareStartDate || !shareEndDate) return;

    setShareResult(null);
    shareReport.mutate(
      {
        recipient_id: shareRecipientId,
        start_date: shareStartDate,
        end_date: shareEndDate,
      },
      {
        onSuccess: (data) => {
          const results = data.results || [];
          const allSuccess = results.every((r: { success: boolean }) => r.success);
          setShareResult({
            success: allSuccess,
            message: allSuccess
              ? 'Rapor basariyla gonderildi!'
              : 'Rapor gonderiminde sorun olustu.',
          });
        },
        onError: () => {
          setShareResult({
            success: false,
            message: 'Rapor gÃ¶nderilemedi. LÃ¼tfen tekrar deneyin.',
          });
        },
      }
    );
  };

  // Set default dates (last 30 days)
  const setDefaultDates = () => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    setShareStartDate(start.toISOString().split('T')[0]);
    setShareEndDate(end.toISOString().split('T')[0]);
  };

  if (!shareStartDate && !shareEndDate) {
    setDefaultDates();
  }

  const tabs = [
    { id: 'recipients' as Tab, label: t('recipientsTab'), icon: UserPlus },
    { id: 'share' as Tab, label: t('shareTab'), icon: Send },
    { id: 'history' as Tab, label: t('historyTab'), icon: History },
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/patient/dementia"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('title')}</h1>
          <p className="text-sm text-gray-500">{t('subtitle')}</p>
        </div>
      </div>

      {/* KVKK Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex items-start gap-3">
        <Shield className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-blue-800">{t('kvkkNotice')}</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition ${
              activeTab === tab.id
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* RECIPIENTS TAB */}
      {activeTab === 'recipients' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">{t('recipientsList')}</h2>
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm"
            >
              <Plus className="w-4 h-4" />
              {t('addRecipient')}
            </button>
          </div>

          {/* Add Recipient Form */}
          {showAddForm && (
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
              <h3 className="text-md font-semibold text-gray-900 mb-4">{t('newRecipient')}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('recipientName')}</label>
                  <input
                    type="text"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                    placeholder={t('namePlaceholder')}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={formEmail}
                    onChange={(e) => setFormEmail(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                    placeholder="ornek@email.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('relationship')}</label>
                  <select
                    value={formRelationship}
                    onChange={(e) => setFormRelationship(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                  >
                    {RELATIONSHIP_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label_tr}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('notifyVia')}</label>
                  <select
                    value={formNotifyVia}
                    onChange={(e) => setFormNotifyVia(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                  >
                    {NOTIFY_VIA_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                {(formNotifyVia === 'telegram' || formNotifyVia === 'both') && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Telegram Chat ID</label>
                    <input
                      type="text"
                      value={formTelegramChatId}
                      onChange={(e) => setFormTelegramChatId(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                      placeholder={t('telegramPlaceholder')}
                    />
                    <p className="text-xs text-gray-400 mt-1">{t('telegramHelp')}</p>
                  </div>
                )}
              </div>

              {/* KVKK Consent */}
              <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={formConsent}
                    onChange={(e) => setFormConsent(e.target.checked)}
                    className="mt-1 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm text-amber-800">
                    {t('consentText')}
                  </span>
                </label>
              </div>

              <div className="flex justify-end gap-3 mt-4">
                <button
                  onClick={resetForm}
                  className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition"
                >
                  {t('cancel')}
                </button>
                <button
                  onClick={handleAddRecipient}
                  disabled={!formName || !formConsent || createRecipient.isPending}
                  className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
                >
                  {createRecipient.isPending ? t('saving') : t('save')}
                </button>
              </div>
            </div>
          )}

          {/* Recipients List */}
          {loadingRecipients ? (
            <div className="text-center py-8 text-gray-500">{t('loading')}</div>
          ) : activeRecipients.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
              <UserPlus className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">{t('noRecipients')}</p>
              <p className="text-sm text-gray-400 mt-1">{t('noRecipientsDesc')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {activeRecipients.map((recipient) => (
                <div
                  key={recipient.id}
                  className="bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                      <span className="text-sm font-bold text-indigo-600">
                        {recipient.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{recipient.name}</h3>
                      <div className="flex items-center gap-3 text-sm text-gray-500">
                        <span>{recipient.relationship_display}</span>
                        <span className="text-gray-300">|</span>
                        <span className="flex items-center gap-1">
                          {recipient.notify_via === 'email' && <Mail className="w-3.5 h-3.5" />}
                          {recipient.notify_via === 'telegram' && <MessageCircle className="w-3.5 h-3.5" />}
                          {recipient.notify_via === 'both' && <Send className="w-3.5 h-3.5" />}
                          {recipient.email || recipient.telegram_chat_id}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteRecipient.mutate(recipient.id)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition"
                    title={t('deactivate')}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* SHARE TAB */}
      {activeTab === 'share' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('shareReport')}</h2>

          {activeRecipients.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-3">{t('noRecipientsForShare')}</p>
              <button
                onClick={() => { setActiveTab('recipients'); setShowAddForm(true); }}
                className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
              >
                {t('addRecipientFirst')}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('selectRecipient')}</label>
                <select
                  value={shareRecipientId}
                  onChange={(e) => setShareRecipientId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                >
                  <option value="">{t('chooseRecipient')}</option>
                  {activeRecipients.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name} ({r.relationship_display} - {r.notify_via_display})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('startDate')}</label>
                  <input
                    type="date"
                    value={shareStartDate}
                    onChange={(e) => setShareStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('endDate')}</label>
                  <input
                    type="date"
                    value={shareEndDate}
                    onChange={(e) => setShareEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-sm"
                  />
                </div>
              </div>

              {shareResult && (
                <div
                  className={`p-3 rounded-lg flex items-center gap-2 text-sm ${
                    shareResult.success
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}
                >
                  {shareResult.success ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <XCircle className="w-4 h-4" />
                  )}
                  {shareResult.message}
                </div>
              )}

              <button
                onClick={handleShare}
                disabled={!shareRecipientId || !shareStartDate || !shareEndDate || shareReport.isPending}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {shareReport.isPending ? t('sending') : t('sendReport')}
              </button>
            </div>
          )}
        </div>
      )}

      {/* HISTORY TAB */}
      {activeTab === 'history' && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('shareHistory')}</h2>
          {loadingHistory ? (
            <div className="text-center py-8 text-gray-500">{t('loading')}</div>
          ) : !shareHistory || shareHistory.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
              <History className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">{t('noHistory')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {shareHistory.map((record) => (
                <div
                  key={record.id}
                  className="bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      record.success ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {record.success ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-600" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 text-sm">
                        {record.recipient_name}
                        <span className="text-gray-400 font-normal ml-2">
                          ({record.share_type === 'email' ? 'Email' : 'Telegram'})
                        </span>
                      </h3>
                      <p className="text-xs text-gray-500">
                        {record.report_period_start} - {record.report_period_end}
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(record.shared_at).toLocaleDateString('tr-TR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
