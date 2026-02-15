import { Metadata } from 'next';

export const metadata: Metadata = { title: 'KVKK Aydinlatma Metni | Norosera', description: 'Norosera KVKK kapsaminda kisisel verilerin korunmasi aydinlatma metni.' };

export default function KVKKPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">KVKK Aydinlatma Metni</h1>
      <div className="prose dark:prose-invert max-w-none space-y-6 text-gray-600 dark:text-gray-300">
        <p className="text-sm text-gray-400">6698 Sayili Kisisel Verilerin Korunmasi Kanunu Kapsaminda</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">1. Veri Sorumlusu</h2>
        <p>UlgarTech ("Norosera"), 6698 sayili KVKK kapsaminda veri sorumlusu sifatiyla, kisisel verilerinizi asagida aciklanan amaclar cercevesinde islemektedir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">2. Islenen Kisisel Veriler</h2>
        <p><strong>Kimlik Bilgileri:</strong> Ad, soyad, dogum tarihi, cinsiyet.</p>
        <p><strong>Iletisim Bilgileri:</strong> E-posta, telefon numarasi.</p>
        <p><strong>Saglik Verileri:</strong> Migren atagi kayitlari, epilepsi nobetleri, ilac kullanim bilgileri, semptom kayitlari, uyku ve wellness verileri.</p>
        <p><strong>Islem Guveniligi:</strong> IP adresi, oturum bilgileri, log kayitlari.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">3. Isleme Amaclari</h2>
        <p>Saglik takibi hizmeti sunulmasi, hekimle veri paylasimi (onayli), platform iyilestirme ve istatistik, yasal yukumluluklerin yerine getirilmesi, bilgi guvenligi surecleri.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">4. Veri Aktarimi</h2>
        <p>Kisisel verileriniz, acik rizaniz olmadan yurt icinde veya yurt disinda ucuncu kisi ve kurumlara aktarilmaz. Saglik verileriniz yalnizca onayli hekimlerle paylasilabilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">5. Veri Saklama Suresi</h2>
        <p>Kisisel verileriniz, isleme amacinin gerektirdigi sure boyunca saklanir. Hesap silme talebiniz uzerine verileriniz yasal sureler disinda imha edilir.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">6. Haklariniz (KVKK Madde 11)</h2>
        <p>Kisisel verilerinize iliskin; islenip islenmedigini ogrenme, islenmisse bilgi talep etme, isleme amacini ogrenme, aktarilip aktarilmadigini ogrenme, duzeltilmesini isteme, silinmesini veya yok edilmesini isteme, islemlerin ucuncu kisilere bildirilmesini isteme, analiz sonucuna itiraz etme, zarara ugramaniz halinde tazminat talep etme haklarina sahipsiniz.</p>

        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">7. Basvuru</h2>
        <p>KVKK kapsamindaki haklarinizi kullanmak icin info@norosera.com adresine yazili basvuruda bulunabilirsiniz.</p>
      </div>
    </div>
  );
}
