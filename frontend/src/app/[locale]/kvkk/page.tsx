export default function KVKKPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto bg-white rounded-lg shadow p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          KVKK Aydinlatma Metni
        </h1>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Veri Sorumlusu
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Norosera olarak kisisel verilerinizin korunmasina buyuk onem
            veriyoruz. 6698 sayili Kisisel Verilerin Korunmasi Kanunu (KVKK)
            kapsaminda, veri sorumlusu sifatiyla sizleri bilgilendirmek
            istiyoruz.
          </p>
          <p className="text-gray-600 leading-relaxed mt-2">
            Veri Sorumlusu: Norosera
          </p>
          <p className="text-gray-600 leading-relaxed">
            Iletisim: kvkk@norosera.com
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Islenen Kisisel Veriler
          </h2>
          <p className="text-gray-600 leading-relaxed mb-2">
            Platformumuz uzerinden asagidaki kisisel verileriniz
            islenmektedir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 ml-2">
            <li>Ad-Soyad</li>
            <li>E-posta adresi</li>
            <li>Telefon numarasi</li>
            <li>Saglik verileri</li>
            <li>IP adresi</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Veri Isleme Amaci
          </h2>
          <p className="text-gray-600 leading-relaxed mb-2">
            Kisisel verileriniz asagidaki amaclarla islenmektedir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 ml-2">
            <li>Saglik takibi ve izleme hizmetlerinin sunulmasi</li>
            <li>Hekim ile veri paylasimi</li>
            <li>Istatistiksel analizler ve hizmet iyilestirme</li>
            <li>Yasal yukumluluklerin yerine getirilmesi</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Veri Aktarimi
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Kisisel verileriniz asagidaki taraflara aktarilabilir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 mt-2 ml-2">
            <li>Hekiminize (saglik takibi kapsaminda)</li>
            <li>
              Yasal zorunluluk halinde yetkili kurum ve kuruluslara
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Haklariniz
          </h2>
          <p className="text-gray-600 leading-relaxed mb-2">
            KVKK kapsaminda asagidaki haklara sahipsiniz:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 ml-2">
            <li>Kisisel verilerinizin islenip islenmedigini ogrenme (bilgi edinme)</li>
            <li>Kisisel verilerinizin eksik veya yanlis islenmis olmasi halinde duzeltilmesini isteme</li>
            <li>Kisisel verilerinizin silinmesini veya yok edilmesini isteme</li>
            <li>Kisisel verilerinizin islenmesine itiraz etme</li>
            <li>Kisisel verilerinizin tasinmasini talep etme (veri tasima)</li>
          </ul>
        </section>

        <section className="mb-4">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Iletisim
          </h2>
          <p className="text-gray-600 leading-relaxed">
            KVKK kapsamindaki talepleriniz icin asagidaki adres uzerinden
            bizimle iletisime gecebilirsiniz:
          </p>
          <p className="text-gray-600 leading-relaxed mt-2 font-medium">
            kvkk@norosera.com
          </p>
        </section>
      </div>
    </div>
  );
}
