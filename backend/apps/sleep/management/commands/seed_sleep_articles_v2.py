"""
Uyku Sağlığı modülü - Ek makaleler (v2).
Uyku terörü, REM davranış bozukluğu, uyurgezerlik, enürezis nokturna,
Parkinson'da uyku, gebelerde uyku bozuklukları.
"""
from django.core.management.base import BaseCommand
from apps.sleep.models import SleepCategory, SleepArticle


class Command(BaseCommand):
    help = 'Uyku modülüne ek hastalık ve bozukluk makaleleri ekler'

    def handle(self, *args, **options):
        cats = {c.slug: c for c in SleepCategory.objects.all()}
        articles = self._get_articles(cats)
        created = 0
        for art in articles:
            _, was_created = SleepArticle.objects.update_or_create(
                slug=art['slug'],
                defaults=art,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} yeni makale eklendi.'))

    def _get_articles(self, cats):
        return [
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'uyku-teroru-gece-dehseti',
                'article_type': 'disorder',
                'title_tr': 'Uyku Terörü (Gece Dehşeti): Nedenleri, Belirtileri ve Tedavisi',
                'title_en': 'Sleep Terror (Night Terror): Causes, Symptoms and Treatment',
                'subtitle_tr': 'Çocuklarda sık görülen ama yetişkinlerde de yaşanabilen korkutucu uyku bozukluğu',
                'subtitle_en': 'A frightening sleep disorder common in children but also occurring in adults',
                'summary_tr': 'Uyku terörü, derin uyku sırasında ani çığlık, ağlama ve yoğun korku ile karakterize bir parasomnidir. Çocukların %1-6\'sında görülür ve genellikle yaşla birlikte kendiliğinden geçer.',
                'summary_en': 'Sleep terror is a parasomnia characterized by sudden screaming, crying and intense fear during deep sleep. It occurs in 1-6% of children and usually resolves spontaneously with age.',
                'content_tr': """## Uyku Terörü Nedir?

Uyku terörü (gece dehşeti, pavor nokturnus), derin uyku (Non-REM N3) evresinden kısmi uyanma ile ortaya çıkan bir parasomni türüdür. Kâbustan farklı olarak, uyku terörü sırasında kişi tam olarak uyanmaz ve genellikle ertesi gün olayı hatırlamaz.

## Epidemiyoloji

- **Çocuklarda:** %1-6 oranında görülür (3-8 yaş arası pik yapar)
- **Yetişkinlerde:** %1-2 oranında görülür
- Erkek çocuklarda kızlara göre daha sık
- Aile öyküsü pozitif ise risk 10 kat artar
- Çoğu çocuk 12 yaşına kadar kendiliğinden iyileşir

## Belirtiler

### Tipik Bir Atak

Genellikle gecenin **ilk üçte birinde** (yatıştan 1-3 saat sonra) gerçekleşir:

1. Kişi aniden yatakta doğrulur
2. Yüksek sesle çığlık atar veya ağlar
3. Gözler açık ama çevreyi tanımaz
4. Yoğun korku ifadesi, terleme, kalp çarpıntısı
5. Sakinleştirme girişimlerine yanıt vermez, hatta ajitasyon artabilir
6. Atak 1-10 dakika sürer (nadiren 30 dakikaya kadar)
7. Kişi kendiliğinden sakinleşir ve uyumaya devam eder
8. **Ertesi sabah hiçbir şey hatırlamaz** (amnezi)

### Kâbustan Farkları

| Özellik | Uyku Terörü | Kâbus |
|---------|-------------|-------|
| Uyku evresi | Non-REM (derin uyku) | REM |
| Zamanlama | Gecenin ilk 1/3'ü | Gecenin son 1/3'ü |
| Uyanma | Kısmi (tam uyanmaz) | Tam uyanma |
| Hatırlama | Hatırlamaz | Canlı hatırlar |
| Motor aktivite | Çığlık, oturma, yürüme | Minimal |
| Otonomik belirtiler | Belirgin (terleme, taşikardi) | Hafif |

## Nedenleri

### Tetikleyici Faktörler
- **Uyku yoksunluğu** — en güçlü tetikleyici
- Ateşli hastalıklar
- Stres ve kaygı
- Uyku programı değişiklikleri
- Dolu mesane (özellikle çocuklarda)
- Gürültü veya dokunma ile kısmi uyandırma
- Bazı ilaçlar (sedatifler, lityum)

### Risk Faktörleri
- Genetik yatkınlık (aile öyküsü %80)
- Uyku apnesi veya diğer uyku bozuklukları
- Huzursuz bacak sendromu
- Gastroözofageal reflü
- Yetişkinlerde: PTSD, anksiyete, depresyon

## Tedavi

### Çocuklarda
- **Güvenceye alma:** Ebeveynlere durumun zararsız olduğu açıklanır
- **Uyku hijyeni:** Düzenli uyku programı, yeterli uyku süresi
- **Güvenlik önlemleri:** Yatak çevresi, merdiven kapıları
- **Planlanmış uyanma:** Atak saatinden 15-30 dakika önce hafifçe uyandırma (5 gece)
- İlaç tedavisi nadiren gerekir

### Yetişkinlerde
- Altta yatan nedenlerin tedavisi (uyku apnesi, stres, ilaç yan etkileri)
- Bilişsel davranışçı terapi
- Gerekirse düşük doz benzodiazepin (kısa süreli)
- Hipnoz bazı vakalarda etkili olabilir

## Ne Zaman Doktora Başvurmalı?

- Ataklar haftada birden fazla tekrarlıyorsa
- Yetişkinlerde ilk kez başladıysa
- Kişi kendine veya başkalarına zarar veriyorsa
- Gündüz işlevselliğini etkiliyorsa
- 12 yaşından sonra devam ediyorsa

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Sleep Terror?

Sleep terror is a parasomnia arising from partial arousal during deep sleep (Non-REM N3). Unlike nightmares, the person does not fully wake up and usually has no memory of the event.

## Key Features
- Occurs in first third of night, lasts 1-10 minutes
- Screaming, intense fear, autonomic arousal
- No memory next morning
- Common in children (1-6%), resolves with age

## Treatment
Reassurance, sleep hygiene, scheduled awakenings for children. Address underlying causes in adults.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 10,
                'is_featured': False,
                'is_published': True,
                'order': 20,
                'cover_image_url': 'https://images.unsplash.com/photo-1511406361295-0a1ff814a0ce?w=800&h=450&fit=crop',
                'references': 'Fleetham JA, Fleming JAE. Parasomnias. CMAJ. 2014;186(8):E273-E280.\nAmerican Academy of Sleep Medicine. ICSD-3. 2014.',
            },
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'rem-uyku-davraris-bozuklugu',
                'article_type': 'disorder',
                'title_tr': 'REM Uyku Davranış Bozukluğu (RBD): Rüyalarınızı Yaşıyor Olabilir misiniz?',
                'title_en': 'REM Sleep Behavior Disorder (RBD): Could You Be Acting Out Your Dreams?',
                'subtitle_tr': 'Uyku sırasında rüyaları fiziksel olarak yaşamak: tanı ve tedavi',
                'subtitle_en': 'Physically acting out dreams during sleep: diagnosis and treatment',
                'summary_tr': 'REM uyku davranış bozukluğu, normalde REM uykusunda gerçekleşen kas atonisinin (gevşekliğinin) kaybolmasıyla rüyaların fiziksel olarak yaşanmasıdır. Parkinson ve Lewy cisimcikli demans gibi nörodejeneratif hastalıkların erken habercisi olabilir.',
                'summary_en': 'REM sleep behavior disorder occurs when the normal muscle atonia during REM sleep is lost, causing physical enactment of dreams. It may be an early herald of neurodegenerative diseases like Parkinson\'s.',
                'content_tr': """## REM Uyku Davranış Bozukluğu Nedir?

Normal REM uykusunda vücut kasları geçici olarak felç olur (atoni) — bu mekanizma rüyalarımızı fiziksel olarak yaşamamızı engeller. REM uyku davranış bozukluğunda (RBD) bu koruyucu mekanizma bozulur ve kişi rüyalarını gerçekten yaşar: konuşur, bağırır, tekme atar, yumruk sallar, hatta yataktan düşer.

## Epidemiyoloji

- 50 yaş üstü kişilerin **%0.5-1**'inde görülür
- **Erkeklerde** kadınlara göre 9 kat daha sık
- Ortalama başlangıç yaşı: 60-70
- RBD tanısı alanların **%80-90**'ında 10-15 yıl içinde nörodejeneratif hastalık gelişir

## Belirtiler

### Uyku Sırasında
- Rüya içeriğiyle uyumlu hareketler (yumruk atma, tekmeleme, koşma)
- Bağırma, küfretme veya ağlama
- Yataktan düşme
- Yatak partnerini istemeden yaralama
- Canlı, aksiyon dolu rüyalar (kovalanma, kavga, savunma)

### Dikkat Çekici Özellikler
- Ataklar genellikle gecenin **ikinci yarısında** (REM yoğun dönem)
- Uyandırıldığında rüyayı net hatırlar
- Uyanıkken davranış ve kişilik tamamen normal
- Rüyalar genellikle şiddet veya tehdit içerikli

## Nörodejeneratif Hastalıklarla İlişki

RBD, aşağıdaki hastalıkların **erken (prodromal) belirtisi** olabilir:

- **Parkinson hastalığı** — RBD'li hastaların %40-65'inde gelişir
- **Lewy cisimcikli demans** — RBD'li hastaların %25-50'sinde gelişir
- **Multisistem atrofisi** — RBD'li hastaların %10-15'inde gelişir

Bu nedenle RBD tanısı alan kişiler düzenli nörolojik takip altında olmalıdır.

### Biomarker Olarak RBD

RBD, alfa-sinüklein patolojisinin en erken klinik belirtilerinden biridir. Motor belirtiler (tremor, bradykinezi) ortaya çıkmadan **10-15 yıl önce** başlayabilir. Bu, nöroprotektif tedavilerin geliştirilmesi için önemli bir zaman penceresi sunar.

## Tanı

### Polisomnografi (PSG)
- **Altın standart tanı yöntemi**
- REM uykusunda kas atonisi kaybı (EMG'de artmış kas aktivitesi)
- Video kaydıyla rüya canlandırma davranışları görülür

### Ayırıcı Tanı
- Uyku terörü (Non-REM parasomni)
- Noktürnal epileptik nöbetler
- Obstrüktif uyku apnesi ile ilişkili hareket
- PTSD ile ilişkili kâbuslar

## Tedavi

### İlaç Tedavisi
- **Klonazepam (0.25-2 mg):** Altın standart, %90 etkili
- **Melatonin (3-12 mg):** Daha güvenli alternatif, özellikle yaşlılarda
- Her iki ilaç da semptomları kontrol eder ama nörodejeneratif süreci durdurmaz

### Güvenlik Önlemleri (Kritik Önem)
- Yatağın yanındaki sert/keskin nesneleri uzaklaştırın
- Yatağı alçaltın veya yere yatak koyun
- Cam eşyaları yatak odasından çıkarın
- Pencereleri kilitleyin
- Yatak partnerinin güvenliğini sağlayın
- Gerekirse ayrı yataklarda uyuma düşünülebilir

### Uzun Vadeli Takip
- 6 ayda bir nörolojik muayene
- Koku alma testi (hiposmi erken Parkinson belirtisi)
- Bilişsel testler
- Gerekirse beyin görüntüleme (DaTSCAN)

## Ne Zaman Doktora Başvurmalı?

- Uyku sırasında tekrarlayan anormal hareketler
- Yatak partnerinizin rüyada hareket ettiğinizi söylemesi
- Yataktan düşme
- Uykuda yaralanma
- 50 yaş üstünde yeni başlayan canlı rüyalar

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is REM Sleep Behavior Disorder?

In RBD, the normal muscle paralysis during REM sleep is lost, causing people to physically act out their dreams. It predominantly affects men over 50 and may be an early sign of Parkinson's or Lewy body dementia.

## Neurodegenerative Disease Link
80-90% of RBD patients develop a neurodegenerative disease within 10-15 years.

## Treatment
Clonazepam or melatonin for symptom control. Safety measures are critical. Regular neurological follow-up recommended.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 10,
                'is_featured': True,
                'is_published': True,
                'order': 21,
                'cover_image_url': 'https://images.unsplash.com/photo-1520206183501-b80df61043c2?w=800&h=450&fit=crop',
                'references': 'Iranzo A, et al. Neurodegenerative disease status and post-mortem pathology in idiopathic REM sleep behaviour disorder. Lancet Neurol. 2013;12(5):443-453.\nAASM. ICSD-3. 2014.',
            },
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'uyurgezerlik-somnambulizm',
                'article_type': 'disorder',
                'title_tr': 'Uyurgezerlik (Somnambülizm): Nedenleri ve Güvenlik Önlemleri',
                'title_en': 'Sleepwalking (Somnambulism): Causes and Safety Measures',
                'subtitle_tr': 'Uyku sırasında bilinçsiz yürüme ve karmaşık davranışlar',
                'subtitle_en': 'Unconscious walking and complex behaviors during sleep',
                'summary_tr': 'Uyurgezerlik, derin uyku sırasında (Non-REM N3) bilinçsiz olarak yataktan kalkma, yürüme ve bazen karmaşık aktiviteler yapma durumudur. Çocuklarda %15\'e varan oranda görülür ve genellikle ergenlikte kendiliğinden geçer.',
                'summary_en': 'Sleepwalking involves unconsciously getting out of bed, walking, and sometimes performing complex activities during deep sleep. It occurs in up to 15% of children and usually resolves in adolescence.',
                'content_tr': """## Uyurgezerlik Nedir?

Uyurgezerlik (somnambülizm), derin uyku evresinden (Non-REM N3) kısmi uyanma ile ortaya çıkan bir parasomnidir. Kişi uyuyor gibi görünür ama yürüme ve bazen karmaşık motor aktiviteler gerçekleştirir.

## Epidemiyoloji

- **Çocuklarda:** %1-15 (pik yaş: 8-12)
- **Yetişkinlerde:** %1-4
- Aile öyküsü pozitifse risk **10 kat** artar
- Her iki ebeveyn uyurgezer ise çocuktaki risk **%60**
- Çoğu çocuk ergenlikte iyileşir

## Belirtiler ve Davranış Kalıpları

### Basit Davranışlar
- Yatakta oturma ve etrafına bakınma
- Yataktan kalkma ve odada dolaşma
- Kapıları açma
- Evin içinde amaçsız yürüme

### Karmaşık Davranışlar (Daha Nadir)
- Giyinme veya soyunma
- Yemek yeme (uyku ile ilişkili yeme bozukluğu)
- Banyo kullanma
- Konuşma (anlaşılmaz veya basit cümleler)
- Ev dışına çıkma
- Araç kullanma (çok nadir ama tehlikeli)

### Tipik Özellikler
- Gözler açık ama bakışlar boş ve donuk
- İletişim kurulamaz veya çok sınırlı
- Uyandırılması zordur; uyandırılırsa konfüzyon yaşar
- Atak süresi: genellikle 5-15 dakika (nadiren 1 saate kadar)
- **Ertesi gün hatırlamaz** veya çok bulanık hatırlar

## Nedenleri ve Tetikleyiciler

### Genetik Faktörler
- HLA-DQB1*05:01 geni ile güçlü ilişki
- Birinci derece akrabalarda uyurgezerlik öyküsü → risk 10 kat

### Tetikleyiciler
- **Uyku yoksunluğu** — en önemli tetikleyici
- Ateşli hastalıklar
- Stres ve kaygı
- Alkol kullanımı
- Bazı ilaçlar (zolpidem, lityum, fenotiyazinler)
- Dolu mesane
- Gürültü
- Obstrüktif uyku apnesi (kısmi uyanma tetikler)

## Güvenlik Önlemleri (Çok Önemli)

### Ev İçi Güvenlik
- Cam kapı ve pencereleri kilitleyin
- Merdivenlere güvenlik kapısı takın
- Keskin ve kırılabilir nesneleri güvenli yere kaldırın
- Yere takılma riski olan kabloları, halı kenarlarını düzeltin
- Çocuklarda ranza kullanmayın
- Yatak odasının kapısına alarm/zil takın

### Atak Sırasında
- Kişiyi **zorla uyandırmaya çalışmayın** — konfüzyon ve ajitasyon artabilir
- Nazikçe yatağa geri yönlendirin
- Tehlikeli bir durumda değilse müdahale etmeyin
- Sakin, düşük sesle konuşun

## Tedavi

### İlaç Dışı Yaklaşımlar
- Düzenli ve yeterli uyku sağlama
- Uyku hijyeni kurallarına uyma
- Stres yönetimi
- **Planlanmış uyanma:** Atak saatinden 15-30 dakika önce hafifçe uyandırma
- Hipnoz (bazı çalışmalarda etkili bulunmuştur)

### İlaç Tedavisi (Ağır Vakalarda)
- Klonazepam (düşük doz)
- SSRI antidepresanlar (bazı vakalarda)
- Melatonin
- Altta yatan uyku apnesi varsa CPAP tedavisi

## Ne Zaman Doktora Başvurmalı?

- Ataklar sık tekrarlıyorsa (haftada birden fazla)
- Kişi kendine veya başkalarına zarar veriyorsa
- Gündüz aşırı uykululuk eşlik ediyorsa
- Yetişkinlikte yeni başladıysa
- 12 yaşından sonra devam ediyorsa
- Diğer uyku bozuklukları eşlik ediyorsa

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Sleepwalking?

Sleepwalking involves unconsciously getting out of bed and walking during deep sleep. It ranges from simple walking to complex behaviors like eating or leaving the house.

## Key Facts
- Affects up to 15% of children, 1-4% of adults
- Strong genetic component (10x risk with family history)
- Usually resolves by adolescence

## Safety is Critical
Lock windows and doors, install stair gates, remove sharp objects. Don't forcefully wake a sleepwalker.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 10,
                'is_featured': False,
                'is_published': True,
                'order': 22,
                'cover_image_url': 'https://images.unsplash.com/photo-1511406361295-0a1ff814a0ce?w=800&h=450&fit=crop',
                'references': 'Stallman HM, Kohler M. Prevalence of Sleepwalking: A Systematic Review and Meta-Analysis. PLoS One. 2016;11(11):e0164769.\nAASM. ICSD-3. 2014.',
            },
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'enurezis-nokturna-gece-islatmasi',
                'article_type': 'disorder',
                'title_tr': 'Enürezis Nokturna (Gece İşlatması): Nedenleri ve Tedavi Yaklaşımları',
                'title_en': 'Nocturnal Enuresis (Bedwetting): Causes and Treatment Approaches',
                'subtitle_tr': 'Çocuklarda yaygın bir sorun: gece idrar kaçırma',
                'subtitle_en': 'A common problem in children: bedwetting',
                'summary_tr': 'Enürezis nokturna, 5 yaşından sonra ayda en az 2 kez uyku sırasında istemsiz idrar kaçırma olarak tanımlanır. Çocukların %15-20\'sinde görülür ve çoğu kendiliğinden düzelir, ancak tedavi süreci hızlandırabilir.',
                'summary_en': 'Nocturnal enuresis is defined as involuntary urination during sleep at least twice a month after age 5. It occurs in 15-20% of children and usually resolves spontaneously.',
                'content_tr': """## Enürezis Nokturna Nedir?

Enürezis nokturna (gece işlatması), 5 yaşını geçmiş çocuklarda uyku sırasında istemsiz idrar kaçırma durumudur. Birçok ebeveynin düşündüğünden çok daha yaygındır ve çocuğun suçu değildir.

## Epidemiyoloji

| Yaş | Prevalans |
|-----|-----------|
| 5 yaş | %15-20 |
| 7 yaş | %10 |
| 10 yaş | %5 |
| 15 yaş | %1-2 |
| Yetişkin | %0.5-1 |

- Erkek çocuklarda kızlara göre **2 kat** daha sık
- Her yıl kendiliğinden düzelme oranı: **%15**
- Aile öyküsü güçlü: Bir ebeveyn enüretik ise risk %44, her ikisi de ise %77

## Türleri

### Primer Enürezis
- Çocuk hiçbir zaman 6 aydan uzun kuru dönem geçirmemiş
- En yaygın form (%75-80)
- Genellikle maturasyonel gecikme

### Sekonder Enürezis
- En az 6 ay kuru dönemden sonra yeniden başlama
- Altta yatan tıbbi veya psikolojik neden araştırılmalı
- Stres, travma, enfeksiyon, diyabet akla gelmeli

## Nedenleri

### Fizyolojik Faktörler
- **Gece ADH (antidiüretik hormon) üretimi yetersizliği:** Gece idrar üretimi artmış
- **Mesane kapasitesi küçüklüğü:** Fonksiyonel mesane kapasitesi yaş ortalamasının altında
- **Derin uyku:** Mesane doluluk sinyallerine uyanamama
- **Gelişimsel gecikme:** Mesane-beyin koordinasyonunun olgunlaşmaması

### Genetik Faktörler
- ENUR1 (kromozom 13q), ENUR2 (kromozom 12q) genleri tanımlanmış
- Genetik yatkınlık %77'ye kadar çıkabilir

### İkincil Nedenler
- İdrar yolu enfeksiyonu
- Kabızlık (rektum mesaneye baskı yapar)
- Uyku apnesi
- Tip 1 diyabet
- Nörolojik problemler (nadir)
- Psikolojik stres (aile içi sorunlar, okul değişikliği, kardeş doğumu)

## Tedavi

### Davranışsal Yaklaşımlar (İlk Basamak)

**Alarm Tedavisi:**
- En etkili uzun vadeli tedavi (%65-75 başarı)
- Nem algılayıcı alarm ıslanma başladığında çocuğu uyandırır
- Çocuk uyanır, tuvalete gider, çarşafı değiştirir
- 2-3 ay düzenli kullanım gerekir
- "Koşullanma" prensibiyle çalışır

**Destekleyici Önlemler:**
- Çocuğu **asla cezalandırmayın veya utandırmayın**
- Kuru geceleri takdir edin ve ödüllendirin (çıkartma takvimi)
- Yatmadan önce tuvalete gitme alışkanlığı
- Akşam sıvı alımını sınırlandırma (yatmadan 2 saat önce)
- Kafeinli içeceklerden kaçınma

### İlaç Tedavisi

**Desmopressin (DDAVP):**
- Gece ADH üretimini taklit eder, idrar üretimini azaltır
- Hızlı etki (%70 yanıt), ancak bırakınca %60-70 nüks
- Kamp, misafirlik gibi durumlarda kısa süreli kullanım için ideal
- Sıvı kısıtlaması ile birlikte kullanılmalı (su intoksikasyonu riski)

**Oksibutinin:**
- Aşırı aktif mesanesi olan çocuklarda
- Mesane kapasitesini artırır

### Kombinasyon Tedavisi
- Alarm + desmopressin: Tek başına alamdan daha etkili olabilir

## Ebeveynlere Önemli Mesajlar

1. **Bu çocuğunuzun suçu değildir** — tembelllik veya davranış problemi değildir
2. Çoğu çocuk kendiliğinden düzelir — sabırlı olun
3. Cezalandırma durumu **kötüleştirir**
4. Tedavi seçenekleri mevcuttur — utanmadan doktora başvurun
5. Çocuğunuzun özgüvenini korumak en önemli önceliktir

## Ne Zaman Doktora Başvurmalı?

- 7 yaşından sonra devam eden gece işlatması
- Daha önce kuru iken yeniden başlayan işlatma (sekonder)
- Gündüz de idrar kaçırma varsa
- Ağrılı veya sık idrar yapma
- Aşırı susuzluk
- Horlama veya uyku apnesi belirtileri
- Kabızlık eşlik ediyorsa

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## What is Nocturnal Enuresis?

Nocturnal enuresis (bedwetting) is involuntary urination during sleep in children over 5 years. It affects 15-20% of 5-year-olds and has strong genetic links.

## Key Points
- Not the child's fault — never punish
- Alarm therapy is most effective long-term treatment (65-75% success)
- Desmopressin provides quick relief for special occasions
- Most children outgrow it naturally

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 10,
                'is_featured': False,
                'is_published': True,
                'order': 23,
                'cover_image_url': 'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&h=450&fit=crop',
                'references': 'Nevéus T, et al. Evaluation of and treatment for monosymptomatic enuresis. J Urol. 2010;183(2):441-447.\nAmerican Academy of Pediatrics. Management of Primary Nocturnal Enuresis. 2014.',
            },
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'parkinson-hastaliginda-uyku-bozukluklari-detayli',
                'article_type': 'disease_sleep',
                'title_tr': 'Parkinson Hastalığında Uyku Bozuklukları: Kapsamlı Rehber',
                'title_en': 'Sleep Disorders in Parkinson\'s Disease: Comprehensive Guide',
                'subtitle_tr': 'Motor belirtilerden önce başlayabilen uyku sorunları',
                'subtitle_en': 'Sleep problems that may begin before motor symptoms',
                'summary_tr': 'Parkinson hastalarının %60-90\'ında uyku bozukluğu görülür. REM uyku davranış bozukluğu, uykusuzluk, gündüz aşırı uykululuğu ve noktüri en yaygın sorunlardır. Uyku bozuklukları motor belirtilerden yıllar önce başlayabilir.',
                'summary_en': 'Sleep disorders occur in 60-90% of Parkinson\'s patients. RBD, insomnia, excessive daytime sleepiness and nocturia are most common. Sleep problems may begin years before motor symptoms.',
                'content_tr': """## Parkinson ve Uyku İlişkisi

Parkinson hastalığı sadece tremor, yavaşlama ve sertlikten ibaret değildir. Hastaların **%60-90**'ı yaşamları boyunca en az bir uyku bozukluğu yaşar. Uyku sorunları motor belirtilerden **10-15 yıl önce** başlayabilir ve yaşam kalitesini ciddi şekilde etkiler.

## Parkinson'da Görülen Uyku Bozuklukları

### 1. REM Uyku Davranış Bozukluğu (RBD)
- Parkinson hastalarının **%30-60**'ında görülür
- Motor belirtilerden **yıllar önce** başlayabilir (prodromal dönem)
- Rüyaları fiziksel olarak yaşama: tekmeleme, yumruklama, bağırma
- Yatak partnerinin yaralanma riski
- **Tedavi:** Klonazepam veya melatonin

### 2. İnsomnia (Uykusuzluk)
- **%30-40** oranında görülür
- Uykuya dalma güçlüğü, gece sık uyanma, sabah erken uyanma
- Nedenleri: Motor belirtiler (tremor, rijidite), ağrı, ilaç yan etkileri, anksiyete, noktüri
- Gece dönme güçlüğü (yatak içi mobilite azalması)
- **Tedavi:** Uyku hijyeni, BDT-İ, ilaç düzenlemesi

### 3. Aşırı Gündüz Uykululuğu (AGU)
- Hastaların **%30-50**'sinde görülür
- Dopaminerjik ilaçların yan etkisi olabilir
- "Uyku atakları" — aniden ve uyarı olmaksızın uykuya dalma (araç kullanırken tehlike!)
- **Tedavi:** İlaç dozlarının ayarlanması, modafinil

### 4. Noktüri (Gece İdrar İhtiyacı)
- **%60-80** oranında görülür
- Otonomik disfonksiyon nedeniyle
- Her gece 2-5 kez tuvalete kalkma
- Uyku parçalanması ve düşme riskini artırır
- **Tedavi:** Akşam sıvı kısıtlaması, desmopressin (dikkatli kullanım)

### 5. Huzursuz Bacak Sendromu ve Periyodik Bacak Hareketleri
- **%15-20** oranında görülür
- Dopaminerjik tedavi ile kısmen düzelebilir ama "augmentasyon" riski var
- Demir düzeyleri kontrol edilmeli

### 6. Uyku Apnesi
- Parkinson hastalarında genel popülasyondan daha sık
- Tanı genellikle atlanır — polisomnografi önemli
- CPAP tedavisi uyku kalitesini ve bilişsel fonksiyonları iyileştirebilir

## Parkinson İlaçlarının Uyku Üzerine Etkileri

| İlaç | Olumlu Etki | Olumsuz Etki |
|------|-------------|--------------|
| Levodopa | Gece motor belirtileri azaltır | Canlı rüyalar, halüsinasyonlar |
| Dopamin agonistleri | Huzursuz bacak düzeltir | Gündüz uykululuğu, uyku atakları |
| MAO-B inhibitörleri | - | Uykusuzluk (sabah alınmalı) |
| Amantadin | - | Uykusuzluk, canlı rüyalar |
| Antikolinerjikler | - | REM uykusu baskılanması |

## Tedavi Yaklaşımları

### Genel Uyku Hijyeni
- Düzenli uyku-uyanma programı
- Yatak odasını karanlık, serin ve sessiz tutma
- Yatmadan önce ekranlardan uzak durma
- Akşam hafif egzersiz (germe, yürüyüş)

### Motor Belirtilerin Gece Yönetimi
- Uzun etkili levodopa formülasyonları (gece boyunca etki)
- Saten çarşaflar (yatakta dönmeyi kolaylaştırır)
- Yatak kenarlarına tutunma barları
- Gece giyilebilir cihazlar (titreşimli hatırlatıcılar)

### Psikolojik Destek
- Uyku ile ilgili kaygıyı azaltma
- BDT-İ (insomnia için bilişsel davranışçı terapi)
- Depresyon tedavisi (antidepresanlar + psikoterapi)

## Bakım Verenlere Öneriler

- Hastanın gece güvenliğini sağlayın (düşme riski)
- RBD atakları sırasında sakin olun, hastayı koruyun
- Uyku değişikliklerini nöroloğa bildirin
- Kendinizin de uyku kalitesine dikkat edin (bakıcı tükenmişliği)

## Ne Zaman Doktora Başvurmalı?

- Gece hareket artışı veya rüyaları yaşama
- Gündüz kontrol edilemeyen uykululuk
- Uyku ilacı ihtiyacı
- Yeni başlayan horlama veya nefes durması
- İlaç değişikliği sonrası uyku bozulması

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez.""",
                'content_en': """## Parkinson's and Sleep

60-90% of Parkinson's patients experience at least one sleep disorder. These may begin 10-15 years before motor symptoms.

## Common Sleep Problems
RBD (30-60%), insomnia (30-40%), excessive daytime sleepiness (30-50%), nocturia (60-80%).

## Treatment
Medication adjustments, sleep hygiene, safety measures for RBD, CPAP for sleep apnea.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 10,
                'is_featured': True,
                'is_published': True,
                'order': 24,
                'related_disease': 'parkinson',
                'cover_image_url': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800&h=450&fit=crop',
                'references': 'Videnovic A, Golombek D. Circadian and sleep disorders in Parkinson\'s disease. Exp Neurol. 2013;243:45-56.\nSchenck CH, et al. REM sleep behavior disorder. Curr Opin Neurol. 2014;27(4):471-478.',
            },
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'gebelikte-uyku-bozukluklari',
                'article_type': 'disease_sleep',
                'title_tr': 'Gebelikte Uyku Bozuklukları: Trimestere Göre Sorunlar ve Çözümler',
                'title_en': 'Sleep Disorders in Pregnancy: Problems and Solutions by Trimester',
                'subtitle_tr': 'Hamilelik döneminde uyku kalitesi neden bozulur ve ne yapılabilir?',
                'subtitle_en': 'Why does sleep quality deteriorate during pregnancy and what can be done?',
                'summary_tr': 'Gebelerin %75\'inden fazlası uyku sorunları yaşar. Hormonal değişiklikler, fiziksel rahatsızlıklar ve psikolojik faktörler her trimesterde farklı uyku bozukluklarına neden olur. Güvenli çözümler mevcuttur.',
                'summary_en': 'More than 75% of pregnant women experience sleep problems. Hormonal changes, physical discomfort, and psychological factors cause different sleep disorders in each trimester.',
                'content_tr': """## Gebelikte Uyku Neden Bozulur?

