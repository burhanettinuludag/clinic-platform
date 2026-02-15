import { Metadata } from 'next';

export const metadata: Metadata = { title: 'Gizlilik Politikasi | Norosera', description: 'Norosera platformu gizlilik politikasi.' };

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Gizlilik Politikasi</h1>
      <div className="prose dark:prose-invert max-w-none space-y-6 text-gray-600 dark:text-gray-300">
        <p className="text-sm text-gray-400">Son guncelleme: Subat 2026</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">1. Veri Sorumlusu</h2>
        <p>UlgarTech ("Norosera"), Ankara Caddesi No 243/2, Bornova, Izmir adresinde mukim olup, kisisel verilerinizin islenmesine iliskin veri sorumlusudur.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">2. Toplanan Veriler</h2>
        <p>Platformumuz asagidaki verileri toplayabilir: ad-soyad, e-posta adresi, telefon numarasi, dogum tarihi, saglik verileri (migren atagi kayitlari, ilac kullanimi, semptom takibi), cihaz ve tarayici bilgileri, IP adresi.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">3. Verilerin Kullanim Amaci</h2>
        <p>Toplanan veriler; saglik takibi hizmeti sunma, kisisellestirilmis icerik olusturma, platform iyilestirme, yasal yukumluluklerin yerine getirilmesi ve guvenlik amacli kullanilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">4. Veri Paylasimi</h2>
        <p>Kisisel verileriniz, acik rizaniz olmadan ucuncu taraflarla paylasilmaz. Saglik verileriniz yalnizca sizin onayla hekiminizle paylasilabilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">5. Veri Guveniligi</h2>
        <p>Verileriniz SSL/TLS sifreleme, JWT token tabanli kimlik dogrulama ve duzenli guvenlik denetimleri ile korunmaktadir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">6. Cerezler</h2>
        <p>Platformumuz oturum yonetimi ve analitik amacli cerezler kullanir. Cerez tercihlerinizi ayarlar sayfasindan yonetebilirsiniz.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">7. Iletisim</h2>
        <p>Gizlilik politikamiz ile ilgili sorulariniz icin info@norosera.com adresinden bize ulasabilirsiniz.</p>
      </div>
    </div>
  );
}
