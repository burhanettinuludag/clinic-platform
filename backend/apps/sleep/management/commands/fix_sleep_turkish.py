"""
Uyku modülü içeriklerindeki ASCII Türkçe karakterleri düzeltir.
Kapsamlı kelime sözlüğü yaklaşımı kullanır.
"""
from django.core.management.base import BaseCommand
from apps.sleep.models import SleepCategory, SleepArticle, SleepTip, SleepFAQ
import re

# Türkçe kelime sözlüğü: ASCII -> doğru Türkçe
# Uzun kelimeler önce gelir (greedy matching)
WORD_MAP = {
    # --- Ö ---
    'ozellikle': 'özellikle', 'ozellikleri': 'özellikleri', 'ozellik': 'özellik',
    'onemli': 'önemli', 'Onemli': 'Önemli', 'onemi': 'önemi',
    'oncelikli': 'öncelikli', 'Oncelikli': 'Öncelikli', 'once': 'önce',
    'oneri': 'öneri', 'Oneri': 'Öneri', 'onerilen': 'önerilen', 'onerileri': 'önerileri',
    'onlenmesinde': 'önlenmesinde', 'onlemler': 'önlemler',
    'ogrenme': 'öğrenme', 'Ogrenme': 'Öğrenme',
    'ogleden': 'öğleden', 'Ogleden': 'Öğleden',
    'olcude': 'ölçüde', 'olculen': 'ölçülen', 'olcum': 'ölçüm',
    'olum': 'ölüm',
    # --- Ü ---
    'uzerinden': 'üzerinden', 'uzerine': 'üzerine', 'uzere': 'üzere',
    'ucuncu': 'üçüncü', 'ucretsiz': 'ücretsiz', 'Ucretsiz': 'Ücretsiz',
    'ust': 'üst', 'uste': 'üste',
    # --- Ş ---
    'baskin': 'baskın', 'baskilar': 'baskılar', 'baskilayabilir': 'baskılayabilir',
    'BASKILAR': 'BASKILAR', 'BASKLAR': 'BASKILER',
    'islev': 'işlev', 'islevlere': 'işlevlere', 'islevselligini': 'işlevselliğini',
    'isaret': 'işaret', 'Isaret': 'İşaret', 'isareti': 'işareti',
    'isler': 'işler', 'islenmesi': 'işlenmesi',
    'dusme': 'düşme', 'duser': 'düşer', 'dusuk': 'düşük', 'dusugu': 'düşüğü',
    'dusure': 'düşüre', 'dusurerek': 'düşürerek', 'dusurebiir': 'düşürebilir',
    'dusunulebilir': 'düşünülebilir', 'dusuklugu': 'düşüklüğü',
    'baslar': 'başlar', 'baslangic': 'başlangıç',
    'disi': 'dışı', 'disinda': 'dışında',
    'isik': 'ışık', 'isigi': 'ışığı', 'isigina': 'ışığına',
    'asiri': 'aşırı', 'Asiri': 'Aşırı',
    'kesif': 'keşif',
    'dusler': 'düşler', 'dus': 'duş',
    'gosterge': 'gösterge', 'gostergesi': 'göstergesi', 'gostermektedir': 'göstermektedir',
    'gostermez': 'göstermez', 'gosteremez': 'gösteremez',
    # --- Ğ ---
    'agri': 'ağrı', 'agrisi': 'ağrısı', 'agrilari': 'ağrıları',
    'baglanti': 'bağlantı', 'baglantilar': 'bağlantılar',
    'bagisiklik': 'bağışıklık',
    'dagitim': 'dağıtım',
    'saglik': 'sağlık', 'Saglik': 'Sağlık', 'sagligi': 'sağlığı',
    'saglikli': 'sağlıklı', 'Saglikli': 'Sağlıklı', 'Sagllikli': 'Sağlıklı',
    'saglama': 'sağlama', 'saglar': 'sağlar', 'saglamak': 'sağlamak',
    'yagli': 'yağlı',
    'yagmur': 'yağmur',
    'degil': 'değil', 'degildir': 'değildir',
    'degisiklikleri': 'değişiklikleri', 'Degisiklikleri': 'Değişiklikleri',
    'degisebilir': 'değişebilir',
    'degerlndirilmelidir': 'değerlendirilmelidir', 'degerlendirilmeli': 'değerlendirilmeli',
    'degerlendirilmesi': 'değerlendirilmesi', 'degerlendirmesi': 'değerlendirmesi',
    'dengesizligi': 'dengesizliği',
    'diger': 'diğer', 'Diger': 'Diğer',
    'dogru': 'doğru',
    'yogunlukta': 'yoğunlukta', 'yogun': 'yoğun',
    'buyume': 'büyüme', 'buyuk': 'büyük', 'Buyuk': 'Büyük',
    'bolumu': 'bölümü',
    'onarim': 'onarım',
    'hucre': 'hücre',
    # --- İ/I ---
    'Ilac': 'İlaç', 'ilac': 'ilaç', 'ilaclarin': 'ilaçların', 'Ilaclarin': 'İlaçların',
    'ilaclar': 'ilaçlar', 'Ilaclar': 'İlaçlar',
    'Ikincil': 'İkincil',
    'Iliskili': 'İlişkili', 'iliskili': 'ilişkili',
    'Iliski': 'İlişki', 'iliski': 'ilişki', 'iliskisi': 'ilişkisi',
    'Ilgili': 'İlgili', 'ilgili': 'ilgili',  # zaten doğru
    'Ileri': 'İleri',
    'Ilk': 'İlk',
    # --- Ç ---
    'cikar': 'çıkar', 'cikin': 'çıkın', 'cikma': 'çıkma', 'cikan': 'çıkan',
    'cocuk': 'çocuk', 'Cocuk': 'Çocuk', 'cocuklarin': 'çocukların',
    'cocukluk': 'çocukluk', 'cocuklarda': 'çocuklarda',
    'cift': 'çift',
    'calisma': 'çalışma', 'calismalarinda': 'çalışmalarında',
    'calismaya': 'çalışmaya',
    'cevre': 'çevre',
    'cene': 'çene',
    # --- Genel kelimeler ---
    'icin': 'için', 'icinde': 'içinde', 'icerir': 'içerir', 'iceren': 'içeren',
    'icerikler': 'içerikler', 'icerikleri': 'içerikleri', 'icermez': 'içermez',
    'icerisinde': 'içerisinde', 'icerigin': 'içeriğin',
    'siklikla': 'sıklıkla', 'sik': 'sık', 'sikligi': 'sıklığı',
    'sirasinda': 'sırasında', 'Sirasinda': 'Sırasında',
    'sicaklik': 'sıcaklık', 'Sicaklik': 'Sıcaklık', 'sicakligi': 'sıcaklığı', 'sicakligini': 'sıcaklığını',
    'sinirlayin': 'sınırlayın', 'Sinirlayin': 'Sınırlayın', 'sinirlamasi': 'sınırlaması',
    'sinira': 'sınıra',
    'salgilanir': 'salgılanır', 'salgilanmasini': 'salgılanmasını', 'salgilanr': 'salgılanır',
    'salgilanmasinda': 'salgılanmasında',
    'surer': 'sürer', 'suren': 'süren', 'suresi': 'süresi', 'sureli': 'süreli',
    'surecin': 'sürecin', 'surede': 'sürede', 'suructur': 'süreçtir',
    'Sure:': 'Süre:', 'Sure ': 'Süre ',
    'surekliligini': 'sürekliliğini',
    'yardimci': 'yardımcı',
    'azalir': 'azalır', 'azalmasi': 'azalması', 'azalmis': 'azalmış', 'Azalmis': 'Azalmış',
    'artar': 'artar',  # doğru
    'artmis': 'artmış', 'artmistir': 'artmıştır',
    'artirma': 'artırma', 'artirmak': 'artırmak', 'artirabilir': 'artırabilir',
    'artirabilecegini': 'artırabilceğini', 'artirir': 'artırır',
    'yapilir': 'yapılır', 'yapilabilir': 'yapılabilir', 'yapilmamis': 'yapılmamış',
    'yaklasim': 'yaklaşım', 'Yaklasim': 'Yaklaşım', 'yaklasimi': 'yaklaşımı',
    'yaklasik': 'yaklaşık',
    'yaygin': 'yaygın', 'Yaygin': 'Yaygın', 'yaygin': 'yaygın',
    'duzensiz': 'düzensiz', 'duzunli': 'düzenli', 'Duzunli': 'Düzenli',
    'duzenli': 'düzenli', 'Duzenli': 'Düzenli',
    'duzenleyici': 'düzenleyici', 'duzenlenmesi': 'düzenlenmesi',
    'norolojik': 'nörolojik', 'Norolojik': 'Nörolojik',
    'noropatolojik': 'nöropatolojik', 'norodejeneratif': 'nörodejeneratif',
    'Norodejeneratif': 'Nörodejeneratif',
    'noroinflamasyon': 'nöroinflamasyon', 'noropati': 'nöropati',
    'Noropati': 'Nöropati', 'noropatii': 'nöropati',
    'yonlu': 'yönlü',
    'yontemleri': 'yöntemleri', 'yontemi': 'yöntemi',
    'Yontemleri': 'Yöntemleri', 'Yontemi': 'Yöntemi',
    'yonlendir': 'yönlendir',
    'gecis': 'geçiş', 'gecen': 'geçen', 'gecirilen': 'geçirilen',
    'gecirmeyin': 'geçirmeyin', 'gecmez': 'geçmez',
    'detayli': 'detaylı',
    'kullanilan': 'kullanılan', 'kullanilabilir': 'kullanılabilir',
    'kullanlmi': 'kullanımı', 'kullanim': 'kullanım', 'kullanilmalidir': 'kullanılmalıdır',
    'tanimlanan': 'tanımlanan', 'tanimlaris': 'tanımlarıs',
    'teshis': 'teşhis',
    'kadinlarda': 'kadınlarda', 'Kadinlarda': 'Kadınlarda',
    'eriskinlerin': 'erişkinlerin', 'Eriskinlerin': 'Erişkinlerin',
    'eriskin': 'erişkin', 'Eriskin': 'Erişkin',
    'guclugu': 'güçlüğü', 'gucluk': 'güçlük', 'guclu': 'güçlü',
    'guclendirin': 'güçlendirin', 'guclenirir': 'güçlenirir',
    'guclenddirmesi': 'güçlendirmesi', 'guclendirmesi': 'güçlendirmesi',
    'guvenli': 'güvenli', 'guvenilirlik': 'güvenilirlik', 'guvenligi': 'güvenliği',
    'gorulur': 'görülür', 'gorulen': 'görülen', 'gorulebilir': 'görülebilir',
    'goruntulenme': 'görüntülenme', 'gorusun': 'görüşün',
    'gorulme': 'görülme',
    'olusur': 'oluşur', 'olusan': 'oluşan', 'olusturur': 'oluşturur',
    'olusabilir': 'oluşabilir',
    'uyaniklik': 'uyanıklık', 'uyanikliga': 'uyanıklığa',
    'uykululugu': 'uykululuğu',
    'orani': 'oranı', 'oraninda': 'oranında',
    'kolaylastirir': 'kolaylaştırır', 'KOLAYLASTIRIR': 'KOLAYLAŞTIRIR',
    'kolaylastirsa': 'kolaylaştırsa',
    'zorlastirir': 'zorlaştırır', 'zorlastiran': 'zorlaştıran',
    'hizlandirir': 'hızlandırır', 'hizlandirarak': 'hızlandırarak',
    'iyilestirici': 'iyileştirici', 'iyilestirir': 'iyileştirir',
    'agrlastiran': 'ağırlaştıran', 'agrlastirirken': 'ağırlaştırırken',
    'kacinma': 'kaçınma', 'kacinin': 'kaçının',
    'kalkin': 'kalkın',
    'yasam': 'yaşam', 'yasamda': 'yaşamda',
    'yasanmasi': 'yaşanması',
    'yas ': 'yaş ', 'Yas ': 'Yaş ',
    'noktüri': 'noktüri',  # zaten doğru
    'fidye': 'fidye',
    'firsati': 'fırsatı',
    'ragmen': 'rağmen',
    'olmasina': 'olmasına',
    'gunduz': 'gündüz', 'Gunduz': 'Gündüz',
    'yuksek': 'yüksek', 'Yuksek': 'Yüksek',
    'kismi': 'kısmi',
    'kisa': 'kısa', 'Kisa': 'Kısa',
    'kalici': 'kalıcı',
    'alinir': 'alınır', 'alinmalidir': 'alınmalıdır',
    'bulunmuyor': 'bulunmuyor',  # doğru
    'yataktan': 'yataktan',  # doğru
    'birakin': 'bırakın', 'birakma': 'bırakma',
    'hissettiginizde': 'hissettiğinizde',
    'uyuyamadiyysaniz': 'uyuyamadıysanız', 'uyuyamadiiysaniz': 'uyuyamadıysanız',
    'uzak': 'uzak',  # doğru
    'olabilir': 'olabilir',  # doğru
    'yapmayin': 'yapmayın',
    'yemeyin': 'yemeyin',  # doğru
    'egzersiz': 'egzersiz',  # doğru
    'egitimi': 'eğitimi', 'egitim': 'eğitim',
    'baharratli': 'baharatlı',
    'gormeyin': 'görmeyin',
    'altin': 'altın', 'Altin': 'Altın',
    'karanlik': 'karanlık', 'Karanlik': 'Karanlık',
    'ayarlamasi': 'ayarlaması', 'ayarlmasi': 'ayarlaması',
    'varsayilar': 'varsayılar',
    'nedeniylee': 'nedeniyle',
    'calisanlari': 'çalışanları',
    'parcasi': 'parçası', 'parçcasi': 'parçası',
    'karsisinda': 'karşısında',
    'karisabilir': 'karışabilir', 'karistirilmamalidir': 'karıştırılmamalıdır',
    'tikenmesi': 'tıkanması',
    'tedavisinde': 'tedavisinde',  # doğru
    'canli': 'canlı',
    'canlandirma': 'canlandırma',
    'hatirlamama': 'hatırlamama',
    'kaldir': 'kaldır',
    'genellikle': 'genellikle',  # doğru
    'kisiye': 'kişiye',
    'hissetmemektir': 'hissetmemektir',  # doğru
    'bilinc': 'bilinç',
    'karmasik': 'karmaşık',
    'fizyolojik': 'fizyolojik',  # doğru
    'uyandirmak': 'uyandırmak',
    'dinlendirici': 'dinlendirici',  # doğru
    'yorgunluk': 'yorgunluk',  # doğru
    'konsantrasyon': 'konsantrasyon',  # doğru
    'Irritabilite': 'İrritabilite',
    'duygudurum': 'duygudurum',  # doğru
    'etkilidir': 'etkilidir',  # doğru
    'bulundurmayin': 'bulundurmayın',
    'sabir': 'sabır',
    'gecikims': 'gecikmiş',
    'Gecikms': 'Gecikmiş',
    'tarafindan': 'tarafından',
    'yenidogan': 'yenidoğan', 'Yenidogan': 'Yenidoğan',
    'nobet': 'nöbet', 'Nobet': 'Nöbet',
    'nobetler': 'nöbetler', 'Nobetler': 'Nöbetler',
    'nobetleri': 'nöbetleri',
    'donem': 'dönem', 'doneminde': 'döneminde',
    'dongusu': 'döngüsü', 'dongusuyle': 'döngüsüyle',
    'dongu': 'döngü', 'dongulerde': 'döngülerde',
    'dongulerin': 'döngülerin',
    'vucut': 'vücut', 'vucudu': 'vücudu', 'vucuduuzzda': 'vücudunuzda',
    'vucudun': 'vücudun',
    'siddet': 'şiddet', 'Siddet': 'Şiddet', 'siddetli': 'şiddetli',
    'seyreder': 'seyreder',  # doğru
    'bolunen': 'bölünen', 'bolunmesi': 'bölünmesi',
    'kurulugu': 'kuruluğu',
    'habercisi': 'habercisi',  # doğru
    'yillar': 'yıllar', 'yil': 'yıl',
    'sonucu': 'sonucu',  # doğru
    'tumoru': 'tümörü',
    'sifirlar': 'sıfırlar',
    'birakma': 'bırakma', 'birakin': 'bırakın',
    'Tablo': 'Tablo',  # doğru
    'gerilemeyi': 'gerilemeyi',  # doğru
    'gerceklesir': 'gerçekleşir',
    'parcalanmasi': 'parçalanması',
    'belirci': 'belirteç',
    'faktoru': 'faktörü', 'faktorleri': 'faktörleri',
    'faktorudur': 'faktörüdür', 'faktorleriyle': 'faktörleriyle',
    'Yas Grubu': 'Yaş Grubu',
    'Onerilen': 'Önerilen',
}