Gebelik, kadın vücudunda dramatik hormonal, fiziksel ve psikolojik değişikliklere neden olur. Bu değişikliklerin çoğu uyku kalitesini doğrudan etkiler. Araştırmalara göre gebelerin **%75-80**'i uyku sorunları yaşar ve uyku kalitesi gebelik ilerledikçe kötüleşir.

## Trimestere Göre Uyku Sorunları

### 1. Trimester (1-12. Hafta)

**Hormonal Değişiklikler:**
- Progesteron artışı → aşırı uyku hali ve gündüz uykululuğu
- Progesteron aynı zamanda sık idrara çıkmaya neden olur
- hCG hormonu → bulantı (sabah hastalığı ama gece de etkileyebilir)

**Yaygın Sorunlar:**
- Gündüz aşırı uyku hali (%80)
- Sık idrara çıkma (%60)
- Mide bulantısı ve kusma (%50-70)
- Göğüslerde hassasiyet → rahat pozisyon bulamama
- Duygusal dalgalanmalar → anksiyete ile uykusuzluk

### 2. Trimester (13-27. Hafta)

Genellikle **en iyi dönem** — birçok kadın rahatlar.

**Yaygın Sorunlar:**
- Canlı ve tuhaf rüyalar (hormonal etki)
- Bacak krampları (%30)
- Burun tıkanıklığı (progesteron etkisi → horlama başlangıcı)
- Reflü başlangıcı
- Huzursuz bacak sendromu başlayabilir

