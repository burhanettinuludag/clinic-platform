import { Metadata } from 'next';

export const metadata: Metadata = { title: 'Kullanim Kosullari | Norosera', description: 'Norosera platformu kullanim kosullari.' };

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Kullanim Kosullari</h1>
      <div className="prose dark:prose-invert max-w-none space-y-6 text-gray-600 dark:text-gray-300">
        <p className="text-sm text-gray-400">Son guncelleme: Subat 2026</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">1. Hizmet Tanimi</h2>
        <p>Norosera, norolojik hastaliklarin takibi ve yonetimi icin gelistirilmis dijital saglik platformudur. Platform tibbi tani, tedavi veya recete yerine gecmez.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">2. Kullanici Sorumlulukari</h2>
        <p>Kullanicilar dogru bilgi saglama, hesap guvenligini koruma ve platformu yasal amaclarla kullanma yukumlulugundedir. 18 yasindan kucuklerin platformu kullanmasi ebeveyn onayina tabidir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">3. Tibbi Sorumluluk Reddi</h2>
        <p>Platform tarafindan sunulan bilgiler genel bilgilendirme amaclidir. Herhangi bir saglik karari almadan once mutlaka bir saglik profesyoneline danisiniz. Norosera, platform uzerinden alinan kararlarin sonuclari icin sorumluluk kabul etmez.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">4. Fikri Mulkiyet</h2>
        <p>Platform uzerindeki tum icerik, tasarim, yazilim ve markalar UlgarTech'e aittir. Izinsiz kopyalama, dagilma veya degistirme yasaktir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">5. Hesap Sonlandirma</h2>
        <p>Norosera, kullanim kosullarini ihlal eden hesaplari onceden bildirimde bulunarak veya bulunmaksizin askiya alabilir veya sonlandirabilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">6. Degisiklikler</h2>
        <p>Bu kosullar onceden bildirimde bulunularak degistirilebilir. Guncel kosullari duzenli olarak kontrol etmeniz onerilir.</p>
      </div>
    </div>
  );
}
