import { Metadata } from 'next';

export const metadata: Metadata = { title: 'KVKK Aydınlatma Metni | Norosera', description: 'Norosera KVKK kapsamında kişisel verilerin korunması aydınlatma metni.' };

export default function KVKKPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">KVKK Aydınlatma Metni</h1>
      <div className="prose dark:prose-invert max-w-none space-y-6 text-gray-600 dark:text-gray-300">
        <p className="text-sm text-gray-400">6698 Sayılı Kişisel Verilerin Korunması Kanunu Kapsamında</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">1. Veri Sorumlusu</h2>
        <p>UlgarTech (&quot;Norosera&quot;), 6698 sayılı KVKK kapsamında veri sorumlusu sıfatıyla, kişisel verilerinizi aşağıda açıklanan amaçlar çerçevesinde işlemektedir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">2. İşlenen Kişisel Veriler</h2>
        <p><strong>Kimlik Bilgileri:</strong> Ad, soyad, doğum tarihi, cinsiyet.</p>
        <p><strong>İletişim Bilgileri:</strong> E-posta, telefon numarası.</p>
        <p><strong>Sağlık Verileri:</strong> Migren atağı kayıtları, epilepsi nöbetleri, ilaç kullanım bilgileri, semptom kayıtları, uyku ve wellness verileri.</p>
        <p><strong>İşlem Güvenliği:</strong> IP adresi, oturum bilgileri, log kayıtları.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">3. İşleme Amaçları</h2>
        <p>Sağlık takibi hizmeti sunulması, hekimle veri paylaşımı (onaylı), platform iyileştirme ve istatistik, yasal yükümlülüklerin yerine getirilmesi, bilgi güvenliği süreçleri.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">4. Veri Aktarımı</h2>
        <p>Kişisel verileriniz, açık rızanız olmadan yurt içinde veya yurt dışında üçüncü kişi ve kurumlara aktarılmaz. Sağlık verileriniz yalnızca onaylı hekimlerle paylaşılabilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">5. Veri Saklama Süresi</h2>
        <p>Kişisel verileriniz, işleme amacının gerektirdiği süre boyunca saklanır. Hesap silme talebiniz üzerine verileriniz yasal süreler dışında imha edilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">6. Haklarınız (KVKK Madde 11)</h2>
        <p>Kişisel verilerinize ilişkin; işlenip işlenmediğini öğrenme, işlenmişse bilgi talep etme, işleme amacını öğrenme, aktarılıp aktarılmadığını öğrenme, düzeltilmesini isteme, silinmesini veya yok edilmesini isteme, işlemlerin üçüncü kişilere bildirilmesini isteme, analiz sonucuna itiraz etme, zarara uğramanız halinde tazminat talep etme haklarına sahipsiniz.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">7. Başvuru</h2>
        <p>KVKK kapsamındaki haklarınızı kullanmak için info@norosera.com adresine yazılı başvuruda bulunabilirsiniz.</p>
      </div>
    </div>
  );
}