### 3. Trimester (28-40. Hafta)

**En zorlu dönem** — uyku kalitesi en düşük seviyeye iner.

**Yaygın Sorunlar:**
- **Sık idrara çıkma** (%90) — bebeğin mesaneye baskısı
- **Rahat pozisyon bulamama** — büyüyen karın
- **Sırt ve kalça ağrısı** (%60)
- **Reflü** (%50-80) — uterus mideye baskı yapar
- **Huzursuz bacak sendromu** (%25-30)
- **Horlama ve uyku apnesi** (%15-25)
- **Sık idrara çıkma** ve gece uyanmaları
- **Doğum kaygısı** ve anksiyete

## Gebelikte Huzursuz Bacak Sendromu

- Gebelerin **%25-30**'unda görülür (genel popülasyonda %5-10)
- Özellikle 3. trimesterde sık
- Demir ve folat eksikliği ile ilişkili
- **Tedavi:** Demir takviyesi (ferritin < 75 ng/mL ise), magnezyum, hafif egzersiz
- İlaç tedavisi gebelikte sınırlıdır — nörolog konsültasyonu gerektirir

## Gebelikte Uyku Apnesi

- Gebelikte gelişen obezite, ödem ve burun tıkanıklığı uyku apnesini tetikleyebilir
- **Riskleri:** Gestasyonel diyabet (%2-3x), preeklampsi (%2-3x), preterm doğum
- Tedavi edilmezse hem anne hem bebek sağlığını tehdit eder
- **Tedavi:** CPAP (gebelikte güvenli)

