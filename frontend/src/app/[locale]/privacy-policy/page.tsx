import { Metadata } from 'next';

export const metadata: Metadata = { title: 'Gizlilik Politikası | Norosera', description: 'Norosera platformu gizlilik politikası.' };

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Gizlilik Politikası</h1>
      <div className="prose dark:prose-invert max-w-none space-y-6 text-gray-600 dark:text-gray-300">
        <p className="text-sm text-gray-400">Son güncelleme: Şubat 2026</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">1. Veri Sorumlusu</h2>
        <p>UlgarTech (&quot;Norosera&quot;), Ankara Caddesi No 243/2, Bornova, İzmir adresinde mukim olup, kişisel verilerinizin işlenmesine ilişkin veri sorumlusudur.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">2. Toplanan Veriler</h2>
        <p>Platformumuz aşağıdaki verileri toplayabilir: ad-soyad, e-posta adresi, telefon numarası, doğum tarihi, sağlık verileri (migren atağı kayıtları, ilaç kullanımı, semptom takibi), cihaz ve tarayıcı bilgileri, IP adresi.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">3. Verilerin Kullanım Amacı</h2>
        <p>Toplanan veriler; sağlık takibi hizmeti sunma, kişiselleştirilmiş içerik oluşturma, platform iyileştirme, yasal yükümlülüklerin yerine getirilmesi ve güvenlik amaçlı kullanılır.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">4. Veri Paylaşımı</h2>
        <p>Kişisel verileriniz, açık rızanız olmadan üçüncü taraflarla paylaşılmaz. Sağlık verileriniz yalnızca sizin onayınızla hekiminizle paylaşılabilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">5. Veri Güvenliği</h2>
        <p>Verileriniz SSL/TLS şifreleme, JWT token tabanlı kimlik doğrulama ve düzenli güvenlik denetimleri ile korunmaktadır.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">6. Çerezler</h2>
        <p>Platformumuz oturum yönetimi ve analitik amaçlı çerezler kullanır. Çerez tercihlerinizi ayarlar sayfasından yönetebilirsiniz.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">7. İletişim</h2>
        <p>Gizlilik politikamız ile ilgili sorularınız için info@norosera.com adresinden bize ulaşabilirsiniz.</p>
      </div>
    </div>
  );
}
