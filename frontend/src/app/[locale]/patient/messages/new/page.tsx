'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from '@/i18n/navigation';
import { UserPlus, Search, ArrowLeft, Send } from 'lucide-react';
import DoctorCard from '@/components/chat/DoctorCard';
import { useDoctorsList, useStartConversation } from '@/hooks/useChatData';
import type { DoctorForChat } from '@/lib/types/chat';
import { Link } from '@/i18n/navigation';

export default function NewMessagePage() {
  const t = useTranslations('messages');
  const router = useRouter();

  const [search, setSearch] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState<DoctorForChat | null>(null);
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');

  const { data: doctors = [], isLoading } = useDoctorsList(
    search ? { search } : undefined
  );
  const startConversation = useStartConversation();

  const handleSend = async () => {
    if (!selectedDoctor || !message.trim()) return;
    try {
      await startConversation.mutateAsync({
        doctor_id: selectedDoctor.id,
        subject,
        initial_message: message.trim(),
      });
      router.push('/patient/messages');
    } catch { /* handled */ }
  };

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Link
          href="/patient/messages"
          className="p-2 rounded-lg hover:bg-gray-100 transition text-gray-500"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center">
            <UserPlus className="w-5 h-5 text-teal-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {(() => { try { return t('newMessage'); } catch { return 'Yeni Mesaj'; } })()}
            </h1>
            <p className="text-sm text-gray-500">Doktor secin ve mesajinizi gonderin</p>
          </div>
        </div>
      </div>

      {/* Step 1: Select Doctor */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
        <h2 className="font-semibold text-gray-800 mb-3">
          1. Doktor Secin
        </h2>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Doktor adi ile arayın..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
        </div>

        {/* Doctor List */}
        <div className="space-y-2 max-h-[300px] overflow-y-auto">
          {isLoading ? (
            <div className="text-center text-gray-400 text-sm py-4">Doktorlar yukleniyor...</div>
          ) : doctors.length === 0 ? (
            <div className="text-center text-gray-400 text-sm py-4">
              {search ? 'Sonuc bulunamadi' : 'Musait doktor bulunmuyor'}
            </div>
          ) : (
            doctors.map((doctor: DoctorForChat) => (
              <DoctorCard
                key={doctor.id}
                doctor={doctor}
                onSelect={setSelectedDoctor}
                selected={selectedDoctor?.id === doctor.id}
              />
            ))
          )}
        </div>
      </div>

      {/* Step 2: Message */}
      {selectedDoctor && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-800 mb-3">
            2. Mesajinizi Yazin
          </h2>

          <div className="mb-3 p-3 bg-teal-50 rounded-lg text-sm text-teal-800">
            Secilen doktor: <strong>{selectedDoctor.full_name}</strong>
            {selectedDoctor.specialty && ` - ${selectedDoctor.specialty}`}
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Konu (Opsiyonel)
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Ornegin: Ilac yan etkileri hakkinda"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mesajiniz *
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Doktorunuza iletmek istediginiz mesaji yazin..."
                rows={4}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
              />
            </div>

            <button
              onClick={handleSend}
              disabled={!message.trim() || startConversation.isPending}
              className="flex items-center gap-2 px-6 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              {startConversation.isPending ? 'Gonderiliyor...' : 'Mesaj Gonder'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