class Command(BaseCommand):
    help = 'Uyku modülü Türkçe karakter düzeltmesi'

    def _fix_text(self, text):
        if not text:
            return text
        # Uzun kelimelerden başla
        sorted_keys = sorted(WORD_MAP.keys(), key=len, reverse=True)
        for old in sorted_keys:
            if old in text:
                text = text.replace(old, WORD_MAP[old])
        return text

    def handle(self, *args, **options):
        count = 0
        for obj in SleepCategory.objects.all():
            obj.name_tr = self._fix_text(obj.name_tr)
            obj.description_tr = self._fix_text(obj.description_tr)
            obj.save()
            count += 1

        for obj in SleepArticle.objects.all():
            obj.title_tr = self._fix_text(obj.title_tr)
            obj.subtitle_tr = self._fix_text(obj.subtitle_tr)
            obj.summary_tr = self._fix_text(obj.summary_tr)
            obj.content_tr = self._fix_text(obj.content_tr)
            obj.meta_title_tr = self._fix_text(obj.meta_title_tr)
            obj.meta_description_tr = self._fix_text(obj.meta_description_tr)
            obj.save()
            count += 1

        for obj in SleepTip.objects.all():
            obj.title_tr = self._fix_text(obj.title_tr)
            obj.content_tr = self._fix_text(obj.content_tr)
            obj.save()
            count += 1

        for obj in SleepFAQ.objects.all():
            obj.question_tr = self._fix_text(obj.question_tr)
            obj.answer_tr = self._fix_text(obj.answer_tr)
            obj.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f'{count} kayıt düzeltildi!'))
