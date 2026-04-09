"""
Haber içeriklerindeki ASCII Türkçe karakterleri düzeltir.
Kapsamlı kelime sözlüğü yaklaşımı kullanır.

Kullanım: python3 manage.py fix_news_turkish
"""
from django.core.management.base import BaseCommand
from apps.content.models import NewsArticle

# Türkçe kelime sözlüğü: ASCII -> doğru Türkçe
# Uzun kelimeler önce gelir (greedy matching via sorted keys)
WORD_MAP = {
    # ── Ö ──
    'ozellikle': 'özellikle', 'ozellikleri': 'özellikleri', 'ozellik': 'özellik',
    'Ozellik': 'Özellik', 'Ozellikle': 'Özellikle',
    'onemli': 'önemli', 'Onemli': 'Önemli', 'onemi': 'önemi', 'Onemi': 'Önemi',
    'oncelikli': 'öncelikli', 'Oncelikli': 'Öncelikli', 'once': 'önce',
    'onceden': 'önceden', 'oncesinden': 'öncesinden',
    'oneri': 'öneri', 'Oneri': 'Öneri', 'onerilen': 'önerilen', 'onerileri': 'önerileri',
    'onlenmesinde': 'önlenmesinde', 'onlemler': 'önlemler',
    'ogrenme': 'öğrenme', 'Ogrenme': 'Öğrenme',
    'olcude': 'ölçüde', 'olculen': 'ölçülen', 'olcum': 'ölçüm', 'Olcum': 'Ölçüm',
    'olculer': 'ölçüler', 'Olculer': 'Ölçüler',
    'olcerek': 'ölçerek', 'olcuyor': 'ölçüyor',
    'onunu': 'önünü', 'onunu aciyor': 'önünü açıyor',
    'ozgurluk': 'özgürlük',
    'ozetliyor': 'özetliyor',
    # ── Ü ──
    'uzerinden': 'üzerinden', 'uzerine': 'üzerine', 'uzere': 'üzere',
    'uzerinde': 'üzerinde', 'Uzerinde': 'Üzerinde',
    'ucuncu': 'üçüncü', 'ucretsiz': 'ücretsiz', 'Ucretsiz': 'Ücretsiz',
    'ucuz': 'ucuz',  # zaten doğru - Latin u
    'uretimine': 'üretimine', 'uretim': 'üretim',
    'Uc ': 'Üç ',
    # ── Ş ──
    'islev': 'işlev', 'islevlere': 'işlevlere',
    'isleme': 'işleme', 'islenmesi': 'işlenmesi',
    'isaret': 'işaret', 'Isaret': 'İşaret',
    'dusme': 'düşme', 'duser': 'düşer', 'dusuk': 'düşük', 'Dusuk': 'Düşük',
    'dusurerek': 'düşürerek',
    'baslar': 'başlar', 'baslangic': 'başlangıç', 'baslamasi': 'başlaması',
    'baslama dan': 'başlamadan', 'baslamadan': 'başlamadan',
    'basari': 'başarı', 'basarili': 'başarılı', 'basardi': 'başardı',
    'baslatti': 'başlattı', 'baslamis': 'başlamış',
    'isik': 'ışık', 'Isik': 'Işık', 'isigi': 'ışığı',
    'asiri': 'aşırı', 'Asiri': 'Aşırı',
    'kesif': 'keşif',
    'gosterge': 'gösterge', 'gostergesi': 'göstergesi',
    'gostermektedir': 'göstermektedir', 'gosterdi': 'gösterdi',
    'gosteriyor': 'gösteriyor',
    'gorulen': 'görülen', 'goruluyor': 'görülüyor',
    'goruntuledi': 'görüntüledi', 'goruntulemeyi': 'görüntülemeyi',
    'goruntulendi': 'görüntülendi', 'Goruntulendi': 'Görüntülendi',
    'Goruntu': 'Görüntü', 'goruntu': 'görüntü',
    'gerceklestirilen': 'gerçekleştirilen', 'gerceklestirdigi': 'gerçekleştirdiği',
    'gerceklesir': 'gerçekleşir',
    'gelistirdi': 'geliştirdi', 'gelistirilen': 'geliştirilen',
    'gelistirdigi': 'geliştirdiği', 'gelistirilmesinde': 'geliştirilmesinde',
    'gelistirilmis': 'geliştirilmiş', 'Gelistirilmis': 'Geliştirilmiş',
    'gelisim': 'gelişim', 'Gelisim': 'Gelişim',
    'gelismeler': 'gelişmeler',
    'iyilestirici': 'iyileştirici', 'iyilestirir': 'iyileştirir',
    'iyilestirdigini': 'iyileştirdiğini', 'iyilesme': 'iyileşme',
    'etkilesim': 'etkileşim', 'Etkilesim': 'Etkileşim',
    'calisma': 'çalışma', 'Calisma': 'Çalışma',
    'calismalar': 'çalışmalar', 'calismalarda': 'çalışmalarda',
    'calismalarin': 'çalışmaların', 'calismalarinda': 'çalışmalarında',
    'calismayi': 'çalışmayı',
    'calismayi kapsayan': 'çalışmayı kapsayan',
    'degisiklikleri': 'değişiklikleri', 'degisiklik': 'değişiklik',
    'degiskenligini': 'değişkenliğini',
    'degerlendirme': 'değerlendirme', 'Degerlendirme': 'Değerlendirme',
    'degil': 'değil', 'degildir': 'değildir',
    'saglik': 'sağlık', 'Saglik': 'Sağlık', 'sagligi': 'sağlığı',
    'saglikli': 'sağlıklı', 'saglama': 'sağlama', 'saglar': 'sağlar',
    'saglayabilir': 'sağlayabilir', 'sagladigini': 'sağladığını',
    'saglandi': 'sağlandı',
    'agri': 'ağrı', 'agrisi': 'ağrısı', 'agrilari': 'ağrıları',
    'Agrisi': 'Ağrısı',
    'yogunlukta': 'yoğunlukta', 'yogun': 'yoğun',
    'buyuk': 'büyük', 'Buyuk': 'Büyük',
    'norolojik': 'nörolojik', 'Norolojik': 'Nörolojik',
    'noroloji': 'nöroloji', 'Noroloji': 'Nöroloji',
    'Norostimulasyon': 'Nörostimülasyon', 'norostimulasyon': 'nörostimülasyon',
    'norodejeneratif': 'nörodejeneratif', 'Norodejeneratif': 'Nörodejeneratif',
    'nobet': 'nöbet', 'Nobet': 'Nöbet',
    'nobetler': 'nöbetler', 'Nobetler': 'Nöbetler',
    'nobetleri': 'nöbetleri', 'nobetlerini': 'nöbetlerini',
    'yontem': 'yöntem', 'Yontem': 'Yöntem',
    'yontemleri': 'yöntemleri', 'yontemi': 'yöntemi',
    'yontemlerle': 'yöntemlerle', 'yontemlerinin': 'yöntemlerinin',
    'yonlu': 'yönlü', 'yonelik': 'yönelik',
    'gecis': 'geçiş', 'gecen': 'geçen', 'gecirilen': 'geçirilen',
    'duzenli': 'düzenli', 'Duzenli': 'Düzenli',
    'duzenlenen': 'düzenlenen',
    'yuksek': 'yüksek', 'Yuksek': 'Yüksek',
    'yukselerken': 'yükselirken',
    'kullanilan': 'kullanılan', 'kullanilabilir': 'kullanılabilir',
    'kullanim': 'kullanım', 'kullanilmalidir': 'kullanılmalıdır',
    'kullanimini': 'kullanımını', 'kullanilacak': 'kullanılacak',
    'kullanima': 'kullanıma',
    'teshis': 'teşhis',
    'guvenlik': 'güvenlik', 'guvenilirlik': 'güvenilirlik',
    'guvenligi': 'güvenliği',
    'gucluk': 'güçlük', 'guclu': 'güçlü',
    'dogruluk': 'doğruluk', 'dogrulukla': 'doğrulukla',
    'dogrudan': 'doğrudan', 'dogruladi': 'doğruladı',
    'dogrulama': 'doğrulama',
    'dogru': 'doğru',
    'olusur': 'oluşur', 'olusan': 'oluşan', 'olusturur': 'oluşturur',
    'olusabilir': 'oluşabilir',
    'kolaylastirir': 'kolaylaştırır',
    'zorlastirir': 'zorlaştırır', 'zorlastiran': 'zorlaştıran',
    'hizlandirir': 'hızlandırır',
    'yaklasim': 'yaklaşım', 'Yaklasim': 'Yaklaşım',
    'yaklasik': 'yaklaşık',
    'yaygin': 'yaygın', 'Yaygin': 'Yaygın',
    'yayinlanan': 'yayınlanan', 'yayinladi': 'yayınladı',
    'yayinladigi': 'yayınladığı', 'yayildigini': 'yayıldığını',
    'yasam': 'yaşam', 'yasamda': 'yaşamda',
    'yasayan': 'yaşayan',
    'diger': 'diğer', 'Diger': 'Diğer',
    'ragmen': 'rağmen',
    'olmasina': 'olmasına',
    'gunduz': 'gündüz', 'Gunduz': 'Gündüz',
    'gunluk': 'günlük', 'Gunluk': 'Günlük',
    'guncellenmis': 'güncellenmiş',
    'gunu': 'günü', 'guncel': 'güncel', 'Guncel': 'Güncel',
    'kadinlarda': 'kadınlarda', 'Kadinlarda': 'Kadınlarda',
    'Kadindan': 'Kadından',
    'vucut': 'vücut', 'vucudu': 'vücudu',
    'dongu': 'döngü', 'dongusu': 'döngüsü',
    # ── İ/I ──
    'Ilac': 'İlaç', 'ilac': 'ilaç',
    'ilaclarin': 'ilaçların', 'Ilaclarin': 'İlaçların',
    'ilaclar': 'ilaçlar', 'Ilaclar': 'İlaçlar',
    'ilacin': 'ilacın', 'Ilacin': 'İlacın',
    'Ilaci': 'İlacı',
    'Ikincil': 'İkincil',
    'Iliskili': 'İlişkili', 'iliskili': 'ilişkili',
    'Iliski': 'İlişki', 'iliski': 'ilişki',
    'Ileri': 'İleri',
    'Ilk': 'İlk',
    'Icin': 'İçin', 'icin': 'için',
    'icinde': 'içinde', 'icerir': 'içerir', 'iceren': 'içeren',
    'icerisinde': 'içerisinde', 'icerigin': 'içeriğin',
    'Incelemede': 'İncelemede',
    'ilerlemesini': 'ilerlemesini',  # doğru
    # ── Ç ──
    'cikar': 'çıkar', 'cikin': 'çıkın', 'cikma': 'çıkma', 'cikan': 'çıkan',
    'cocuk': 'çocuk', 'Cocuk': 'Çocuk', 'cocuklarin': 'çocukların',
    'cocukluk': 'çocukluk', 'Cocukluk': 'Çocukluk', 'cocuklarda': 'çocuklarda',
    'cift': 'çift',
    'cevre': 'çevre',
    'cene': 'çene',
    'cekici': 'çekici',
    'cizdi': 'çizdi',
    'Cigirlari': 'Çığırları', 'cigirlari': 'çığırları',
    'Cigirlara': 'Çığırlara', 'cigirlara': 'çığırlara',
    # ── Ğ ──
    'bagirsak': 'bağırsak', 'Bagirsak': 'Bağırsak',
    'bagisiklik': 'bağışıklık',
    'baglanti': 'bağlantı', 'baglantilar': 'bağlantılar',
    # ── Genel kelimeler ──
    'siklikla': 'sıklıkla', 'sik': 'sık', 'sikligi': 'sıklığı',
    'sikligini': 'sıklığını',
    'sirasinda': 'sırasında', 'Sirasinda': 'Sırasında',
    'sicaklik': 'sıcaklık', 'Sicaklik': 'Sıcaklık',
    'sinirli': 'sınırlı', 'sinirlayin': 'sınırlayın',
    'salgilanir': 'salgılanır',
    'surer': 'sürer', 'suren': 'süren', 'suresi': 'süresi',
    'surec': 'süreç', 'Surec': 'Süreç', 'surecinde': 'sürecinde',
    'sureci': 'süreci',
    'surekli': 'sürekli',
    'yardimci': 'yardımcı',
    'azalir': 'azalır', 'azalmasi': 'azalması',
    'azaltiyor': 'azaltıyor', 'azalttigi': 'azalttığı', 'Azalttigi': 'Azalttığı',
    'azalttigi': 'azalttığı',
    'artirmak': 'artırmak', 'artirabilir': 'artırabilir',
    'artirir': 'artırır', 'artirma': 'artırma',
    'artirdigini': 'artırdığını', 'artirdigini gosteriyor': 'artırdığını gösteriyor',
    'yapilir': 'yapılır', 'yapilabilir': 'yapılabilir',
    'yapilmamis': 'yapılmamış',
    'detayli': 'detaylı',
    'kadinlarda': 'kadınlarda',
    'kisiye': 'kişiye', 'kisilik': 'kişilik', 'kisiyi': 'kişiyi',
    'bilinc': 'bilinç',
    'karmasik': 'karmaşık',
    'canli': 'canlı',
    'hatirlamama': 'hatırlamama',
    'kisa': 'kısa', 'Kisa': 'Kısa',
    'kalici': 'kalıcı',
    'alinir': 'alınır',
    'birakin': 'bırakın', 'birakma': 'bırakma',
    'yapmayin': 'yapmayın',
    'altin': 'altın', 'Altin': 'Altın',
    'karanlik': 'karanlık', 'Karanlik': 'Karanlık',
    'parcasi': 'parçası',
    'tarafindan': 'tarafından',
    'yenidogan': 'yenidoğan', 'Yenidogan': 'Yenidoğan',
    'donem': 'dönem', 'doneminde': 'döneminde',
    'siddet': 'şiddet', 'Siddet': 'Şiddet', 'siddetli': 'şiddetli',
    'yillar': 'yıllar', 'yil': 'yıl', 'yilinin': 'yılının',
    'tumoru': 'tümörü',
    'faktoru': 'faktörü', 'faktorleri': 'faktörleri',
    'sonuc': 'sonuç', 'Sonuc': 'Sonuç',
    'sonuclari': 'sonuçları', 'Sonuclari': 'Sonuçları',
    'sonuclar': 'sonuçlar', 'sonuclarin': 'sonuçların',
    'sonucunda': 'sonucunda',  # doğru
    'farkindaligin': 'farkındalığın', 'Farkindaligin': 'Farkındalığın',
    'farkindalik': 'farkındalık', 'Farkindalik': 'Farkındalık',
    'farkindaliigina': 'farkındalığına',
    'bilissel': 'bilişsel', 'Bilissel': 'Bilişsel',
    'Oyunlarin': 'Oyunların', 'oyunlarin': 'oyunların',
    'Yuruyusun': 'Yürüyüşün', 'yuruyusun': 'yürüyüşün',
    'Kanitlandi': 'Kanıtlandı', 'kanitlandi': 'kanıtlandı',
    'kanitlanmistir': 'kanıtlanmıştır',
    'Giyilebilir': 'Giyilebilir',  # doğru
    'Direncli': 'Dirençli', 'direncli': 'dirençli',
    'Onayladi': 'Onayladı', 'onayladi': 'onayladı',
    'onaylanan': 'onaylanan',  # doğru
    'Cocukluk': 'Çocukluk', 'cocukluk': 'çocukluk',
    'Kilavuz': 'Kılavuz', 'kilavuz': 'kılavuz',
    'kilavuzun': 'kılavuzun',
    'Aciyor': 'Açıyor', 'aciyor': 'açıyor',
    'acilar': 'açılar',
    'Cihazi': 'Cihazı', 'cihazi': 'cihazı',
    'cihaz': 'cihaz',  # doğru
    'Populer': 'Popüler', 'populer': 'popüler',
    'Duzeltme': 'Düzeltme', 'duzeltme': 'düzeltme',
    'Arsivlendi': 'Arşivlendi', 'arsivlendi': 'arşivlendi',
    'Arastirma': 'Araştırma', 'arastirma': 'araştırma',
    'arastirmacilari': 'araştırmacıları', 'arastirmacilarin': 'araştırmacıların',
    'Arastirmacilari': 'Araştırmacıları',
    'Arasturma': 'Araştırma', 'arasturma': 'araştırma',
    'girisim': 'girişim', 'Girisim': 'Girişim',
    'kullanici': 'kullanıcı', 'Kullanici': 'Kullanıcı',
    'hastalik': 'hastalık', 'Hastalik': 'Hastalık',
    'hastaliklarda': 'hastalıklarda', 'hastalikta': 'hastalıkta',
    'hastaligi': 'hastalığı', 'hastaligini': 'hastalığını',
    'hastaliginin': 'hastalığının',
    'hastalarin': 'hastaların', 'hastalarinda': 'hastalarında',
    'hastalarinin': 'hastalarının', 'hastalarina': 'hastalarına',
    'hastaligin': 'hastalığın',
    'odaklaniyor': 'odaklanıyor', 'odakli': 'odaklı',
    'aliskanlik': 'alışkanlık', 'aliskanliklari': 'alışkanlıkları',
    'gecmez': 'geçmez',
    'Turkiye': 'Türkiye', 'turkiye': 'türkiye',
    "Turkiye'de": "Türkiye'de", "Turkiye'deki": "Türkiye'deki",
    'Turk': 'Türk', 'turk': 'türk',
    'tum': 'tüm',
    'ticarilesmesi': 'ticarileşmesi',
    'secenek': 'seçenek', 'Secenegi': 'Seçeneği', 'secenegi': 'seçeneği',
    'disinda': 'dışında',
    'ulasilan': 'ulaşılan',
    'belirgin': 'belirgin',  # doğru
    'belirledi': 'belirledi',  # doğru
    'belirtiyor': 'belirtiyor',  # doğru
    'kapsamli': 'kapsamlı',
    'kapsaminda': 'kapsamında',
    'ortaya': 'ortaya',  # doğru
    'beklenenin': 'beklenenin',  # doğru
    'bekleniyor': 'bekleniyor',  # doğru
    'saptandi': 'saptandı',
    'gordugunun': 'gördüğünün',
    'altini': 'altını',
    'anlamli': 'anlamlı',
    'kiyasla': 'kıyasla',
    'yarisina': 'yarısına',
    'bulanti': 'bulantı',
    'kizariklikti': 'kızarıklıktı',
    'indi': 'indi',  # doğru
    'genelinde': 'genelinde',  # doğru
    'sunuluyor': 'sunuluyor',  # doğru
    'sunulan': 'sunulan',  # doğru
    'dikkat': 'dikkat',  # doğru
    'olarak': 'olarak',  # doğru
    'orani': 'oranı', 'oranlarini': 'oranlarını',
    'takip': 'takip',  # doğru
    'dagitim': 'dağıtım',
    'disbiyozis': 'disbiyozis',  # doğru
    'mudahalelerin': 'müdahalelerin',
    'miniaturize': 'minyatürize',
    'stimulasyon': 'stimülasyon', 'stimulasyonunun': 'stimülasyonunun',
    'stimulasyonu': 'stimülasyonu',
    'imkani': 'imkânı',
    'muayene': 'muayene',  # doğru
    'oldugunu': 'olduğunu',
    'olacagini': 'olacağını',
    'oldugunu ortaya': 'olduğunu ortaya',
    'koydu': 'koydu',  # doğru
    'tespit': 'tespit',  # doğru
    'ulke': 'ülke',
    'ilde': 'ilde',  # doğru
    'Ilac Ajansi': 'İlaç Ajansı',
    'Ilac Dairesi': 'İlaç Dairesi',
    'Bas Agrisi': 'Baş Ağrısı',
    'bas agrisi': 'baş ağrısı',
    # ── Eksik kelimeler ──
    'populasyonda': 'popülasyonda', 'populasyonun': 'popülasyonun',
    'orneklem': 'örneklem', 'Orneklem': 'Örneklem',
    'yalnizca': 'yalnızca', 'Yalnizca': 'Yalnızca',
    'ayrica': 'ayrıca', 'Ayrica': 'Ayrıca',
    'Detaylari': 'Detayları', 'detaylari': 'detayları',
    'Araştırmasi': 'Araştırması', 'arastirmasi': 'araştırması',
    'Dernegi': 'Derneği', 'dernegi': 'derneği',
    'prevalansi': 'prevalansı',
    'yukselerken': 'yükselirken',
    'sinir': 'sinir', 'sinirinin': 'sinirinin',
    'Haftasi': 'Haftası', 'haftasi': 'haftası',
    'ilacinin': 'ilacının',
    'secenekleri': 'seçenekleri',
    'degerlendirmesi': 'değerlendirmesi',
    'degerlendirilmelidir': 'değerlendirilmelidir',
    'uygulamislardir': 'uygulamışlardır',
    'etkiledigini': 'etkilediğini',
    'etkilendigini': 'etkilendiğini',
    'etkilendigi': 'etkilendiği',
    'tedavisinde': 'tedavisinde',  # doğru
    'yayinlandi': 'yayınlandı',
    'yayinlanmistir': 'yayınlanmıştır',
    'yapildi': 'yapıldı', 'yapildigi': 'yapıldığı',
    'yapilmis': 'yapılmış', 'yapilmasi': 'yapılması',
    'Bilgilendirilmesi': 'Bilgilendirilmesi',  # doğru
    'bilimsel': 'bilimsel',  # doğru
    'tedavisi': 'tedavisi',  # doğru
    'noronlarin': 'nöronların', 'noronlar': 'nöronlar',
    'ortaya cikmaktadir': 'ortaya çıkmaktadır',
    'cikmaktadir': 'çıkmaktadır',
    'bulgusu': 'bulgusu',  # doğru
    'istatistikleri': 'istatistikleri',  # doğru
    'gelismis': 'gelişmiş', 'Gelismis': 'Gelişmiş',
    'uygulanmasi': 'uygulanması',
    'uygulamanin': 'uygulamanın',
    'uygulamasi': 'uygulaması',
    'erismistir': 'erişmiştir',
    'erisim': 'erişim', 'Erisim': 'Erişim',
    'teshisin': 'teşhisin',
    'gosterdi': 'gösterdi',
    'gosterir': 'gösterir',
    'cevresindeki': 'çevresindeki',
    'iciyor': 'içiyor',
    'iciniz': 'içiniz',
    'ucte': 'üçte',
    'bulunmustur': 'bulunmuştur',
    'ongorulmektedir': 'öngörülmektedir',
    'ongoren': 'öngören',
    'hazirlanan': 'hazırlanan', 'hazirlayan': 'hazırlayan',
    'hazirlik': 'hazırlık', 'Hazirlik': 'Hazırlık',
    'Hastanesi': 'Hastanesi',  # doğru
    'hastanede': 'hastanede',  # doğru
    'olusumu': 'oluşumu', 'olusumunu': 'oluşumunu',
    'tedavinin': 'tedavinin',  # doğru
    'goruntuleme': 'görüntüleme', 'Goruntuleme': 'Görüntüleme',
    'hastaliklari': 'hastalıkları', 'Hastaliklari': 'Hastalıkları',
    'dogrulamistir': 'doğrulamıştır',
    'kanitlar': 'kanıtlar', 'kanit': 'kanıt',
    'kanitlara': 'kanıtlara',
    'kanitlanmis': 'kanıtlanmış',
    'riskleri': 'riskleri',  # doğru
    'tarafindandir': 'tarafındandır',
    'surecte': 'süreçte',
    'saglanmasi': 'sağlanması',
    'deneklerin': 'deneklerin',  # doğru
    'saglanmistir': 'sağlanmıştır',
    'Ruhsat': 'Ruhsat',  # doğru
    'Aldi': 'Aldı', 'aldi': 'aldı',
    'almistir': 'almıştır',
    'anlasma': 'anlaşma', 'Anlasma': 'Anlaşma',
    'anlasilan': 'anlaşılan',
    'anlasmazlik': 'anlaşmazlık',
    'bolumleri': 'bölümleri', 'bolum': 'bölüm', 'Bolum': 'Bölüm',
    'bolumde': 'bölümde', 'bolumdeki': 'bölümdeki',
    'deneysel': 'deneysel',  # doğru
    'memnuniyetini': 'memnuniyetini',  # doğru
    'basarilmistir': 'başarılmıştır',
    'teshis konulmasi': 'teşhis konulması',
    'Bulunamadi': 'Bulunamadı',
    # ── Bileşik düzeltmeler ──
    'Farkindaligin Onemi': 'Farkındalığın Önemi',
}