## Güvenli Uyku Pozisyonları

### Önerilen: Sol Yan Yatış (SOS — Sleep On Side)
- Vena kava inferior baskısını önler
- Plasenta kan akışını optimize eder
- Dizlerin arasına yastık koyma rahatlatır
- Sırt arkasına destek yastık

### Kaçınılması Gereken: Sırt Üstü (3. Trimester)
- Büyük damarlar üzerine baskı → tansiyon düşmesi, baş dönmesi
- Uteroplasental kan akışı azalması
- Ölü doğum riskinde artış (araştırmalarla desteklenmiş)

## Gebelikte Güvenli Uyku Stratejileri

### Yapılması Gerekenler
- **Gebelik yastığı** kullanın (U veya C şeklinde)
- Düzenli hafif egzersiz (yürüyüş, yüzme, prenatal yoga)
- Yatmadan 2 saat önce sıvı alımını azaltın
- Küçük ve sık öğünler yiyin (reflü için)
- Yatak başını hafifçe yükseltin (reflü için)
- Gevşeme teknikleri (nefes egzersizleri, meditasyon)
- Demir, folat, magnezyum takviyeleri (doktor önerisiyle)

### Kaçınılması Gerekenler
- Kafeinli içecekler (özellikle öğleden sonra)
- Ağır akşam yemeği
- Uyku ilacı (doktor onayı olmadan ASLA)
- Uzun gündüz uykuları
- Yatakta ekran kullanımı
- Bitkisel çaylar (bazıları gebelikte güvenli değildir — doktora danışın)

