"""
Uyku Sagligi modulu icin seed data.
Kategoriler, makaleler, ipuclari ve SSS olusturur.
"""
from django.core.management.base import BaseCommand
from apps.sleep.models import SleepCategory, SleepArticle, SleepTip, SleepFAQ


class Command(BaseCommand):
    help = 'Uyku sagligi modulu icin ornek icerik olusturur'

    def handle(self, *args, **options):
        self._create_categories()
        self._create_articles()
        self._create_tips()
        self._create_faqs()
        self.stdout.write(self.style.SUCCESS('Uyku sagligi icerikleri basariyla olusturuldu!'))

    def _create_categories(self):
        categories = [
            {
                'slug': 'uyku-bozukluklari',
                'name_tr': 'Uyku Bozukluklari',
                'name_en': 'Sleep Disorders',
                'description_tr': 'Insomnia, uyku apnesi, narkolepsi, parasomni ve diger uyku bozukluklari hakkinda detayli bilgiler.',
                'description_en': 'Detailed information about insomnia, sleep apnea, narcolepsy, parasomnia and other sleep disorders.',
                'icon': 'alert-circle',
                'order': 1,
            },
            {
                'slug': 'uyku-hijyeni',
                'name_tr': 'Uyku Hijyeni',
                'name_en': 'Sleep Hygiene',
                'description_tr': 'Sagllikli uyku aliskanliklari, uyku ortami duzenleme ve uyku kalitesini artirma yontemleri.',
                'description_en': 'Healthy sleep habits, sleep environment optimization and methods to improve sleep quality.',
                'icon': 'sparkles',
                'order': 2,
            },
            {
                'slug': 'tani-yontemleri',
                'name_tr': 'Tani Yontemleri',
                'name_en': 'Diagnostic Methods',
                'description_tr': 'Polisomnografi, aktigrafi, MSLT ve uyku bozukluklarinda kullanilan tani araclari.',
                'description_en': 'Polysomnography, actigraphy, MSLT and diagnostic tools used in sleep disorders.',
                'icon': 'stethoscope',
                'order': 3,
            },
            {
                'slug': 'hastalikta-uyku',
                'name_tr': 'Hastalikta Uyku',
                'name_en': 'Sleep in Disease',
                'description_tr': 'Migren, Alzheimer, Parkinson, diyabet, ADHD ve diger hastaliklarda uyku ozellikleri.',
                'description_en': 'Sleep characteristics in migraine, Alzheimer, Parkinson, diabetes, ADHD and other diseases.',
                'icon': 'heart-pulse',
                'order': 4,
            },
            {
                'slug': 'uyku-sagligi',
                'name_tr': 'Uyku Sagligi',
                'name_en': 'Sleep Health',
                'description_tr': 'Uyku fizyolojisi, uyku evreleri, sirkadiyen ritim ve genel uyku sagligi bilgileri.',
                'description_en': 'Sleep physiology, sleep stages, circadian rhythm and general sleep health information.',
                'icon': 'moon',
                'order': 5,
            },
        ]

        for cat_data in categories:
            SleepCategory.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data,
            )
        self.stdout.write(f'  {len(categories)} kategori olusturuldu.')

    def _create_articles(self):
        cats = {c.slug: c for c in SleepCategory.objects.all()}
        articles = self._get_articles(cats)
        for art_data in articles:
            SleepArticle.objects.update_or_create(
                slug=art_data['slug'],
                defaults=art_data,
            )
        self.stdout.write(f'  {len(articles)} makale olusturuldu.')

    def _get_articles(self, cats):
        return [
            # ===== UYKU BOZUKLUKLARI =====
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'insomnia-uykusuzluk-nedir',
                'article_type': 'disorder',
                'title_tr': 'Insomnia (Uykusuzluk) Nedir?',
                'title_en': 'What is Insomnia?',
                'subtitle_tr': 'Uykusuzlugun nedenleri, belirtileri ve tedavi yontemleri',
                'subtitle_en': 'Causes, symptoms and treatment methods of insomnia',
                'summary_tr': 'Insomnia, uykuya dalma veya uyku surekliligini saglama guclugu olarak tanimlanan en yaygin uyku bozuklugudur. Eriskinlerin yaklasik %30-35\'inde gorulen bu durum, yasam kalitesini ciddi sekilde etkiler.',
                'summary_en': 'Insomnia is the most common sleep disorder defined as difficulty falling asleep or maintaining sleep. This condition, seen in approximately 30-35% of adults, seriously affects quality of life.',
                'content_tr': """## Insomnia (Uykusuzluk) Nedir?

Insomnia, yeterli uyku firsati ve uygun ortam olmasina ragmen uykuya dalma, uyku surekliligini saglama veya sabah erken uyanma ile karakterize bir uyku bozuklugudur.

### Epidemiyoloji

- Eriskinlerin **%30-35**'inde akut insomnia gorulur
- **%10-15**'inde kronik insomnia mevcuttur
- Kadinlarda erkeklere oranla **1.5 kat** daha sik gorulur
- Yas ile birlikte prevalans artar

### Insomnia Turleri

**Akut (Kisa Sureli) Insomnia:**
- 3 aydan kisa suren uykusuzluk
- Genellikle stres, yasam degisiklikleri veya cevre faktorleriyle tetiklenir
- Cogu vakada kendilginden duzelebilir

**Kronik Insomnia:**
- Haftada en az 3 gece, 3 aydan uzun suren uykusuzluk
- Gunduz islevselligini bozan belirtilerle birlikte seyreder
- Tedavi gerektirir

### Nedenleri

**Birincil Nedenler:**
- Stres ve anksiyete
- Depresyon
- Yanlis uyku aliskanlikari
- Sirkadiyen ritim bozukluklari

**Ikincil Nedenler:**
- Kronik agri sendromlari
- Solunum hastaliklari (astim, KOAH)
- Gastroozofageal reflu
- Norolojik hastaliklar
- Ilac yan etkileri (beta-blokerler, steroidler, SSRI'lar)

### Belirtileri

- Uykuya dalma guclugu (>30 dakika)
- Gece sik uyanma
- Sabah erken uyanma ve tekrar uyuyamama
- Dinlendirici olmayan uyku
- Gunduz yorgunluk ve enerji dusugu
- Konsantrasyon guclugu
- Irritabilite ve duygudurum degisiklikleri

### Tani

- Detayli uyku anamnezi
- Uyku guncesi (en az 2 hafta)
- Pittsburgh Uyku Kalitesi Indeksi (PUKI)
- Insomnia Siddet Indeksi (ISI)
- Gerekirse polisomnografi

### Tedavi

**Farmakolojik Olmayan Tedaviler (Birinci Basamak):**
- **Bilissel Davranisci Terapi (BDT-I):** Altin standart tedavi
- Uyku hijyeni egitimi
- Uyaran kontrolu teknigi
- Uyku kisitlama terapisi
- Gevseyme teknikleri

**Farmakolojik Tedavi:**
- Kisa sureli kullanim icin benzodiazepin reseptor agonistleri
- Melatonin ve melatonin reseptor agonistleri
- Dusuk doz antidepresanlar (trazodon, doksepin)
- Oreksn reseptor antagonistleri (suvoreksant)

> **Onemli:** Uyku ilaclari mutlaka hekim kontrolunde ve kisa sureli kullanilmalidir.""",
                'content_en': """## What is Insomnia?

Insomnia is a sleep disorder characterized by difficulty falling asleep, maintaining sleep, or early morning awakening despite adequate sleep opportunity and appropriate environment.

### Epidemiology

- Acute insomnia occurs in **30-35%** of adults
- **10-15%** have chronic insomnia
- **1.5 times** more common in women than men
- Prevalence increases with age

### Types of Insomnia

**Acute (Short-term) Insomnia:**
- Insomnia lasting less than 3 months
- Usually triggered by stress, life changes, or environmental factors
- Can resolve spontaneously in most cases

**Chronic Insomnia:**
- Insomnia occurring at least 3 nights per week for more than 3 months
- Accompanied by symptoms that impair daytime functioning
- Requires treatment

### Causes

**Primary Causes:**
- Stress and anxiety
- Depression
- Poor sleep habits
- Circadian rhythm disorders

**Secondary Causes:**
- Chronic pain syndromes
- Respiratory diseases (asthma, COPD)
- Gastroesophageal reflux
- Neurological diseases
- Medication side effects (beta-blockers, steroids, SSRIs)

### Symptoms

- Difficulty falling asleep (>30 minutes)
- Frequent nighttime awakenings
- Early morning awakening and inability to fall back asleep
- Non-restorative sleep
- Daytime fatigue and low energy
- Difficulty concentrating
- Irritability and mood changes

### Treatment

**Non-pharmacological Treatments (First-line):**
- **Cognitive Behavioral Therapy (CBT-I):** Gold standard treatment
- Sleep hygiene education
- Stimulus control technique
- Sleep restriction therapy
- Relaxation techniques

> **Important:** Sleep medications should always be used under physician supervision and for short-term use only.""",
                'reading_time_minutes': 8,
                'is_featured': True,
                'order': 1,
                'references': 'American Academy of Sleep Medicine. International Classification of Sleep Disorders, 3rd ed.\nMorin CM, et al. Insomnia disorder. Nat Rev Dis Primers. 2015;1:15026.\nRiemann D, et al. European guideline for the diagnosis and treatment of insomnia. J Sleep Res. 2017;26(6):675-700.',
            },
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'uyku-apnesi-sendromu',
                'article_type': 'disorder',
                'title_tr': 'Uyku Apnesi Sendromu',
                'title_en': 'Sleep Apnea Syndrome',
                'subtitle_tr': 'Obstruktif uyku apnesi: tani, risk faktorleri ve CPAP tedavisi',
                'subtitle_en': 'Obstructive sleep apnea: diagnosis, risk factors and CPAP treatment',
                'summary_tr': 'Obstruktif uyku apnesi (OUA), uyku sirasinda ust hava yolunun tekrarli tikenmesi sonucu olusan nefes durmalariyla karakterize ciddi bir uyku bozuklugudur. Tedavi edilmezse kardiyovaskuler hastalik riskini onemli olcude artirir.',
                'summary_en': 'Obstructive sleep apnea (OSA) is a serious sleep disorder characterized by repeated breathing pauses caused by upper airway obstruction during sleep.',
                'content_tr': """## Uyku Apnesi Sendromu

Obstruktif uyku apnesi (OUA), uyku sirasinda ust hava yolunun kismi (hipopne) veya tam (apne) tikenmesi ile karakterize bir uyku bozuklugudur.

### Epidemiyoloji

- Eriskin erkeklerde **%13-33**, kadinlarda **%6-19** prevalans
- Obezite en onemli risk faktorudur
- Yas ile birlikte sikligi artar
- Cogu hasta teshis edilmemistir

### Risk Faktorleri

- **Obezite** (BMI > 30 kg/m2)
- Erkek cinsiyet
- Ileri yas (>50)
- Boyun cevresi (erkek >43 cm, kadin >38 cm)
- Buyuk tonsiller, kucuk cene yapisi
- Aile oykusu
- Alkol ve sedatif kullanlmi
- Sigara

### Belirtiler

**Gece Belirtileri:**
- Yuksek sesli ve duzensiz horlama
- Tanigin gozlemledigi nefes durmalari
- Gece bougulma hissi ile uyanma
- Noktüri (gece sik idrara cikma)
- Agiz kurulugu

**Gunduz Belirtileri:**
- Asiri gunduz uykululugu
- Sabah bas agrisi
- Konsantrasyon guclugu
- Hafiza problemleri
- Irritabilite
- Libido azalmasi

### Komplikasyonlar

- **Kardiyovaskuler:** Hipertansiyon, aritmi, kalp yetmezligi, inme
- **Metabolik:** Insulin direnci, tip 2 diyabet
- **Norolojik:** Kognitif bozukluk, depresyon
- **Trafik kazasi:** Normal populasyona gore 2-7 kat artmis risk

### Tani

**Polisomnografi (PSG):**
- Altin standart tani yontemi
- Uyku laboratuvarinda gece boyu kayit
- Apne-Hipopne Indeksi (AHI) hesaplanir
  - Hafif: AHI 5-15
  - Orta: AHI 15-30
  - Agir: AHI >30

**Ev Tipi Uyku Testi:**
- Komplikasyonsuz vakalarda kullanilabilir
- Daha kolay uygulanir, daha ucuz

### Tedavi

**Yasam Tarzi Degisiklikleri:**
- Kilo verme (BMI'yi normal sinira getirme)
- Alkol ve sedatiflerden kacinma
- Sigara birakma
- Yan yatarak uyuma

**CPAP (Continuous Positive Airway Pressure):**
- Orta ve agir OUA icin standart tedavi
- Maske ile pozitif hava basinci uygular
- Hava yolunu acik tutar
- Uyum icin sabir gerekir

**Oral Apareyler:**
- Hafif-orta OUA veya CPAP intoleransi icin
- Alt ceneyi onde konumlandirir

**Cerrahi Secenekler:**
- Uvulopalatofaringoplasti (UPPP)
- Tonsillektomi
- Hipoglossal sinir stimulasyonu""",
                'content_en': """## Sleep Apnea Syndrome

Obstructive sleep apnea (OSA) is a sleep disorder characterized by partial (hypopnea) or complete (apnea) obstruction of the upper airway during sleep.

### Epidemiology

- Prevalence of **13-33%** in adult men, **6-19%** in women
- Obesity is the most important risk factor
- Frequency increases with age
- Most patients remain undiagnosed

### Risk Factors

- **Obesity** (BMI > 30 kg/m2)
- Male sex
- Advanced age (>50)
- Neck circumference (male >43 cm, female >38 cm)
- Large tonsils, small jaw structure
- Family history
- Alcohol and sedative use
- Smoking

### Treatment

**CPAP (Continuous Positive Airway Pressure):**
- Standard treatment for moderate to severe OSA
- Applies positive air pressure via mask
- Keeps the airway open
- Requires patience for compliance""",
                'reading_time_minutes': 10,
                'is_featured': True,
                'order': 2,
                'references': 'Benjafield AV, et al. Estimation of the global prevalence of obstructive sleep apnoea. Lancet Respir Med. 2019;7(8):687-698.\nPatel SR. Obstructive Sleep Apnea. Ann Intern Med. 2019;171(11):ITC81-ITC96.',
            },
            {
                'category': cats['uyku-bozukluklari'],
                'slug': 'parasomniler',
                'article_type': 'disorder',
                'title_tr': 'Parasomniler: Uyku Sirasinda Anormal Davranislar',
                'title_en': 'Parasomnias: Abnormal Behaviors During Sleep',
                'subtitle_tr': 'Uyurgezerlik, gece teroru, REM uyku davranis bozuklugu ve diger parasomniler',
                'subtitle_en': 'Sleepwalking, night terrors, REM sleep behavior disorder and other parasomnias',
                'summary_tr': 'Parasomniler, uyku sirasinda veya uyku-uyaniklik gecislerinde ortaya cikan istenmeyen fiziksel olaylar veya deneyimlerdir. Cocuklarda daha sik gorulen bu bozukluklar eriskinlerde de ciddi sorunlara yol acabilir.',
                'summary_en': 'Parasomnias are undesirable physical events or experiences that occur during sleep or during sleep-wake transitions.',
                'content_tr': """## Parasomniler

Parasomniler, uyku sirasinda ortaya cikan anormal hareketler, davranislar, duygular, algilar ve duslerdir.

### Siniflandirma

**NREM Parasomniileri (Uyarilma Bozukluklari):**

**1. Uyurgezerlik (Somnambulizm):**
- Derin uyku sirasinda ortaya cikar
- Karmasik motor davranislar (yurume, konusma, yeme)
- Cocuklarin %15-40'inda gorulebilir
- Genellikle pubertede azalir
- Uyku yoksunlugu ve stres tetikleyebilir

**2. Gece Teroru (Pavor Nocturnus):**
- Derin uykudan ani, dehsetli bir ciglikla uyanma
- Otonomik belirtiler: tasikardi, terleme, mydriazis
- Cocuklarda %1-6.5 oraninda gorulur
- Olaylari hatirlamama tipiktir
- Kabus ile karistirilmamalidir

**3. Konfuzyonel Uyarilmalar:**
- Uykudan kalkarken zihinsel konfuzyon
- Zaman ve mekan oryantasyon bozuklugu
- Cocuklarda daha yaygin

**REM Parasomniileri:**

**1. REM Uyku Davranis Bozuklugu (RBD):**
- REM uykusunda normal aton yerine hareket
- Ruya icerigini canlandirma (vurma, tekmeleme)
- 50 yas ustu erkeklerde daha sik
- **Onemli:** Parkinson ve Lewy cisimcikli demans habercisi olabilir
- Nörodejeneratif hastalik riski %80'e kadar cikar

**2. Kabuslar (Nightmare Disorder):**
- REM uykusunda canli, korkutucu dusler
- Uyanma sonrasi oryantasyon bozulmaz
- PTSD ile guclu iliski

### Tedavi Yaklasimi

- Uyku hijyeni duzenlenmesi
- Tetikleyici faktorlerin eliminasyonu
- Guvenlik onlemleri (ozellikle uyurgezerlikte)
- Gerekirse farmakoterapi (klonazepam, melatonin)
- RBD'de norolojik takip""",
                'content_en': """## Parasomnias

Parasomnias are abnormal movements, behaviors, emotions, perceptions, and dreams that occur during sleep.

### Classification

**NREM Parasomnias (Arousal Disorders):**

**1. Sleepwalking (Somnambulism):**
- Occurs during deep sleep
- Complex motor behaviors (walking, talking, eating)
- Can be seen in 15-40% of children

**2. Night Terrors (Pavor Nocturnus):**
- Sudden, terrified awakening from deep sleep with screaming
- Autonomic symptoms: tachycardia, sweating, mydriasis

**REM Parasomnias:**

**1. REM Sleep Behavior Disorder (RBD):**
- Movement during REM sleep instead of normal atonia
- Acting out dream content (hitting, kicking)
- **Important:** May be a harbinger of Parkinson's and Lewy body dementia""",
                'reading_time_minutes': 7,
                'is_featured': False,
                'order': 3,
                'references': 'Fleetham JA, Fleming JA. Parasomnias. CMAJ. 2014;186(8):E273-E280.\nPostuma RB, et al. Risk and predictors of dementia and parkinsonism in RBD. Neurology. 2019;92(1):e59-e67.',
            },
            # ===== UYKU HIJYENI =====
            {
                'category': cats['uyku-hijyeni'],
                'slug': 'uyku-hijyeni-kurallari',
                'article_type': 'hygiene',
                'title_tr': 'Uyku Hijyeni: 12 Altin Kural',
                'title_en': 'Sleep Hygiene: 12 Golden Rules',
                'subtitle_tr': 'Uyku kalitenizi artirmak icin bilimsel olarak kanitlanmis yontemler',
                'subtitle_en': 'Scientifically proven methods to improve your sleep quality',
                'summary_tr': 'Uyku hijyeni, iyi bir uyku icin gerekli aliskanlik ve cevre kosullarini kapsayan temel kurallar butunudur. Bu kurallara uymak bircogu uyku sorunun onlenmesinde birinci basamak yaklasimdir.',
                'summary_en': 'Sleep hygiene is a set of fundamental rules covering the habits and environmental conditions necessary for good sleep.',
                'content_tr': """## Uyku Hijyeni: 12 Altin Kural

Uyku hijyeni, iyi bir gece uykusu icin optimize edilmis aliskanlik ve cevre kosullarini kapsar. Arastirmalar bu kurallara uymanin uyku kalitesini %40'a kadar artirabilecegini gostermektedir.

### 1. Duzunli Uyku-Uyanma Programi
- Her gun ayni saatte yatin ve kalkin
- Hafta sonlari bile 1 saatten fazla sapma yapmayin
- Sirkadiyen ritminizi guclendirin

### 2. Yatak Odasi Ortami
- **Sicaklik:** 18-20 derece C (ideal)
- **Karanlik:** Karanlik perdeler veya uyku maskesi
- **Sessizlik:** Beyaz gurultu makinesi kullanabilirsiniz
- Yatak odasini sadece uyku ve cinsellik icin kullanin

### 3. Mavi Isik Maruziyetini Sinirlayin
- Uyumadan 1-2 saat once ekranlari birakin
- Telefon, tablet, bilgisayar ekranlarindaki mavi isik melatonin salgilanmasini baskilar
- Gece modu veya mavi isik filtresi kullanin

### 4. Kafein Tuketimini Sinirlayin
- Ogleden sonra 14:00'ten sonra kafein almayin
- Kafeinin yari omru 5-6 saattir
- Cay, kola, cikolata da kafein icerir

### 5. Alkol ve Sigaradan Kacinin
- Alkol uykuya dalmayi kolaylastirsa da uyku kalitesini bozar
- REM uykusunu baskilar
- Nikotin uyarici etkilidir

### 6. Duzunli Egzersiz Yapin
- Haftada en az 150 dakika orta yogunlukta egzersiz
- Uyumadan 3-4 saat once agir egzersizden kacinin
- Sabah veya ogle egzersizi uyku kalitesini artirir

### 7. Akuam Yemeklerine Dikkat Edin
- Yatmadan 2-3 saat once agir yemek yemeyin
- Baharratli ve yagli yiyeceklerden kacinin
- Hafif bir atistirmalik (muz, badlem) uyumaya yardimci olabilir

### 8. Gunduz Uykulari (Nap)
- 20-30 dakikayi gecirmeyin
- Ogleden sonra 15:00'ten sonra uyumayin
- Gece uykusunu bozmayacak sekilde planlayin

### 9. Yatak Odasinda Saat Gormeyin
- Saate bakmak anksiyeteyi artirir
- Alarmdan baska saat bulundurmayin

### 10. Uyumadan Once Gevseyin
- Ilik bir dus (vucusu isiduyuicu sogutur)
- Kitap okuma
- Meditasyon veya nefes egzersizleri
- Hafif germe hareketleri

### 11. Gunes Isigina Cikin
- Sabah ilk 30 dakikada dis mekan isigina cikin
- Sirkadiyen ritminizi senkronize edin
- Kis aylarinda isik terapisi dusunulebilir

### 12. Yatakta Uyuyamiyorsaniz Kalkin
- 20 dakika iceinde uyuyamadiyysaniz yataktan kalkin
- Losu isikta sakin bir aktivite yapin
- Uykulu hissettiginizde tekrar yatin

> **Not:** Bu kurallar genel onerilerdir. Devam eden uyku sorunlari icin mutlaka bir uyku uzmani veya noroloji uzmani ile gorusun.""",
                'content_en': """## Sleep Hygiene: 12 Golden Rules

Sleep hygiene covers optimized habits and environmental conditions for a good night's sleep. Research shows that following these rules can improve sleep quality by up to 40%.

### 1. Regular Sleep-Wake Schedule
- Go to bed and wake up at the same time every day
- Don't deviate more than 1 hour even on weekends

### 2. Bedroom Environment
- **Temperature:** 18-20 degrees C (ideal)
- **Darkness:** Blackout curtains or sleep mask
- **Quiet:** You can use a white noise machine

### 3. Limit Blue Light Exposure
- Stop screens 1-2 hours before bed
- Blue light from screens suppresses melatonin

### 4. Limit Caffeine Intake
- No caffeine after 2:00 PM
- Caffeine half-life is 5-6 hours

### 5. Avoid Alcohol and Smoking
- Alcohol disrupts sleep quality despite helping you fall asleep

### 6. Exercise Regularly
- At least 150 minutes of moderate exercise per week
- Avoid heavy exercise 3-4 hours before bed""",
                'reading_time_minutes': 6,
                'is_featured': True,
                'order': 1,
                'references': 'Irish LA, et al. The role of sleep hygiene in promoting public health. Sleep Med Rev. 2015;22:23-36.\nStepanski EJ, Wyatt JK. Use of sleep hygiene in the treatment of insomnia. Sleep Med Rev. 2003;7(3):215-225.',
            },
            # ===== TANI YONTEMLERI =====
            {
                'category': cats['tani-yontemleri'],
                'slug': 'polisomnografi-uyku-testi',
                'article_type': 'diagnosis',
                'title_tr': 'Polisomnografi (PSG): Uyku Laboratuvari Testi',
                'title_en': 'Polysomnography (PSG): Sleep Laboratory Test',
                'subtitle_tr': 'Uyku bozukluklarinda altin standart tani yontemi',
                'subtitle_en': 'Gold standard diagnostic method in sleep disorders',
                'summary_tr': 'Polisomnografi, uyku sirasinda beyin dalgalari, goz hareketleri, kas aktivitesi, solunum, kalp ritmi ve oksijen duzeylerinin esanli olarak kaydedildigi kapsamli bir uyku testidir.',
                'summary_en': 'Polysomnography is a comprehensive sleep test that simultaneously records brain waves, eye movements, muscle activity, breathing, heart rhythm, and oxygen levels during sleep.',
                'content_tr': """## Polisomnografi (PSG)

Polisomnografi, uyku bozukluklarinin tanisinda altin standart olarak kabul edilen kapsamli bir uyku testidir.

### Nedir?

PSG, uyku sirasinda birden fazla fizyolojik parametrenin esanli olarak kaydedilmesidir. Test genellikle uyku laboratuvarinda, gece boyunca yapilir.

### Kaydedilen Parametreler

**Noropsikiyatrik:**
- **EEG (Elektroensefalografi):** Beyin dalgalari - uyku evrelerini belirler
- **EOG (Elektrookülografi):** Goz hareketleri - REM uykusunu saptar
- **EMG (Elektromiyografi):** Kas tonusu - ceene ve bacak kaslari

**Kardiyorespiratuar:**
- **Oronazal akis:** Burun ve agizdan hava akisi
- **Torakoabdominal hareket:** Gogus ve karin hareketleri
- **SpO2:** Pulse oksimetri ile oksijen satürasyonu
- **EKG:** Kalp ritmi

**Diger:**
- Horlama mikrofonu
- Vücut pozisyonu sensoru
- Bacak hareketi sensoru (PLM)

### Endikasyonlari

- Uyku apnesi suphesi
- Narkolepsi degerlendirmesi
- REM uyku davranis bozuklugu
- Gece nobet suphesi (epilepsi)
- Aciklanamayan asiri gunduz uykululugu
- CPAP titrasyonu

### Test Sureci

1. **Aksam:** Laboratuvara gelis, sensorlerin takilmasi (45-60 dk)
2. **Gece:** 6-8 saat uyku kaydii
3. **Sabah:** Sensorlerin cikarilmasi, taburculuk
4. **Sonuc:** Uyku uzmani tarafindan raporlama (1-2 hafta)

### Olculen Parametreler

- **AHI (Apne-Hipopne Indeksi):** Saatte kac kez nefes durur/azalir
- **Uyku etkinligi:** Yatakta gecirilen surenin ne kadari uykulk
- **Uyku latensi:** Uykuya dalma suresi
- **REM latensi:** Ilk REM evresine kadar gecen sure
- **Arousal indeksi:** Saatteki mikro-uyanma sayisi

### Ev Tipi Uyku Testi

- Daha basit, ev ortaminda yapilabilir
- Genellikle 4 kanal: akis, efor, SpO2, nabiz
- Komplikasyonsuz OUA suphesinde yeterli
- EEG icermez, uyku evrelerini gosteremez""",
                'content_en': """## Polysomnography (PSG)

Polysomnography is a comprehensive sleep test considered the gold standard in diagnosing sleep disorders.

### What is it?

PSG is the simultaneous recording of multiple physiological parameters during sleep. The test is usually performed overnight in a sleep laboratory.

### Recorded Parameters

- **EEG:** Brain waves - determines sleep stages
- **EOG:** Eye movements - detects REM sleep
- **EMG:** Muscle tone
- **Oronasal flow:** Airflow
- **SpO2:** Oxygen saturation
- **ECG:** Heart rhythm""",
                'reading_time_minutes': 7,
                'is_featured': True,
                'order': 1,
                'references': 'Kapur VK, et al. Clinical Practice Guideline for Diagnostic Testing for Adult OSA. J Clin Sleep Med. 2017;13(3):479-504.\nBerry RB, et al. AASM Scoring Manual Updates. J Clin Sleep Med. 2023.',
            },
            # ===== HASTALIKTA UYKU =====
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'migrende-uyku-bozukluklari',
                'article_type': 'disease_sleep',
                'title_tr': 'Migrende Uyku Bozukluklari',
                'title_en': 'Sleep Disorders in Migraine',
                'subtitle_tr': 'Migren ve uyku arasindaki cift yonlu iliski',
                'subtitle_en': 'The bidirectional relationship between migraine and sleep',
                'summary_tr': 'Migren hastalari arasinda uyku bozukluklari prevalansi genel populasyona gore 2-8 kat daha yuksektir. Uyku bozukluklari migreni tetiklerken, migren de uyku kalitesini bozmaktadir.',
                'summary_en': 'The prevalence of sleep disorders among migraine patients is 2-8 times higher than in the general population.',
                'content_tr': """## Migrende Uyku Bozukluklari

Migren ve uyku bozukluklari arasinda guclu bir cift yonlu iliski vardir. Bu iliski, ortak noropatolojik mekanizmalar uzerinden gerceklesir.

### Epidemiyoloji

- Migren hastalarinin **%50-75**'inde uyku bozuklugu mevcuttur
- Insomnia riski **2-3 kat** artmistir
- Uyku apnesi prevalansi **%36-56** arasindadir
- Kronik migrende uyku bozuklugu orani daha da yuksektir

### Migren ve Uyku: Ortak Mekanizmalar

**Serotonerjik Sistem:**
- Serotonin hem uyku duzenlenmesinde hem de migren patofizyolojisinde anahtar rol oynar
- Raphe cekirdekleri her iki sureci de kontrol eder

**Hipotalamus:**
- Sirkadiyen ritim kontrolu
- Migren ataklarinin sirkadiyen paterni
- Oreksin/hipokretin sistemi

**Trigeminovaskuler Sistem:**
- Uyku sirasinda aktive olabilir
- Gece migren ataklarinin mekanizmasi

### Uyku Bozukluklari Migreni Nasil Tetikler?

1. **Uyku yoksunlugu:** En guclu migren tetikleyicilerinden biri
2. **Asiri uyuma:** Hafta sonu migreni
3. **Duzensiz uyku programi:** Vardiyali calisma riski
4. **Uyku apnesi:** Hipoksi ve uyku fragmentasyonu
5. **Insomnia:** Kronik stres ve noroinflamasyon

### Migren Uyku Kalitesini Nasil Bozar?

- Gece migren ataklari uyku bütünlügünü bozar
- Migrenle iliskili anksiyete uykuya dalmayi zorlastirir
- Profilaktik ilaclarin uyku uzerine yan etkileri
- Agri nedeniylee gece uyanmalari

### Yonetim Stratejileri

**Uyku Hijyeni Optimizasyonu:**
- Duzunli uyku programi (hafta sonu dahil)
- 7-8 saat uyku hedefi
- Karanlik ve sessiz uyku ortami

**Uyku Guncesi Tutma:**
- Uyku suresi ve kalitesi kaydi
- Migren ataklariyla korelasyon analizi
- Tetikleyici paternlerini belirleme

**Farmakolojik Yaklasim:**
- Amitriptilin: Hem migren profilaksisi hem uyku duzenleyici
- Melatonin: Sirkadiyen ritim duzenlenmesi
- Uyku apnesi varsa CPAP tedavisi

> **Klinik Oneri:** Her migren hastasinin uyku kalitesi degerlendirilmeli ve uyku bozukluklari taranmalidir.""",
                'content_en': """## Sleep Disorders in Migraine

There is a strong bidirectional relationship between migraine and sleep disorders, occurring through shared neuropathological mechanisms.

### Epidemiology

- **50-75%** of migraine patients have sleep disorders
- Insomnia risk is increased **2-3 times**
- Sleep apnea prevalence is **36-56%**

### How Sleep Disorders Trigger Migraine

1. **Sleep deprivation:** One of the strongest migraine triggers
2. **Oversleeping:** Weekend migraine
3. **Irregular sleep schedule:** Shift work risk
4. **Sleep apnea:** Hypoxia and sleep fragmentation""",
                'reading_time_minutes': 8,
                'is_featured': True,
                'related_disease': 'migraine',
                'order': 1,
                'references': 'Tiseo C, et al. Migraine and sleep disorders: a systematic review. J Headache Pain. 2020;21(1):126.\nVgontzas A, Pavlovic JM. Sleep Disorders and Migraine. Continuum. 2018;24(4):1040-1061.',
            },
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'alzheimer-hastaliginda-uyku',
                'article_type': 'disease_sleep',
                'title_tr': 'Alzheimer Hastaliginda Uyku Bozukluklari',
                'title_en': 'Sleep Disorders in Alzheimer\'s Disease',
                'subtitle_tr': 'Uyku bozukluklari Alzheimer\'in hem belirtisi hem de risk faktorudur',
                'subtitle_en': 'Sleep disorders are both a symptom and risk factor for Alzheimer\'s',
                'summary_tr': 'Alzheimer hastalarinin %60-70\'inde uyku bozukluklari gorulur. Dahasi, kronik uyku bozukluklari beta-amiloid birikiminini hizlandirarak Alzheimer riskini artirabilir.',
                'summary_en': 'Sleep disorders occur in 60-70% of Alzheimer\'s patients. Moreover, chronic sleep disorders may increase Alzheimer\'s risk by accelerating beta-amyloid accumulation.',
                'content_tr': """## Alzheimer Hastaliginda Uyku Bozukluklari

Uyku ve Alzheimer hastaligi arasindaki iliski, son yillarda norobilimdeki en heyecan verici arastirma alanlarindan biri olmustur.

### Glimfatik Sistem ve Beta-Amiloid

- Beyindeki **glimfatik sistem** uyku sirasinda aktive olur
- Bu sistem beta-amiloid ve tau proteinlerini temizler
- Yetersiz uyku, toksin birikimine yol acar
- Tek bir gece uyku yoksunlugu bile beta-amiloid duzeylerini **%5-30** artirir

### Alzheimer'da Gorulen Uyku Bozukluklari

**1. Sirkadiyen Ritim Bozulmalari:**
- "Sundowning" (gunbatimi sendromu): Aksam saatlerinde ajitasyon
- Gunduz-gece dongusu bozulmasi
- Suprakiazmatik cekirdek dejenerasyonu

**2. Uyku Fragmentasyonu:**
- Sik gece uyanmalari
- Azalmis yavas dalga uykusu
- Azalmis REM uykusu

**3. Asiri Gunduz Uykululugu:**
- Hastalik ilerledikce artar
- Beyin sapi uyku merkezlerinin etkilenmesi

**4. REM Uyku Davranis Bozuklugu:**
- Lewy cisimcikli demans ile guclu iliski
- Norodejeneratif sureecin erken belirtisi

### Uyku Bozukluklari Alzheimer Riskini Artirir mi?

Kanitlar guclu bir evet'i isaret ediyor:
- 25+ yillik takip calismalarinda insomnia **%51** artmis demans riski
- Uyku apnesi kognitif gerilemeyi hizlandirir
- 6 saatten az uyku beta-amiloid birikimiyle iliskili
- Yavas dalga uykusu azalmasi erken belirci olabilir

### Bakim Veren Yukunu

- Alzheimer hastalarinin uyku bozukluklari bakim verenleri en cok zorlayan belirtidir
- Gece gezinme, gunduz uyuklama, gece ajitasyonu
- Bakim veren tukenmisligi ve depresyonu

### Tedavi Yaklasimi

**Non-farmakolojik (Oncelikli):**
- Gunduz isik maruziyeti (2000+ lux, 30-120 dk)
- Duzunli fiziksel aktivite
- Gece ortaminin duzenlenmesi
- Sosyal aktiviteler ve rutinler

**Farmakolojik:**
- Melatonin (0.5-5 mg, yatmadan once)
- Trazodon (dusuk doz)
- Uyku apnesi varsa CPAP
- Benzodiazepinlerden kacinilmali (dusme riski, konfuzyon)""",
                'content_en': """## Sleep Disorders in Alzheimer's Disease

The relationship between sleep and Alzheimer's disease has become one of the most exciting research areas in neuroscience.

### Glymphatic System and Beta-Amyloid

- The brain's **glymphatic system** activates during sleep
- This system clears beta-amyloid and tau proteins
- Insufficient sleep leads to toxin accumulation
- Even a single night of sleep deprivation increases beta-amyloid levels by **5-30%**""",
                'reading_time_minutes': 9,
                'is_featured': True,
                'related_disease': 'alzheimer',
                'order': 2,
                'references': 'Xie L, et al. Sleep drives metabolite clearance from the adult brain. Science. 2013;342(6156):373-377.\nShi L, et al. Sleep disturbances increase the risk of dementia. Alzheimers Dement. 2018;14(10):1235-1247.',
            },
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'parkinson-hastaliginda-uyku',
                'article_type': 'disease_sleep',
                'title_tr': 'Parkinson Hastaliginda Uyku Sorunlari',
                'title_en': 'Sleep Problems in Parkinson\'s Disease',
                'subtitle_tr': 'REM uyku davranis bozuklugundan insomniaya: Parkinson ve uyku',
                'subtitle_en': 'From REM sleep behavior disorder to insomnia: Parkinson and sleep',
                'summary_tr': 'Parkinson hastalarinin %60-90\'inda uyku bozukluklari gorulur. REM uyku davranis bozuklugu, Parkinson\'un motor belirtilerinden yillar once ortaya cikabilir ve erken tani icin onemli bir biyobelirtectir.',
                'summary_en': 'Sleep disorders occur in 60-90% of Parkinson\'s patients. REM sleep behavior disorder can appear years before Parkinson\'s motor symptoms.',
                'content_tr': """## Parkinson Hastaliginda Uyku Sorunlari

Parkinson hastaligi (PH) yalnizca bir hareket bozuklugu degildir; uyku bozukluklari hastaligin en erken ve en sik gorulen non-motor belirtileri arasindadir.

### REM Uyku Davranis Bozuklugu (RBD) - Erken Uyari Isareti

- PH hastalarinin **%30-60**'inda gorulur
- Motor belirtilerden **5-15 yil** once ortaya cikabilir
- RBD'li hastalarin **%80-90**'i zamanla sinukleinopati gelisir
- Alfa-sinuklein patolojisinin erken gostergesi

**Klinik Ozellikler:**
- Ruya canlandirma davranislari
- Yataktan dusme
- Es partnere zarar verme
- Canli, siklikla siddet iceren dusler

### Diger Uyku Bozukluklari

**1. Insomnia (%30-80):**
- Uyku fragmentasyonu en sik gorulen sorun
- Motor belirtiler (tremor, rijidite) uyumayi zorlastirir
- Noktüri nedeniyle sik uyanma
- Dopaminerjik ilaclarin uyku uzerine etkileri

**2. Asiri Gunduz Uykululugu (%15-50):**
- Dopamin agonistlerinin yan etkisi
- Ani uyku ataklari (surucu guvenligi riski)
- Beyin sapi uyku merkezlerinin dejenerasyonu

**3. Huzursuz Bacak Sendromu (%15-20):**
- Dopamin disfonksiyonu ile ortak mekanizma
- Aksam ve gece bacaklarda hareket ettirme durtüsü
- Demir eksikligi ile iliskili olabilir

**4. Uyku Apnesi:**
- Ust hava yolu kas tonusu azalmasi
- Noktürnal stridor (laringeal distoni)

### Tedavi

**RBD Icin:**
- Melatonin (3-12 mg): Birinci basamak, guvenli
- Klonazepam (0.25-2 mg): Etkili ama dusme riski
- Yatak guvenligi onlemleri

**Insomnia Icin:**
- Uyku hijyeni optimizasyonu
- Gece dopaminerjik tedavi ayarlmasi
- Melatonin
- BDT-I (bilissel davranisci terapi)

**Gunduz Uykululugu Icin:**
- Ilac rejiminin gozden gecirilmesi
- Planli kisa uykuler (nap)
- Modafinil (seciici vakalarda)""",
                'content_en': """## Sleep Problems in Parkinson's Disease

Parkinson's disease (PD) is not just a movement disorder; sleep disorders are among the earliest and most common non-motor symptoms.

### REM Sleep Behavior Disorder (RBD) - Early Warning Sign

- Occurs in **30-60%** of PD patients
- Can appear **5-15 years** before motor symptoms
- **80-90%** of RBD patients eventually develop synucleinopathy""",
                'reading_time_minutes': 8,
                'is_featured': False,
                'related_disease': 'parkinson',
                'order': 3,
                'references': 'Schenck CH, et al. REM sleep behavior disorder: clinical, developmental, and neuroscience perspectives. Sleep. 2019;42(1).\nVidenovic A, Golombek D. Circadian and Sleep Disorders in Parkinson Disease. Exp Neurol. 2017;297:221-229.',
            },
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'diyabette-uyku-bozukluklari',
                'article_type': 'disease_sleep',
                'title_tr': 'Diyabette Uyku Bozukluklari',
                'title_en': 'Sleep Disorders in Diabetes',
                'subtitle_tr': 'Kan sekeri kontrolu ve uyku kalitesi arasindaki kritik baglanti',
                'subtitle_en': 'The critical link between blood sugar control and sleep quality',
                'summary_tr': 'Tip 2 diyabet hastalarinin %50-70\'inde uyku bozuklugu vardir. Yetersiz uyku insulin direncini artirir, kan sekeri kontrolunu zorlastirir ve diyabet komplikasyonlarini hizlandirir.',
                'summary_en': '50-70% of type 2 diabetes patients have sleep disorders. Insufficient sleep increases insulin resistance and complicates blood sugar control.',
                'content_tr': """## Diyabette Uyku Bozukluklari

Diyabet ve uyku bozukluklari arasinda guclu bir cift yonlu iliski vardir. Bu iliski metabolik, hormonal ve norolojik mekanizmalar uzerinden isler.

### Uyku Yoksunlugu ve Insulin Direnci

- 4-5 saat uyku, insulin duyarliligini **%40** azaltir
- Kortizol ve buyume hormonu dengesizligi
- Ghrelin artar (istah artar), leptin azalir (tokluk azalir)
- Sempatik sinir sistemi aktivasyonu

### Diyabette Sik Gorulen Uyku Bozukluklari

**1. Obstruktif Uyku Apnesi (%58-86):**
- Diyabet hastalarinda cok yuksek prevalans
- Intermittan hipoksi insulin direncini artirir
- CPAP tedavisi HbA1c'yi dusurebiir

**2. Insomnia (%40-60):**
- Noktüri: Hiperglisemi nedeniyle sik idrara cikma
- Periferik noropati: Gece agrisi ve uyusma
- Huzursuz bacak sendromu

**3. Huzursuz Bacak Sendromu (%15-30):**
- Diyabetik periferik noropatii ile iliskili
- Demir metabolizmasi bozukluklari

### Uyku ve Kan Sekeri Dongusu

- Yetersiz uyku -> artan kortizol -> insulin direnci -> hiperglisemi
- Hiperglisemi -> poliüri -> noktüri -> uyku bölünmesi
- Kisir dongu!

### Yonetim

- Kan sekeri regulasyonu
- Uyku apnesi taramasi ve CPAP
- Uyku hijyeni
- Noropatik agri yonetimi
- Egzersiz programi""",
                'content_en': """## Sleep Disorders in Diabetes

There is a strong bidirectional relationship between diabetes and sleep disorders.

### Sleep Deprivation and Insulin Resistance

- 4-5 hours of sleep reduces insulin sensitivity by **40%**
- Cortisol and growth hormone imbalance
- Ghrelin increases (appetite up), leptin decreases (satiety down)""",
                'reading_time_minutes': 7,
                'is_featured': False,
                'related_disease': 'diabetes',
                'order': 4,
                'references': 'Reutrakul S, Van Cauter E. Sleep influences on obesity, insulin resistance, and risk of type 2 diabetes. Metabolism. 2018;84:56-66.',
            },
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'adhd-ve-uyku',
                'article_type': 'disease_sleep',
                'title_tr': 'ADHD\'de Uyku Bozukluklari',
                'title_en': 'Sleep Disorders in ADHD',
                'subtitle_tr': 'Dikkat eksikligi hiperaktivite bozuklugu ve uyku iliskisi',
                'subtitle_en': 'The relationship between ADHD and sleep',
                'summary_tr': 'ADHD\'li bireylerin %25-50\'sinde uyku bozukluklari gorulur. Uyku sorunlari ADHD belirtilerini agırlastirirken, ADHD tedavisinde kullanilan stimulanlar da uyku kalitesini etkileyebilir.',
                'summary_en': 'Sleep disorders occur in 25-50% of individuals with ADHD. Sleep problems worsen ADHD symptoms while stimulants used in ADHD treatment can also affect sleep quality.',
                'content_tr': """## ADHD'de Uyku Bozukluklari

ADHD ve uyku bozukluklari arasindaki iliski karmasik ve cok katmanlidir. Uyku sorunlari hem ADHD'nin bir parçcasi hem de belirtileri agrlastiran bagimsiz bir faktor olabilir.

### ADHD'de Uyku Bozuklugu Tipleri

**1. Uykuya Dalma Guclugu:**
- ADHD'nin en sik uyku sikayeti
- "Zihin kapanmiyor" fenomeni
- Gecikms uyku fazii sendromu (DSPS) yaygin
- Melatonin salgilanmasinda 1.5 saat gecikme

**2. Uyku Surekliliginde Bozulma:**
- Huzursuz uyku
- Sik gece uyanmalari
- Uyku etkinligi dusuklugu

**3. Sabah Kalkma Guclugu:**
- "Uyku sarhoöslugu" (sleep inertia)
- Gecikims sirkadiyen ritim
- Okul/is performansini etkiler

**4. Huzursuz Bacak Sendromu ve PLMD:**
- ADHD'de prevalans %20-44
- Demir eksikligi ortak mekanizma
- Ferritin <50 ng/mL durumunda demir takviyesi

### Stimulan Ilaclar ve Uyku

- Metilfenidat ve amfetaminler uyku latensini uzatabilir
- Uzun etkili formullerin aksam dozlari uyku bozabilir
- Ancak bazi hastalarda stimulanlar uyku kalitesini iyilestirir
- Ilac zamanlamas ve doz ayarlamasi kritik

### Yonetim Stratejileri

**Davranissal:**
- Siki uyku rutini
- Yatak odasi duzeni (uyaran azaltma)
- Ekran suresi sinirlamasi
- Fiziksel aktivite (ama yatmadan 3 saat once degil)

**Farmakolojik:**
- Melatonin (uykuya dalma icin en etkili)
- Ilac zamanlamas optimizasyonu
- Gerekirse kisa etkili stimulana gecis""",
                'content_en': """## Sleep Disorders in ADHD

The relationship between ADHD and sleep disorders is complex and multilayered.

### Types of Sleep Disorders in ADHD

**1. Difficulty Falling Asleep:**
- Most common sleep complaint in ADHD
- "Mind won't shut off" phenomenon
- Delayed sleep phase syndrome (DSPS) is common

**2. Restless Legs Syndrome and PLMD:**
- Prevalence in ADHD is 20-44%
- Iron deficiency as shared mechanism""",
                'reading_time_minutes': 7,
                'is_featured': False,
                'related_disease': 'adhd',
                'order': 5,
                'references': 'Hvolby A. Associations of sleep disturbance with ADHD. Atten Defic Hyperact Disord. 2015;7(1):1-18.\nDiaz-Roman A, et al. Sleep in ADHD: a meta-analysis. Pediatrics. 2018;141(3):e20171743.',
            },
            {
                'category': cats['hastalikta-uyku'],
                'slug': 'epilepside-uyku-iliskisi',
                'article_type': 'disease_sleep',
                'title_tr': 'Epilepside Uyku ve Nöbet Iliskisi',
                'title_en': 'Sleep and Seizure Relationship in Epilepsy',
                'subtitle_tr': 'Uyku evreleri, nobet zamanlamasi ve epilepsi tedavisinde uyku faktorü',
                'subtitle_en': 'Sleep stages, seizure timing and the sleep factor in epilepsy treatment',
                'summary_tr': 'Epilepsi hastalarinin %30-50\'sinde uyku bozukluklari gorulur. Bazi nobet tipleri belirli uyku evrelerinde ortaya cikar ve uyku yoksunlugu nobet esigini dusurur.',
                'summary_en': 'Sleep disorders occur in 30-50% of epilepsy patients. Some seizure types occur during specific sleep stages.',
                'content_tr': """## Epilepside Uyku ve Nöbet Iliskisi

Epilepsi ve uyku arasinda karmasik bir iliski vardir. Uyku nobetleri hem tetikleyebilir hem de baskilayabilir; epilepsi de uyku yapisini bozabilir.

### Uyku Evreleri ve Nöbetler

**NREM Uykusu (Evre N1-N3):**
- Nobet olusumunu KOLAYLASTIRIR
- Ozellikle N2 ve N3 (derin uyku) evreleri
- Kortikal senkronizasyon artisi
- Jeneralize tonik-klonik nobetler
- Gece frontal lob epilepsisi

**REM Uykusu:**
- Nobet olusumunu BASKLAR
- Kortikal desenkronizasyon
- Kas atonisi
- Fokal nobetler yayilma gostermez

### Uykuyla Iliskili Epilepsi Sendromlari

**1. Gece Frontal Lob Epilepsisi:**
- Nöobetler NREM uykusunda
- Paroksismal gece distonisi
- Parasomnilerle karisabilir
- Karbamezapin tedavide etkili

**2. Benign Rolandik Epilepsi:**
- Cocukluk caginin en sik epilepsisi
- Nobetler genellikle uykulda
- Iyi prognoz

**3. Juvenil Miyoklonik Epilepsi:**
- Sabah uyanma doneminde nobetler
- Uyku yoksunlugu guclu tetikleyici
- Valproat tedavide altinn standart

### Uyku Yoksunlugu ve Nobet Esigi

- Uyku yoksunlugu epilepside en guclu nobet tetikleyicilerinden biridir
- EEG'de interiktal dechargeleri artirir
- Nobet esigini dusurur
- Antiepileptik ilac etkinligini azaltabilir

### Antiepileptik Ilaclar ve Uyku

| Ilac | Uyku Etkisi |
|------|-------------|
| Karbamazepin | Uyku kalitesini artirabilir |
| Valproat | Uyku yapisini bozabilir |
| Lamotrijin | Nötr - hafif uyku iyilestirici |
| Levetirasetam | Insomnia yapabilir |
| Gabapentin | Derin uyku artirir |

### Yonetim Onerileri

- Duzenli uyku programi (en onemli basamak)
- 7-9 saat uyku hedefi
- Uyku yoksunlugundan kacinma
- Uyku apnesi taramasi
- EEG'de uyku kaydinin degerlendirilmesi""",
                'content_en': """## Sleep and Seizure Relationship in Epilepsy

There is a complex relationship between epilepsy and sleep. Sleep can both trigger and suppress seizures; epilepsy can also disrupt sleep architecture.

### Sleep Stages and Seizures

**NREM Sleep:** Facilitates seizure generation
**REM Sleep:** Suppresses seizure generation""",
                'reading_time_minutes': 8,
                'is_featured': False,
                'related_disease': 'epilepsy',
                'order': 6,
                'references': 'Bazil CW. Sleep and Epilepsy. Continuum. 2017;23(4):1032-1048.\nDerry CP, et al. Sleep and epilepsy. Epilepsy Behav. 2013;26(3):394-404.',
            },
            # ===== UYKU SAGLIGI =====
            {
                'category': cats['uyku-sagligi'],
                'slug': 'uyku-evreleri-ve-fizyolojisi',
                'article_type': 'general',
                'title_tr': 'Uyku Evreleri ve Fizyolojisi',
                'title_en': 'Sleep Stages and Physiology',
                'subtitle_tr': 'Uyku sirasinda beyninizde ve vucuduuzzda neler olur?',
                'subtitle_en': 'What happens in your brain and body during sleep?',
                'summary_tr': 'Uyku, NREM ve REM olmak uzere iki ana evreden olusan aktif bir suructur. Her evre farkli fizyolojik islevlere sahiptir ve saglikli bir uyku icin tüm evrelerin yeterli suredte yasanmasi gerekir.',
                'summary_en': 'Sleep is an active process consisting of two main stages: NREM and REM. Each stage has different physiological functions.',
                'content_tr': """## Uyku Evreleri ve Fizyolojisi

Uyku, basitce "bilinc kapanmasi" degil; beynin aktif olarak calismaya devam ettigi, vucudun onarim ve yenilenme sureclelerinin gerceklestigi karmasik bir fizyolojik durumdur.

### Uyku Evreleri

**Evre N1 (Hafif Uyku) - %5:**
- Uyanikliktan uykuya gecis
- Kolayca uyanilabilir
- Yavas goz hareketleri
- Kas tonusunde hafif azalma
- Sure: 5-10 dakika

**Evre N2 (Orta Derinlikte Uyku) - %45-55:**
- Uykunun en buyuk bolumu
- Uyku iğcikleri ve K-kompleksleri
- Vucut sicakligi duser
- Kalp hizi ve solunum yavasliar
- Hafiza konsolidasyonu baslar

**Evre N3 (Derin Uyku / Yavas Dalga Uykusu) - %15-25:**
- En dinlendirici evre
- Delta dalgalari baskin
- Buyume hormonu salgilanr
- Hücre onarimi ve baggisiklik sistemi guclenddirmesi
- Uyandirmak zordur
- Yas ile azalir

**REM Uykusu - %20-25:**
- Hizli goz hareketleri
- Canli ruyalar
- Kas atonisi (felc benzeri durum)
- Beyin aktivitesi uyanikliga benzer
- Duygusal hafiza islenmesi
- Ogrenme ve yaratcilik

### Uyku Dongusu

- Bir dongu yaklasik **90 dakika** surer
- Gece boyunca **4-6 dongu** yasanir
- Ilk dongulerde derin uyku baskin
- Son dongulerde REM uykusu uzar
- Her dongunun sonunda kisa uyanmalar normal

### Sirkadiyen Ritim

- **Suprakiazmatik cekirdek (SCN):** Beynin biyolojik saati
- Isik-karanlik dongusuyle senkronize olur
- **Melatonin:** Karanlikta artar, uykuyu baslatir
- **Kortizol:** Sabah artar, uyanmayi saglar

### Ne Kadar Uyku Gerekli?

| Yas Grubu | Onerilen Sure |
|-----------|---------------|
| Yenidogan (0-3 ay) | 14-17 saat |
| Bebek (4-11 ay) | 12-15 saat |
| Kucuk cocuk (1-2 yas) | 11-14 saat |
| Okul oncesi (3-5 yas) | 10-13 saat |
| Okul cagi (6-13 yas) | 9-11 saat |
| Ergen (14-17 yas) | 8-10 saat |
| Eriskin (18-64 yas) | 7-9 saat |
| Yasli (65+ yas) | 7-8 saat |""",
                'content_en': """## Sleep Stages and Physiology

Sleep is not simply "loss of consciousness" but a complex physiological state where the brain continues to actively work.

### Sleep Stages

**Stage N1 (Light Sleep) - 5%**
**Stage N2 (Medium Deep Sleep) - 45-55%**
**Stage N3 (Deep Sleep / Slow Wave Sleep) - 15-25%**
**REM Sleep - 20-25%**

### Sleep Cycle

- One cycle lasts approximately **90 minutes**
- **4-6 cycles** occur throughout the night""",
                'reading_time_minutes': 7,
                'is_featured': True,
                'order': 1,
                'references': 'Carskadon MA, Dement WC. Normal Human Sleep: An Overview. In: Principles and Practice of Sleep Medicine. 6th ed.\nNational Sleep Foundation. Sleep Duration Recommendations. Sleep Health. 2015;1(1):40-43.',
            },
        ]

    def _create_tips(self):
        tips = [
            {'title_tr': 'Her gun ayni saatte uyanin', 'title_en': 'Wake up at the same time every day', 'content_tr': 'Hafta ici ve hafta sonu ayni saatte uyanmak sirkadiyen ritminizi guclenirir ve gece daha kolay uyumanizi saglar.', 'content_en': 'Waking up at the same time on weekdays and weekends strengthens your circadian rhythm.', 'icon': 'alarm-clock', 'order': 1},
            {'title_tr': 'Yatak odanizi serin tutun', 'title_en': 'Keep your bedroom cool', 'content_tr': 'Ideal uyku sicakligi 18-20 derecedir. Serin ortam melatonin salgilanmasini destekler.', 'content_en': 'Ideal sleep temperature is 18-20 degrees. Cool environment supports melatonin secretion.', 'icon': 'thermometer', 'order': 2},
            {'title_tr': 'Yatmadan once ekranlardan uzak durun', 'title_en': 'Stay away from screens before bed', 'content_tr': 'Telefon ve tablet ekranlarindaki mavi isik melatonin salgilanmasini %50 ye kadar baskilayabilir.', 'content_en': 'Blue light from phone and tablet screens can suppress melatonin secretion by up to 50%.', 'icon': 'smartphone-off', 'order': 3},
            {'title_tr': 'Ogleden sonra kafein almayin', 'title_en': 'No caffeine after noon', 'content_tr': 'Kafeinin yari omru 5-6 saattir. Ogle sonrasi kahve, cay akksam uykunuzu bozar.', 'content_en': 'Caffeine half-life is 5-6 hours. Afternoon coffee or tea disrupts your evening sleep.', 'icon': 'coffee', 'order': 4},
            {'title_tr': 'Sabah gunes isigina cikin', 'title_en': 'Get morning sunlight', 'content_tr': 'Sabah ilk 30 dakikada dis mekan isigina cikmak sirkadiyen saatinizi sifirlar.', 'content_en': 'Getting outdoor light in the first 30 minutes resets your circadian clock.', 'icon': 'sun', 'order': 5},
            {'title_tr': '20 dakika kuralini uygulayin', 'title_en': 'Apply the 20-minute rule', 'content_tr': '20 dakika iceinde uyuyamadiiysaniz yataktan kalkin, sakin bir aktivite yapin.', 'content_en': 'If you can\'t fall asleep within 20 minutes, get out of bed and do a calm activity.', 'icon': 'clock', 'order': 6},
            {'title_tr': 'Duzenli egzersiz yapin', 'title_en': 'Exercise regularly', 'content_tr': 'Haftada 150 dk orta yogunlukta egzersiz uyku kalitesini %65 artirabilir. Yatmadan 3 saat once bitirin.', 'content_en': '150 min of moderate exercise per week can improve sleep quality by 65%.', 'icon': 'activity', 'order': 7},
            {'title_tr': 'Ilik bir dus alin', 'title_en': 'Take a warm shower', 'content_tr': 'Yatmadan 1 saat once ilik dus almak vucut sicakligini dusurerek uyumaya yardimci olur.', 'content_en': 'A warm shower 1 hour before bed helps lower body temperature to aid sleep.', 'icon': 'droplets', 'order': 8},
        ]
        for tip_data in tips:
            SleepTip.objects.update_or_create(
                title_tr=tip_data['title_tr'],
                defaults=tip_data,
            )
        self.stdout.write(f'  {len(tips)} ipucu olusturuldu.')

    def _create_faqs(self):
        cats = {c.slug: c for c in SleepCategory.objects.all()}
        faqs = [
            {'category': cats.get('uyku-sagligi'), 'question_tr': 'Yetiskinler icin ideal uyku suresi nedir?', 'question_en': 'What is the ideal sleep duration for adults?', 'answer_tr': 'Yetiskinler icin onerilen uyku suresi 7-9 saattir. Ancak bu kisiden kisiye degisebilir. Onemli olan dinlenmis uyanmak ve gunduz uykulu hissetmemektir.', 'answer_en': 'The recommended sleep duration for adults is 7-9 hours. However, this can vary from person to person.', 'order': 1},
            {'category': cats.get('uyku-bozukluklari'), 'question_tr': 'Horlama tehlikeli midir?', 'question_en': 'Is snoring dangerous?', 'answer_tr': 'Horlama her zaman tehlikeli degildir ancak uyku apnesi belirtisi olabilir. Yuksek sesli, duzensiz horlama, gunduz uykululugu ve taniklanan nefes durmalari varsa mutlaka degerlndirilmelidir.', 'answer_en': 'Snoring is not always dangerous but can be a sign of sleep apnea. Loud, irregular snoring with daytime sleepiness should be evaluated.', 'order': 2},
            {'category': cats.get('uyku-hijyeni'), 'question_tr': 'Melatonin takviyesi guvenli midir?', 'question_en': 'Is melatonin supplementation safe?', 'answer_tr': 'Kisa sureli kullanimda melatonin genellikle guvenlidir. Ancak uzun sureli kullanim icin hekim tavsiyesi gerekir. Doz genellikle 0.5-5 mg arasinda, yatmadan 30-60 dakika once alinir.', 'answer_en': 'Melatonin is generally safe for short-term use. However, physician advice is needed for long-term use.', 'order': 3},
            {'category': cats.get('uyku-bozukluklari'), 'question_tr': 'Uyku apnesi tedavi edilmezse ne olur?', 'question_en': 'What happens if sleep apnea is not treated?', 'answer_tr': 'Tedavi edilmeyen uyku apnesi hipertansiyon, kalp krizi, inme, diyabet ve trafik kazasi riskini onemli olcude artirir. CPAP tedavisi bu riskleri azaltir.', 'answer_en': 'Untreated sleep apnea significantly increases the risk of hypertension, heart attack, stroke, diabetes and traffic accidents.', 'order': 4},
            {'category': cats.get('uyku-sagligi'), 'question_tr': 'Gunduz uyumak zararli midir?', 'question_en': 'Is daytime napping harmful?', 'answer_tr': '20-30 dakikalik kisa uykuler faydalidirr. Ancak 30 dakikayi gecen veya ogleden sonra gec yapilan uykuler gece uykusunu bozabilir.', 'answer_en': 'Short naps of 20-30 minutes are beneficial. However, naps longer than 30 minutes or late afternoon naps can disrupt nighttime sleep.', 'order': 5},
            {'category': cats.get('tani-yontemleri'), 'question_tr': 'Polisomnografi icin hastanede mi kalmam gerekir?', 'question_en': 'Do I need to stay in hospital for polysomnography?', 'answer_tr': 'Evet, klasik polisomnografi uyku laboratuvaarinda gece boyu yapilir. Ancak bazi durumlarda ev tipi uyku testi de kullanilabilir. Doktorunuz sizin icin uygun yontemi belirleyecektir.', 'answer_en': 'Yes, classical polysomnography is performed overnight in a sleep laboratory. However, home sleep tests can be used in some cases.', 'order': 6},
        ]
        for faq_data in faqs:
            SleepFAQ.objects.update_or_create(
                question_tr=faq_data['question_tr'],
                defaults=faq_data,
            )
        self.stdout.write(f'  {len(faqs)} SSS olusturuldu.')