class Command(BaseCommand):
    help = 'Haber içeriklerindeki ASCII Türkçe karakterleri düzeltir'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Değişiklikleri kaydetmeden göster',
        )

    def _fix_text(self, text):
        if not text:
            return text
        # Uzun kelimelerden başla (greedy)
        sorted_keys = sorted(WORD_MAP.keys(), key=len, reverse=True)
        for old in sorted_keys:
            if old in text:
                text = text.replace(old, WORD_MAP[old])
        return text

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        count = 0
        changed = 0

        text_fields = ['title_tr', 'excerpt_tr', 'body_tr', 'meta_description', 'meta_title',
                        'featured_image_alt']

        for article in NewsArticle.objects.all():
            modified = False
            for field in text_fields:
                old_val = getattr(article, field, None)
                if not old_val:
                    continue
                new_val = self._fix_text(old_val)
                if new_val != old_val:
                    if dry_run:
                        self.stdout.write(f'\n--- {article.slug} [{field}] ---')
                        self.stdout.write(f'  ÖNCE:  {old_val[:120]}')
                        self.stdout.write(f'  SONRA: {new_val[:120]}')
                    setattr(article, field, new_val)
                    modified = True

            if modified and not dry_run:
                article.save()
                changed += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  Düzeltildi: {article.title_tr[:70]}'
                ))
            count += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\n[DRY RUN] {count} haber kontrol edildi. Değişiklik kaydedilmedi.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n{changed}/{count} haber düzeltildi!'
            ))
