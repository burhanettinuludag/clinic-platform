export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto bg-white rounded-lg shadow p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Gizlilik Politikasi
        </h1>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Toplanan Bilgiler
          </h2>
          <p className="text-gray-600 leading-relaxed mb-2">
            Platformumuz asagidaki bilgileri toplamaktadir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 ml-2">
            <li>
              <span className="font-medium">Kisisel veriler:</span> Ad-soyad,
              e-posta, telefon numarasi
            </li>
            <li>
              <span className="font-medium">Saglik verileri:</span> Saglik
              kayitlari, olcum sonuclari, hekim notlari
            </li>
            <li>
              <span className="font-medium">Kullanim verileri:</span> Tarayici
              bilgisi, IP adresi, erisim zamanlari, sayfa goruntulemeleri
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Bilgilerin Kullanimi
          </h2>
          <p className="text-gray-600 leading-relaxed mb-2">
            Toplanan bilgiler asagidaki amaclarla kullanilmaktadir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 ml-2">
            <li>Hizmet kalitesinin iyilestirilmesi</li>
            <li>Saglik takibi ve izleme</li>
            <li>Hekim ile iletisim ve veri paylasimi</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Veri Guvenligi
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Verilerinizin guvenligini saglamak icin asagidaki onlemleri
            almaktayiz:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 mt-2 ml-2">
            <li>SSL/TLS ile sifrelenmis iletisim</li>
            <li>Sifrelenmis veri depolama (encrypted storage)</li>
            <li>Erisim kontrolu ve yetkilendirme mekanizmalari</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Cerezler
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Platformumuzda asagidaki cerez turleri kullanilmaktadir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 mt-2 ml-2">
            <li>
              <span className="font-medium">Zorunlu cerezler:</span> Platformun
              duzgun calismasi icin gerekli temel cerezler
            </li>
            <li>
              <span className="font-medium">Analitik cerezler:</span> Kullanim
              istatistikleri ve hizmet iyilestirme amacli cerezler
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Ucuncu Taraf Hizmetleri
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Platformumuz asagidaki ucuncu taraf hizmet saglayicilarini
            kullanmaktadir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 mt-2 ml-2">
            <li>
              <span className="font-medium">iyzico:</span> Odeme isleme
              hizmetleri
            </li>
            <li>
              <span className="font-medium">Hosting saglayicilari:</span> Veri
              barindirma ve sunucu hizmetleri
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Degisiklikler
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Bu gizlilik politikasi zaman zaman guncellenebilir. Degisiklikler
            yapildiginda, guncellenmis politika bu sayfada yayinlanacaktir.
            Onemli degisiklikler icin kullanicilarimiza e-posta yoluyla
            bildirimde bulunulacaktir.
          </p>
        </section>

        <section className="mb-4">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Iletisim
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Gizlilik politikamiz hakkinda sorulariniz icin asagidaki adres
            uzerinden bizimle iletisime gecebilirsiniz:
          </p>
          <p className="text-gray-600 leading-relaxed mt-2 font-medium">
            privacy@norosera.com
          </p>
        </section>
      </div>
    </div>
  );
}
