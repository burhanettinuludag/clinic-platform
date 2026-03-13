"""
Migren Egitim Seti - 5 modul x 5 kart = 25 egitim icerigi + 5 quiz + rozetler.
Kullanim: python3 manage.py seed_migraine_education
"""
from django.core.management.base import BaseCommand
from apps.content.models import (
    ContentCategory, EducationItem, EducationQuiz, QuizQuestion,
)
from apps.patients.models import DiseaseModule
from apps.gamification.models import Badge


class Command(BaseCommand):
    help = 'Migren egitim seti: 25 kart, 5 quiz, 7 rozet'

    def handle(self, *args, **options):
        # Migren modulu
        migraine_module = DiseaseModule.objects.filter(slug='migraine').first()
        if not migraine_module:
            migraine_module = DiseaseModule.objects.filter(disease_type='migraine').first()
        if not migraine_module:
            self.stderr.write('Migren modulu bulunamadi! Once seed_modules calistirin.')
            return

        # ─── Kategoriler ───
        categories = {}
        cat_data = [
            ('migraine-basics', 'Migreni Taniyalim', 'Understanding Migraine', 1),
            ('migraine-triggers', 'Tetikleyiciler', 'Triggers', 2),
            ('migraine-attack', 'Atak Yonetimi', 'Attack Management', 3),
            ('migraine-lifestyle', 'Yasam Tarzi', 'Lifestyle', 4),
            ('migraine-advanced', 'Ileri Konular', 'Advanced Topics', 5),
        ]
        for slug, name_tr, name_en, order in cat_data:
            cat, _ = ContentCategory.objects.update_or_create(
                slug=slug,
                defaults={'name_tr': name_tr, 'name_en': name_en, 'order': order + 100},
            )
            categories[slug] = cat

        # ─── 25 Egitim Karti ───
        cards = self._get_cards()
        created_cards = 0
        for card in cards:
            cat = categories[card['category']]
            _, created = EducationItem.objects.update_or_create(
                slug=card['slug'],
                defaults={
                    'title_tr': card['title_tr'],
                    'title_en': card['title_en'],
                    'body_tr': card['body_tr'],
                    'body_en': card['body_en'],
                    'content_type': 'text',
                    'disease_module': migraine_module,
                    'category': cat,
                    'order': card['order'],
                    'is_published': True,
                    'estimated_duration_minutes': card.get('duration', 4),
                },
            )
            if created:
                created_cards += 1

        self.stdout.write(f'EducationItem: {created_cards} yeni, {len(cards) - created_cards} guncellendi.')

        # ─── 5 Quiz ───
        quizzes_data = self._get_quizzes()
        created_quizzes = 0
        for qd in quizzes_data:
            cat = categories[qd['category']]
            quiz, created = EducationQuiz.objects.update_or_create(
                slug=qd['slug'],
                defaults={
                    'title_tr': qd['title_tr'],
                    'title_en': qd['title_en'],
                    'description_tr': qd['description_tr'],
                    'description_en': qd['description_en'],
                    'disease_module': migraine_module,
                    'category': cat,
                    'passing_score_percent': 60,
                    'points_reward': 10,
                    'is_published': True,
                    'order': qd['order'],
                },
            )
            if created:
                created_quizzes += 1

            # Quiz'e ait kartlari bagla
            quiz_items = EducationItem.objects.filter(
                category=cat, disease_module=migraine_module
            )
            quiz.education_items.set(quiz_items)

            # Sorulari ekle
            for i, q in enumerate(qd['questions'], 1):
                QuizQuestion.objects.update_or_create(
                    quiz=quiz,
                    order=i,
                    defaults={
                        'question_tr': q['question_tr'],
                        'question_en': q['question_en'],
                        'options': q['options'],
                        'explanation_tr': q.get('explanation_tr', ''),
                        'explanation_en': q.get('explanation_en', ''),
                    },
                )

        self.stdout.write(f'EducationQuiz: {created_quizzes} yeni, {len(quizzes_data) - created_quizzes} guncellendi.')

        # ─── Rozetler ───
        badges = self._get_badges()
        created_badges = 0
        for b in badges:
            _, created = Badge.objects.update_or_create(
                requirement_type=b['requirement_type'],
                requirement_value=b['requirement_value'],
                defaults=b,
            )
            if created:
                created_badges += 1

        self.stdout.write(f'Badge: {created_badges} yeni, {len(badges) - created_badges} guncellendi.')
        self.stdout.write(self.style.SUCCESS('Migren egitim seti basariyla yuklendi!'))

    def _get_cards(self):
        """25 egitim karti verisi."""
        return [
            # ═══ MODUL 1: Migreni Taniyalim ═══
            {
                'slug': 'migraine-101-nedir',
                'category': 'migraine-basics',
                'order': 1,
                'duration': 4,
                'title_tr': 'Migren Nedir?',
                'title_en': 'What is Migraine?',
                'body_tr': (
                    '## Migren: Sadece Bas Agrisi Degil\n\n'
                    'Migren, tekrarlayan ve genellikle siddetli bas agrilari ile karakterize norolojik bir hastaliktir. '
                    'Sadece bir bas agrisi olmaktan cok otesinde, beyindeki sinir hucreleri ve kimyasal degisikliklerle iliskili karmasik bir durumdur.\n\n'
                    '### Normal Bas Agrisindan Farki\n\n'
                    '- **Siddet:** Migren agrisi genellikle orta-siddetli duzeydir ve gunluk aktiviteleri engeller\n'
                    '- **Konum:** Genellikle basin bir tarafinda hissedilir (tek tarafli)\n'
                    '- **Nitelik:** Zonklayici, atan tarzdadir\n'
                    '- **Eslik eden belirtiler:** Bulanti, kusma, isik ve ses hassasiyeti\n'
                    '- **Sure:** 4-72 saat arasinda devam edebilir\n\n'
                    'Migren, dunya genelinde yaklasik 1 milyar insani etkileyen en yaygin norolojik hastaliklar arasindadir.'
                ),
                'body_en': (
                    '## Migraine: More Than Just a Headache\n\n'
                    'Migraine is a neurological condition characterized by recurring and usually severe headaches. '
                    'Far beyond just a headache, it is a complex condition related to nerve cells and chemical changes in the brain.\n\n'
                    '### How It Differs from Regular Headaches\n\n'
                    '- **Severity:** Migraine pain is usually moderate to severe and interferes with daily activities\n'
                    '- **Location:** Usually felt on one side of the head (unilateral)\n'
                    '- **Quality:** Throbbing, pulsating nature\n'
                    '- **Associated symptoms:** Nausea, vomiting, light and sound sensitivity\n'
                    '- **Duration:** Can last 4-72 hours\n\n'
                    'Migraine affects approximately 1 billion people worldwide, making it one of the most common neurological conditions.'
                ),
            },
            {
                'slug': 'migraine-102-turleri',
                'category': 'migraine-basics',
                'order': 2,
                'duration': 4,
                'title_tr': 'Migren Turleri',
                'title_en': 'Types of Migraine',
                'body_tr': (
                    '## Migren Turleri\n\n'
                    '### Aurasiz Migren\n'
                    'En yaygin tur olup migren hastalarinin yaklasik %70-80\'inde gorulur. Aura (uyari belirtileri) olmadan dogrudan agri baslar.\n\n'
                    '### Aurali Migren\n'
                    'Agri baslamadan once 15-60 dakika suren gorsel, duyusal veya konusma bozukluklari yasanir:\n'
                    '- **Gorsel aura:** Parlak noktalar, zigzag cizgiler, gorme alani kaybi\n'
                    '- **Duyusal aura:** Kol veya yuzde karincilanma, uyusma\n'
                    '- **Konusma aurasi:** Sozcuk bulmada zorluk\n\n'
                    '### Kronik Migren\n'
                    'Ayda 15 gun veya daha fazla bas agrisi (en az 8 gunu migren ozelligi tasir). Tedavi gerektiren onemli bir durumdur.\n\n'
                    '### Diger Turler\n'
                    '- Hemiplejik migren (gecici felc belirtileri)\n'
                    '- Vestibular migren (bas donmesi agrili)\n'
                    '- Retinal migren (tek gozde gecici gorme kaybi)'
                ),
                'body_en': (
                    '## Types of Migraine\n\n'
                    '### Migraine Without Aura\n'
                    'The most common type, occurring in approximately 70-80% of migraine patients. Pain starts directly without warning symptoms.\n\n'
                    '### Migraine With Aura\n'
                    'Visual, sensory, or speech disturbances lasting 15-60 minutes occur before pain starts:\n'
                    '- **Visual aura:** Bright spots, zigzag lines, visual field loss\n'
                    '- **Sensory aura:** Tingling or numbness in arm or face\n'
                    '- **Speech aura:** Difficulty finding words\n\n'
                    '### Chronic Migraine\n'
                    'Headache 15 or more days per month (at least 8 days with migraine features). An important condition requiring treatment.\n\n'
                    '### Other Types\n'
                    '- Hemiplegic migraine (temporary paralysis symptoms)\n'
                    '- Vestibular migraine (with dizziness)\n'
                    '- Retinal migraine (temporary vision loss in one eye)'
                ),
            },
            {
                'slug': 'migraine-103-fazlari',
                'category': 'migraine-basics',
                'order': 3,
                'duration': 5,
                'title_tr': 'Migren Ataklarinin 4 Fazi',
                'title_en': 'The 4 Phases of a Migraine Attack',
                'body_tr': (
                    '## Migren Ataginin 4 Fazi\n\n'
                    'Bir migren atagi genellikle dort faz halinde ilerler. Her hastada tum fazlar gorulmeyebilir.\n\n'
                    '### 1. Prodrom (On Belirti) Fazi - 24-48 saat once\n'
                    '- Ruh hali degisiklikleri (asiri mutluluk veya huysuzluk)\n'
                    '- Yiyecek istekleri (ozellikle tatli)\n'
                    '- Boyun sertligi\n'
                    '- Esneme artisi, yorgunluk\n'
                    '- Kabizlik veya ishal\n\n'
                    '### 2. Aura Fazi - 15-60 dakika\n'
                    '- Gorsel bozukluklar (zigzag, parlak noktalar)\n'
                    '- Uyusma, karincilanma\n'
                    '- Her hastada gorulmez\n\n'
                    '### 3. Agri (Atak) Fazi - 4-72 saat\n'
                    '- Zonklayici siddetli bas agrisi\n'
                    '- Isik ve ses hassasiyeti (fotofobi, fonofobi)\n'
                    '- Bulanti, kusma\n'
                    '- Fiziksel aktiviteyle artis\n\n'
                    '### 4. Postdrom (Sonrasi) Fazi - 24-48 saat\n'
                    '- Yorgunluk, bitkinlik\n'
                    '- Konsantrasyon guclugu\n'
                    '- Hafif bas agrisi\n'
                    '- Ruh hali degisiklikleri'
                ),
                'body_en': (
                    '## The 4 Phases of a Migraine Attack\n\n'
                    'A migraine attack typically progresses through four phases. Not all patients experience every phase.\n\n'
                    '### 1. Prodrome Phase - 24-48 hours before\n'
                    '- Mood changes (excessive happiness or irritability)\n'
                    '- Food cravings (especially sweets)\n'
                    '- Neck stiffness\n'
                    '- Increased yawning, fatigue\n'
                    '- Constipation or diarrhea\n\n'
                    '### 2. Aura Phase - 15-60 minutes\n'
                    '- Visual disturbances (zigzag, bright spots)\n'
                    '- Numbness, tingling\n'
                    '- Not present in all patients\n\n'
                    '### 3. Pain (Attack) Phase - 4-72 hours\n'
                    '- Throbbing severe headache\n'
                    '- Light and sound sensitivity (photophobia, phonophobia)\n'
                    '- Nausea, vomiting\n'
                    '- Worsened by physical activity\n\n'
                    '### 4. Postdrome Phase - 24-48 hours\n'
                    '- Fatigue, exhaustion\n'
                    '- Difficulty concentrating\n'
                    '- Mild headache\n'
                    '- Mood changes'
                ),
            },
            {
                'slug': 'migraine-104-kimde-gorulur',
                'category': 'migraine-basics',
                'order': 4,
                'duration': 3,
                'title_tr': 'Kimlerde Gorulur?',
                'title_en': 'Who Gets Migraines?',
                'body_tr': (
                    '## Migren Kimlerde Gorulur?\n\n'
                    '### Cinsiyet Farki\n'
                    'Kadinlarda erkeklere gore 3 kat daha fazla gorulur. Bu fark ozellikle ureme caginda belirgindir ve hormonal '
                    'degisikliklerle iliskilidir.\n\n'
                    '### Yas\n'
                    '- Genellikle ergenlikte baslar (12-17 yas)\n'
                    '- En yogun donem: 30-40 yaslar\n'
                    '- Menopoz sonrasi kadinlarda azalma egilimi\n\n'
                    '### Genetik\n'
                    'Migren guclu bir genetik bilesendir. Ailesinde migren olan kisiler %50-75 oraninda migrene yatkin olabilir.\n\n'
                    '### Risk Faktorleri\n'
                    '- Aile oykusu (en guclu faktor)\n'
                    '- Kadin cinsiyet\n'
                    '- Hormonal degisimler\n'
                    '- Stresli yasam\n'
                    '- Uyku duzensizligi\n'
                    '- Obezite'
                ),
                'body_en': (
                    '## Who Gets Migraines?\n\n'
                    '### Gender Difference\n'
                    'Women are 3 times more likely to experience migraines than men. This difference is particularly pronounced during '
                    'reproductive years and is related to hormonal changes.\n\n'
                    '### Age\n'
                    '- Usually starts in adolescence (ages 12-17)\n'
                    '- Peak period: 30-40 years old\n'
                    '- Tends to decrease in post-menopausal women\n\n'
                    '### Genetics\n'
                    'Migraine has a strong genetic component. People with a family history may be 50-75% more susceptible.\n\n'
                    '### Risk Factors\n'
                    '- Family history (strongest factor)\n'
                    '- Female gender\n'
                    '- Hormonal changes\n'
                    '- Stressful lifestyle\n'
                    '- Sleep irregularity\n'
                    '- Obesity'
                ),
            },
            {
                'slug': 'migraine-105-siklik',
                'category': 'migraine-basics',
                'order': 5,
                'duration': 3,
                'title_tr': 'Atak Sikligi ve Takibin Onemi',
                'title_en': 'Attack Frequency and Importance of Tracking',
                'body_tr': (
                    '## Atak Sikliginizi Takip Edin\n\n'
                    'Migren ataklarinizin sikligini bilmek tedavi planlamasi icin kritiktir.\n\n'
                    '### Siklik Siniflamasi\n'
                    '- **Dusuk siklik:** Ayda 1-4 atak\n'
                    '- **Orta siklik:** Ayda 5-9 atak\n'
                    '- **Yuksek siklik:** Ayda 10-14 atak\n'
                    '- **Kronik:** Ayda 15+ gun bas agrisi\n\n'
                    '### Neden Takip Onemli?\n'
                    '- Tetikleyicilerinizi belirlemek\n'
                    '- Tedavi etkinligini degerlendirmek\n'
                    '- Hekiminize dogru bilgi verebilmek\n'
                    '- Kronik migrene gecisi erken fark etmek\n\n'
                    '### Norosera ile Takip\n'
                    'Norosera uygulamasi uzerinden her ataginizi kaydederek kisisel migren profillnizi olusturabilirsiniz. '
                    'Ataginizin siddeti, suresi, tetikleyicileri ve kullandiginiz ilaclari not edin.'
                ),
                'body_en': (
                    '## Track Your Attack Frequency\n\n'
                    'Knowing your migraine attack frequency is critical for treatment planning.\n\n'
                    '### Frequency Classification\n'
                    '- **Low frequency:** 1-4 attacks per month\n'
                    '- **Medium frequency:** 5-9 attacks per month\n'
                    '- **High frequency:** 10-14 attacks per month\n'
                    '- **Chronic:** 15+ headache days per month\n\n'
                    '### Why Tracking Matters\n'
                    '- Identify your triggers\n'
                    '- Evaluate treatment effectiveness\n'
                    '- Provide accurate information to your doctor\n'
                    '- Detect early transition to chronic migraine\n\n'
                    '### Tracking with Norosera\n'
                    'Using the Norosera app, you can create your personal migraine profile by recording each attack. '
                    'Note the severity, duration, triggers, and medications used for each attack.'
                ),
            },

            # ═══ MODUL 2: Tetikleyiciler ═══
            {
                'slug': 'migraine-201-besin',
                'category': 'migraine-triggers',
                'order': 11,
                'duration': 4,
                'title_tr': 'Besin Tetikleyicileri',
                'title_en': 'Food Triggers',
                'body_tr': (
                    '## Beslenme ve Migren\n\n'
                    '### En Yaygin Besin Tetikleyicileri\n'
                    '- **Alkol:** Ozellikle kirmizi sarap (tiramin icerigi)\n'
                    '- **Kafein:** Asiri tuketim veya ani birakma\n'
                    '- **Cikolata:** Feniletilamin icerigi\n'
                    '- **Olgun peynirler:** Tiramin icerigi\n'
                    '- **Islenmis etler:** Nitrat koruyucular\n'
                    '- **MSG (monosodyum glutamat):** Hazir gidalarda\n\n'
                    '### Onemli Not\n'
                    'Her kisinin tetikleyicileri farklidir. Bir kisi icin tetikleyici olan besin baska birini etkilemeyebilir. '
                    'Besin gunlugu tutarak kendi tetikleyicilerinizi kesfedebilirsiniz.\n\n'
                    '### Ogun Duzeni\n'
                    'Ogun atlama, migren icin onemli bir tetikleyicidir. Kan sekerindeki ani dususler atagi tetikleyebilir. '
                    'Gunde 3 ana ogun duzenli saatlerde yemeye ozen gosterin.'
                ),
                'body_en': (
                    '## Nutrition and Migraine\n\n'
                    '### Most Common Food Triggers\n'
                    '- **Alcohol:** Especially red wine (tyramine content)\n'
                    '- **Caffeine:** Excessive consumption or sudden withdrawal\n'
                    '- **Chocolate:** Phenylethylamine content\n'
                    '- **Aged cheeses:** Tyramine content\n'
                    '- **Processed meats:** Nitrate preservatives\n'
                    '- **MSG (monosodium glutamate):** In processed foods\n\n'
                    '### Important Note\n'
                    'Everyone has different triggers. A food that triggers migraine in one person may not affect another. '
                    'You can discover your own triggers by keeping a food diary.\n\n'
                    '### Meal Schedule\n'
                    'Skipping meals is an important migraine trigger. Sudden drops in blood sugar can trigger an attack. '
                    'Try to eat 3 main meals at regular times each day.'
                ),
            },
            {
                'slug': 'migraine-202-cevresel',
                'category': 'migraine-triggers',
                'order': 12,
                'duration': 4,
                'title_tr': 'Cevresel Tetikleyiciler',
                'title_en': 'Environmental Triggers',
                'body_tr': (
                    '## Cevresel Faktorler\n\n'
                    '### Hava Degisiklikleri\n'
                    'Basinc degisimleri, nem orani ve sicaklik farklari migreni tetikleyebilir. Firtina oncesi donemlerde '
                    'atak riski artar.\n\n'
                    '### Isik\n'
                    '- Parlak gunes isigi\n'
                    '- Floresan aydinlatma\n'
                    '- Bilgisayar/telefon ekran isigi\n'
                    '- Titreyen isiklar\n\n'
                    '### Koku\n'
                    '- Agir parfumler\n'
                    '- Boya, tiner kokulari\n'
                    '- Sigara dumani\n\n'
                    '### Ses\n'
                    '- Yuksek sesli ortamlar\n'
                    '- Ani gurultular\n'
                    '- Uzun sureli gurultu maruziyeti\n\n'
                    '### Koruma Onerileri\n'
                    '- Gunes gozlugu takin\n'
                    '- Ekran filtresi kullanin\n'
                    '- Havalandirma iyi olan ortamlarda bulunun\n'
                    '- Hava durumunu takip edin'
                ),
                'body_en': (
                    '## Environmental Factors\n\n'
                    '### Weather Changes\n'
                    'Pressure changes, humidity, and temperature differences can trigger migraines. Attack risk increases '
                    'during pre-storm periods.\n\n'
                    '### Light\n'
                    '- Bright sunlight\n'
                    '- Fluorescent lighting\n'
                    '- Computer/phone screen light\n'
                    '- Flickering lights\n\n'
                    '### Smell\n'
                    '- Strong perfumes\n'
                    '- Paint, thinner odors\n'
                    '- Cigarette smoke\n\n'
                    '### Sound\n'
                    '- Loud environments\n'
                    '- Sudden noises\n'
                    '- Prolonged noise exposure\n\n'
                    '### Protection Tips\n'
                    '- Wear sunglasses\n'
                    '- Use screen filters\n'
                    '- Stay in well-ventilated spaces\n'
                    '- Monitor weather conditions'
                ),
            },
            {
                'slug': 'migraine-203-hormonal',
                'category': 'migraine-triggers',
                'order': 13,
                'duration': 4,
                'title_tr': 'Hormonal Tetikleyiciler',
                'title_en': 'Hormonal Triggers',
                'body_tr': (
                    '## Hormonlar ve Migren\n\n'
                    'Kadinlarda migren genellikle hormonal degisikliklerle yakindan iliskilidir.\n\n'
                    '### Adet Dongusu\n'
                    'Adet oncesi ve sirasindaki ostrojen dususu migreni tetikleyebilir. "Menstruel migren" olarak adlandirilir '
                    've adet doneminin 2 gun oncesi ile 3. gunu arasinda olusur.\n\n'
                    '### Gebelik\n'
                    '- Ilk trimesterde artabilir\n'
                    '- 2. ve 3. trimesterde cogu hastada azalir\n'
                    '- Emzirme doneminde genellikle iyilesme gorulur\n\n'
                    '### Menopoz\n'
                    '- Perimenopoz doneminde ataklar artabilir\n'
                    '- Menopoz sonrasi cogu hastada iyilesme\n\n'
                    '### Dogum Kontrol Haplari\n'
                    'Ozellikle ostrojen iceren haplarda migren artisi olabilir. Aurali migreniniz varsa hekiminizle mutlaka gorusun.'
                ),
                'body_en': (
                    '## Hormones and Migraine\n\n'
                    'In women, migraine is often closely linked to hormonal changes.\n\n'
                    '### Menstrual Cycle\n'
                    'Estrogen drops before and during menstruation can trigger migraine. Called "menstrual migraine," it occurs '
                    'between 2 days before and the 3rd day of the period.\n\n'
                    '### Pregnancy\n'
                    '- May increase in the first trimester\n'
                    '- Decreases in most patients during 2nd and 3rd trimesters\n'
                    '- Generally improves during breastfeeding\n\n'
                    '### Menopause\n'
                    '- Attacks may increase during perimenopause\n'
                    '- Most patients improve after menopause\n\n'
                    '### Birth Control Pills\n'
                    'Migraine may increase especially with estrogen-containing pills. If you have migraine with aura, definitely consult your doctor.'
                ),
            },
            {
                'slug': 'migraine-204-stres-uyku',
                'category': 'migraine-triggers',
                'order': 14,
                'duration': 4,
                'title_tr': 'Stres ve Uyku Duzensizligi',
                'title_en': 'Stress and Sleep Irregularity',
                'body_tr': (
                    '## Stres ve Uyku\n\n'
                    '### Stres - 1 Numarali Tetikleyici\n'
                    'Stres, migren hastalarinin %70\'inden fazlasinda tetikleyici olarak raporlanir. Ilginc bir sekilde, '
                    'stres sirasinda degil stresin azaldigi anda ("let-down migreni") atak gelebilir.\n\n'
                    '### Uyku Duzensizligi\n'
                    '- **Az uyumak:** Kronik uyku eksikligi atagi tetikler\n'
                    '- **Cok uyumak:** Hafta sonu fazla uyumak da risk\n'
                    '- **Duzensiz saatler:** Yatis-kalkis saatlerindeki degisimler\n'
                    '- **Kotu uyku kalitesi:** Sik uyanma, horlanma\n\n'
                    '### Stres Yonetimi Onerileri\n'
                    '- Derin nefes egzersizleri (4-7-8 teknigi)\n'
                    '- Duzenli fiziksel aktivite\n'
                    '- Meditasyon veya mindfulness\n'
                    '- Is-yasam dengesine dikkat\n\n'
                    '### Uyku Hijyeni\n'
                    '- Her gun ayni saatte yatin ve kalkin\n'
                    '- Yatak odasini karanlik ve serin tutun\n'
                    '- Yatmadan 1 saat once ekranlardan uzak durun\n'
                    '- Kafeinli icecekleri ogleden sonra kesintiye ugratin'
                ),
                'body_en': (
                    '## Stress and Sleep\n\n'
                    '### Stress - The #1 Trigger\n'
                    'Stress is reported as a trigger by more than 70% of migraine patients. Interestingly, attacks may come '
                    'not during stress but when stress subsides ("let-down migraine").\n\n'
                    '### Sleep Irregularity\n'
                    '- **Too little sleep:** Chronic sleep deprivation triggers attacks\n'
                    '- **Too much sleep:** Oversleeping on weekends is also risky\n'
                    '- **Irregular hours:** Changes in bedtime and wake time\n'
                    '- **Poor sleep quality:** Frequent waking, snoring\n\n'
                    '### Stress Management Tips\n'
                    '- Deep breathing exercises (4-7-8 technique)\n'
                    '- Regular physical activity\n'
                    '- Meditation or mindfulness\n'
                    '- Attention to work-life balance\n\n'
                    '### Sleep Hygiene\n'
                    '- Go to bed and wake up at the same time every day\n'
                    '- Keep the bedroom dark and cool\n'
                    '- Stay away from screens 1 hour before bed\n'
                    '- Cut off caffeinated drinks in the afternoon'
                ),
            },
            {
                'slug': 'migraine-205-gunluk',
                'category': 'migraine-triggers',
                'order': 15,
                'duration': 3,
                'title_tr': 'Tetikleyici Gunlugu Tutma',
                'title_en': 'Keeping a Trigger Diary',
                'body_tr': (
                    '## Kendi Tetikleyicilerinizi Kesfedin\n\n'
                    'Her migren hastasinin tetikleyicileri farklidir. Tetikleyici gunlugu tutarak kendi kalibinizi bulabilirsiniz.\n\n'
                    '### Gunlugunuze Neler Yazin?\n'
                    '- Atagtan onceki 24 saatte ne yediniz, ne ictisiniz\n'
                    '- Kac saat uyudunuz, uyku kaliteniz nasil\n'
                    '- Stres seviyeniz (1-10 arasi)\n'
                    '- Hava durumu (sicak, soguk, ruzgarli, basincli)\n'
                    '- Kadinlar icin adet dongusu gunu\n'
                    '- Fiziksel aktivite durumu\n'
                    '- Ozel kokular veya isiklar\n\n'
                    '### Norosera ile Otomatik Takip\n'
                    'Norosera uygulamasi hava durumu verilerini otomatik kaydeder ve atak kayitlarinizla eslestirerek size '
                    'kisisel tetikleyici analizi sunar. Her atak sonrasi kisa bir kayit bile cok degerlidir.'
                ),
                'body_en': (
                    '## Discover Your Own Triggers\n\n'
                    'Every migraine patient has different triggers. You can find your own pattern by keeping a trigger diary.\n\n'
                    '### What to Write in Your Diary\n'
                    '- What you ate and drank in the 24 hours before the attack\n'
                    '- How many hours you slept and your sleep quality\n'
                    '- Your stress level (1-10 scale)\n'
                    '- Weather conditions (hot, cold, windy, pressure)\n'
                    '- For women: menstrual cycle day\n'
                    '- Physical activity status\n'
                    '- Notable smells or lights\n\n'
                    '### Automatic Tracking with Norosera\n'
                    'The Norosera app automatically records weather data and matches it with your attack records to provide '
                    'personalized trigger analysis. Even a brief record after each attack is very valuable.'
                ),
            },

            # ═══ MODUL 3: Atak Yonetimi ═══
            {
                'slug': 'migraine-301-ilk-30dk',
                'category': 'migraine-attack',
                'order': 21,
                'duration': 4,
                'title_tr': 'Ilk 30 Dakika Kurali',
                'title_en': 'The First 30 Minutes Rule',
                'body_tr': (
                    '## Atak Basladiginda: Ilk 30 Dakika Kritik\n\n'
                    'Migren atagi basladiginda yaptiginiz ilk mudahale cok onemlidir. Erken mudahale atagin siddetini ve suresini azaltabilir.\n\n'
                    '### Hemen Yapmaniz Gerekenler\n'
                    '1. **Sessiz, karanlik bir ortama gecin** - Isik ve sesi minimuma indirin\n'
                    '2. **Hekiminizin onerdigi ilaci alin** - Gecikmeyin, erken almak etkiyi artirir\n'
                    '3. **Su icin** - Dehidrasyon agrivi kotulestir\n'
                    '4. **Soguk kompres uygulayin** - Alin veya enseye buz torbasi\n'
                    '5. **Uzanin ama uyumaya zorlamayin** - Rahat bir pozisyon bulun\n\n'
                    '### Neden Erken Mudahale?\n'
                    'Migren progresif bir surecdir. Agri yolagi bir kez tam olarak aktive olursa durdurmak zorlasilr. '
                    'Bu yuzden ilk belirtilerde hizli hareket etmek cok onemlidir.'
                ),
                'body_en': (
                    '## When an Attack Starts: The First 30 Minutes Are Critical\n\n'
                    'Your initial response when a migraine starts is very important. Early intervention can reduce the severity and duration.\n\n'
                    '### What to Do Immediately\n'
                    '1. **Move to a quiet, dark environment** - Minimize light and sound\n'
                    '2. **Take the medication your doctor recommended** - Don\'t delay, early intake increases effectiveness\n'
                    '3. **Drink water** - Dehydration worsens pain\n'
                    '4. **Apply cold compress** - Ice pack on forehead or back of neck\n'
                    '5. **Lie down but don\'t force sleep** - Find a comfortable position\n\n'
                    '### Why Early Intervention?\n'
                    'Migraine is a progressive process. Once the pain pathway is fully activated, it becomes harder to stop. '
                    'That\'s why acting quickly at the first signs is very important.'
                ),
            },
            {
                'slug': 'migraine-302-evde-onlemler',
                'category': 'migraine-attack',
                'order': 22,
                'duration': 4,
                'title_tr': 'Evde Yapabilecekleriniz',
                'title_en': 'What You Can Do at Home',
                'body_tr': (
                    '## Ilacsiz Atak Yonetimi\n\n'
                    '### Soguk ve Sicak Tedavi\n'
                    '- **Soguk kompres:** Alin, sakaklara veya enseye 15-20 dk uygulayin. Kan damarlarini daraltarak agrivi azaltir\n'
                    '- **Sicak uygulama:** Boyun ve omuzlardaki kas gerginligine iyi gelir\n\n'
                    '### Aroma Terapisi\n'
                    '- Nane yagi (mentol): Sakaklara az miktarda surun\n'
                    '- Lavanta: Rahatlama ve uyku icin\n\n'
                    '### Gevşeme Teknikleri\n'
                    '- Progresif kas gevsetme: Ayaktan basa dogru kas gruplrini sirayla kasip gevsetin\n'
                    '- 4-7-8 nefes teknigi: 4 sn nefes al, 7 sn tut, 8 sn yavasce ver\n\n'
                    '### Karanlık Oda\n'
                    '- Isiklari kapatip perdeleri cekin\n'
                    '- Telefonunuzu sessiz moda alin\n'
                    '- Goz bandı kullanabilirsiniz\n\n'
                    '### Kafein\n'
                    'Az miktarda kafein (bir fincan kahve) agri kesicilerin etkisini arttirabilir. Ancak duzensiz kafein kullanimi tetikleyici olabilir.'
                ),
                'body_en': (
                    '## Non-Medication Attack Management\n\n'
                    '### Cold and Heat Therapy\n'
                    '- **Cold compress:** Apply to forehead, temples, or neck for 15-20 min. Reduces pain by constricting blood vessels\n'
                    '- **Heat application:** Helps with neck and shoulder muscle tension\n\n'
                    '### Aromatherapy\n'
                    '- Peppermint oil (menthol): Apply small amount to temples\n'
                    '- Lavender: For relaxation and sleep\n\n'
                    '### Relaxation Techniques\n'
                    '- Progressive muscle relaxation: Tense and release muscle groups from feet to head\n'
                    '- 4-7-8 breathing: Inhale 4s, hold 7s, exhale slowly 8s\n\n'
                    '### Dark Room\n'
                    '- Turn off lights and close curtains\n'
                    '- Put phone on silent\n'
                    '- Consider using an eye mask\n\n'
                    '### Caffeine\n'
                    'A small amount of caffeine (one cup of coffee) can enhance pain reliever effectiveness. However, irregular caffeine use can be a trigger.'
                ),
            },
            {
                'slug': 'migraine-303-ilac-prensipleri',
                'category': 'migraine-attack',
                'order': 23,
                'duration': 5,
                'title_tr': 'Ilac Kullanim Prensipleri',
                'title_en': 'Medication Usage Principles',
                'body_tr': (
                    '## Migren Ilac Kullanimi Hakkinda Genel Bilgiler\n\n'
                    '**Not:** Spesifik ilac onerileri icin mutlaka hekiminize danisin. Burada genel prensipler verilmektedir.\n\n'
                    '### Akut Tedavi (Atak Sirasinda)\n'
                    '- Agri baslar baslamaz alin, beklemeyin\n'
                    '- Hekiminizin onerdigi dozu asin\n'
                    '- Bulanti varsa hekiminize bildirin (farkli form onerilebilir)\n\n'
                    '### Onleyici Tedavi (Profilaksi)\n'
                    '- Ayda 4+ atak varsa dusunulur\n'
                    '- Gunluk duzenli kullanim gerektirir\n'
                    '- Etkisi 4-8 haftada ortaya cikar\n'
                    '- Hekiminizle gorusmeden birakmayin\n\n'
                    '### Ilac Asiri Kullanim Bas Agrisi\n'
                    'Ayda 10-15 gunun uzerinde agri kesici kullanimi paradoksal olarak daha fazla bas agrisi yapabilir. '
                    'Buna "ilac asiri kullanim bas agrisi" denir. Hekiminize danisarak ilac tuketimini takip edin.\n\n'
                    '### Onemli Uyarilar\n'
                    '- Baskasinin ilacini kullanmayin\n'
                    '- Doz degisikligini hekimsiz yapmayin\n'
                    '- Yan etkileri kaydedin ve hekiminize bildirin'
                ),
                'body_en': (
                    '## General Information About Migraine Medication\n\n'
                    '**Note:** Always consult your doctor for specific medication recommendations. General principles are provided here.\n\n'
                    '### Acute Treatment (During Attack)\n'
                    '- Take it as soon as pain starts, don\'t wait\n'
                    '- Don\'t exceed the dose recommended by your doctor\n'
                    '- Inform your doctor if you have nausea (different forms may be suggested)\n\n'
                    '### Preventive Treatment (Prophylaxis)\n'
                    '- Considered when there are 4+ attacks per month\n'
                    '- Requires daily regular use\n'
                    '- Effect appears in 4-8 weeks\n'
                    '- Don\'t stop without consulting your doctor\n\n'
                    '### Medication Overuse Headache\n'
                    'Using pain relievers more than 10-15 days per month can paradoxically cause more headaches. '
                    'This is called "medication overuse headache." Track medication use in consultation with your doctor.\n\n'
                    '### Important Warnings\n'
                    '- Don\'t use someone else\'s medication\n'
                    '- Don\'t change doses without doctor approval\n'
                    '- Record side effects and report to your doctor'
                ),
            },
            {
                'slug': 'migraine-304-kirmizi-bayraklar',
                'category': 'migraine-attack',
                'order': 24,
                'duration': 3,
                'title_tr': 'Kirmizi Bayraklar: Ne Zaman Acile Gidin',
                'title_en': 'Red Flags: When to Go to the ER',
                'body_tr': (
                    '## Acil Durumlar\n\n'
                    'Cogu migren atagi evde yonetilebilir. Ancak bazi durumlar acil tibbi yardim gerektirir.\n\n'
                    '### Hemen Acile Gidin\n'
                    '- Hayatinizdaki en siddetli bas agrisi ("yildirim bas agrisi")\n'
                    '- Ani baslangicli, saniyeler icinde zirveye ulasan agri\n'
                    '- Ates + boyun sertligi + bas agrisi\n'
                    '- Konusma bozuklugu, gorememe, yuruyememe\n'
                    '- Kol veya bacakta guc kaybi\n'
                    '- Nobet gecirme\n'
                    '- Bilinc bulanikligi veya bilinc kaybi\n'
                    '- Kafa travmasi sonrasi bas agrisi\n\n'
                    '### Hekiminizi Arayin\n'
                    '- 72 saatten uzun suren atak\n'
                    '- Ilacin islemedigi ataklar\n'
                    '- Normalde olmayan yeni belirtiler\n'
                    '- Atak sikliginda ani artis\n\n'
                    '**Supheliyseniz, aramaktan cekinmeyin. Gec kalmaktansa erken danismak her zaman daha iyidir.**'
                ),
                'body_en': (
                    '## Emergency Situations\n\n'
                    'Most migraine attacks can be managed at home. However, some situations require emergency medical care.\n\n'
                    '### Go to the ER Immediately\n'
                    '- The worst headache of your life ("thunderclap headache")\n'
                    '- Sudden onset, reaching peak within seconds\n'
                    '- Fever + neck stiffness + headache\n'
                    '- Speech difficulty, inability to see or walk\n'
                    '- Loss of strength in arm or leg\n'
                    '- Seizure\n'
                    '- Confusion or loss of consciousness\n'
                    '- Headache after head trauma\n\n'
                    '### Call Your Doctor\n'
                    '- Attack lasting more than 72 hours\n'
                    '- Attacks where medication doesn\'t work\n'
                    '- New symptoms you\'ve never had before\n'
                    '- Sudden increase in attack frequency\n\n'
                    '**When in doubt, don\'t hesitate to call. It\'s always better to consult early than to be late.**'
                ),
            },
            {
                'slug': 'migraine-305-acil-plan',
                'category': 'migraine-attack',
                'order': 25,
                'duration': 3,
                'title_tr': 'Kisisel Atak Plani Olusturun',
                'title_en': 'Create Your Personal Attack Plan',
                'body_tr': (
                    '## Kisisel Atak Yonetim Planiniz\n\n'
                    'Onceden hazir bir plan, atak sirasinda daha hizli ve dogru hareket etmenizi saglar.\n\n'
                    '### Planinizda Olmasii Gerekenler\n'
                    '1. **Ilac bilgisi:** Hangi ilaci, ne doz, ne zaman\n'
                    '2. **Ilk adimlar:** Nereye cekileceksiniz, ne yapcaksiniz\n'
                    '3. **Iletisim listesi:** Hekiminizin telefonu, yakinlariniz\n'
                    '4. **Acil durum kriterleri:** Ne zaman acile gideceksiniz\n'
                    '5. **Is/okul plani:** Kime haber vereceksiniz\n\n'
                    '### Yakinlarinizi Bilgilendirin\n'
                    'Aileniz, is arkadaslariniz ve yakin cevreniiz migreniz hakkinda bilgilendirilmis olmalidir. '
                    'Atak geldiginde size nasil yardim edebileceklerini anlatin.\n\n'
                    '### Acil Cantaniz\n'
                    '- Ilaclariniz\n'
                    '- Soguk kompres (aninda sogutan jel)\n'
                    '- Gunes gozlugu\n'
                    '- Su sisesi\n'
                    '- Kulak tikaci'
                ),
                'body_en': (
                    '## Your Personal Attack Management Plan\n\n'
                    'Having a plan ready in advance helps you act faster and more correctly during an attack.\n\n'
                    '### What Your Plan Should Include\n'
                    '1. **Medication info:** Which medication, what dose, when\n'
                    '2. **First steps:** Where will you retreat, what will you do\n'
                    '3. **Contact list:** Your doctor\'s phone, close contacts\n'
                    '4. **Emergency criteria:** When to go to the ER\n'
                    '5. **Work/school plan:** Who to notify\n\n'
                    '### Inform Your Close Ones\n'
                    'Your family, coworkers, and close circle should be informed about your migraine. '
                    'Tell them how they can help you when an attack comes.\n\n'
                    '### Your Emergency Bag\n'
                    '- Your medications\n'
                    '- Cold compress (instant cooling gel)\n'
                    '- Sunglasses\n'
                    '- Water bottle\n'
                    '- Earplugs'
                ),
            },

            # ═══ MODUL 4: Yasam Tarzi ═══
            {
                'slug': 'migraine-401-uyku',
                'category': 'migraine-lifestyle',
                'order': 31,
                'duration': 4,
                'title_tr': 'Uyku Hijyeni',
                'title_en': 'Sleep Hygiene',
                'body_tr': (
                    '## Saglikli Uyku, Daha Az Migren\n\n'
                    'Duzenli uyku migren yonetiminin temelidir. Uyku bozukluklari hem tetikleyici hem de migreni kotulestirebilir.\n\n'
                    '### Altin Kurallar\n'
                    '- Her gun ayni saatte yatin ve kalkin (hafta sonu dahil)\n'
                    '- 7-8 saat uyku hedefleyin\n'
                    '- Yatak odasini sadece uyku icin kullanin\n'
                    '- Oda sicakligi 18-20 derece ideal\n'
                    '- Yatmadan 2 saat once agir yemek yemeyin\n'
                    '- Kafein ogleden sonra icmeyin\n'
                    '- Alkol uyku kalitesini bozar\n\n'
                    '### Ekran Isigi\n'
                    'Yatmadan en az 1 saat once telefon, tablet ve bilgisayari birakin. Mavi isik melatonin uerimini baskirar '
                    'vee uyku kalitesini dusurur.\n\n'
                    '### Uyku Gunlugu\n'
                    'Uyku saatlerinizi ve kalitesini not edin. Migren ataklariyla karsilastirarak uyku-migren iliskinizi anlayabilirsiniz.'
                ),
                'body_en': (
                    '## Healthy Sleep, Fewer Migraines\n\n'
                    'Regular sleep is the foundation of migraine management. Sleep disorders can both trigger and worsen migraines.\n\n'
                    '### Golden Rules\n'
                    '- Go to bed and wake up at the same time every day (including weekends)\n'
                    '- Aim for 7-8 hours of sleep\n'
                    '- Use the bedroom only for sleeping\n'
                    '- Room temperature of 18-20 degrees is ideal\n'
                    '- Don\'t eat heavy meals 2 hours before bed\n'
                    '- Don\'t drink caffeine in the afternoon\n'
                    '- Alcohol disrupts sleep quality\n\n'
                    '### Screen Light\n'
                    'Put away phone, tablet, and computer at least 1 hour before bed. Blue light suppresses melatonin production '
                    'and reduces sleep quality.\n\n'
                    '### Sleep Diary\n'
                    'Record your sleep hours and quality. By comparing with migraine attacks, you can understand your sleep-migraine relationship.'
                ),
            },
            {
                'slug': 'migraine-402-beslenme',
                'category': 'migraine-lifestyle',
                'order': 32,
                'duration': 4,
                'title_tr': 'Beslenme Duzeni',
                'title_en': 'Nutrition Plan',
                'body_tr': (
                    '## Migren Dostu Beslenme\n\n'
                    '### Temel Prensipler\n'
                    '- Ogun atlamamak en onemli kural\n'
                    '- Gunde 3 ana ogun + 2 ara ogun\n'
                    '- Kan sekerini dengede tutun\n'
                    '- Yeterli su icin (gunde en az 2 litre)\n\n'
                    '### Faydali Besinler\n'
                    '- **Magnezyum zengin:** Ispanak, badem, avokado, kuru baklagiller\n'
                    '- **B2 vitamini:** Yumurta, sut, brokoli\n'
                    '- **Omega-3:** Somon, uskumru, ceviz, keten tohumu\n'
                    '- **CoQ10:** Fistik, soya, ispanak\n\n'
                    '### Kacinilmasi Gerekenler\n'
                    '- Islenmis gidalar ve hazir yemekler\n'
                    '- Asiri kafein (gunde 200 mg ustu)\n'
                    '- Yapay tatlandiricilar (aspartam)\n'
                    '- Asiri tuz tuketimi\n\n'
                    '### Hidrasyon\n'
                    'Dehidrasyon migren tetikleyicisidir. Gune bir bardak su ile baslayin ve gun boyunca duzenli icin.'
                ),
                'body_en': (
                    '## Migraine-Friendly Nutrition\n\n'
                    '### Basic Principles\n'
                    '- Not skipping meals is the most important rule\n'
                    '- 3 main meals + 2 snacks per day\n'
                    '- Keep blood sugar balanced\n'
                    '- Drink enough water (at least 2 liters daily)\n\n'
                    '### Beneficial Foods\n'
                    '- **Magnesium-rich:** Spinach, almonds, avocado, legumes\n'
                    '- **Vitamin B2:** Eggs, milk, broccoli\n'
                    '- **Omega-3:** Salmon, mackerel, walnuts, flaxseed\n'
                    '- **CoQ10:** Peanuts, soy, spinach\n\n'
                    '### Foods to Avoid\n'
                    '- Processed foods and ready meals\n'
                    '- Excessive caffeine (over 200 mg/day)\n'
                    '- Artificial sweeteners (aspartame)\n'
                    '- Excessive salt consumption\n\n'
                    '### Hydration\n'
                    'Dehydration is a migraine trigger. Start the day with a glass of water and drink regularly throughout the day.'
                ),
            },
            {
                'slug': 'migraine-403-hidrasyon',
                'category': 'migraine-lifestyle',
                'order': 33,
                'duration': 3,
                'title_tr': 'Su ve Hidrasyon',
                'title_en': 'Water and Hydration',
                'body_tr': (
                    '## Suyun Onemi\n\n'
                    'Dehidrasyon, en sik gozardı edilen migren tetikleyicilerinden biridir.\n\n'
                    '### Neden Su Onemli?\n'
                    '- Beyin %75 oraninda sudan olusur\n'
                    '- Su kaybi beyin hacmini gecici olarak azaltir\n'
                    '- Dehidrasyon kan yogunlugunu artirarak beyine kan akisini etkiler\n\n'
                    '### Gunluk Su Ihtiyaci\n'
                    '- **Genel oneri:** Vucut aginizin kg basina 30-35 ml\n'
                    '- **Ornek:** 70 kg = 2.1-2.5 litre/gun\n'
                    '- Sicak havada, egzersizde ve atakta daha fazla\n\n'
                    '### Pratik Ipuclari\n'
                    '- Yanınızda her zaman su sisesi tasiyin\n'
                    '- Telefona su hatirlatma alarmi kurun\n'
                    '- Her ogunle 1-2 bardak su icin\n'
                    '- Idrar renginiz acik sari olmali\n'
                    '- Cay ve kahve su yerine gecmez (kafein diuretiktir)\n\n'
                    '### Norosera Su Takibi\n'
                    'Uygulamadaki su takip modulu ile gunluk su tuketiminizi kaydedebilir ve hedeflerinizi takip edebilirsiniz.'
                ),
                'body_en': (
                    '## The Importance of Water\n\n'
                    'Dehydration is one of the most frequently overlooked migraine triggers.\n\n'
                    '### Why Water Matters\n'
                    '- The brain is about 75% water\n'
                    '- Water loss temporarily reduces brain volume\n'
                    '- Dehydration increases blood viscosity, affecting blood flow to the brain\n\n'
                    '### Daily Water Needs\n'
                    '- **General recommendation:** 30-35 ml per kg of body weight\n'
                    '- **Example:** 70 kg = 2.1-2.5 liters/day\n'
                    '- More in hot weather, during exercise, and during attacks\n\n'
                    '### Practical Tips\n'
                    '- Always carry a water bottle with you\n'
                    '- Set water reminder alarms on your phone\n'
                    '- Drink 1-2 glasses of water with each meal\n'
                    '- Your urine should be light yellow\n'
                    '- Tea and coffee don\'t count as water (caffeine is diuretic)\n\n'
                    '### Norosera Water Tracking\n'
                    'With the water tracking module in the app, you can record your daily water intake and track your goals.'
                ),
            },
            {
                'slug': 'migraine-404-egzersiz',
                'category': 'migraine-lifestyle',
                'order': 34,
                'duration': 4,
                'title_tr': 'Egzersiz ve Fiziksel Aktivite',
                'title_en': 'Exercise and Physical Activity',
                'body_tr': (
                    '## Hareket Edin, Migreni Azaltin\n\n'
                    'Duzenli egzersiz migren ataklarinin sikligini ve siddetini azalttigi bilimsel olarak kanitlanmistir.\n\n'
                    '### Onerilen Egzersizler\n'
                    '- **Yuruyus:** Haftada 5 gun, 30 dakika tempolu yuruyus\n'
                    '- **Yuzme:** Eklem dostu, beden ve zihin icin faydali\n'
                    '- **Yoga:** Stres azaltma + esneklik + nefes kontrolu\n'
                    '- **Bisiklet:** Orta tempoda\n'
                    '- **Pilates:** Postureyi duzeltir, boyun gerginligini azaltir\n\n'
                    '### Dikkat Edilmesi Gerekenler\n'
                    '- Yavaş baslayıp kademeli artirin\n'
                    '- Yeterli su icin (egzersiz oncesi, sirasi, sonrasi)\n'
                    '- Asiri yogun egzersiz tetikleyici olabilir\n'
                    '- Atak sirasinda egzersiz yapmayin\n'
                    '- Isınma ve soguma yapın\n\n'
                    '### Haftalik Hedef\n'
                    '- Haftada 150 dakika orta siddetli aerobik aktivite\n'
                    '- Veya haftada 75 dakika yogun aktivite\n'
                    '- Haftada 2 gun kas guclendirme'
                ),
                'body_en': (
                    '## Move More, Reduce Migraines\n\n'
                    'Regular exercise has been scientifically proven to reduce the frequency and severity of migraine attacks.\n\n'
                    '### Recommended Exercises\n'
                    '- **Walking:** Brisk walking 30 minutes, 5 days a week\n'
                    '- **Swimming:** Joint-friendly, beneficial for body and mind\n'
                    '- **Yoga:** Stress reduction + flexibility + breath control\n'
                    '- **Cycling:** At moderate pace\n'
                    '- **Pilates:** Corrects posture, reduces neck tension\n\n'
                    '### Points to Consider\n'
                    '- Start slowly and gradually increase\n'
                    '- Drink enough water (before, during, after exercise)\n'
                    '- Excessively intense exercise can be a trigger\n'
                    '- Don\'t exercise during an attack\n'
                    '- Do warm-up and cool-down\n\n'
                    '### Weekly Target\n'
                    '- 150 minutes of moderate aerobic activity per week\n'
                    '- Or 75 minutes of vigorous activity per week\n'
                    '- Strength training 2 days per week'
                ),
            },
            {
                'slug': 'migraine-405-stres-yonetimi',
                'category': 'migraine-lifestyle',
                'order': 35,
                'duration': 4,
                'title_tr': 'Stres Yonetimi Teknikleri',
                'title_en': 'Stress Management Techniques',
                'body_tr': (
                    '## Stresi Yonetin, Migreni Kontrol Edin\n\n'
                    '### 1. Derin Nefes (4-7-8 Teknigi)\n'
                    '- 4 saniye burundan nefes alin\n'
                    '- 7 saniye tutun\n'
                    '- 8 saniye agizdan yavesca verin\n'
                    '- Gunde 2 kez, 4 tekrar yapin\n\n'
                    '### 2. Progresif Kas Gevsetme\n'
                    '- Ayak parmaklarindan baslayarak yüzünüze dogru ilerleyin\n'
                    '- Her kas grubunu 5 sn kasin, 10 sn gevsetin\n'
                    '- 15-20 dk suerer\n\n'
                    '### 3. Mindfulness (Farkindalik)\n'
                    '- Gunde 10 dakika sessiz oturun\n'
                    '- Nefesinize odaklanin\n'
                    '- Dusuncelerinizi yargilamadan gozlemleyin\n\n'
                    '### 4. Gunluk Rutinler\n'
                    '- Sabah 10 dakika kendinize zaman ayirin\n'
                    '- Dogada vakit gecirin\n'
                    '- Sosyal baglantılarinizi koruyun\n'
                    '- Hayir demeyi ogrenin\n\n'
                    '### 5. Profesyonel Destek\n'
                    'Stres yonetilemez hale geldiginde bir psikolog veya psikiyatrdan destek almaktan cekinmeyin. '
                    'Bilissel davranisci terapi (BDT) migren yonetiminde etkili oldugu kanitlanmistir.'
                ),
                'body_en': (
                    '## Manage Stress, Control Migraine\n\n'
                    '### 1. Deep Breathing (4-7-8 Technique)\n'
                    '- Inhale through nose for 4 seconds\n'
                    '- Hold for 7 seconds\n'
                    '- Exhale slowly through mouth for 8 seconds\n'
                    '- Do 4 repetitions, twice daily\n\n'
                    '### 2. Progressive Muscle Relaxation\n'
                    '- Start from your toes and progress up to your face\n'
                    '- Tense each muscle group for 5s, relax for 10s\n'
                    '- Takes 15-20 minutes\n\n'
                    '### 3. Mindfulness\n'
                    '- Sit quietly for 10 minutes daily\n'
                    '- Focus on your breath\n'
                    '- Observe your thoughts without judgment\n\n'
                    '### 4. Daily Routines\n'
                    '- Set aside 10 minutes for yourself each morning\n'
                    '- Spend time in nature\n'
                    '- Maintain social connections\n'
                    '- Learn to say no\n\n'
                    '### 5. Professional Support\n'
                    'Don\'t hesitate to seek support from a psychologist or psychiatrist when stress becomes unmanageable. '
                    'Cognitive behavioral therapy (CBT) has been proven effective in migraine management.'
                ),
            },

            # ═══ MODUL 5: Ileri Konular ═══
            {
                'slug': 'migraine-501-kronik',
                'category': 'migraine-advanced',
                'order': 41,
                'duration': 4,
                'title_tr': 'Kronik Migren',
                'title_en': 'Chronic Migraine',
                'body_tr': (
                    '## Kronik Migren: Ne Zaman Endiselenin?\n\n'
                    '### Tanim\n'
                    'Ayda 15 veya daha fazla gun bas agrisi ve bunlarin en az 8 gununde migren ozelliklerinin bulunmasi.\n\n'
                    '### Episodikten Kronige Gecis\n'
                    'Migren bazen zamanla kroniklesebilir. Risk faktorleri:\n'
                    '- Asiri ilac kullanimi\n'
                    '- Obezite\n'
                    '- Uyku bozuklugu\n'
                    '- Depresyon ve anksiyete\n'
                    '- Kafein asiri tuketimi\n'
                    '- Tedavisiz birakilan episodik migren\n\n'
                    '### Tedavi Yaklasimi\n'
                    '- Onleyici tedavi mutlaka gereklidir\n'
                    '- Yasam tarzi degisiklikleri onemlidir\n'
                    '- Ilac asiri kullanimi varsa duzeltilmelidir\n'
                    '- Yeni tedaviler (CGRP inhibitorleri) kronik migre icin umut verici\n\n'
                    '### Umut Var\n'
                    'Kronik migren tedavi edilebilir bir durumdur. Dogru tedavi ve yasam tarzi degisiklikleri ile '
                    'cogu hasta episodik migrene donebilir.'
                ),
                'body_en': (
                    '## Chronic Migraine: When to Be Concerned\n\n'
                    '### Definition\n'
                    'Headache 15 or more days per month, with migraine features on at least 8 of those days.\n\n'
                    '### Transition from Episodic to Chronic\n'
                    'Migraine can sometimes become chronic over time. Risk factors:\n'
                    '- Medication overuse\n'
                    '- Obesity\n'
                    '- Sleep disorders\n'
                    '- Depression and anxiety\n'
                    '- Excessive caffeine consumption\n'
                    '- Untreated episodic migraine\n\n'
                    '### Treatment Approach\n'
                    '- Preventive treatment is essential\n'
                    '- Lifestyle changes are important\n'
                    '- Medication overuse must be corrected\n'
                    '- New treatments (CGRP inhibitors) are promising for chronic migraine\n\n'
                    '### There is Hope\n'
                    'Chronic migraine is a treatable condition. With proper treatment and lifestyle changes, '
                    'most patients can return to episodic migraine.'
                ),
            },
            {
                'slug': 'migraine-502-cocuklarda',
                'category': 'migraine-advanced',
                'order': 42,
                'duration': 4,
                'title_tr': 'Cocuklarda Migren',
                'title_en': 'Migraine in Children',
                'body_tr': (
                    '## Cocuklarda Migren\n\n'
                    '### Farkli Belirtiler\n'
                    'Cocuklarda migren eriskinlerden farkli seyredebilir:\n'
                    '- Agri her iki tarafta olabilir (tek tarafli olmak zorunda degil)\n'
                    '- Suresi daha kisa olabilir (2-72 saat)\n'
                    '- Karin agrisi on planda olabilir (abdominal migren)\n'
                    '- Bulanti ve kusma daha belirgin\n'
                    '- Solukluk ve halsizlik gorelebilir\n\n'
                    '### Okulda Migren\n'
                    '- Ogretmenleri bilgilendirin\n'
                    '- Sessiz bir dinlenme alani talep edin\n'
                    '- Duzensiz ogle yemegi saatlerine dikkat\n'
                    '- Ekran suresi siniri onemli\n\n'
                    '### Ne Yapabilirsiniz?\n'
                    '- Duzenli uyku ve beslenme\n'
                    '- Ekran suresi sinirlamasi\n'
                    '- Fiziksel aktivite tesvik\n'
                    '- Tetikleyici gunlugu tutturun\n'
                    '- Cocuk nrologu ile takip'
                ),
                'body_en': (
                    '## Migraine in Children\n\n'
                    '### Different Symptoms\n'
                    'Migraine in children may present differently from adults:\n'
                    '- Pain can be on both sides (doesn\'t have to be unilateral)\n'
                    '- Duration can be shorter (2-72 hours)\n'
                    '- Abdominal pain may be prominent (abdominal migraine)\n'
                    '- Nausea and vomiting are more pronounced\n'
                    '- Pallor and fatigue may be seen\n\n'
                    '### Migraine at School\n'
                    '- Inform teachers\n'
                    '- Request a quiet rest area\n'
                    '- Watch for irregular lunch times\n'
                    '- Screen time limits are important\n\n'
                    '### What You Can Do\n'
                    '- Regular sleep and nutrition\n'
                    '- Screen time limitation\n'
                    '- Encourage physical activity\n'
                    '- Have them keep a trigger diary\n'
                    '- Follow-up with a pediatric neurologist'
                ),
            },
            {
                'slug': 'migraine-503-hamilelik',
                'category': 'migraine-advanced',
                'order': 43,
                'duration': 4,
                'title_tr': 'Hamilelik ve Migren',
                'title_en': 'Pregnancy and Migraine',
                'body_tr': (
                    '## Hamileyken Migren Yonetimi\n\n'
                    '### Iyi Haber\n'
                    'Hamile kadinlarin %60-70\'inde migren 2. ve 3. trimesterde belirgin olarak azalir veya tamamen durur.\n\n'
                    '### Ilac Kullanimi\n'
                    '- Bircok migren ilaci hamilelihkte kontraendikedir\n'
                    '- Hamileligi planliyorsanız hekiminizle onceden gorusun\n'
                    '- Kullandiginiz ilaclari hekimsiz birakmayin veya degistirmeyin\n'
                    '- Gebelikte guvenli kabul edilen seceenekler vardir\n\n'
                    '### Ilacsiz Yontemler On Planda\n'
                    '- Soguk kompres\n'
                    '- Dinlenme ve uyku\n'
                    '- Gevsetme teknikleri\n'
                    '- Akupunktur (deneyimli uzmanla)\n'
                    '- Magnezyum destegi (hekim onerisiyle)\n\n'
                    '### Ne Zaman Endiselenin?\n'
                    '- Hamilelikteki yeni bas agrisi her zaman arastirilmalidir\n'
                    '- Preeklampsi belirtilerine dikkat (tansiyon yuksekligi + bas agrisi)\n'
                    '- Gorusme bozuklugu + bas agrisi acil muayene gerektirir'
                ),
                'body_en': (
                    '## Managing Migraine During Pregnancy\n\n'
                    '### Good News\n'
                    'In 60-70% of pregnant women, migraine significantly decreases or completely stops in the 2nd and 3rd trimesters.\n\n'
                    '### Medication Use\n'
                    '- Many migraine medications are contraindicated during pregnancy\n'
                    '- Consult your doctor in advance if planning pregnancy\n'
                    '- Don\'t stop or change medications without medical advice\n'
                    '- There are options considered safe during pregnancy\n\n'
                    '### Non-Medication Methods Take Priority\n'
                    '- Cold compress\n'
                    '- Rest and sleep\n'
                    '- Relaxation techniques\n'
                    '- Acupuncture (with experienced practitioner)\n'
                    '- Magnesium supplement (with doctor\'s recommendation)\n\n'
                    '### When to Be Concerned\n'
                    '- New headache during pregnancy should always be investigated\n'
                    '- Watch for preeclampsia signs (high blood pressure + headache)\n'
                    '- Visual disturbance + headache requires emergency evaluation'
                ),
            },
            {
                'slug': 'migraine-504-yeni-tedaviler',
                'category': 'migraine-advanced',
                'order': 44,
                'duration': 4,
                'title_tr': 'Yeni Tedavi Yaklasımlari',
                'title_en': 'New Treatment Approaches',
                'body_tr': (
                    '## Migren Tedavisinde Yenilikler\n\n'
                    '### CGRP Inhibitorleri\n'
                    'Son yillarin en onemli gelismesi. CGRP (kalsitonin geni iliskili peptid) migren atagi sirasinda '
                    'artan bir maddedir. Bu ilaclar CGRP\'yi veya reseptorunu bloke eder:\n'
                    '- Aylik veya 3 aylik enjeksiyon olarak\n'
                    '- Agiz yoluyla (gepantlar)\n'
                    '- Ozellikle kronik migren icin etkili\n\n'
                    '### Noromodulasyon Cihazlari\n'
                    '- **Transkutanoz supraorbital stimulasyon** (Cefaly): Alin bandiyla sinir uyarimi\n'
                    '- **Vagus sinir stimulasyonu** (gammaCore): Boyundaki vagus sinirin uyarimi\n'
                    '- Ilacsiz alternatif olarak tercih edilebilir\n\n'
                    '### Dijital Terapiler\n'
                    '- Mobil uygulama tabanli BDT programlari\n'
                    '- Biyofeedback cihazlari\n'
                    '- Yapay zeka destekli atak tahmini\n\n'
                    '### Onemli\n'
                    'Tedavi karari her zaman hekiminizle birlikte verilmelidir. '
                    'Doğru tedavyi bulmak zaman alabilir, sabırli olun.'
                ),
                'body_en': (
                    '## Innovations in Migraine Treatment\n\n'
                    '### CGRP Inhibitors\n'
                    'The most important development in recent years. CGRP (calcitonin gene-related peptide) is a substance '
                    'that increases during migraine attacks. These drugs block CGRP or its receptor:\n'
                    '- As monthly or quarterly injections\n'
                    '- Orally (gepants)\n'
                    '- Particularly effective for chronic migraine\n\n'
                    '### Neuromodulation Devices\n'
                    '- **Transcutaneous supraorbital stimulation** (Cefaly): Nerve stimulation via forehead band\n'
                    '- **Vagus nerve stimulation** (gammaCore): Stimulation of the vagus nerve in the neck\n'
                    '- Can be preferred as a drug-free alternative\n\n'
                    '### Digital Therapies\n'
                    '- Mobile app-based CBT programs\n'
                    '- Biofeedback devices\n'
                    '- AI-assisted attack prediction\n\n'
                    '### Important\n'
                    'Treatment decisions should always be made together with your doctor. '
                    'Finding the right treatment may take time, be patient.'
                ),
            },
            {
                'slug': 'migraine-505-norosera-kullanimi',
                'category': 'migraine-advanced',
                'order': 45,
                'duration': 3,
                'title_tr': 'Norosera ile Migren Yonetimi',
                'title_en': 'Managing Migraine with Norosera',
                'body_tr': (
                    '## Norosera\'yi Etkin Kullanin\n\n'
                    '### Atak Kaydi\n'
                    '- Her atagi siddet, sure ve belirtilerle kaydedin\n'
                    '- Tetikleyicileri secin\n'
                    '- Kullandiginiz ilaci not edin\n'
                    '- Ilacin etkisini degerlendirin\n\n'
                    '### Tetikleyici Analizi\n'
                    '- Hava durumu verileri otomatik kaydedilir\n'
                    '- Besin gunlugu tutarak beslenme tetikleyicilerini belirleyin\n'
                    '- Uyku ve stres verilerinizi girin\n'
                    '- Uygulama size kisisel tetikleyici raporunuzu olusturur\n\n'
                    '### Hekim Raporlari\n'
                    '- Atak istatistiklerinizi PDF olarak paylasabilirsiniz\n'
                    '- Hekiminiz panelinden takibinizi gorebilir\n'
                    '- Daha verimli hekim gorusmeleri yapabilirsiniz\n\n'
                    '### Ilac Hatirlatmalari\n'
                    '- Onleyici ilaclariniz icin gunluk hatirlatmalar\n'
                    '- Ilac kullnim takibi\n\n'
                    '### Egitim Icerikleri\n'
                    'Bu egitim setini tamamladiktan sonra diger modulleri de kesfedebilirsiniz. '
                    'Duzenli bilgi edinmek hastaligizinizi yonetmenize yardimci olur.'
                ),
                'body_en': (
                    '## Use Norosera Effectively\n\n'
                    '### Attack Recording\n'
                    '- Record each attack with severity, duration, and symptoms\n'
                    '- Select triggers\n'
                    '- Note the medication used\n'
                    '- Evaluate medication effectiveness\n\n'
                    '### Trigger Analysis\n'
                    '- Weather data is automatically recorded\n'
                    '- Identify food triggers by keeping a food diary\n'
                    '- Enter your sleep and stress data\n'
                    '- The app creates your personal trigger report\n\n'
                    '### Doctor Reports\n'
                    '- Share your attack statistics as PDF\n'
                    '- Your doctor can see your follow-up from their panel\n'
                    '- Have more productive doctor visits\n\n'
                    '### Medication Reminders\n'
                    '- Daily reminders for preventive medications\n'
                    '- Medication usage tracking\n\n'
                    '### Educational Content\n'
                    'After completing this education set, you can explore other modules as well. '
                    'Regular learning helps you manage your condition.'
                ),
            },
        ]

    def _get_quizzes(self):
        """5 quiz ve sorulari."""
        return [
            {
                'slug': 'quiz-migraine-basics',
                'category': 'migraine-basics',
                'order': 1,
                'title_tr': 'Migreni Taniyalim - Quiz',
                'title_en': 'Understanding Migraine - Quiz',
                'description_tr': 'Migren temelleri hakkindaki bilgilerinizi test edin.',
                'description_en': 'Test your knowledge about migraine basics.',
                'questions': [
                    {
                        'question_tr': 'Migren ataginin agri fazi tipik olarak ne kadar surer?',
                        'question_en': 'How long does the pain phase of a migraine attack typically last?',
                        'options': [
                            {'text_tr': '30 dakika - 1 saat', 'text_en': '30 minutes - 1 hour', 'is_correct': False},
                            {'text_tr': '4-72 saat', 'text_en': '4-72 hours', 'is_correct': True},
                            {'text_tr': '1-2 saat', 'text_en': '1-2 hours', 'is_correct': False},
                            {'text_tr': '1 hafta', 'text_en': '1 week', 'is_correct': False},
                        ],
                        'explanation_tr': 'Migren agri fazi tipik olarak 4-72 saat surer. 72 saatten uzun surendse acil basvuru gerekebilir.',
                        'explanation_en': 'The pain phase typically lasts 4-72 hours. If lasting longer than 72 hours, emergency care may be needed.',
                    },
                    {
                        'question_tr': 'Aurali migrende en sik gorulen aura turu hangisidir?',
                        'question_en': 'What is the most common type of aura in migraine with aura?',
                        'options': [
                            {'text_tr': 'Gorsel aura (parlak noktalar, zigzag)', 'text_en': 'Visual aura (bright spots, zigzag)', 'is_correct': True},
                            {'text_tr': 'Isitsel aura', 'text_en': 'Auditory aura', 'is_correct': False},
                            {'text_tr': 'Koku aurasi', 'text_en': 'Olfactory aura', 'is_correct': False},
                            {'text_tr': 'Tat aurasi', 'text_en': 'Taste aura', 'is_correct': False},
                        ],
                        'explanation_tr': 'Gorsel aura en sik gorulen tur olup parlak noktalar, zigzag cizgiler veya gorme alani kaybi olarak ortaya cikar.',
                        'explanation_en': 'Visual aura is the most common type, presenting as bright spots, zigzag lines, or visual field loss.',
                    },
                    {
                        'question_tr': 'Migren hangi cinsiyette daha sik gorulur?',
                        'question_en': 'Which gender is more commonly affected by migraine?',
                        'options': [
                            {'text_tr': 'Erkeklerde', 'text_en': 'Males', 'is_correct': False},
                            {'text_tr': 'Kadinlarda (3 kat fazla)', 'text_en': 'Females (3 times more)', 'is_correct': True},
                            {'text_tr': 'Esit oranda', 'text_en': 'Equal rates', 'is_correct': False},
                            {'text_tr': 'Cocuklarda', 'text_en': 'Children', 'is_correct': False},
                        ],
                        'explanation_tr': 'Kadinlarda erkeklere gore 3 kat daha sik gorulur. Bu fark hormonal degisikliklerle iliskilidir.',
                        'explanation_en': 'Women are 3 times more likely than men. This difference is related to hormonal changes.',
                    },
                    {
                        'question_tr': 'Kronik migren tanisi icin ayda kac gun bas agrisi olmalidir?',
                        'question_en': 'How many headache days per month define chronic migraine?',
                        'options': [
                            {'text_tr': '5 veya daha fazla', 'text_en': '5 or more', 'is_correct': False},
                            {'text_tr': '10 veya daha fazla', 'text_en': '10 or more', 'is_correct': False},
                            {'text_tr': '15 veya daha fazla', 'text_en': '15 or more', 'is_correct': True},
                            {'text_tr': '20 veya daha fazla', 'text_en': '20 or more', 'is_correct': False},
                        ],
                        'explanation_tr': 'Ayda 15 veya daha fazla gun bas agrisi (en az 8 gunu migren ozellikli) kronik migren olarak tanilanir.',
                        'explanation_en': 'Headache 15 or more days per month (at least 8 with migraine features) is defined as chronic migraine.',
                    },
                ],
            },
            {
                'slug': 'quiz-migraine-triggers',
                'category': 'migraine-triggers',
                'order': 2,
                'title_tr': 'Tetikleyiciler - Quiz',
                'title_en': 'Triggers - Quiz',
                'description_tr': 'Migren tetikleyicileri hakkindaki bilgilerinizi test edin.',
                'description_en': 'Test your knowledge about migraine triggers.',
                'questions': [
                    {
                        'question_tr': 'Migren hastalarinda en sik raporlanan tetikleyici nedir?',
                        'question_en': 'What is the most commonly reported trigger in migraine patients?',
                        'options': [
                            {'text_tr': 'Cikolata', 'text_en': 'Chocolate', 'is_correct': False},
                            {'text_tr': 'Stres', 'text_en': 'Stress', 'is_correct': True},
                            {'text_tr': 'Hava degisikligi', 'text_en': 'Weather change', 'is_correct': False},
                            {'text_tr': 'Alkol', 'text_en': 'Alcohol', 'is_correct': False},
                        ],
                        'explanation_tr': 'Stres, migren hastalarinin %70\'inden fazlasinda tetikleyici olarak raporlanir ve 1 numarali tetikleyicidir.',
                        'explanation_en': 'Stress is reported by more than 70% of migraine patients and is the #1 trigger.',
                    },
                    {
                        'question_tr': '"Let-down migreni" ne anlama gelir?',
                        'question_en': 'What does "let-down migraine" mean?',
                        'options': [
                            {'text_tr': 'Stres sirasinda gelen migren', 'text_en': 'Migraine during stress', 'is_correct': False},
                            {'text_tr': 'Stres azaldiktan sonra gelen migren', 'text_en': 'Migraine after stress subsides', 'is_correct': True},
                            {'text_tr': 'Uyku sonrasi migren', 'text_en': 'Migraine after sleep', 'is_correct': False},
                            {'text_tr': 'Yemek sonrasi migren', 'text_en': 'Migraine after eating', 'is_correct': False},
                        ],
                        'explanation_tr': 'Let-down migreni, stres doneminden sonra rahatlamayla birlikte gelen atak demektir. Hafta sonu migrenleri buna ornektir.',
                        'explanation_en': 'Let-down migraine refers to attacks that come with relaxation after a stressful period. Weekend migraines are an example.',
                    },
                    {
                        'question_tr': 'Kirmizi sarabin migren tetikleyicisi olmasi hangi maddeyle iliskilidir?',
                        'question_en': 'Which substance makes red wine a migraine trigger?',
                        'options': [
                            {'text_tr': 'Kafein', 'text_en': 'Caffeine', 'is_correct': False},
                            {'text_tr': 'Tiramin', 'text_en': 'Tyramine', 'is_correct': True},
                            {'text_tr': 'Gluten', 'text_en': 'Gluten', 'is_correct': False},
                            {'text_tr': 'Laktoz', 'text_en': 'Lactose', 'is_correct': False},
                        ],
                        'explanation_tr': 'Kirmizi sarap ve olgun peynirler tiramin icerir. Tiramin beyin kimyasini etkileyerek migreni tetikleyebilir.',
                        'explanation_en': 'Red wine and aged cheeses contain tyramine. Tyramine can trigger migraine by affecting brain chemistry.',
                    },
                ],
            },
            {
                'slug': 'quiz-migraine-attack',
                'category': 'migraine-attack',
                'order': 3,
                'title_tr': 'Atak Yonetimi - Quiz',
                'title_en': 'Attack Management - Quiz',
                'description_tr': 'Migren atagi yonetimi bilgilerinizi test edin.',
                'description_en': 'Test your knowledge about migraine attack management.',
                'questions': [
                    {
                        'question_tr': 'Migren atagi basladiginda ilk yapilmasi gereken nedir?',
                        'question_en': 'What is the first thing to do when a migraine attack starts?',
                        'options': [
                            {'text_tr': 'Egzersiz yapmak', 'text_en': 'Exercise', 'is_correct': False},
                            {'text_tr': 'Ilaci hemen almak ve karanlik ortama gecmek', 'text_en': 'Take medication immediately and move to dark environment', 'is_correct': True},
                            {'text_tr': 'Kahve icmek', 'text_en': 'Drink coffee', 'is_correct': False},
                            {'text_tr': 'Beklemek', 'text_en': 'Wait', 'is_correct': False},
                        ],
                        'explanation_tr': 'Erken mudahale kritiktir. Ilk 30 dakika icinde ilac almak ve sessiz karanlik ortama gecmek atagin siddetini azaltir.',
                        'explanation_en': 'Early intervention is critical. Taking medication within the first 30 minutes and moving to a quiet dark environment reduces attack severity.',
                    },
                    {
                        'question_tr': 'Asagidakilerden hangisi acil servise gitmeyi gerektirir?',
                        'question_en': 'Which of the following requires going to the emergency room?',
                        'options': [
                            {'text_tr': 'Her zamankine benzer migren atagi', 'text_en': 'Migraine attack similar to usual', 'is_correct': False},
                            {'text_tr': 'Hafif bulanti', 'text_en': 'Mild nausea', 'is_correct': False},
                            {'text_tr': 'Ani baslayan hayatinizin en siddetli agrisi', 'text_en': 'Sudden worst headache of your life', 'is_correct': True},
                            {'text_tr': 'Isik hassasiyeti', 'text_en': 'Light sensitivity', 'is_correct': False},
                        ],
                        'explanation_tr': 'Ani, saniyeler icinde zirveye ulasan "yildirim bas agrisi" acil tibbi degerlendirme gerektirir.',
                        'explanation_en': '"Thunderclap headache" reaching peak within seconds requires emergency medical evaluation.',
                    },
                    {
                        'question_tr': 'Ilac asiri kullanim bas agrisi ne demektir?',
                        'question_en': 'What is medication overuse headache?',
                        'options': [
                            {'text_tr': 'Ilacin yan etkisi olan bas agrisi', 'text_en': 'Headache as a side effect', 'is_correct': False},
                            {'text_tr': 'Ayda 10-15+ gun agri kesici kullanmaktan kaynaklanan bas agrisi', 'text_en': 'Headache from using painkillers 10-15+ days/month', 'is_correct': True},
                            {'text_tr': 'Ilac alerjisi', 'text_en': 'Drug allergy', 'is_correct': False},
                            {'text_tr': 'Ilac etkilesimi', 'text_en': 'Drug interaction', 'is_correct': False},
                        ],
                        'explanation_tr': 'Ayda 10-15 gunun uzerinde agri kesici kullanimi paradoksal olarak daha fazla bas agrisina neden olabilir.',
                        'explanation_en': 'Using painkillers more than 10-15 days per month can paradoxically cause more headaches.',
                    },
                    {
                        'question_tr': 'Soguk kompres nereye uygulanmalidir?',
                        'question_en': 'Where should cold compress be applied?',
                        'options': [
                            {'text_tr': 'Karni', 'text_en': 'Abdomen', 'is_correct': False},
                            {'text_tr': 'Alin, sakaklar veya ense', 'text_en': 'Forehead, temples or back of neck', 'is_correct': True},
                            {'text_tr': 'Bilek', 'text_en': 'Wrist', 'is_correct': False},
                            {'text_tr': 'Ayak tabani', 'text_en': 'Sole of foot', 'is_correct': False},
                        ],
                        'explanation_tr': 'Soguk kompres alin, sakaklara veya enseye 15-20 dakika uygulanir ve kan damarlarini daraltarak agrivi azaltir.',
                        'explanation_en': 'Cold compress applied to forehead, temples, or neck for 15-20 minutes reduces pain by constricting blood vessels.',
                    },
                ],
            },
            {
                'slug': 'quiz-migraine-lifestyle',
                'category': 'migraine-lifestyle',
                'order': 4,
                'title_tr': 'Yasam Tarzi - Quiz',
                'title_en': 'Lifestyle - Quiz',
                'description_tr': 'Migren icin yasam tarzi onerilerini test edin.',
                'description_en': 'Test lifestyle recommendations for migraine.',
                'questions': [
                    {
                        'question_tr': 'Migren hastasi icin ideal uyku suresi ne kadardir?',
                        'question_en': 'What is the ideal sleep duration for a migraine patient?',
                        'options': [
                            {'text_tr': '5-6 saat', 'text_en': '5-6 hours', 'is_correct': False},
                            {'text_tr': '7-8 saat', 'text_en': '7-8 hours', 'is_correct': True},
                            {'text_tr': '9-10 saat', 'text_en': '9-10 hours', 'is_correct': False},
                            {'text_tr': 'Farketmez', 'text_en': 'Doesn\'t matter', 'is_correct': False},
                        ],
                        'explanation_tr': '7-8 saat duzenli uyku ideal olup hem az uyumak hem cok uyumak migreni tetikleyebilir.',
                        'explanation_en': '7-8 hours of regular sleep is ideal; both too little and too much sleep can trigger migraine.',
                    },
                    {
                        'question_tr': 'Haftada kac dakika orta siddetli egzersiz onerilir?',
                        'question_en': 'How many minutes of moderate exercise per week is recommended?',
                        'options': [
                            {'text_tr': '60 dakika', 'text_en': '60 minutes', 'is_correct': False},
                            {'text_tr': '150 dakika', 'text_en': '150 minutes', 'is_correct': True},
                            {'text_tr': '300 dakika', 'text_en': '300 minutes', 'is_correct': False},
                            {'text_tr': 'Egzersiz onerilmez', 'text_en': 'Exercise not recommended', 'is_correct': False},
                        ],
                        'explanation_tr': 'Haftada 150 dakika orta siddetli aerobik aktivite migren ataklarinin sikligini ve siddetini azaltir.',
                        'explanation_en': '150 minutes of moderate aerobic activity per week reduces the frequency and severity of migraine attacks.',
                    },
                    {
                        'question_tr': 'Gunluk su tuketimi icin genel oneri nedir?',
                        'question_en': 'What is the general recommendation for daily water intake?',
                        'options': [
                            {'text_tr': 'Kg basina 10-15 ml', 'text_en': '10-15 ml per kg', 'is_correct': False},
                            {'text_tr': 'Kg basina 30-35 ml', 'text_en': '30-35 ml per kg', 'is_correct': True},
                            {'text_tr': 'Kg basina 50-60 ml', 'text_en': '50-60 ml per kg', 'is_correct': False},
                            {'text_tr': 'Sadece susadiginda', 'text_en': 'Only when thirsty', 'is_correct': False},
                        ],
                        'explanation_tr': 'Vucut aginizin kg basina 30-35 ml su icmeniz onerilir (ornegin 70 kg icin 2.1-2.5 litre).',
                        'explanation_en': '30-35 ml per kg of body weight is recommended (e.g., 2.1-2.5 liters for 70 kg).',
                    },
                ],
            },
            {
                'slug': 'quiz-migraine-advanced',
                'category': 'migraine-advanced',
                'order': 5,
                'title_tr': 'Ileri Konular - Quiz',
                'title_en': 'Advanced Topics - Quiz',
                'description_tr': 'Ileri migren konulari hakkindaki bilgilerinizi test edin.',
                'description_en': 'Test your knowledge about advanced migraine topics.',
                'questions': [
                    {
                        'question_tr': 'Hamile kadinlarin yuzde kacinda migren 2. trimesterde azalir?',
                        'question_en': 'In what percentage of pregnant women does migraine decrease in the 2nd trimester?',
                        'options': [
                            {'text_tr': '%20-30', 'text_en': '20-30%', 'is_correct': False},
                            {'text_tr': '%40-50', 'text_en': '40-50%', 'is_correct': False},
                            {'text_tr': '%60-70', 'text_en': '60-70%', 'is_correct': True},
                            {'text_tr': '%90-100', 'text_en': '90-100%', 'is_correct': False},
                        ],
                        'explanation_tr': 'Hamile kadinlarin %60-70\'inde migren 2. ve 3. trimesterde belirgin azalir veya tamamen durur.',
                        'explanation_en': 'In 60-70% of pregnant women, migraine significantly decreases or stops completely in the 2nd and 3rd trimesters.',
                    },
                    {
                        'question_tr': 'CGRP inhibitorleri ne yapar?',
                        'question_en': 'What do CGRP inhibitors do?',
                        'options': [
                            {'text_tr': 'Agri sinyalini bloklarlar', 'text_en': 'Block pain signals', 'is_correct': False},
                            {'text_tr': 'Migren sirasinda artan CGRP peptidini veya reseptorunu bloklarlar', 'text_en': 'Block CGRP peptide or receptor that increases during migraine', 'is_correct': True},
                            {'text_tr': 'Kan basincini dusururler', 'text_en': 'Lower blood pressure', 'is_correct': False},
                            {'text_tr': 'Uyku duzenleler', 'text_en': 'Regulate sleep', 'is_correct': False},
                        ],
                        'explanation_tr': 'CGRP inhibitorleri migren atagi sirasinda artan CGRP maddesini veya reseptorunu bloke ederek ataklari onler.',
                        'explanation_en': 'CGRP inhibitors prevent attacks by blocking the CGRP substance or receptor that increases during migraine.',
                    },
                    {
                        'question_tr': 'Cocuklarda migren eriskinlerden nasil farklidir?',
                        'question_en': 'How is migraine in children different from adults?',
                        'options': [
                            {'text_tr': 'Her zaman daha siddetlidir', 'text_en': 'Always more severe', 'is_correct': False},
                            {'text_tr': 'Her iki tarafta agri olabilir ve karin agrisi on planda olabilir', 'text_en': 'Pain can be bilateral and abdominal pain may be prominent', 'is_correct': True},
                            {'text_tr': 'Sadece aurali olur', 'text_en': 'Only with aura', 'is_correct': False},
                            {'text_tr': 'Tedavi gerektirmez', 'text_en': 'No treatment needed', 'is_correct': False},
                        ],
                        'explanation_tr': 'Cocuklarda agri her iki tarafta olabilir, suresi daha kisa olabilir ve karin agrisi (abdominal migren) on planda olabilir.',
                        'explanation_en': 'In children, pain can be on both sides, duration can be shorter, and abdominal pain (abdominal migraine) may be prominent.',
                    },
                    {
                        'question_tr': 'Kronik migrenden episodik migrene donmek mumkun mudur?',
                        'question_en': 'Is it possible to return from chronic to episodic migraine?',
                        'options': [
                            {'text_tr': 'Hayir, kronik migren kalicidir', 'text_en': 'No, chronic migraine is permanent', 'is_correct': False},
                            {'text_tr': 'Evet, dogru tedavi ve yasam tarzi degisiklikleri ile mumkundur', 'text_en': 'Yes, possible with proper treatment and lifestyle changes', 'is_correct': True},
                            {'text_tr': 'Sadece ameliyatla', 'text_en': 'Only with surgery', 'is_correct': False},
                            {'text_tr': 'Sadece ilacla', 'text_en': 'Only with medication', 'is_correct': False},
                        ],
                        'explanation_tr': 'Kronik migren tedavi edilebilir bir durumdur. Dogru tedavi ve yasam tarzi degisiklikleri ile cogu hasta episodik migrene donebilir.',
                        'explanation_en': 'Chronic migraine is a treatable condition. With proper treatment and lifestyle changes, most patients can return to episodic migraine.',
                    },
                ],
            },
        ]

    def _get_badges(self):
        """Egitim rozetleri."""
        return [
            {
                'name_tr': 'Migren Ogrencisi',
                'name_en': 'Migraine Student',
                'description_tr': '5 egitim kartini tamamladiniz',
                'description_en': 'Completed 5 education cards',
                'icon': 'book-open',
                'color': 'teal',
                'category': 'education',
                'rarity': 'common',
                'points_reward': 10,
                'requirement_type': 'education_items_completed',
                'requirement_value': 5,
                'is_active': True,
            },
            {
                'name_tr': 'Bilgi Avcisi',
                'name_en': 'Knowledge Hunter',
                'description_tr': '15 egitim kartini tamamladiniz',
                'description_en': 'Completed 15 education cards',
                'icon': 'target',
                'color': 'indigo',
                'category': 'education',
                'rarity': 'uncommon',
                'points_reward': 25,
                'requirement_type': 'education_items_completed',
                'requirement_value': 15,
                'is_active': True,
            },
            {
                'name_tr': 'Migren Uzmani',
                'name_en': 'Migraine Expert',
                'description_tr': '25 egitim kartini tamamladiniz - tam program',
                'description_en': 'Completed all 25 education cards - full program',
                'icon': 'award',
                'color': 'amber',
                'category': 'education',
                'rarity': 'rare',
                'points_reward': 50,
                'requirement_type': 'education_items_completed',
                'requirement_value': 25,
                'is_active': True,
            },
            {
                'name_tr': 'Quiz Sampiyonu',
                'name_en': 'Quiz Champion',
                'description_tr': '3 quiz\'i basariyla gectin',
                'description_en': 'Successfully passed 3 quizzes',
                'icon': 'trophy',
                'color': 'yellow',
                'category': 'education',
                'rarity': 'uncommon',
                'points_reward': 20,
                'requirement_type': 'quizzes_passed',
                'requirement_value': 3,
                'is_active': True,
            },
            {
                'name_tr': 'Tam Puan',
                'name_en': 'Perfect Score',
                'description_tr': 'Bir quiz\'den tam puan aldiniz',
                'description_en': 'Got a perfect score on a quiz',
                'icon': 'star',
                'color': 'gold',
                'category': 'education',
                'rarity': 'rare',
                'points_reward': 15,
                'requirement_type': 'quiz_perfect_score',
                'requirement_value': 1,
                'is_active': True,
            },
            {
                'name_tr': '7 Gunluk Egitim Serisi',
                'name_en': '7-Day Education Streak',
                'description_tr': '7 gun ust uste egitim tamamladiniz',
                'description_en': 'Completed education 7 days in a row',
                'icon': 'flame',
                'color': 'orange',
                'category': 'streak',
                'rarity': 'uncommon',
                'points_reward': 15,
                'requirement_type': 'education_streak_days',
                'requirement_value': 7,
                'is_active': True,
            },
            {
                'name_tr': '21 Gunluk Egitim Serisi',
                'name_en': '21-Day Education Streak',
                'description_tr': '21 gun ust uste egitim tamamladiniz - aliskanlik kazandiniz!',
                'description_en': 'Completed education 21 days in a row - you formed a habit!',
                'icon': 'flame',
                'color': 'red',
                'category': 'streak',
                'rarity': 'epic',
                'points_reward': 50,
                'requirement_type': 'education_streak_days',
                'requirement_value': 21,
                'is_active': True,
            },
        ]