## Doğum Sonrası Uyku

Doğum sonrası uyku bozukluğu kaçınılmazdır:
- İlk 3 ayda ortalama gece uykusu **5-6 saate** düşer
- Uyku parçalanması (bebeğin beslenmesi)
- Postpartum depresyon riski artışı
- Partner ile nöbet usulü gece bakımı önerilir
- Bebek uyurken siz de uyuyun
- Destek ağınızdan yardım isteyin

## Ne Zaman Doktora Başvurmalı?

- Yüksek sesli, düzensiz horlama başladıysa
- Nefes durması fark edildiyse
- Bacaklarda şiddetli huzursuzluk ve hareket ihtiyacı
- Gündüz aşırı ve kontrol edilemeyen uykululuk
- Ciddi uykusuzluk (haftada 3+ gece)
- Depresyon veya anksiyete belirtileri
- Bacaklarda şişme ile birlikte uyku güçlüğü

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez. Gebelikte herhangi bir ilaç veya takviye kullanmadan önce mutlaka doktorunuza danışın.""",
                'content_en': """## Why Does Sleep Deteriorate in Pregnancy?

75-80% of pregnant women experience sleep problems due to hormonal, physical, and psychological changes.

## By Trimester
1st: Excessive sleepiness, nausea, frequent urination.
2nd: Best period, but vivid dreams, leg cramps may begin.
3rd: Most difficult — back pain, reflux, restless legs, frequent urination.

