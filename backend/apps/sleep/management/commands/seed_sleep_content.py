"""
Uyku Sağlığı modülü için zengin içerik seed'i.
Mevcut içerikleri düzeltir + yeni makaleler, ipuçları ve SSS ekler.
Tüm Türkçe karakterler doğru kullanılmıştır (ğ, ş, ç, ı, ö, ü, İ).
"""
from django.core.management.base import BaseCommand
from apps.sleep.models import SleepCategory, SleepArticle, SleepTip, SleepFAQ


class Command(BaseCommand):
    help = 'Uyku sağlığı modülüne zengin içerik ekler (Türkçe karakter düzeltmeleri dahil)'

    def handle(self, *args, **options):
        self._fix_categories()
        self._create_articles()
        self._create_tips()
        self._create_faqs()
        total = SleepArticle.objects.filter(is_published=True).count()
        self.stdout.write(self.style.SUCCESS(f'Uyku içerikleri güncellendi! Toplam {total} yayınlanmış makale.'))

    def _fix_categories(self):
        """Mevcut kategorilerdeki Türkçe karakter sorunlarını düzelt."""
        fixes = {
            'uyku-bozukluklari': {
                'name_tr': 'Uyku Bozuklukları',
                'description_tr': 'İnsomnia, uyku apnesi, narkolepsi, parasomni ve diğer uyku bozuklukları hakkında detaylı bilgiler.',
            },
            'uyku-hijyeni': {
                'name_tr': 'Uyku Hijyeni',
                'description_tr': 'Sağlıklı uyku alışkanlıkları, uyku ortamı düzenleme ve uyku kalitesini artırma yöntemleri.',
            },
            'tani-yontemleri': {
                'name_tr': 'Tanı Yöntemleri',
                'description_tr': 'Polisomnografi, aktigrafi, MSLT ve uyku bozukluklarında kullanılan tanı araçları.',
            },
            'hastalikta-uyku': {
                'name_tr': 'Hastalıkta Uyku',
                'description_tr': 'Migren, Alzheimer, Parkinson, diyabet, DEHB ve diğer hastalıklarda uyku özellikleri.',
            },
            'uyku-sagligi': {
                'name_tr': 'Uyku Sağlığı',
                'description_tr': 'Uyku fizyolojisi, uyku evreleri, sirkadiyen ritim ve genel uyku sağlığı bilgileri.',
            },
        }
        for slug, data in fixes.items():
            SleepCategory.objects.filter(slug=slug).update(**data)
        self.stdout.write('  Kategori Türkçe karakterleri düzeltildi.')

    def _create_articles(self):
        cats = {c.slug: c for c in SleepCategory.objects.all()}
        articles = self._get_new_articles(cats)
        created = 0
        updated = 0
        for art in articles:
            _, was_created = SleepArticle.objects.update_or_create(
                slug=art['slug'],
                defaults=art,
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  {created} yeni makale oluşturuldu, {updated} makale güncellendi.')

    def _get_new_articles(self, cats):
        return [
            # ===== UYKU HİJYENİ =====
            {
                'category': cats['uyku-hijyeni'],
                'slug': 'uyku-hijyeni-nedir',
                'article_type': 'hygiene',
                'title_tr': 'Uyku Hijyeni Nedir? Kaliteli Uykunun 12 Altın Kuralı',
                'title_en': 'What is Sleep Hygiene? 12 Golden Rules for Quality Sleep',
                'subtitle_tr': 'Bilimsel kanıtlarla desteklenen uyku hijyeni kuralları ve uygulamaları',
                'subtitle_en': 'Evidence-based sleep hygiene rules and practices',
                'summary_tr': 'Uyku hijyeni, kaliteli ve yeterli uyku için uygulanması gereken davranışsal ve çevresel düzenlemelerin bütünüdür. Bu rehberde bilimsel olarak kanıtlanmış 12 temel kuralı öğreneceksiniz.',
                'summary_en': 'Sleep hygiene encompasses behavioral and environmental adjustments needed for quality, sufficient sleep. In this guide, you will learn 12 scientifically proven fundamental rules.',
                'content_tr': """## Uyku Hijyeni Nedir?

Uyku hijyeni, sağlıklı uyku düzenini destekleyen alışkanlıklar ve çevre koşullarının bütünüdür. Amerikan Uyku Tıbbı Akademisi (AASM) tarafından uyku bozukluklarının tedavisinde ilk basamak olarak önerilmektedir.

İyi bir uyku hijyeni, sadece uykusuzluk çekenlere değil, herkese fayda sağlar. Araştırmalar, uyku hijyeni kurallarına uyanların %65 daha iyi uyku kalitesi bildirdiğini göstermektedir.

## 12 Altın Kural

### 1. Düzenli Uyku Saati Belirleyin

Her gün (hafta sonları dahil) aynı saatte yatağa girin ve aynı saatte kalkın. Vücudunuzun biyolojik saati (sirkadiyen ritim) düzenli programlara ihtiyaç duyar.

- Yatış ve kalkış saatleri arasındaki fark 30 dakikayı geçmemelidir
- Hafta sonu "uyku telafisi" sirkadiyen ritmi bozar
- İdeal uyku süresi yetişkinler için 7-9 saattir

### 2. Yatak Odanızı Uyku İçin Optimize Edin

Yatak odanız sadece uyku ve cinsel aktivite için kullanılmalıdır.

- **Sıcaklık:** 18-20°C ideal oda sıcaklığıdır
- **Karanlık:** Tamamen karartma perdeleri kullanın; melatonin üretimi karanlıkta artar
- **Sessizlik:** Rahatsız edici sesler varsa beyaz gürültü makinesi kullanabilirsiniz
- **Yatak:** Rahat bir yatak ve yastık seçimi uyku kalitesini doğrudan etkiler

### 3. Ekranlardan Uzak Durun

Yatmadan en az 60 dakika önce tüm ekranları (telefon, tablet, bilgisayar, televizyon) kapatın.

- Ekranların yaydığı mavi ışık melatonin üretimini %50'ye kadar baskılayabilir
- Sosyal medya ve haberler beyni uyarır, uykuya geçişi zorlaştırır
- Ekran yerine kitap okumak veya müzik dinlemek tercih edilmelidir

### 4. Kafein Tüketimini Sınırlayın

Öğleden sonra saat 14:00'ten sonra kafeinli içeceklerden kaçının.

- Kafeinin yarı ömrü 5-7 saattir; öğlen içilen kahve gece hâlâ etkili olabilir
- Çay, kola, enerji içecekleri ve çikolatada da kafein bulunur
- Kafeinsiz kahve bile az miktarda kafein içerir
- Bireysel kafein hassasiyeti farklılık gösterir

### 5. Alkol ve Sigaradan Kaçının

Alkol başlangıçta uyutucu etki yapsa da uyku kalitesini ciddi şekilde bozar.

- Alkol REM uykusunu baskılar ve gece uyanmalarını artırır
- Yatmadan en az 4 saat önce alkol tüketimi durdurulmalıdır
- Nikotin uyarıcı etkili bir maddedir; uyku kalitesini düşürür
- Sigara içenler içmeyenlere göre 4 kat daha fazla dinlendirici olmayan uyku bildirmektedir

### 6. Düzenli Egzersiz Yapın

Haftada en az 150 dakika orta yoğunlukta aerobik egzersiz uyku kalitesini artırır.

- Sabah veya öğle saatlerinde yapılan egzersiz en faydalıdır
- Yatmadan 3-4 saat önce yoğun egzersizden kaçının
- Yoga ve esneme hareketleri akşam yapılabilir
- Düzenli egzersiz derin uyku süresini %75'e kadar artırabilir

### 7. Yatmadan Önce Ağır Yemekten Kaçının

Son öğün yatmadan en az 2-3 saat önce yenmelidir.

- Ağır, yağlı ve baharatlı yemekler mide rahatsızlığına neden olabilir
- Aç yatmak da uyku kalitesini bozar; hafif bir atıştırmalık tercih edilebilir
- Triptofan içeren yiyecekler (süt, ceviz, muz) uykuya yardımcı olabilir
- Yatmadan önce aşırı sıvı tüketimi gece tuvalete kalkma ihtiyacını artırır

### 8. Rahatlatıcı Bir Gece Rutini Oluşturun

Yatmadan 30-60 dakika önce sakinleştirici aktiviteler yapın.

- Ilık bir duş veya banyo (vücut sıcaklığındaki düşüş uykuyu tetikler)
- Hafif germe veya nefes egzersizleri
- Meditasyon veya farkındalık uygulamaları
- Sakinleştirici müzik dinleme
- Kitap okuma (kâğıt kitap tercih edin)

### 9. Yatakta Uyanık Kalmayın

20 dakika içinde uyuyamıyorsanız yataktan kalkın.

- Loş ışıklı başka bir odaya geçin
- Sakin bir aktivite yapın (kitap okuma gibi)
- Uykulu hissettiğinizde tekrar yatağa dönün
- Bu teknik "uyaran kontrolü" olarak bilinir ve beyninizin yatağı uykuyla ilişkilendirmesini sağlar

### 10. Gündüz Uykusunu Sınırlayın

Gündüz şekerlemesi yapacaksanız bazı kurallara dikkat edin.

- Maksimum 20-30 dakika ile sınırlandırın
- Saat 15:00'ten sonra gündüz uykusundan kaçının
- Kısa şekerlemeler (power nap) dikkat ve performansı artırır
- Uzun gündüz uykusu gece uykusunu olumsuz etkiler

### 11. Güneş Işığından Faydalanın

Sabah ilk iş güneş ışığına maruz kalın.

- Sabah ışığı sirkadiyen ritmi senkronize eder
- Kalkınca 15-30 dakika doğal ışık alın
- Kış aylarında ışık terapisi lambaları (10.000 lux) kullanılabilir
- Gün içinde dışarıda vakit geçirmek gece uyku kalitesini artırır

### 12. Stres Yönetimini Öğrenin

Yatmadan önce endişe ve kaygılarla mücadele edin.

- "Endişe günlüğü" tutun: yatmadan 2 saat önce kaygılarınızı yazın
- Yapılacaklar listesi hazırlayın, böylece zihniniz rahatlar
- Progresif kas gevşetme tekniği uygulayın
- 4-7-8 nefes tekniği: 4 saniye nefes al, 7 saniye tut, 8 saniye ver

## Ne Zaman Doktora Başvurmalı?

Uyku hijyeni kurallarını 2-4 hafta uygulamanıza rağmen uyku probleminiz devam ediyorsa bir uyku uzmanına başvurun. Altta yatan bir uyku bozukluğu olabilir.

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Sleep Hygiene?

Sleep hygiene is a set of habits and environmental conditions that support healthy sleep patterns. It is recommended by the American Academy of Sleep Medicine (AASM) as the first-line approach for treating sleep disorders.

Good sleep hygiene benefits everyone, not just those suffering from insomnia. Research shows that people who follow sleep hygiene rules report 65% better sleep quality.

## 12 Golden Rules

### 1. Set a Regular Sleep Schedule
Go to bed and wake up at the same time every day, including weekends.

### 2. Optimize Your Bedroom
Keep your bedroom cool (18-20°C), dark, and quiet.

### 3. Avoid Screens Before Bed
Turn off all screens at least 60 minutes before bedtime.

### 4. Limit Caffeine Intake
Avoid caffeinated beverages after 2:00 PM.

### 5. Avoid Alcohol and Tobacco
Both substances significantly impair sleep quality.

### 6. Exercise Regularly
At least 150 minutes of moderate aerobic exercise per week improves sleep.

### 7. Avoid Heavy Meals Before Bed
Eat your last meal at least 2-3 hours before bedtime.

### 8. Create a Relaxing Bedtime Routine
Spend 30-60 minutes on calming activities before sleep.

### 9. Don't Stay Awake in Bed
If you can't sleep within 20 minutes, get up and do a quiet activity.

### 10. Limit Daytime Naps
Keep naps to 20-30 minutes, before 3:00 PM.

### 11. Get Sunlight Exposure
Get 15-30 minutes of natural light in the morning.

### 12. Manage Stress
Use worry journals, breathing exercises, and progressive muscle relaxation.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 8,
                'is_featured': True,
                'is_published': True,
                'order': 1,
                'references': 'Irish LA, et al. The role of sleep hygiene in promoting public health. Sleep Med Rev. 2015;22:23-36.\nStepanski EJ, Wyatt JK. Use of sleep hygiene in the treatment of insomnia. Sleep Med Rev. 2003;7(3):215-225.\nAmerican Academy of Sleep Medicine. Healthy Sleep Habits. 2020.',
            },
            {
                'category': cats['uyku-hijyeni'],
                'slug': 'ideal-yatak-odasi-nasil-olmali',
                'article_type': 'hygiene',
                'title_tr': 'İdeal Yatak Odası Nasıl Olmalı?',
                'title_en': 'How Should the Ideal Bedroom Be?',
                'subtitle_tr': 'Uyku kalitesini artıran yatak odası düzenlemeleri',
                'subtitle_en': 'Bedroom arrangements that improve sleep quality',
                'summary_tr': 'Yatak odanızın sıcaklığı, aydınlatması, ses düzeyi ve düzeni uyku kalitenizi doğrudan etkiler. Bilimsel araştırmalarla desteklenen ideal yatak odası koşullarını öğrenin.',
                'summary_en': 'Your bedroom temperature, lighting, noise level and layout directly affect your sleep quality. Learn ideal bedroom conditions supported by scientific research.',
                'content_tr': """## İdeal Yatak Odası Nasıl Olmalı?

Uyku kalitesinin en önemli belirleyicilerinden biri uyku ortamıdır. National Sleep Foundation araştırmalarına göre, uyku ortamını optimize eden kişiler %72 daha iyi uyku kalitesi bildirmektedir.

## Sıcaklık

Yatak odası sıcaklığı uyku kalitesini etkileyen en kritik faktörlerden biridir.

- **İdeal aralık:** 18-20°C (65-68°F)
- Vücut sıcaklığı uyku öncesi doğal olarak düşer; serin ortam bu süreci destekler
- Çok sıcak odalar REM uykusunu bozar ve gece terlemesine neden olur
- Çok soğuk odalar uykuya dalmayı zorlaştırır
- Nefes alabilen pamuklu çarşaflar ve mevsime uygun yorgan tercih edin

## Aydınlatma

Işık, vücudun melatonin üretimini doğrudan kontrol eder.

- **Tam karanlık** en ideal uyku koşuludur
- Karartma perdeleri veya panjur kullanın
- LED saat ve standby ışıkları bile melatonin üretimini baskılayabilir
- Gece ışığı gerekiyorsa kırmızı veya turuncu tonlarda seçin (mavi ışıktan kaçının)
- Göz bandı etkili ve ucuz bir çözümdür

## Ses

Gürültü, farkında olmasanız bile uyku yapısını bozar.

- Trafik, komşu ve hayvan sesleri mikro uyanmalara neden olur
- **Beyaz gürültü** veya **doğa sesleri** rahatsız edici sesleri maskeler
- Kulak tıkacı, gürültülü ortamlar için etkili bir çözümdür (25-33 dB azaltma)
- Düzenli, monoton sesler uykuyu destekler; ani sesler bozar

## Yatak ve Yastık

Doğru yatak seçimi kronik ağrıyı ve uyku kalitesini doğrudan etkiler.

- Yatak her 7-10 yılda bir değiştirilmelidir
- Orta sertlikte yatak çoğu kişi için idealdir
- Uyku pozisyonunuza uygun yastık seçin:
  - **Sırt üstü:** Orta kalınlıkta, boyun desteği olan yastık
  - **Yan yatış:** Kalın, omuz ile baş arasını dolduran yastık
  - **Yüzüstü:** İnce veya yastıksız (bu pozisyon önerilmez)
- Alerjisi olanlara hipoalerjenik yatak ve kılıf önerilir

## Düzen ve Temizlik

Dağınık ve kirli bir ortam bilinçaltında stres yaratır.

- Yatak odasını düzenli ve sade tutun
- Çalışma masası, bilgisayar ve iş malzemeleri yatak odasında olmamalı
- Haftada bir çarşaf değiştirin
- Yatak odasını havalandırın; temiz hava uyku kalitesini artırır
- Bitki ve çiçekler (lavanta gibi) rahatlatıcı etki yapabilir

## Teknoloji

Yatak odası teknolojiyle mümkün olduğunca az donatılmalıdır.

- Televizyon yatak odasından çıkarılmalıdır
- Telefon şarjı yatak odasının dışında yapılmalıdır
- Akıllı saat yerine geleneksel çalar saat kullanın
- Gece modu veya mavi ışık filtresi yeterli değildir; ekranı tamamen kapatın

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## How Should the Ideal Bedroom Be?

One of the most important determinants of sleep quality is the sleep environment. According to National Sleep Foundation research, people who optimize their sleep environment report 72% better sleep quality.

## Temperature
The ideal bedroom temperature is 18-20°C (65-68°F).

## Lighting
Complete darkness is the most ideal sleep condition. Use blackout curtains.

## Sound
Use white noise or nature sounds to mask disturbing noises.

## Bed and Pillow
Replace your mattress every 7-10 years. Choose pillows suited to your sleep position.

## Organization
Keep the bedroom tidy, simple, and free of work materials.

## Technology
Minimize technology in the bedroom. Remove TVs and charge phones outside.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 5,
                'is_featured': False,
                'is_published': True,
                'order': 2,
                'references': 'National Sleep Foundation. Bedroom Poll. 2012.\nOkamoto-Mizuno K, Mizuno K. Effects of thermal environment on sleep and circadian rhythm. J Physiol Anthropol. 2012;31(1):14.',
            },
            {
                'category': cats['uyku-hijyeni'],
                'slug': 'mavi-isik-ve-ekranlar-uyku-dusmani',
                'article_type': 'hygiene',
                'title_tr': 'Mavi Işık ve Ekranlar: Uykumuzun Görünmez Düşmanı',
                'title_en': 'Blue Light and Screens: The Invisible Enemy of Our Sleep',
                'subtitle_tr': 'Ekranların uyku üzerindeki etkisi ve korunma yolları',
                'subtitle_en': 'The impact of screens on sleep and protection methods',
                'summary_tr': 'Akıllı telefonlar, tabletler ve bilgisayarlardan yayılan mavi ışık melatonin üretimini baskılayarak uyku-uyanıklık döngüsünü bozar. İşte bilmeniz gerekenler ve yapabilecekleriniz.',
                'summary_en': 'Blue light from smartphones, tablets and computers suppresses melatonin production and disrupts the sleep-wake cycle. Here is what you need to know and what you can do.',
                'content_tr': """## Mavi Işık Nedir?

Mavi ışık, görünür ışık spektrumunda 450-490 nanometre dalga boyuna sahip, yüksek enerjili bir ışık türüdür. Güneş ışığında doğal olarak bulunur ve gündüz uyanıklığımızı sağlar. Ancak yapay kaynaklardan (ekranlar, LED aydınlatmalar) gece saatlerinde maruz kalındığında uyku düzenini ciddi şekilde bozar.

## Mavi Işık Uykuyu Nasıl Etkiler?

### Melatonin Baskılanması

Melatonin, beynimizin "uyku hormonu" olarak bilinen ve pineal bezden salgılanan bir hormondur. Karanlık ortamda üretimi artar, ışıkta ise baskılanır.

- Yatmadan 2 saat önce ekran kullanımı melatonin üretimini **%58'e kadar** baskılayabilir
- Melatonin baskılanması uykuya dalma süresini ortalama **30-60 dakika** uzatır
- Mavi ışık, diğer renklere kıyasla melatonini 2 kat daha fazla baskılar

### Sirkadiyen Ritim Kayması

- Gece mavi ışık maruziyeti biyolojik saati **1.5 saate kadar** geciktirebilir
- Bu durum "sosyal jet lag" olarak adlandırılır
- Kronik sirkadiyen ritim kayması obezite, diyabet ve depresyon riskini artırır

### Uyku Yapısı Bozulması

- REM uykusu süresi kısalır
- Derin uyku (N3) evresi azalır
- Gece uyanmaları artar
- Sabah yorgun uyanma hissi oluşur

## Hangi Ekranlar Ne Kadar Mavi Işık Yayar?

| Cihaz | Mavi Işık Yoğunluğu |
|-------|---------------------|
| Akıllı telefon | Yüksek |
| Tablet | Yüksek |
| Dizüstü bilgisayar | Orta-Yüksek |
| Masaüstü monitör | Orta-Yüksek |
| Televizyon | Orta (mesafe nedeniyle) |
| E-kitap okuyucu (e-ink) | Çok düşük |

## Korunma Yolları

### Akşam Rutini
- Yatmadan **60-90 dakika** önce tüm ekranları kapatın
- Bu sürede kitap okuyun, müzik dinleyin veya meditasyon yapın
- Telefonu yatak odasının dışında şarj edin

### Teknolojik Çözümler
- **Gece modu (Night Shift / Night Light):** Mavi ışığı %50-70 azaltır ama tamamen yok etmez
- **Mavi ışık filtreli gözlük:** Akşam zorunlu ekran kullanımında faydalı olabilir
- **f.lux / Twilight gibi uygulamalar:** Ekran rengini gün batımından sonra otomatik sıcak tona çevirir
- **Amber/kırmızı gece lambası:** Yatak odasında mavi ışıksız aydınlatma

### Gündüz Önerileri
- Sabah güneş ışığına çıkmak sirkadiyen ritmi güçlendirir
- Gündüz yeterli doğal ışık almak gece melatonin üretimini artırır
- Her 20 dakikada 20 saniye uzağa bakmak (20-20-20 kuralı) göz yorgunluğunu azaltır

## Çocuklar ve Gençlerde Ekran Etkisi

Çocukların ve gençlerin gözleri mavi ışığa daha hassastır:

- 14 yaş altında mavi ışık retinaya **%60 daha fazla** ulaşır
- Okul çağı çocuklarında ekran kullanımı uyku süresini ortalama **45 dakika** kısaltır
- Amerikan Pediatri Akademisi önerileri:
  - 2 yaş altı: Ekran yok
  - 2-5 yaş: Günde maksimum 1 saat
  - 6+ yaş: Tutarlı sınırlar belirleyin
  - Yatmadan 1 saat önce tüm yaş gruplarında ekran kapatılmalı

## Sonuç

Mavi ışık modern yaşamın kaçınılmaz bir parçasıdır, ancak bilinçli alışkanlıklarla olumsuz etkilerini minimize edebilirsiniz. En önemli adım: yatmadan en az 1 saat önce ekranları kapatmaktır.

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Blue Light?

Blue light is a high-energy light type in the visible spectrum at 450-490 nanometer wavelength. It naturally exists in sunlight and helps maintain our daytime alertness. However, exposure from artificial sources at night seriously disrupts sleep patterns.

## How Does Blue Light Affect Sleep?

Blue light suppresses melatonin production by up to 58%, delays sleep onset by 30-60 minutes, and shifts the circadian rhythm by up to 1.5 hours.

## Protection Methods

- Turn off all screens 60-90 minutes before bed
- Use night mode features on devices
- Get morning sunlight to strengthen circadian rhythm
- Use amber/red night lights in bedrooms

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 7,
                'is_featured': True,
                'is_published': True,
                'order': 3,
                'references': 'Chang AM, et al. Evening use of light-emitting eReaders negatively affects sleep. PNAS. 2015;112(4):1232-1237.\nHarvard Health Publishing. Blue light has a dark side. 2020.\nTouitou Y, et al. Association between light at night, melatonin secretion, sleep deprivation, and the internal clock. Life Sciences. 2017;173:94-106.',
            },
            # ===== UYKU SAĞLIĞI (Genel) =====
            {
                'category': cats['uyku-sagligi'],
                'slug': 'kac-saat-uyumalisiniz',
                'article_type': 'general',
                'title_tr': 'Kaç Saat Uyumalısınız? Yaşa Göre İdeal Uyku Süreleri',
                'title_en': 'How Many Hours Should You Sleep? Ideal Sleep Duration by Age',
                'subtitle_tr': 'Amerikan Uyku Vakfı önerilerine göre yaşa özel uyku süreleri',
                'subtitle_en': 'Age-specific sleep durations according to National Sleep Foundation recommendations',
                'summary_tr': 'Uyku ihtiyacı yaşa göre değişir. Yenidoğanlar 14-17 saat uyurken, yetişkinler için 7-9 saat önerilir. Yetersiz uyku bağışıklık sistemini zayıflatır, obezite ve kalp hastalığı riskini artırır.',
                'summary_en': 'Sleep needs vary by age. While newborns sleep 14-17 hours, 7-9 hours is recommended for adults. Insufficient sleep weakens the immune system and increases obesity and heart disease risk.',
                'content_tr': """## Yaşa Göre İdeal Uyku Süreleri

National Sleep Foundation (Amerikan Uyku Vakfı) tarafından yayınlanan ve 300'den fazla bilimsel çalışmaya dayanan güncel öneriler:

| Yaş Grubu | Önerilen Süre | Kabul Edilebilir Aralık |
|-----------|---------------|------------------------|
| Yenidoğan (0-3 ay) | 14-17 saat | 11-19 saat |
| Bebek (4-11 ay) | 12-15 saat | 10-18 saat |
| Küçük çocuk (1-2 yaş) | 11-14 saat | 9-16 saat |
| Okul öncesi (3-5 yaş) | 10-13 saat | 8-14 saat |
| Okul çağı (6-13 yaş) | 9-11 saat | 7-12 saat |
| Ergen (14-17 yaş) | 8-10 saat | 7-11 saat |
| Genç yetişkin (18-25 yaş) | 7-9 saat | 6-11 saat |
| Yetişkin (26-64 yaş) | 7-9 saat | 6-10 saat |
| Yaşlı (65+ yaş) | 7-8 saat | 5-9 saat |

## Yetersiz Uykunun Sağlığa Etkileri

### Kısa Vadeli Etkiler
- **Bilişsel:** Dikkat dağınıklığı, hafıza sorunları, karar verme güçlüğü
- **Duygusal:** İrritabilite, kaygı, motivasyon düşüklüğü
- **Fiziksel:** Reaksiyon süresinin uzaması (24 saat uyanıklık = 0.10 promil alkol etkisi)
- **Bağışıklık:** Soğuk algınlığına yakalanma riski 4.2 kat artar

### Uzun Vadeli Etkiler
- **Kardiyovasküler:** Kalp krizi riski %48 artar (günde 6 saatten az uyuyanlarda)
- **Metabolik:** Tip 2 diyabet riski %37 artar
- **Obezite:** Yetersiz uyku ghrelin (açlık hormonu) artışı ve leptin (tokluk hormonu) azalmasına neden olur
- **Nörolojik:** Alzheimer hastalığı riski artar (beyin toksik atıkları uyku sırasında temizler)
- **Psikolojik:** Depresyon riski 2.5 kat fazladır

## Fazla Uyumak da Zararlı mı?

Evet, düzenli olarak 9 saatten fazla uyumak da sağlık riskleri taşır:

- Kalp hastalığı riski %38 artar
- Tip 2 diyabet riski artar
- Depresyon belirtileri artabilir
- Altta yatan bir sağlık sorununun işareti olabilir

## Uyku Kalitenizi Nasıl Değerlendirirsiniz?

Yeterli ve kaliteli uyku aldığınızın göstergeleri:

- 30 dakika içinde uykuya dalabiliyorsunuz
- Gece en fazla 1 kez uyanıyorsunuz
- Uyanırsanız 20 dakika içinde tekrar uyuyabiliyorsunuz
- Sabah alarmsız ya da ilk alarmla kalkabiliyorsunuz
- Gündüz dinlenmiş ve enerjik hissediyorsunuz
- Gündüz uykusuna ihtiyaç duymuyorsunuz

## Uyku Sürenizi Nasıl Optimize Edersiniz?

1. **Bir hafta boyunca** alarm kurmadan doğal uyandığınız saati not edin
2. **Uyku günlüğü** tutun: yatış, kalkış, uyanma sayısı
3. Gerçek uyku sürenizi hesaplayın (yatakta geçen süre ≠ uyku süresi)
4. 7-9 saat aralığında **kendi optimalinizi** bulun
5. Düzenli bir program oluşturun ve buna sadık kalın

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## Ideal Sleep Duration by Age

According to the National Sleep Foundation, recommended sleep hours vary significantly by age group. Adults need 7-9 hours, while newborns need 14-17 hours.

## Effects of Insufficient Sleep
Short-term: cognitive impairment, mood issues, weakened immunity.
Long-term: increased risk of heart disease, diabetes, obesity, Alzheimer's, and depression.

## Is Too Much Sleep Harmful?
Yes, regularly sleeping more than 9 hours also carries health risks.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 6,
                'is_featured': True,
                'is_published': True,
                'order': 4,
                'references': 'Hirshkowitz M, et al. National Sleep Foundation sleep time duration recommendations. Sleep Health. 2015;1(1):40-43.\nCohen S, et al. Sleep habits and susceptibility to the common cold. Arch Intern Med. 2009;169(1):62-67.',
            },
            {
                'category': cats['uyku-sagligi'],
                'slug': 'sirkadiyen-ritim-biyolojik-saat',
                'article_type': 'general',
                'title_tr': 'Sirkadiyen Ritim: Vücudumuzun Biyolojik Saati',
                'title_en': 'Circadian Rhythm: Our Body\'s Biological Clock',
                'subtitle_tr': 'Biyolojik saatin uyku, hormonlar ve sağlık üzerindeki etkisi',
                'subtitle_en': 'The impact of biological clock on sleep, hormones and health',
                'summary_tr': 'Sirkadiyen ritim, vücudumuzdaki yaklaşık 24 saatlik biyolojik döngüdür. Uyku-uyanıklık döngüsünden hormon salgılanmasına, vücut sıcaklığından bağışıklık sistemine kadar birçok işlevi düzenler.',
                'summary_en': 'Circadian rhythm is the approximately 24-hour biological cycle in our body that regulates sleep-wake cycles, hormone secretion, body temperature, and immune function.',
                'content_tr': """## Sirkadiyen Ritim Nedir?

Sirkadiyen ritim (Latince "circa" = yaklaşık, "diem" = gün), yaklaşık 24 saatlik periyodlarla tekrarlanan biyolojik döngüdür. 2017 Nobel Tıp Ödülü, sirkadiyen ritmin moleküler mekanizmalarını keşfeden bilim insanlarına verilmiştir.

Vücudumuzdaki "ana saat" beynin hipotalamus bölgesindeki **suprakiyazmatik çekirdekte (SCN)** bulunur. Bu küçük yapı yaklaşık 20.000 nörondan oluşur ve göz retinasından aldığı ışık sinyalleriyle senkronize olur.

## Sirkadiyen Ritim Neyi Kontrol Eder?

### Uyku-Uyanıklık Döngüsü
- Akşam karanlığında melatonin üretimi başlar → uyku hissi
- Sabah ışığında melatonin baskılanır, kortizol yükselir → uyanıklık
- Öğleden sonra hafif bir uykululuk dönemi (13:00-15:00) normaldir

### Hormon Döngüsü
- **Melatonin:** Akşam 21:00-23:00'te yükselmeye başlar, gece 02:00-04:00'te pik yapar
- **Kortizol:** Sabah 06:00-08:00'de en yüksek seviyededir (Cortisol Awakening Response)
- **Büyüme hormonu:** Derin uykunun ilk 3 saatinde pik yapar
- **Leptin/Ghrelin:** Uyku düzeni bozulunca iştah kontrolü bozulur

### Vücut Sıcaklığı
- En düşük: Gece 04:00-05:00 civarı
- En yüksek: Akşam 18:00-19:00 civarı
- Uyku öncesi vücut sıcaklığı düşmeye başlar (uykuyu tetikler)

### Bilişsel Performans
- En yüksek dikkat: Sabah 10:00 civarı
- En iyi koordinasyon: Öğleden sonra 14:30 civarı
- En hızlı reaksiyon: Akşam 15:30 civarı
- En düşük performans: Gece 03:00-05:00 arası

## Kronotip: Sabahçı mısınız, Gececi mi?

Genetik olarak belirlenen uyku-uyanıklık tercihinize "kronotip" denir:

- **Sabahçı tip (Tokuş):** Erken yatar, erken kalkar. Sabah en üretkendir. Toplumun ~%25'i.
- **Gececi tip (Baykuş):** Geç yatar, geç kalkar. Akşam en üretkendir. Toplumun ~%25'i.
- **Ara tip:** Toplumun ~%50'si. Her iki uca da uyum sağlayabilir.

Kronotipinizi zorlamak yerine, mümkünse yaşam düzeninizi kronotipi̇ni̇ze uyarlayın.

## Sirkadiyen Ritmi Bozan Faktörler

### Jet Lag
- Her saat dilimi farkı için 1 gün uyum süresi gerekir
- Doğuya seyahat batıya seyahate göre daha zordur
- Varış yerinin saatine göre yemek ve ışık programı ayarlayın

### Vardiyalı Çalışma
- Gece çalışanlarında kalp hastalığı riski %40 artar
- Vardiya değişimlerinde ileri dönüş (sabah→öğle→gece) tercih edilmelidir
- Stratejik ışık maruziyeti ve karanlık uyku ortamı önemlidir

### Sosyal Jet Lag
- Hafta içi ve hafta sonu uyku saatleri arasındaki 2+ saatlik fark
- Toplumun %87'sini etkiler
- Obezite ve depresyon riski ile ilişkili

## Sirkadiyen Ritmi Güçlendirmenin 5 Yolu

1. **Sabah güneş ışığı:** Kalktıktan sonra 30 dakika içinde doğal ışığa çıkın
2. **Düzenli öğün saatleri:** Yemek saatleri de biyolojik saati etkiler
3. **Akşam loş ışık:** Gün batımından sonra ortam aydınlatmasını azaltın
4. **Düzenli egzersiz:** Tercihen aynı saatte, sabah veya öğle vakti
5. **Tutarlı uyku programı:** Hafta sonları dahil aynı saatlerde uyuyun ve kalkın

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Circadian Rhythm?

Circadian rhythm is a biological cycle that repeats in approximately 24-hour periods. The 2017 Nobel Prize in Medicine was awarded to scientists who discovered its molecular mechanisms.

The "master clock" in our body is located in the suprachiasmatic nucleus (SCN) of the hypothalamus.

## What Does Circadian Rhythm Control?
Sleep-wake cycle, hormones (melatonin, cortisol), body temperature, and cognitive performance.

## Chronotype
Your genetically determined sleep-wake preference: morning type (~25%), evening type (~25%), or intermediate (~50%).

## Factors That Disrupt Circadian Rhythm
Jet lag, shift work, and social jet lag (weekend sleep schedule differences).

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 7,
                'is_featured': True,
                'is_published': True,
                'order': 5,
                'references': 'Nobel Prize Committee. The Nobel Prize in Physiology or Medicine 2017. NobelPrize.org.\nRoenneberg T, et al. Social Jetlag and Obesity. Current Biology. 2012;22(10):939-943.',
            },
            {
                'category': cats['uyku-sagligi'],
                'slug': 'uyku-evreleri-rem-nrem',
                'article_type': 'general',
                'title_tr': 'Uyku Evreleri: REM ve Non-REM Uykusu',
                'title_en': 'Sleep Stages: REM and Non-REM Sleep',
                'subtitle_tr': 'Uyku sırasında beyninizde neler olur?',
                'subtitle_en': 'What happens in your brain during sleep?',
                'summary_tr': 'Uyku homojen bir süreç değildir. Gece boyunca 4-6 kez tekrarlanan döngülerde Non-REM (N1, N2, N3) ve REM evreleri arasında geçiş yaparız. Her evrenin vücut ve beyin için farklı işlevleri vardır.',
                'summary_en': 'Sleep is not a homogeneous process. We cycle through Non-REM (N1, N2, N3) and REM stages 4-6 times per night. Each stage serves different functions for body and brain.',
                'content_tr': """## Uyku Evreleri Nelerdir?

Bir gece uykusu boyunca yaklaşık 90 dakikalık döngüler halinde farklı uyku evreleri arasında geçiş yaparız. Her döngüde Non-REM ve REM evreleri sırasıyla gerçekleşir.

## Non-REM Uykusu

### N1 - Hafif Uyku (Geçiş Evresi)
- Süre: Her döngüde 1-5 dakika
- Toplam uyku süresinin %5'i
- Uyanıklıktan uykuya geçiş
- Kas tonusu yavaşça azalır
- Kolay uyanılabilir
- Hipnagojik halüsinasyonlar (düşmeye başlama hissi) görülebilir

### N2 - Orta Derinlikte Uyku
- Süre: Her döngüde 10-25 dakika
- Toplam uyku süresinin **%45-55**'i (en uzun evre)
- Kalp hızı ve vücut sıcaklığı düşer
- Uyku iğcikleri (sleep spindles) ve K-kompleksleri görülür
- Hafıza konsolidasyonu başlar
- Çevresel uyaranlara duyarlılık azalır

### N3 - Derin Uyku (Yavaş Dalga Uykusu)
- Süre: Her döngüde 20-40 dakika (gecenin ilk yarısında daha uzun)
- Toplam uyku süresinin **%15-20**'si
- **En restoratif evre** - fiziksel onarım burada gerçekleşir
- Büyüme hormonu salgılanır
- Bağışıklık sistemi güçlenir
- Kas ve doku onarımı yapılır
- Beyin toksik atıkları temizler (glimfatik sistem)
- Uyandırılması en zor evre
- Derin uyku eksikliği → gündüz yorgunluk, ağrı hassasiyeti artışı

## REM Uykusu (Hızlı Göz Hareketleri)

- Süre: Her döngüde 10-60 dakika (gecenin ikinci yarısında uzar)
- Toplam uyku süresinin **%20-25**'i
- **Rüyaların çoğu** bu evrede görülür
- Gözler hızla hareket eder
- Vücut kasları geçici olarak felç olur (uyku atonisi - rüyaları fiziksel olarak yaşamamak için)
- **Duygusal hafıza** işlenir ve konsolide edilir
- **Öğrenme ve yaratıcılık** güçlenir
- Beyin aktivitesi uyanıklık dönemine benzer
- REM eksikliği → duygusal dengesizlik, öğrenme güçlüğü

## Bir Gecede Uyku Döngüleri

Tipik bir 8 saatlik uyku yaklaşık **5 döngüden** oluşur:

**1. Döngü (ilk 90 dk):** Çok kısa REM, uzun derin uyku (N3)
**2. Döngü:** N3 hâlâ baskın, REM süresi biraz uzar
**3. Döngü:** N3 azalmaya başlar, REM uzar
**4. Döngü:** Az N3, uzun REM dönemi
**5. Döngü:** N3 neredeyse yok, en uzun REM dönemi (45-60 dk)

Bu nedenle:
- Gecenin **ilk yarısı** fiziksel onarım için kritiktir (derin uyku)
- Gecenin **ikinci yarısı** zihinsel işleme için kritiktir (REM)
- Erken yatıp erken kalkmak her iki evreden de yeterli pay almayı sağlar

## Uyku Kalitesini Etkileyen Faktörler

| Faktör | Derin Uyku Etkisi | REM Etkisi |
|--------|-------------------|------------|
| Alkol | Azaltır | Ciddi baskılar |
| Kafein | Geciktirir | Hafif azaltır |
| Egzersiz | Artırır | Nötr |
| Stres | Azaltır | Bozabilir |
| Yaş | Yaşla azalır | Göreceli stabil |
| Uyku apnesi | Bozar | Ciddi bozar |

## Uyku Evreleri ve Sağlık

- **Derin uyku eksikliği:** Kronik yorgunluk, ağrıya duyarlılık artışı, zayıf bağışıklık
- **REM eksikliği:** Depresyon, anksiyete, öğrenme ve hafıza sorunları
- **Her iki evre yeterli olduğunda:** Fiziksel ve zihinsel performans optimum seviyede

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What Are Sleep Stages?

During a night's sleep, we cycle through different stages approximately every 90 minutes. Each cycle includes Non-REM and REM stages.

## Non-REM Sleep
- N1: Light sleep, transition phase (5% of sleep)
- N2: Medium-depth sleep, memory consolidation begins (45-55%)
- N3: Deep sleep, physical restoration, growth hormone release (15-20%)

## REM Sleep
- Rapid eye movements, vivid dreams (20-25%)
- Emotional memory processing, learning enhancement
- Body muscles temporarily paralyzed

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 7,
                'is_featured': False,
                'is_published': True,
                'order': 6,
                'references': 'Patel AK, et al. Physiology, Sleep Stages. StatPearls. 2023.\nXie L, et al. Sleep drives metabolite clearance from the adult brain. Science. 2013;342(6156):373-377.',
            },
            # ===== UYKU BOZUKLUKLARI =====
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'uyku-apnesi-belirtileri-tedavisi',
                'article_type': 'disorder',
                'title_tr': 'Uyku Apnesi: Belirtileri, Riskleri ve Tedavi Yöntemleri',
                'title_en': 'Sleep Apnea: Symptoms, Risks and Treatment Methods',
                'subtitle_tr': 'Horlama uyku apnesinin habercisi olabilir',
                'subtitle_en': 'Snoring may be a harbinger of sleep apnea',
                'summary_tr': 'Obstrüktif uyku apnesi, uyku sırasında üst hava yolunun tekrarlayan tıkanması ile karakterize ciddi bir uyku bozukluğudur. Tedavi edilmezse kalp krizi, inme ve ani ölüm riskini artırır.',
                'summary_en': 'Obstructive sleep apnea is a serious sleep disorder characterized by repeated upper airway obstruction during sleep. If untreated, it increases risk of heart attack, stroke and sudden death.',
                'content_tr': """## Uyku Apnesi Nedir?

Uyku apnesi, uyku sırasında nefesin tekrarlayan şekilde durması veya azalmasıyla karakterize bir bozukluktur. En yaygın türü **Obstrüktif Uyku Apne Sendromu (OUAS)**'dur.

- Yetişkinlerin **%4-7**'sinde görülür
- Erkeklerde kadınlara göre **2-3 kat** daha sık
- Hastaların **%80**'i tanı almamıştır

### Apne ve Hipopne Nedir?
- **Apne:** Hava akımının en az 10 saniye tamamen durması
- **Hipopne:** Hava akımının en az 10 saniye %50'den fazla azalması
- **Apne-Hipopne İndeksi (AHİ):** Saatte kaç kez apne/hipopne olduğu
  - Normal: < 5
  - Hafif: 5-15
  - Orta: 15-30
  - Ağır: > 30

## Belirtiler

### Gece Belirtileri
- **Horlama:** Genellikle yüksek sesli ve düzensiz
- Nefes durması (partner tarafından fark edilir)
- Boğulma hissiyle uyanma
- Ağız kuruluğu
- Gece sık idrara çıkma (noktüri)
- Aşırı terleme

### Gündüz Belirtileri
- Aşırı gündüz uykululuğu
- Sabah baş ağrısı
- Konsantrasyon güçlüğü ve unutkanlık
- İrritabilite ve depresyon
- Cinsel istek azalması
- Trafik kazası riski 2-7 kat artar

## Risk Faktörleri

- **Obezite:** En önemli risk faktörü (BKİ > 30)
- Boyun çevresi: Erkeklerde > 43 cm, kadınlarda > 38 cm
- Yaş: 40 yaş üstünde risk artar
- Erkek cinsiyet
- Aile öyküsü
- Anatomik faktörler: Büyük bademcik, küçük çene, geniş dil
- Alkol ve sedatif ilaç kullanımı
- Sigara

## Tanı

Kesin tanı **polisomnografi** (uyku laboratuvarında gece testi) ile konur:
- EEG (beyin dalgaları)
- EOG (göz hareketleri)
- EMG (kas aktivitesi)
- Oksimetre (kan oksijen düzeyi)
- Hava akım sensörleri
- Göğüs ve karın hareketleri

**Ev tipi uyku testi** hafif-orta şüphe durumunda alternatif olabilir.

## Tedavi

### Yaşam Tarzı Değişiklikleri
- Kilo verme (BKİ normalleştiğinde AHİ %50-60 azalabilir)
- Alkol ve sedatiflerden kaçınma
- Sırt üstü uyumaktan kaçınma (yan yatış)
- Sigara bırakma

### CPAP (Sürekli Pozitif Hava Yolu Basıncı)
- **Altın standart tedavi**
- Burun maskesi aracılığıyla hava basıncı uygular
- Hava yolunun açık kalmasını sağlar
- Etkisi ilk geceden hissedilir
- Düzenli kullanım gereklidir (gece en az 4 saat)

### Ağız İçi Cihazlar (OAT)
- Hafif-orta uyku apnesinde alternatif
- Alt çeneyi öne konumlandırarak hava yolunu açar
- Diş hekimi tarafından kişiye özel üretilir

### Cerrahi Tedavi
- CPAP'a uyum sağlayamayanlar için
- Uvulopalatofaringoplasti (UPPP)
- Bademcik alınması
- İleri vakalarda çene ilerletme cerrahisi

## Tedavi Edilmezse Ne Olur?

Tedavi edilmeyen uyku apnesi ciddi sağlık sonuçlarına yol açar:
- Hipertansiyon riski 3 kat artar
- Kalp krizi riski %30 artar
- İnme riski 4 kat artar
- Tip 2 diyabet riski 2.5 kat artar
- Ani kardiyak ölüm riski artar (özellikle gece saatlerinde)

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Sleep Apnea?

Sleep apnea is a disorder characterized by repeated stopping or reduction of breathing during sleep. The most common type is Obstructive Sleep Apnea Syndrome (OSAS).

## Symptoms
Night: loud snoring, breathing pauses, choking awakenings.
Day: excessive sleepiness, morning headaches, concentration problems.

## Treatment
CPAP therapy is the gold standard. Weight loss, oral appliances, and surgery are alternatives.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 8,
                'is_featured': True,
                'is_published': True,
                'order': 7,
                'references': 'Benjafield AV, et al. Estimation of the global prevalence and burden of obstructive sleep apnoea. Lancet Respir Med. 2019;7(8):687-698.\nAASM. Clinical Practice Guideline for the Treatment of OSA in Adults. 2019.',
            },
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'huzursuz-bacak-sendromu',
                'article_type': 'disorder',
                'title_tr': 'Huzursuz Bacak Sendromu (RLS)',
                'title_en': 'Restless Legs Syndrome (RLS)',
                'subtitle_tr': 'Bacaklardaki rahatsızlık hissi uykunuzu mu bozuyor?',
                'subtitle_en': 'Is the uncomfortable feeling in your legs disrupting your sleep?',
                'summary_tr': 'Huzursuz bacak sendromu, özellikle dinlenme ve akşam saatlerinde bacaklarda karşı konulamaz bir hareket ettirme ihtiyacı ile karakterize nörolojik bir bozukluktur.',
                'summary_en': 'Restless legs syndrome is a neurological disorder characterized by an irresistible urge to move the legs, especially during rest and evening hours.',
                'content_tr': """## Huzursuz Bacak Sendromu Nedir?

Huzursuz Bacak Sendromu (HBS), bacaklarda karıncalanma, yanma, ağrı veya sızlama gibi rahatsız edici duyumlarla birlikte karşı konulamaz bir hareket ettirme dürtüsü ile karakterize nörolojik bir bozukluktur.

- Yetişkinlerin **%5-10**'unda görülür
- Kadınlarda 2 kat daha sıktır
- Yaşla birlikte sıklığı artar
- Hastaların **%80**'inde periyodik bacak hareketleri de eşlik eder

## Belirtiler

Temel tanı kriterleri (tümü gerekli):

1. **Bacakları hareket ettirme dürtüsü** — genellikle rahatsız edici duyumlarla birlikte
2. **Dinlenme ve hareketsizlikte başlar veya kötüleşir** — oturma, uzanma
3. **Hareketle geçici olarak rahatlar** — yürüme, germe
4. **Akşam ve gece kötüleşir** — sirkadiyen özellik

### Duyumların Tanımlanması
Hastalar genellikle şu ifadeleri kullanır:
- "Bacaklarımın içinde böcek yürüyor gibi"
- "Karıncalanma ve iğne batması"
- "Derin bir sızlama ve çekme hissi"
- "Bacaklarımı hareket ettirmek zorunda hissediyorum"

## Nedenleri

### Birincil (İdiyopatik) HBS
- Genetik yatkınlık (%60 aile öyküsü pozitif)
- Beyindeki dopamin sisteminde işlev bozukluğu
- Demir metabolizması anormalliği

### İkincil HBS
- **Demir eksikliği:** En sık ikincil neden (ferritin < 50 ng/mL)
- **Gebelik:** %25-30 kadında gebeliğin son trimesterinde görülür
- **Böbrek yetmezliği:** Diyaliz hastalarının %30-40'ında
- **Periferik nöropati**
- **İlaçlar:** Antidepresanlar, antihistaminikler, antiemetikler

## Tedavi

### Yaşam Tarzı Değişiklikleri
- Düzenli orta yoğunlukta egzersiz
- Kafein, alkol ve nikotinden kaçınma
- Düzenli uyku programı
- Bacak masajı ve ılık banyo
- Zihinsel olarak dikkat çekici aktiviteler (bulmaca, el işi)

### Demir Takviyesi
- Ferritin < 75 ng/mL ise demir takviyesi önerilir
- Oral demir (demir sülfat 325 mg + C vitamini)
- Ağır vakalarda intravenöz demir

### İlaç Tedavisi
- **Dopamin agonistleri:** Pramipeksol, ropinirol (ilk tercih)
- **Alfa-2-delta ligandları:** Gabapentin, pregabalin
- **Opioidler:** Ağır, dirençli vakalarda
- Tedavi kararı uyku uzmanı tarafından verilmelidir

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Restless Legs Syndrome?

RLS is a neurological disorder characterized by uncomfortable sensations and an irresistible urge to move the legs, primarily during rest and evening hours.

## Symptoms
Urge to move legs, worsens at rest, relieved by movement, worse in evening.

## Treatment
Iron supplementation if deficient, lifestyle changes, dopamine agonists for severe cases.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 6,
                'is_featured': False,
                'is_published': True,
                'order': 8,
                'references': 'Allen RP, et al. Restless legs syndrome/Willis-Ekbom disease diagnostic criteria. Sleep Med. 2014;15(8):860-873.',
            },
            # ===== TANI YÖNTEMLERİ =====
            {
                'category': cats['tani-yontemleri'],
                'slug': 'uyku-gunlugu-nasil-tutulur',
                'article_type': 'diagnosis',
                'title_tr': 'Uyku Günlüğü Nasıl Tutulur?',
                'title_en': 'How to Keep a Sleep Diary?',
                'subtitle_tr': 'Uyku probleminizi anlamanın ilk adımı',
                'subtitle_en': 'The first step to understanding your sleep problem',
                'summary_tr': 'Uyku günlüğü, uyku alışkanlıklarınızı ve sorunlarınızı takip etmek için kullanılan basit ama etkili bir araçtır. Doktorunuza başvurmadan önce en az 2 hafta uyku günlüğü tutmanız önerilir.',
                'summary_en': 'A sleep diary is a simple but effective tool for tracking your sleep habits and problems. It is recommended to keep a sleep diary for at least 2 weeks before visiting your doctor.',
                'content_tr': """## Uyku Günlüğü Nedir?

Uyku günlüğü, günlük uyku alışkanlıklarınızı kaydettiğiniz bir takip aracıdır. Uyku uzmanları, tanı ve tedavi sürecinde hastalardan sıklıkla uyku günlüğü tutmalarını ister.

## Neden Uyku Günlüğü Tutmalısınız?

- Uyku düzeninizi **objektif olarak** görmek için
- Uyku kalitenizi etkileyen **tetikleyicileri** belirlemek için
- Doktora başvurduğunuzda **somut veri** sunmak için
- Tedavi sürecinde **ilerlemeyi** takip etmek için
- Kendi uyku ihtiyacınızı ve **kronotipinizi** keşfetmek için

## Günlük Olarak Neleri Kaydetmelisiniz?

### Akşam (Yatmadan Önce)
- Yatağa girdiğiniz saat
- Gün içinde aldığınız kafeinli içecekler (saat ve miktar)
- Alkol tüketimi (saat ve miktar)
- Egzersiz yapıp yapmadığınız (tür, süre, saat)
- Son yemek saati
- Gün içinde yaşanan stresli olaylar
- Kullandığınız ilaçlar
- Ekran kullanım saatleri

### Sabah (Uyandığınızda)
- Uyandığınız saat
- Yatağa girdikten ne kadar sonra uyuduğunuz (tahmin)
- Gece kaç kez uyandığınız
- Uyanırsanız ne kadar süre uyanık kaldığınız
- Sabah nasıl hissediyorsunuz (1-5 arası puanlayın)
- Rüya görüp görmediğiniz

### Gündüz
- Gündüz uykusu yapıp yapmadığınız (süre ve saat)
- Gündüz enerji seviyeniz (1-5 arası)
- Gündüz uykululuk hissi yaşayıp yaşamadığınız

## Uyku Günlüğü Örneği

| Bilgi | Pazartesi | Salı | Çarşamba |
|-------|-----------|------|----------|
| Yatağa giriş | 23:15 | 23:30 | 23:00 |
| Uykuya dalma süresi | ~25 dk | ~40 dk | ~15 dk |
| Gece uyanma sayısı | 2 | 3 | 1 |
| Sabah kalkış | 07:00 | 06:45 | 07:15 |
| Sabah hissi (1-5) | 3 | 2 | 4 |
| Kafein | 2 kahve (09:00, 14:30) | 3 kahve (09:00, 13:00, 16:00) | 1 kahve (09:00) |
| Egzersiz | 30 dk yürüyüş | Yok | 45 dk yüzme |
| Gündüz uykusu | Yok | 20 dk (14:00) | Yok |
| Ekran (son) | 22:45 | 23:20 | 22:00 |
| Stres düzeyi (1-5) | 3 | 4 | 2 |

## İpuçları

- **En az 2 hafta** kesintisiz tutun
- Sabah uyandığınızda hemen doldurun (unutmadan)
- Saatleri **dakika hassasiyetinde** yazın
- Dürüst olun — "doğru" cevap aramayın
- Telefon uygulaması veya kâğıt defter kullanabilirsiniz
- Doktor randevunuza götürün

## Ne Zaman Doktora Gitmelisiniz?

Uyku günlüğünüz şunları gösteriyorsa bir uyku uzmanına başvurun:

- Haftada 3+ gece uykuya dalma süresi > 30 dakika
- Düzenli olarak gece 3+ kez uyanma
- Sabah sürekli yorgun uyanma
- Gündüz aşırı uyuklama
- 2+ hafta boyunca uyku kalitesi puanı sürekli düşük

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is a Sleep Diary?

A sleep diary is a tracking tool where you record your daily sleep habits. Sleep specialists frequently ask patients to keep one during diagnosis and treatment.

## What to Record
Evening: bedtime, caffeine, alcohol, exercise, screen time.
Morning: wake time, time to fall asleep, night awakenings, morning feeling.
Daytime: naps, energy level, sleepiness.

## Tips
Keep for at least 2 weeks. Fill in immediately upon waking. Be honest.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 5,
                'is_featured': False,
                'is_published': True,
                'order': 9,
                'references': 'Carney CE, et al. The Consensus Sleep Diary. Sleep. 2012;35(2):287-302.',
            },
            # ===== UYKU HİJYENİ - Beslenme =====
            {
                'category': cats['uyku-hijyeni'],
                'slug': 'uyku-ve-beslenme-iliskisi',
                'article_type': 'hygiene',
                'title_tr': 'Uyku ve Beslenme İlişkisi: Ne Yemeli, Ne Yememeli?',
                'title_en': 'Sleep and Nutrition: What to Eat and Avoid',
                'subtitle_tr': 'Uyku kalitesini artıran ve bozan besinler',
                'subtitle_en': 'Foods that improve and impair sleep quality',
                'summary_tr': 'Beslenme alışkanlıklarınız uyku kalitenizi doğrudan etkiler. Triptofan, magnezyum ve melatonin içeren besinler uykuyu desteklerken, kafein, şeker ve ağır yağlı yiyecekler uyku kalitesini bozar.',
                'summary_en': 'Your eating habits directly affect your sleep quality. Foods containing tryptophan, magnesium and melatonin support sleep, while caffeine, sugar and heavy fatty foods impair it.',
                'content_tr': """## Beslenme ve Uyku Arasındaki Bağlantı

Bilimsel araştırmalar, yediğimiz yiyeceklerin uyku kalitesi, süresi ve yapısı üzerinde doğrudan etkisi olduğunu göstermektedir. Akdeniz diyeti gibi dengeli beslenme kalıpları daha iyi uyku kalitesiyle ilişkilendirilmiştir.

## Uykuyu Destekleyen Besinler

### Triptofan Kaynakları
Triptofan, serotonin ve melatonin üretimi için gerekli bir amino asittir.

- **Hindi eti:** En zengin triptofan kaynaklarından biri
- **Süt ve süt ürünleri:** Geleneksel "sıcak süt" tavsiyesinin bilimsel dayanağı
- **Muz:** Triptofan + doğal magnezyum
- **Ceviz:** Triptofan + doğal melatonin içerir
- **Yumurta:** Özellikle sarısı triptofan açısından zengin
- **Tofu ve soya ürünleri**

### Melatonin İçeren Besinler
- **Vişne (özellikle ekşi vişne):** En zengin doğal melatonin kaynağı; vişne suyu uyku süresini 84 dakika artırabilir
- **Ceviz:** 3.5 ng/g melatonin içerir
- **Domates**
- **Çilek ve üzüm**
- **Pirinç** (özellikle jasmine pirinci)

### Magnezyum Kaynakları
Magnezyum kas gevşemesini ve sinir sistemi sakinleşmesini destekler.

- Koyu yeşil yapraklı sebzeler (ıspanak, pazı)
- Badem ve kaju
- Avokado
- Tam tahıllar
- Bitter çikolata (%70+)
- Kabak çekirdeği

### Diğer Destekleyici Besinler
- **Kivi:** Günde 2 kivi yemek uykuya dalma süresini %35 kısaltabilir
- **Yulaf:** Melatonin üretimini destekleyen B6 vitamini içerir
- **Bal:** Az miktarda bal, triptofanın beyine taşınmasını kolaylaştırır
- **Papatya çayı:** Apigenin içerir; hafif sakinleştirici etki

## Uykuyu Bozan Besinler ve İçecekler

### Kafein
- **Yarı ömrü:** 5-7 saat (kişiye göre değişir)
- Saat 14:00'ten sonra tüketilmemelidir
- Gizli kafein kaynakları: çay, kola, çikolata, bazı ağrı kesiciler
- Kafeinsiz kahvede bile 2-15 mg kafein bulunur

### Alkol
- Uykuya dalmayı kolaylaştırır AMA uyku kalitesini bozar
- REM uykusunu baskılar
- Gece uyanmalarını artırır
- Horlama ve uyku apnesini kötüleştirir
- Yatmadan en az 4 saat önce alkol bırakılmalıdır

### Şeker ve Rafine Karbonhidratlar
- Kan şekeri dalgalanmaları gece uyanmalara neden olur
- Yüksek glisemik indeksli yiyecekler uykuya dalma süresini kısaltabilir ama uyku kalitesini bozar
- Akşam tatlısı yerine meyve tercih edin

### Yağlı ve Baharatlı Yiyecekler
- Gastroözofageal reflüyü tetikler
- Sindirim yükü artar, uyku kalitesi düşer
- Yatmadan 3 saat önce ağır yemeklerden kaçının

## İdeal Akşam Atıştırmalıkları

Yatmadan 1-2 saat önce hafif bir atıştırmalık yapılabilir:

- Bir avuç ceviz veya badem
- Bir bardak ılık süt (ballı veya sade)
- Bir muz
- Yulaf ezmesi (küçük porsiyon)
- Tam buğday krakerle peynir
- Papatya veya ıhlamur çayı

## Pratik Öneriler

1. **Son ana öğün** yatmadan en az 2-3 saat önce olsun
2. **Akşam yemeği** hafif ve dengeli olsun
3. **Sıvı alımını** yatmadan 2 saat önce azaltın (gece tuvalete kalkma)
4. **Kafeinli içecekleri** öğleden sonra kesin
5. **Alkol** en geç yatmadan 4 saat önce bırakılsın
6. **Aç yatmak** da uyku kalitesini bozar; hafif bir atıştırmalık yapın

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## The Connection Between Nutrition and Sleep

Scientific research shows that what we eat directly affects sleep quality. Mediterranean diet patterns are associated with better sleep.

## Sleep-Supporting Foods
Tryptophan sources (turkey, milk, banana, walnuts), melatonin-rich foods (tart cherries, walnuts), and magnesium sources (dark leafy greens, almonds).

## Sleep-Disrupting Foods
Caffeine (avoid after 2 PM), alcohol (impairs REM sleep), sugar, and heavy/spicy foods.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 7,
                'is_featured': False,
                'is_published': True,
                'order': 10,
                'references': 'St-Onge MP, et al. Effects of Diet on Sleep Quality. Advances in Nutrition. 2016;7(5):938-949.\nPigeon WR, et al. Effects of a tart cherry juice beverage on the sleep of older adults. J Med Food. 2010;13(3):579-583.',
            },
            # ===== UYKU HİJYENİ - Egzersiz =====
            {
                'category': cats['uyku-hijyeni'],
                'slug': 'egzersiz-ve-uyku-kalitesi',
                'article_type': 'hygiene',
                'title_tr': 'Egzersiz ve Uyku: Hareket Ederek Daha İyi Uyuyun',
                'title_en': 'Exercise and Sleep: Sleep Better by Moving',
                'subtitle_tr': 'Fiziksel aktivitenin uyku üzerindeki olumlu etkileri',
                'subtitle_en': 'Positive effects of physical activity on sleep',
                'summary_tr': 'Düzenli egzersiz, uyku kalitesini artırmanın en etkili doğal yöntemlerinden biridir. Haftada 150 dakika orta yoğunlukta egzersiz, derin uyku süresini artırır ve uykuya dalma süresini kısaltır.',
                'summary_en': 'Regular exercise is one of the most effective natural methods to improve sleep quality. 150 minutes of moderate exercise per week increases deep sleep and shortens sleep onset.',
                'content_tr': """## Egzersiz Neden Uyku Kalitesini Artırır?

Fiziksel aktivitenin uyku üzerindeki olumlu etkileri birçok bilimsel çalışmayla kanıtlanmıştır. Düzenli egzersiz yapan kişiler:

- **%65 daha iyi** uyku kalitesi bildirmektedir
- Uykuya dalma süresi ortalama **13 dakika** kısalır
- Toplam uyku süresi ortalama **42 dakika** uzar
- Derin uyku süresi **%75'e kadar** artabilir

### Fizyolojik Mekanizmalar

1. **Vücut sıcaklığı:** Egzersiz vücut sıcaklığını artırır; sonraki düşüş uyku tetikleyicisidir
2. **Adenozin birikimi:** Fiziksel aktivite uyku baskısını (adenozin) artırır
3. **Anksiyete azalması:** Egzersiz stres hormonlarını (kortizol) düzenler
4. **Sirkadiyen ritim:** Düzenli egzersiz biyolojik saati güçlendirir
5. **Endorfin salınımı:** Genel iyilik hali artar, uyku kalitesi yükselir

## Hangi Egzersiz, Ne Zaman?

### Aerobik Egzersiz
- Yürüyüş, koşu, yüzme, bisiklet
- En çok araştırılmış ve kanıtlanmış tür
- Haftada 150 dakika orta yoğunluk veya 75 dakika yüksek yoğunluk
- **En iyi zamanlama:** Sabah veya öğle

### Direnç Egzersizi (Ağırlık Çalışması)
- Uyku kalitesini artırır ve gece uyanmalarını azaltır
- Haftada 2-3 seans önerilir
- Yatmadan en az 2 saat önce tamamlanmalı

### Yoga ve Esneme
- Yatmadan önce yapılabilecek en güvenli egzersiz türü
- Parasempatik sinir sistemini aktive eder (rahatlama)
- Özellikle strese bağlı uykusuzlukta çok etkili
- Nefes egzersizleriyle birleştirildiğinde etkisi artar

### Tai Chi ve Qigong
- Hafif-orta yoğunlukta hareketler
- Yaşlılarda uyku kalitesini önemli ölçüde artırır
- Her yaşa uygun, düşük sakatlık riski

## Egzersiz Zamanlaması

| Zaman | Uyku Etkisi | Öneri |
|-------|-------------|-------|
| Sabah (06:00-10:00) | En iyi | Sirkadiyen ritmi güçlendirir |
| Öğle (11:00-14:00) | Çok iyi | Gündüz enerjisi artırır |
| Öğleden sonra (14:00-17:00) | İyi | Vücut sıcaklığı pik yapar |
| Akşam (17:00-19:00) | Kabul edilebilir | Hafif-orta yoğunlukta kalın |
| Gece (19:00+) | Dikkatli olun | Yalnızca yoga/esneme |

**Önemli:** Yatmadan 2-3 saat önce yoğun egzersiz yapmak uykuya dalmayı zorlaştırabilir. Ancak bu bireysel farklılık gösterir — bazı kişiler akşam egzersizinden olumsuz etkilenmez.

## Özel Durumlar

### Uykusuzluk Çekenlere Öneriler
- Sabah yürüyüşü ile başlayın (30 dakika)
- Kademeli olarak yoğunluğu artırın
- Akşam yoga veya nefes egzersizi ekleyin
- 4-6 hafta sonra belirgin iyileşme beklenir

### Yaşlılarda Egzersiz
- Düşük yoğunluklu aktiviteler bile faydalıdır
- Yürüyüş, su aerobiği, sandalye egzersizleri
- Uyku ilacı ihtiyacını azaltabilir
- Denge ve koordinasyon da iyileşir

## Pratik Başlangıç Planı

**1. Hafta:** Günde 15 dakika yürüyüş
**2. Hafta:** Günde 20 dakika yürüyüş + 5 dakika esneme
**3. Hafta:** Günde 25 dakika yürüyüş + 10 dakika esneme
**4. Hafta:** 30 dakika yürüyüş + 10 dakika esneme veya yoga

Anahtar: **Düzenlilik** yoğunluktan daha önemlidir. Her gün yapılan 20 dakikalık yürüyüş, haftada bir yapılan 2 saatlik koşudan daha etkilidir.

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## Why Does Exercise Improve Sleep?

Regular exercisers report 65% better sleep quality, fall asleep 13 minutes faster, and sleep 42 minutes longer on average.

## Best Exercise Types
Aerobic: walking, running, swimming. Resistance training. Yoga and stretching (safe before bed).

## Timing
Morning exercise is best for circadian rhythm. Avoid intense exercise 2-3 hours before bed.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 6,
                'is_featured': False,
                'is_published': True,
                'order': 11,
                'references': 'Kredlow MA, et al. The effects of physical activity on sleep: a meta-analytic review. J Behav Med. 2015;38(3):427-449.\nKline CE. The bidirectional relationship between exercise and sleep. Am J Lifestyle Med. 2014;8(6):375-379.',
            },
            # ===== Stres ve Uyku =====
            {
                'category': cats['uyku-hijyeni'],
                'slug': 'stres-kaygi-ve-uykusuzluk',
                'article_type': 'hygiene',
                'title_tr': 'Stres, Kaygı ve Uykusuzluk: Kısır Döngüyü Kırmak',
                'title_en': 'Stress, Anxiety and Insomnia: Breaking the Vicious Cycle',
                'subtitle_tr': 'Stresi yönetmenin uyku kalitesi üzerindeki etkisi',
                'subtitle_en': 'The impact of stress management on sleep quality',
                'summary_tr': 'Stres ve kaygı, uykusuzluğun en yaygın nedenlerinden biridir. Uykusuzluk ise stresi artırarak bir kısır döngü oluşturur. Bu döngüyü kırmak için etkili gevşeme teknikleri ve bilişsel stratejiler mevcuttur.',
                'summary_en': 'Stress and anxiety are among the most common causes of insomnia. Insomnia increases stress, creating a vicious cycle. Effective relaxation techniques and cognitive strategies exist to break this cycle.',
                'content_tr': """## Stres-Uyku Kısır Döngüsü

Stres → uykusuzluk → daha fazla stres → daha kötü uyku... Bu döngü, tedavi edilmezse kronikleşebilir.

### Neler Olur?
- Stres kortizol (stres hormonu) seviyesini yükseltir
- Yüksek kortizol uykuya dalmayı zorlaştırır
- Yetersiz uyku ertesi gün stres toleransını düşürür
- Düşük stres toleransı daha fazla kaygıya neden olur
- Yatağa "acaba bu gece uyuyabilecek miyim?" endişesiyle girilir

## Etkili Gevşeme Teknikleri

### 1. Progresif Kas Gevşetme (PMR)
Vücudunuzdaki her kas grubunu sırayla gerip gevşetme tekniğidir.

**Nasıl Yapılır:**
- Rahat bir pozisyonda uzanın veya oturun
- Ayak parmaklarından başlayarak yukarı doğru ilerleyin
- Her kas grubunu 5 saniye gerin, sonra 10 saniye gevşetin
- Germe ve gevşeme arasındaki farkı hissedin
- Tüm vücudu tamamlamak yaklaşık 15-20 dakika sürer

### 2. 4-7-8 Nefes Tekniği
Dr. Andrew Weil tarafından popülerleştirilen bu teknik parasempatik sinir sistemini aktive eder.

**Nasıl Yapılır:**
- 4 saniye boyunca burundan nefes alın
- 7 saniye boyunca nefesinizi tutun
- 8 saniye boyunca ağızdan yavaşça verin
- 4 döngü tekrarlayın
- Günde 2 kez pratik yapın

### 3. Vücut Tarama Meditasyonu (Body Scan)
Farkındalık (mindfulness) temelli bir teknik.

**Nasıl Yapılır:**
- Sırt üstü rahat uzanın
- Gözlerinizi kapatın
- Dikkatinizi ayak uçlarından başlayarak yavaşça yukarı taşıyın
- Her bölgede duyumları yargılamadan gözlemleyin
- Gerginlik fark ederseniz nefesle birlikte bırakmayı hayal edin
- 10-20 dakika uygulayın

### 4. Endişe Günlüğü ve Planlama Tekniği
Yatmadan 2-3 saat önce yapılacak bir yazma egzersizi.

**Nasıl Yapılır:**
- Bir kâğıda o gün sizi endişelendiren her şeyi yazın
- Her endişenin yanına yapabileceğiniz bir adım yazın
- Yapılacaklar listesi oluşturun (ertesi gün için)
- Kâğıdı kapatın ve "bu endişeler artık kâğıtta, bende değil" deyin
- Bu teknik "yapılandırılmış endişe zamanı" olarak bilinir

### 5. Görselleştirme (Visualization)
Huzurlu bir ortam hayal etme tekniği.

**Nasıl Yapılır:**
- Gözlerinizi kapatın
- Sizi rahatlatan bir mekân hayal edin (sahil, orman, dağ...)
- Tüm duyularınızı kullanın: rüzgârı hissedin, denizi duyun, çiçekleri koklayın
- Bu mekânda güvende ve rahat olduğunuzu hissedin
- 10-15 dakika bu görselleştirmede kalın

## Bilişsel Yaklaşımlar

### Uyku Hakkındaki Olumsuz Düşünceleri Değiştirin

| Olumsuz Düşünce | Gerçekçi Alternatif |
|-----------------|---------------------|
| "Bu gece de uyuyamayacağım" | "Her gece farklıdır; gevşersem uyku gelecektir" |
| "Uyuyamazsam yarın felaket olur" | "Bir gece kötü uyku ciddi sonuçlara yol açmaz" |
| "Hep böyle olacak" | "Uyku sorunları tedavi edilebilir" |
| "8 saat uyumalıyım" | "Kaliteli 6-7 saat, kötü 8 saatten iyidir" |

### Paradoksal Niyet Tekniği
Uyumaya çalışmak yerine, uyanık kalmaya çalışın. Bu paradoks, performans kaygısını azaltır ve ironik olarak uykuya dalmayı kolaylaştırır.

## Yatmadan Önce 5 Adımlık Rahatlama Rutini

1. **22:00** — Ekranları kapatın, loş ışığa geçin
2. **22:15** — Endişe günlüğünü yazın / yapılacaklar listesi
3. **22:30** — Ilık duş veya ayak banyosu
4. **22:45** — Progresif kas gevşetme veya nefes egzersizi
5. **23:00** — Yatağa girin, görselleştirme veya body scan yapın

## Ne Zaman Profesyonel Yardım Almalı?

- Uykusuzluk 4 haftadan uzun sürüyorsa
- Gündüz işlevselliğiniz ciddi şekilde etkileniyorsa
- Kaygı veya depresyon belirtileri varsa
- Kendi kendinize yönetemiyorsanız

**Bilişsel Davranışçı Terapi-İnsomnia (BDT-İ)** kronik uykusuzlukta ilaç tedavisinden daha etkili ve kalıcı sonuçlar veren kanıtlanmış bir tedavi yöntemidir.

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## The Stress-Sleep Vicious Cycle

Stress leads to insomnia, which increases stress, creating a chronic cycle.

## Relaxation Techniques
Progressive Muscle Relaxation, 4-7-8 Breathing, Body Scan Meditation, Worry Journaling, and Visualization.

## Cognitive Approaches
Challenge negative thoughts about sleep. Try paradoxical intention technique.

## When to Get Help
If insomnia lasts more than 4 weeks, CBT-I is the most effective treatment.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 8,
                'is_featured': True,
                'is_published': True,
                'order': 12,
                'references': 'Morin CM, et al. Cognitive Behavioral Therapy for Insomnia. Ann Intern Med. 2006;144:I-34.\nOng JC, et al. A randomized controlled trial of mindfulness meditation for chronic insomnia. Sleep. 2014;37(9):1553-1563.',
            },
        ]

    def _create_tips(self):
        tips = [
            {
                'title_tr': 'Düzenli Uyku Saati',
                'title_en': 'Regular Sleep Schedule',
                'content_tr': 'Her gün (hafta sonları dahil) aynı saatte yatın ve kalkın. Vücudunuzun biyolojik saati düzenli programa ihtiyaç duyar.',
                'content_en': 'Go to bed and wake up at the same time every day, including weekends.',
                'icon': 'clock',
                'order': 1,
            },
            {
                'title_tr': 'Ekranlardan Uzak Durun',
                'title_en': 'Avoid Screens',
                'content_tr': 'Yatmadan en az 60 dakika önce telefon, tablet ve bilgisayarı kapatın. Mavi ışık melatonin üretimini baskılar.',
                'content_en': 'Turn off phones, tablets and computers at least 60 minutes before bed.',
                'icon': 'smartphone-off',
                'order': 2,
            },
            {
                'title_tr': 'Serin Yatak Odası',
                'title_en': 'Cool Bedroom',
                'content_tr': 'Yatak odası sıcaklığını 18-20°C arasında tutun. Serin ortam daha derin ve kaliteli uyku sağlar.',
                'content_en': 'Keep bedroom temperature between 18-20°C for deeper, better quality sleep.',
                'icon': 'thermometer',
                'order': 3,
            },
            {
                'title_tr': 'Kafeine Dikkat',
                'title_en': 'Watch Your Caffeine',
                'content_tr': 'Öğleden sonra saat 14:00\'ten sonra kahve, çay ve kola içmekten kaçının. Kafeinin yarı ömrü 5-7 saattir.',
                'content_en': 'Avoid coffee, tea and cola after 2:00 PM. Caffeine has a half-life of 5-7 hours.',
                'icon': 'coffee',
                'order': 4,
            },
            {
                'title_tr': 'Sabah Güneş Işığı',
                'title_en': 'Morning Sunlight',
                'content_tr': 'Sabah kalktığınızda 15-30 dakika doğal güneş ışığına çıkın. Bu, sirkadiyen ritminizi güçlendirir.',
                'content_en': 'Get 15-30 minutes of natural sunlight after waking to strengthen your circadian rhythm.',
                'icon': 'sun',
                'order': 5,
            },
            {
                'title_tr': '20 Dakika Kuralı',
                'title_en': '20-Minute Rule',
                'content_tr': 'Yatakta 20 dakikadan fazla uyanık kalmayın. Uyuyamıyorsanız kalkın, sakin bir aktivite yapın ve uykulu hissettiğinizde dönün.',
                'content_en': 'Don\'t stay awake in bed for more than 20 minutes. If you can\'t sleep, get up and return when sleepy.',
                'icon': 'timer',
                'order': 6,
            },
            {
                'title_tr': 'Rahatlatıcı Akşam Rutini',
                'title_en': 'Relaxing Evening Routine',
                'content_tr': 'Yatmadan 30 dakika önce ılık duş, hafif esneme veya kitap okuma gibi rahatlatıcı aktiviteler yapın.',
                'content_en': 'Do relaxing activities like warm shower, light stretching or reading 30 minutes before bed.',
                'icon': 'moon',
                'order': 7,
            },
            {
                'title_tr': 'Hafif Akşam Yemeği',
                'title_en': 'Light Dinner',
                'content_tr': 'Son yemeğinizi yatmadan en az 2-3 saat önce yiyin. Ağır ve baharatlı yemeklerden kaçının.',
                'content_en': 'Eat your last meal at least 2-3 hours before bed. Avoid heavy and spicy foods.',
                'icon': 'utensils',
                'order': 8,
            },
            {
                'title_tr': 'Günlük Egzersiz',
                'title_en': 'Daily Exercise',
                'content_tr': 'Günde en az 30 dakika orta yoğunlukta egzersiz yapın (yürüyüş bile yeterli). Ancak yatmadan 3 saat önce yoğun egzersizden kaçının.',
                'content_en': 'Do at least 30 minutes of moderate exercise daily. Avoid intense exercise within 3 hours of bedtime.',
                'icon': 'activity',
                'order': 9,
            },
            {
                'title_tr': 'Karanlık Yatak Odası',
                'title_en': 'Dark Bedroom',
                'content_tr': 'Karartma perdeleri kullanın ve LED saatleri örtün. Karanlık ortam melatonin üretimini artırır.',
                'content_en': 'Use blackout curtains and cover LED clocks. Darkness increases melatonin production.',
                'icon': 'eye-off',
                'order': 10,
            },
            {
                'title_tr': 'Alkol Uykuyu Bozar',
                'title_en': 'Alcohol Disrupts Sleep',
                'content_tr': 'Alkol uyutucu görünse de uyku kalitesini ciddi şekilde bozar. REM uykusunu baskılar ve gece uyanmalarını artırır.',
                'content_en': 'Alcohol may seem sedating but seriously impairs sleep quality and suppresses REM sleep.',
                'icon': 'wine-off',
                'order': 11,
            },
            {
                'title_tr': '4-7-8 Nefes Tekniği',
                'title_en': '4-7-8 Breathing Technique',
                'content_tr': '4 saniye nefes alın, 7 saniye tutun, 8 saniye verin. Bu teknik parasempatik sinir sistemini aktive ederek uykuya dalmayı kolaylaştırır.',
                'content_en': 'Breathe in for 4 seconds, hold for 7, exhale for 8. This activates the parasympathetic nervous system.',
                'icon': 'wind',
                'order': 12,
            },
        ]

        for tip_data in tips:
            SleepTip.objects.update_or_create(
                title_tr=tip_data['title_tr'],
                defaults=tip_data,
            )
        self.stdout.write(f'  {len(tips)} ipucu oluşturuldu/güncellendi.')

    def _create_faqs(self):
        cats = {c.slug: c for c in SleepCategory.objects.all()}
        faqs = [
            {
                'question_tr': 'Yetişkinler kaç saat uyumalıdır?',
                'question_en': 'How many hours should adults sleep?',
                'answer_tr': 'Amerikan Uyku Vakfı\'na göre yetişkinler (18-64 yaş) günde 7-9 saat, 65 yaş üstü bireyler 7-8 saat uyumalıdır. Ancak bireysel ihtiyaçlar farklılık gösterebilir. Sabah alarmsız uyanabiliyor ve gündüz enerjik hissediyorsanız yeterli uyku alıyorsunuz demektir.',
                'answer_en': 'According to the National Sleep Foundation, adults (18-64) should sleep 7-9 hours daily, and those over 65 should sleep 7-8 hours. Individual needs may vary.',
                'category': cats['uyku-sagligi'],
                'order': 1,
            },
            {
                'question_tr': 'Uyku hijyeni nedir ve neden önemlidir?',
                'question_en': 'What is sleep hygiene and why is it important?',
                'answer_tr': 'Uyku hijyeni, sağlıklı uyku düzenini destekleyen davranışsal ve çevresel düzenlemelerdir. Düzenli uyku saati, serin ve karanlık yatak odası, yatmadan önce ekran kullanmama, kafein sınırlama gibi alışkanlıkları kapsar. İyi uyku hijyeni, uyku kalitesini %65\'e kadar artırabilir ve birçok uyku bozukluğunun tedavisinde ilk basamak olarak önerilir.',
                'answer_en': 'Sleep hygiene encompasses behavioral and environmental adjustments supporting healthy sleep. It can improve sleep quality by up to 65% and is recommended as first-line treatment for many sleep disorders.',
                'category': cats['uyku-hijyeni'],
                'order': 2,
            },
            {
                'question_tr': 'Gündüz uykusu (şekerleme) zararlı mıdır?',
                'question_en': 'Are daytime naps harmful?',
                'answer_tr': 'Kısa gündüz uykusu (20-30 dakika, saat 15:00\'ten önce) dikkat, performans ve ruh halini iyileştirir. Ancak 30 dakikadan uzun veya geç saatte yapılan gündüz uykusu gece uykusunu olumsuz etkileyebilir. Kronik uykusuzluk çekiyorsanız gündüz uykusundan kaçınmanız önerilir.',
                'answer_en': 'Short naps (20-30 minutes, before 3 PM) improve attention, performance and mood. However, naps longer than 30 minutes or late in the day can negatively affect nighttime sleep.',
                'category': cats['uyku-sagligi'],
                'order': 3,
            },
            {
                'question_tr': 'Horlama ne zaman ciddi bir sorun olabilir?',
                'question_en': 'When can snoring be a serious problem?',
                'answer_tr': 'Horlama, yüksek sesli ve düzensiz olduğunda, nefes durmalarıyla birlikte olduğunda veya gündüz aşırı uykululuğa neden olduğunda ciddi olabilir. Bu belirtiler obstrüktif uyku apnesine işaret edebilir. Uyku apnesi tedavi edilmezse kalp krizi, inme ve ani ölüm riskini artırır. Horlayan ve gündüz uyuklayan herkes bir uyku uzmanına başvurmalıdır.',
                'answer_en': 'Snoring can be serious when loud and irregular, accompanied by breathing pauses, or causing excessive daytime sleepiness. These symptoms may indicate obstructive sleep apnea.',
                'category': cats['uyku-bozukluklari'],
                'order': 4,
            },
            {
                'question_tr': 'Mavi ışık uykuyu nasıl etkiler?',
                'question_en': 'How does blue light affect sleep?',
                'answer_tr': 'Ekranlardan yayılan mavi ışık, melatonin (uyku hormonu) üretimini %58\'e kadar baskılayabilir. Bu durum uykuya dalma süresini 30-60 dakika uzatır ve biyolojik saati 1.5 saate kadar geciktirir. Yatmadan en az 60 dakika önce ekranları kapatmanız önerilir. Gece modu filtreleri yardımcı olabilir ama ekranı kapatmak kadar etkili değildir.',
                'answer_en': 'Blue light from screens can suppress melatonin production by up to 58%, extending time to fall asleep by 30-60 minutes. Turn off screens at least 60 minutes before bed.',
                'category': cats['uyku-hijyeni'],
                'order': 5,
            },
            {
                'question_tr': 'Alkol uykuya yardımcı olur mu?',
                'question_en': 'Does alcohol help with sleep?',
                'answer_tr': 'Hayır. Alkol başlangıçta uyutucu etki yapsa da uyku kalitesini ciddi şekilde bozar. REM uykusunu baskılar, gece uyanmalarını artırır ve horlama ile uyku apnesini kötüleştirir. Düzenli alkol tüketimi uyku bozukluklarının en önemli nedenlerinden biridir.',
                'answer_en': 'No. Although alcohol initially has a sedating effect, it seriously impairs sleep quality by suppressing REM sleep and increasing nighttime awakenings.',
                'category': cats['uyku-hijyeni'],
                'order': 6,
            },
            {
                'question_tr': 'Uyku ilacı kullanmalı mıyım?',
                'question_en': 'Should I use sleeping pills?',
                'answer_tr': 'Uyku ilaçları kısa süreli kullanım için reçete edilebilir, ancak uzun vadeli çözüm değildir. Bağımlılık riski, tolerans gelişimi ve gündüz sersemliği gibi yan etkileri vardır. Bilişsel Davranışçı Terapi (BDT-İ) kronik uykusuzlukta ilaçtan daha etkili ve kalıcı sonuçlar verir. Herhangi bir uyku ilacı kullanmadan önce mutlaka doktorunuza danışın.',
                'answer_en': 'Sleep medications can be prescribed for short-term use but are not a long-term solution. CBT-I is more effective than medication for chronic insomnia. Always consult your doctor.',
                'category': cats['uyku-bozukluklari'],
                'order': 7,
            },
            {
                'question_tr': 'Hafta sonu uyku telafisi yapılabilir mi?',
                'question_en': 'Can you make up for lost sleep on weekends?',
                'answer_tr': 'Kısmen. Bir-iki gecelik uyku borcunu hafta sonu telafi edebilirsiniz, ancak kronik uyku borcu tam olarak geri ödenmez. Dahası, hafta sonu geç yatıp geç kalkmak "sosyal jet lag" yaratır ve sirkadiyen ritmi bozar. En sağlıklı yaklaşım her gün aynı saatte uyumak ve kalkmaktır.',
                'answer_en': 'Partially. You can recover from one or two nights of sleep debt, but chronic sleep debt cannot be fully repaid. Weekend sleep-ins create "social jet lag" disrupting circadian rhythm.',
                'category': cats['uyku-sagligi'],
                'order': 8,
            },
            {
                'question_tr': 'Rüya görmek normal midir?',
                'question_en': 'Is dreaming normal?',
                'answer_tr': 'Evet, herkes rüya görür. Rüyalar ağırlıklı olarak REM uykusu döneminde görülür ve duygusal hafızanın işlenmesinde, öğrenmenin pekiştirilmesinde ve yaratıcılığın artmasında önemli rol oynar. Rüyaları hatırlamamak rüya görmediğiniz anlamına gelmez. Kabus sıklığı stres ve travma ile artabilir.',
                'answer_en': 'Yes, everyone dreams. Dreams occur primarily during REM sleep and play important roles in emotional memory processing and learning consolidation. Not remembering dreams does not mean you did not dream.',
                'category': cats['uyku-sagligi'],
                'order': 9,
            },
            {
                'question_tr': 'Ne zaman bir uyku uzmanına başvurmalıyım?',
                'question_en': 'When should I see a sleep specialist?',
                'answer_tr': 'Şu durumlarda uyku uzmanına başvurmanız önerilir: 4 haftadan uzun süren uykusuzluk, gündüz aşırı uyuklama, yüksek sesli ve düzensiz horlama, uyku sırasında nefes durmaları, bacaklarda huzursuzluk hissi, gece sık uyanma, sabah sürekli baş ağrısı, veya uyku hijyeni kurallarına rağmen düzelmeyen uyku kalitesi.',
                'answer_en': 'See a sleep specialist if you have: insomnia lasting over 4 weeks, excessive daytime sleepiness, loud snoring, breathing pauses during sleep, restless legs, frequent night awakenings, or persistent morning headaches.',
                'category': cats['uyku-bozukluklari'],
                'order': 10,
            },
        ]

        for faq_data in faqs:
            SleepFAQ.objects.update_or_create(
                question_tr=faq_data['question_tr'],
                defaults=faq_data,
            )
        self.stdout.write(f'  {len(faqs)} SSS oluşturuldu/güncellendi.')
