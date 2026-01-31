export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto bg-white rounded-lg shadow p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Kullanim Kosullari
        </h1>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Hizmet Tanimi
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Norosera, dijital saglik takibi ve izleme hizmeti sunan bir
            platformdur. Platform, kullanicilarin saglik verilerini
            kaydetmelerine, takip etmelerine ve hekimleriyle paylasmalarina
            olanak tanir.
          </p>
          <p className="text-gray-600 leading-relaxed mt-2 font-medium text-amber-700">
            Onemli: Bu platform bir tibbi teshis araci degildir. Saglik
            konusundaki kararlariniz icin mutlaka bir saglik profesyoneline
            danismaniz gerekmektedir.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Kullanim Sartlari
          </h2>
          <p className="text-gray-600 leading-relaxed mb-2">
            Platformu kullanabilmek icin asagidaki sartlari kabul etmeniz
            gerekmektedir:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 ml-2">
            <li>18 yasindan buyuk olmaniz gerekmektedir</li>
            <li>
              Kayit sirasinda dogru ve guncel bilgiler vermeniz gerekmektedir
            </li>
            <li>
              Hesap guvenliginizden siz sorumlusunuz; sifrenizi baskalaryla
              paylasmayiniz
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Saglik Uyarisi
          </h2>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 leading-relaxed font-medium">
              Bu platform tibbi tavsiye, teshis veya tedavi yerine gecmez.
              Saglik sorunlariniz icin mutlaka bir saglik profesyoneline
              basvurunuz.
            </p>
            <p className="text-red-800 leading-relaxed mt-2 font-bold">
              Acil durumlarda 112&#39;yi arayin.
            </p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Dijital Urun Satis
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Platform uzerinden satin alinan dijital urunler lisans ile
            sunulmaktadir. Satin alma isleminden itibaren 7 gun icinde iade
            talebinde bulunabilirsiniz. Iade kosullari:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-1 mt-2 ml-2">
            <li>Dijital urun henuz kullanilmamis olmalidir</li>
            <li>Iade talebi satin alma tarihinden itibaren 7 gun icinde yapilmalidir</li>
            <li>Iade islemleri ayni odeme yontemi uzerinden gerceklestirilir</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Fikri Mulkiyet
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Platform uzerindeki tum icerikler, tasarimlar, logolar, metinler,
            gorseller ve yazilimlar Norosera&#39;a aittir. Bu iceriklerin
            izinsiz kopyalanmasi, dagitilmasi veya kullanilmasi yasaktir.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Sorumluluk Sinirlamasi
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Norosera, platformun kullanimindan kaynaklanan saglik
            sonuclari konusunda herhangi bir sorumluluk kabul etmez. Platform
            yalnizca bilgi amacli bir aractir ve tibbi karar verme surecinde
            tek basina kullanilmamalidir.
          </p>
        </section>

        <section className="mb-4">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">
            Degisiklikler
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Bu kullanim kosullari zaman zaman guncellenebilir. Degisiklikler
            yapildiginda, guncellenmis kosullar bu sayfada yayinlanacaktir.
            Platformu kullanmaya devam etmeniz, guncellenmis kosullari kabul
            ettiginiz anlamina gelir.
          </p>
        </section>
      </div>
    </div>
  );
}