## Safe Sleep Position
Left side sleeping is recommended, especially in the 3rd trimester. Avoid sleeping on your back.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 10,
                'is_featured': True,
                'is_published': True,
                'order': 25,
                'cover_image_url': 'https://images.unsplash.com/photo-1544126592-807ade215a0b?w=800&h=450&fit=crop',
                'references': 'Mindell JA, et al. Sleep patterns and sleep disturbances across pregnancy. Sleep Med. 2015;16(4):483-488.\nPien GW, Schwab RJ. Sleep disorders during pregnancy. Sleep. 2004;27(7):1405-1417.',
            },
            # ── 7. Uyku Testi (Polisomnografi) ────────────────────────
            {
                'category': cats['tani-yontemleri'],
                'slug': 'uyku-testi-polisomnografi-nedir',
                'article_type': 'diagnosis',
                'title_tr': 'Uyku Testi Nedir? Polisomnografi Nasıl Çekilir?',
                'title_en': 'What Is a Sleep Test? How Is Polysomnography Performed?',
                'subtitle_tr': 'Uyku laboratuvarında bir gece: teste hazırlıktan sonuçlara kadar her şey',
                'subtitle_en': 'A night in the sleep lab: everything from preparation to results',
                'summary_tr': 'Polisomnografi (PSG), uyku bozukluklarının tanısında altın standart yöntemdir. Uyku laboratuvarında bir gece kalarak beyin dalgaları, göz hareketleri, kas aktivitesi, solunum ve kalp ritmi eş zamanlı kaydedilir.',
                'summary_en': 'Polysomnography (PSG) is the gold standard for diagnosing sleep disorders. Brain waves, eye movements, muscle activity, breathing and heart rhythm are simultaneously recorded during an overnight stay in a sleep laboratory.',
                'content_tr': """## Polisomnografi (PSG) Nedir?

Polisomnografi, uyku sırasında vücudun çeşitli fizyolojik parametrelerini eş zamanlı olarak kaydeden, uyku tıbbının en kapsamlı tanı yöntemidir. "Poli" (çok), "somno" (uyku), "grafi" (kayıt) kelimelerinden türemiştir.

Uyku laboratuvarında deneyimli bir uyku teknisyeni eşliğinde, genellikle gece boyunca gerçekleştirilir. Test tamamen ağrısız ve invaziv olmayan bir işlemdir.

## Hangi Durumlarda İstenir?

### Kesin Endikasyonlar
- **Uyku apnesi şüphesi** — horlama, tanık olunan nefes durması, gündüz uykululuğu
- **Narkolepsi** — gündüz aşırı uyku hali, katapleksi atakları
- **REM uyku davranış bozukluğu** — uyku sırasında şiddetli hareketler
- **Periyodik bacak hareket bozukluğu** — uyku sırasında tekrarlayan bacak hareketleri
- **Açıklanamayan kronik uykusuzluk** — diğer tedavilere yanıt vermeyen

### Göreceli Endikasyonlar
- Parasomniler (uyurgezerlik, uyku terörü) — atipik veya şiddetli olgularda
- Epilepsi — gece nöbetlerini uyku bozukluğundan ayırt etmek için
- CPAP basınç titrasyonu — uyku apnesi tedavisinde optimal basınç belirleme
- Mesleki gereklilikler — pilot, şoför gibi uyku apnesi taraması gereken mesleklerde

## Testten Önce: Hazırlık

### 1-2 Hafta Öncesinden
- Doktorunuz uyku günlüğü tutmanızı isteyebilir
- Kullandığınız tüm ilaçları bildirin (bazıları geçici olarak kesilebilir)
- Kafein ve alkol alışkanlıklarınızı not edin

### Test Günü Yapılması Gerekenler
- **Normal günlük rutininizi sürdürün** — olağandışı egzersiz veya stres yaratmayın
- **Öğleden sonra kafein almayın** (çay, kahve, kola, enerji içeceği)
- **Alkol kullanmayın** — uyku yapısını bozar, test sonuçlarını etkiler
- **Gündüz uyumayın** — gece doğal uykunuzu kolaylaştırır
- **Saçlarınızı yıkayın** — jöle, sprey, saç kremi kullanmayın (elektrotların yapışmasını engeller)
- **Yüzünüze krem sürmeyin** — sensörlerin temasını bozar
- **Rahat pijamalarınızı getirin**
- **Kendi yastığınızı getirebilirsiniz** (birçok laboratuvar buna izin verir)

### Yanınıza Almanız Gerekenler
- Pijama ve gecelik kıyafetler
- Diş fırçası ve kişisel bakım malzemeleri
- Sabah giyeceğiniz kıyafet
- Düzenli kullandığınız ilaçlar
- Kimlik ve sevk belgesi
- İsteğe bağlı: kendi yastığınız, kitap

## Uyku Laboratuvarına Varış

Genellikle akşam **20:00-21:00** arası laboratuvara gelmeniz istenir.

### Oda
Uyku laboratuvarı odaları hastane odalarından çok otel odasına benzer. Karanlık, sessiz ve sıcaklığı ayarlanabilir bir ortam sağlanır. Yataklar ev yatağına yakın konforda seçilir. Odada kamera ve mikrofon bulunur — uyku teknisyeni geceyi başka bir odadan izler.

### Kayıt ve Tanışma
- Teknisyen sizi karşılar ve işlemi ayrıntılı açıklar
- Tıbbi öykünüz gözden geçirilir
- Sorularınız yanıtlanır
- Pijamalarınızı giyer ve rahatlamanız için biraz zaman verilir

## Sensörlerin Takılması

Bu aşama yaklaşık **30-45 dakika** sürer. Teknisyen çeşitli sensörleri vücudunuzun farklı bölgelerine yerleştirir:

### Baş Bölgesi (EEG — Elektroensefalografi)
- **Kafatasına 6-8 elektrot** yapıştırılır (suda çözünen yapıştırıcı ile)
- Beyin dalgalarını kaydeder
- Uyku evrelerini belirler (N1, N2, N3, REM)
- Ağrısızdır — sadece yapışkan hissi

### Göz Çevresi (EOG — Elektrookülografi)
- Her gözün dış köşesine birer elektrot
- Göz hareketlerini kaydeder
- REM uykusunu tespit eder

### Çene (EMG — Elektromiyografi)
- Çene altına 2-3 elektrot
- Kas tonusunu (gerginliğini) ölçer
- REM uykusunda kaslar gevşer — bu ayrımı yakalar

### Bacaklar (Bacak EMG)
- Her iki bacağın ön yüzüne (tibialis anterior kasına) birer elektrot
- Periyodik bacak hareketlerini kaydeder
- Huzursuz bacak sendromunun değerlendirilmesi

### Göğüs ve Karın (Solunum Çabası)
- Göğüse ve karına elastik bantlar (solunum effort kemerleri)
- Nefes alma çabasını ölçer
- Obstrüktif/santral apne ayrımı yapar

### Burun ve Ağız (Hava Akışı)
- Burun altına küçük bir kanül (nasal basınç transdüseri)
- Burun ve ağız önüne termistör (sıcaklık algılayıcı)
- Nefes durmasını (apne) ve azalmasını (hipopne) tespit eder

### Parmak (Pulse Oksimetre)
- İşaret parmağına veya kulak memesine klips
- Kan oksijen seviyesini sürekli ölçer
- Uyku apnesinin şiddetini belirler (desatürasyon)

### Göğüs (EKG — Elektrokardiyografi)
- Göğse 2 elektrot
- Kalp ritmini kaydeder
- Uyku apnesine bağlı aritmi tespiti

### Ek Sensörler
- **Pozisyon sensörü** — uyku pozisyonunu kaydeder (sırt üstü, yan vb.)
- **Horlama mikrofonu** — boğaz bölgesine yerleştirilir
- **Video kaydı** — gece boyunca kızılötesi kamera ile

## Test Süreci

### Kalibrasyon (Biyokalibrasyon)
Sensörler takıldıktan sonra teknisyen kısa komutlar verir:
- "Gözlerinizi sağa-sola çevirin" → EOG kontrolü
- "Dişlerinizi sıkın" → EMG kontrolü
- "Derin nefes alın" → Solunum sensörleri kontrolü
- "Ayaklarınızı yukarı kaldırın" → Bacak EMG kontrolü

### Uyku Süreci
- Işıklar kapatılır ve uyumanız istenir
- **Normal uykuya dalma süreniz yeterlidir** — çoğu kişi 20-40 dakikada uyur
- İlk gece etkisi: Alışık olmadığınız ortamda biraz daha geç uyuyabilirsiniz — bu normaldir
- Tuvalet ihtiyacı için teknisyeni arayabilirsiniz (bazı kablolar çıkarılır)
- Gece boyunca minimum 6 saat kayıt hedeflenir
- Teknisyen geceyi ayrı bir odadan ekranda izler

### Sabah
- Genellikle **06:00-07:00** civarında uyandırılırsınız
- Sensörler çıkarılır (yapıştırıcı ılık su ile çözülür)
- Duş imkânı olabilir (laboratuvara göre değişir)
- İşlem toplam 8-10 saat sürer (akşam varış → sabah ayrılış)

## Ne Kaydedilir? Parametreler

| Parametre | Sensör | Ne Ölçer |
|-----------|--------|----------|
| EEG | Kafa elektrotları | Beyin dalgaları, uyku evreleri |
| EOG | Göz elektrotları | Göz hareketleri (REM tespiti) |
| EMG (çene) | Çene elektrotları | Kas tonusu |
| EMG (bacak) | Bacak elektrotları | Periyodik bacak hareketleri |
| Nasal basınç | Burun kanülü | Hava akışı |
| Termistör | Burun/ağız | Apne/hipopne tespiti |
| SpO₂ | Parmak oksimetre | Kan oksijen düzeyi |
| EKG | Göğüs elektrotları | Kalp ritmi |
| Solunum çabası | Göğüs/karın bandı | Solunum eforu |
| Pozisyon | Pozisyon sensörü | Uyku pozisyonu |
| Ses | Mikrofon | Horlama |
| Video | Kızılötesi kamera | Hareket, davranış |

## Sonuçların Değerlendirilmesi

### Kim Değerlendirir?
Kayıtlar uyku tıbbı uzmanı (somnolog) tarafından **manual olarak** skorlanır. Bu süreç genellikle 2-5 iş günü alır.

### Uyku Evreleri
Test boyunca uyku evreleri her **30 saniyelik dönemde** (epoch) belirlenir:
- **N1 (Hafif uyku):** Uyanıklık-uyku geçişi, %5-10
- **N2 (Orta uyku):** Uyku iğcikleri ve K-kompleksleri, %45-55
- **N3 (Derin uyku):** Delta dalgaları, %15-25, fiziksel restorasyon
- **REM (Rüya uykusu):** Hızlı göz hareketleri, %20-25, hafıza konsolidasyonu
- **Uyanıklık:** Gece uyanma dönemleri

### Temel Ölçümler

**Uyku Etkinliği:**
- Yatakta geçirilen süreye karşı uyunan süre oranı
- Normal: >%85
- Düşük etkinlik uykusuzluğa işaret eder

**AHI (Apne-Hipopne İndeksi):**
Uyku apnesinin şiddetini gösteren en önemli parametre
- **Normal:** < 5 olay/saat
- **Hafif:** 5-15 olay/saat
- **Orta:** 15-30 olay/saat
- **Ağır:** > 30 olay/saat

**ODI (Oksijen Desatürasyon İndeksi):**
- Saat başına oksijen düşüşü sayısı
- AHI ile birlikte değerlendirilir

**PLM İndeksi (Periyodik Bacak Hareketi):**
- Saat başına tekrarlayan bacak hareketi sayısı
- >15/saat patolojik kabul edilir

**Uyku Latansı:**
- Yataktan uyuyana kadar geçen süre
- Normal: 10-20 dakika
- <5 dakika: Aşırı uykululuk
- >30 dakika: Uyku başlatma güçlüğü

### Sonuç Raporu
Raporda şunlar yer alır:
- Uyku evreleri dağılımı (hipnogram)
- Toplam uyku süresi ve etkinliği
- AHI, ODI değerleri
- Minimum ve ortalama SpO₂
- Bacak hareket indeksi
- Horlama süresi ve şiddeti
- Pozisyona göre apne dağılımı
- Tanı ve tedavi önerisi

## Split-Night Çalışma

Bazı durumlarda gecenin ilk yarısında tanı, ikinci yarısında CPAP titrasyonu yapılır:
- İlk 2 saatte AHI ≥ 40 saptanırsa gecenin geri kalanında CPAP başlanır
- Hem tanı hem tedavi tek gecede tamamlanır
- Hastaya ek bir gece yatış gerektirmez

## Evde Uyku Testi (HSAT)

Tüm hastaların laboratuvara gelmesi gerekmez. **Ev tipi uyku testi** bazı durumlar için uygundur:

### Ev Testi Yapılabilecek Durumlar
- Orta-yüksek uyku apnesi şüphesi olan yetişkinler
- Ciddi eşlik eden hastalığı olmayanlar

### Ev Testi Yapılamayacak Durumlar
- Çocuklar
- Kalp yetmezliği, KOAH gibi ciddi eşlik eden hastalıklar
- Santral uyku apnesi şüphesi
- Narkolepsi, RBD, parasomni şüphesi
- Negatif ev testi sonucu ama klinik şüphe devam ediyorsa → laboratuvar PSG gerekir

### Ev Testi ve Laboratuvar Karşılaştırması

| Özellik | Laboratuvar PSG | Ev Testi (HSAT) |
|---------|----------------|-----------------|
| Sensör sayısı | 15-20+ | 4-7 |
| EEG (beyin dalgası) | Var | Yok |
| Uyku evresi belirleme | Var | Yok |
| Bacak hareketi | Var | Sınırlı |
| Video | Var | Yok |
| Teknisyen gözetimi | Var | Yok |
| Maliyet | Yüksek | Düşük |
| Konfor | Laboratuvar ortamı | Ev ortamı |
| Güvenilirlik | Altın standart | Yeterli (apne için) |

## MSLT ve MWT: Gündüz Testleri

### MSLT (Multiple Sleep Latency Test — Çoklu Uyku Latansı Testi)
- Narkolepsi tanısında altın standart
- PSG'nin ertesi günü yapılır
- Her 2 saatte bir (10:00, 12:00, 14:00, 16:00, 18:00) 20 dakika uyuma fırsatı
- Ortalama uyku latansı < 8 dakika ve ≥ 2 SOREMP → narkolepsi

### MWT (Maintenance of Wakefulness Test — Uyanıklık Sürdürme Testi)
- Tedavi etkinliğini değerlendirmede kullanılır
- Karanlık, sessiz odada oturarak uyanık kalmaya çalışma
- Meslek değerlendirmeleri için (pilot, şoför vb.)

## Sık Sorulan Sorular

### "Laboratuvarda uyuyamam, test geçersiz olur mu?"
Çoğu kişi endişelendiğinin aksine uyuyabilir. İlk gece etkisi nedeniyle uyku kaliteniz biraz düşük olabilir — bu normaldir ve sonuçları genellikle etkilemez. Minimum 4-6 saat uyku kaydı yeterlidir.

### "Ağrılı mı?"
Hayır. Sensörler yapıştırıcı veya elastik bantlarla tutturulur. İğne kullanılmaz. Hafif rahatsızlık hissi olabilir ama ağrı yoktur.

### "Sonuçlar ne zaman çıkar?"
Genellikle 3-7 iş günü içinde. Sonuçlar uyku uzmanı tarafından değerlendirilip raporlanır.

### "Test tekrarı gerekir mi?"
Tedavi başlandıktan sonra (CPAP titrasyonu gibi) veya semptomlar değiştiğinde tekrar gerekebilir. Ev testi negatif ama şüphe devam ediyorsa laboratuvar PSG yapılır.

### "SGK karşılıyor mu?"
Evet. Uyku apnesi şüphesiyle istenen PSG SGK tarafından karşılanır. Doktor sevki gereklidir.

### "Çocuklara yapılır mı?"
Evet. Çocuklarda uyku apnesi, parasomni ve epilepsi ayrımı için pediatrik PSG uygulanır. Ebeveynin kalması genellikle mümkündür.

## Ne Zaman Uyku Testi Yaptırmalısınız?

Aşağıdaki belirtilerden biri veya birkaçı varsa doktorunuza danışın:
- Yüksek sesli ve düzensiz horlama
- Uyku sırasında nefes durması (eşiniz fark ediyorsa)
- Gündüz aşırı uykululuk, konsantrasyon güçlüğü
- Sabah baş ağrısı ve ağızda kuruluk
- Gece sık idrara kalkma
- Uyku sırasında şiddetli hareket veya konuşma
- Tedaviye dirençli uykusuzluk
- Açıklanamayan gündüz yorgunluğu

> Bu bilgiler genel sağlık eğitimi amaçlıdır ve tıbbi tavsiye yerine geçmez. Uyku sorunlarınız için mutlaka bir uyku tıbbı uzmanına başvurun.""",
                'content_en': """## What Is Polysomnography (PSG)?

Polysomnography is the most comprehensive diagnostic method in sleep medicine, simultaneously recording various physiological parameters during sleep. It is performed overnight in a sleep laboratory under the supervision of a trained sleep technician. The test is completely painless and non-invasive.

## When Is It Ordered?
- Suspected sleep apnea — snoring, witnessed breathing pauses, daytime sleepiness
- Narcolepsy — excessive daytime sleepiness
- REM sleep behavior disorder — violent movements during sleep
- Periodic limb movement disorder
- Treatment-resistant chronic insomnia

## What Is Recorded?
EEG (brain waves), EOG (eye movements), EMG (muscle tone), breathing effort, airflow, blood oxygen, ECG, leg movements, body position, snoring, and video.

## Key Measurements
- AHI (Apnea-Hypopnea Index): Normal <5, Mild 5-15, Moderate 15-30, Severe >30
- Sleep efficiency: Normal >85%
- Sleep latency: Normal 10-20 minutes

## Home Sleep Test (HSAT)
A simplified version for adults with moderate-high sleep apnea suspicion. Uses fewer sensors. Not suitable for children or complex cases.

> This information is for general health education and does not replace medical advice.""",
                'reading_time_minutes': 12,
                'is_featured': True,
                'is_published': True,
                'order': 26,
                'cover_image_url': 'https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&h=450&fit=crop',
                'references': 'Berry RB, et al. The AASM Manual for the Scoring of Sleep and Associated Events. American Academy of Sleep Medicine. 2020.\nKapur VK, et al. Clinical practice guideline for diagnostic testing for adult obstructive sleep apnea. J Clin Sleep Med. 2017;13(3):479-504.\nSateia MJ. International classification of sleep disorders-third edition. Chest. 2014;146(5):1387-1394.',
                'author_name': 'Norosera Tıbbi İçerik Ekibi',
            },
        ]
