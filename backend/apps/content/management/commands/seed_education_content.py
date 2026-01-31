"""
Seed education content for all disease modules.
Usage: python manage.py seed_education_content
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.content.models import ContentCategory, Article, EducationItem
from apps.patients.models import DiseaseModule


class Command(BaseCommand):
    help = 'Seeds education content for disease modules'

    def handle(self, *args, **options):
        self.stdout.write('Seeding education content...')

        # Create categories
        categories = self.create_categories()

        # Get disease modules
        modules = {m.slug: m for m in DiseaseModule.objects.all()}

        # Create content for each module
        self.create_migraine_content(modules.get('migraine'), categories)
        self.create_dementia_content(modules.get('dementia'), categories)
        self.create_epilepsy_content(modules.get('epilepsy'), categories)
        self.create_parkinson_content(modules.get('parkinson'), categories)

        # Create general articles
        self.create_general_articles(categories)

        self.stdout.write(self.style.SUCCESS('Education content seeded successfully!'))

    def create_categories(self):
        categories_data = [
            {'slug': 'basics', 'name_tr': 'Temel Bilgiler', 'name_en': 'Basics', 'order': 1},
            {'slug': 'treatment', 'name_tr': 'Tedavi', 'name_en': 'Treatment', 'order': 2},
            {'slug': 'lifestyle', 'name_tr': 'Yaşam Tarzı', 'name_en': 'Lifestyle', 'order': 3},
            {'slug': 'prevention', 'name_tr': 'Önleme', 'name_en': 'Prevention', 'order': 4},
            {'slug': 'exercises', 'name_tr': 'Egzersizler', 'name_en': 'Exercises', 'order': 5},
            {'slug': 'nutrition', 'name_tr': 'Beslenme', 'name_en': 'Nutrition', 'order': 6},
            {'slug': 'faq', 'name_tr': 'Sık Sorulan Sorular', 'name_en': 'FAQ', 'order': 7},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, _ = ContentCategory.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat.slug] = cat
            self.stdout.write(f'  Category: {cat.name_en}')

        return categories

    def create_migraine_content(self, module, categories):
        if not module:
            self.stdout.write(self.style.WARNING('Migraine module not found'))
            return

        self.stdout.write('Creating migraine content...')

        education_items = [
            {
                'slug': 'migraine-what-is',
                'title_tr': 'Migren Nedir?',
                'title_en': 'What is Migraine?',
                'body_tr': '''Migren, tekrarlayan ve şiddetli baş ağrıları ile karakterize nörolojik bir hastalıktır.

## Belirtiler
- Zonklayıcı veya nabız atar tarzda ağrı
- Genellikle başın bir tarafında
- Bulantı ve kusma
- Işığa ve sese duyarlılık
- Görme bozuklukları (aura)

## Aura Nedir?
Aura, migren atağından önce yaşanan geçici nörolojik belirtilerdir:
- Parlak noktalar veya zigzag çizgiler görme
- Görme alanında kayıp
- Uyuşma veya karıncalanma
- Konuşma güçlüğü

## Migren Türleri
1. **Auralı Migren**: Baş ağrısından önce görsel veya duyusal belirtiler
2. **Aurasız Migren**: En yaygın tip, aura olmadan şiddetli baş ağrısı
3. **Kronik Migren**: Ayda 15 veya daha fazla gün baş ağrısı''',
                'body_en': '''Migraine is a neurological condition characterized by recurring, severe headaches.

## Symptoms
- Throbbing or pulsating pain
- Usually on one side of the head
- Nausea and vomiting
- Sensitivity to light and sound
- Visual disturbances (aura)

## What is Aura?
Aura consists of temporary neurological symptoms before a migraine attack:
- Seeing bright spots or zigzag lines
- Vision loss
- Numbness or tingling
- Speech difficulty

## Types of Migraine
1. **Migraine with Aura**: Visual or sensory symptoms before headache
2. **Migraine without Aura**: Most common type, severe headache without aura
3. **Chronic Migraine**: Headache 15 or more days per month''',
                'content_type': 'text',
                'category': categories['basics'],
                'order': 1,
                'estimated_duration_minutes': 5,
            },
            {
                'slug': 'migraine-triggers',
                'title_tr': 'Migren Tetikleyicileri',
                'title_en': 'Migraine Triggers',
                'body_tr': '''Migren ataklarını tetikleyen faktörleri tanımak, atakları önlemenin ilk adımıdır.

## Yaygın Tetikleyiciler

### Beslenme
- Alkol (özellikle kırmızı şarap)
- Kafein (fazla veya az tüketim)
- Yaşlandırılmış peynirler
- İşlenmiş gıdalar
- Yapay tatlandırıcılar
- Öğün atlama

### Çevresel
- Parlak veya titreyen ışıklar
- Güçlü kokular
- Hava değişiklikleri
- Yüksek sesler

### Yaşam Tarzı
- Stres veya stres sonrası rahatlama
- Uyku düzensizliği
- Fiziksel yorgunluk
- Dehidrasyon

### Hormonal (Kadınlarda)
- Adet döngüsü
- Hamilelik
- Menopoz
- Doğum kontrol hapları

## Tetikleyici Günlüğü
Tetikleyicilerinizi belirlemek için günlük tutun:
- Ne yediniz/içtiniz?
- Kaç saat uyudunuz?
- Stres seviyeniz nasıldı?
- Hava durumu nasıldı?''',
                'body_en': '''Identifying migraine triggers is the first step in preventing attacks.

## Common Triggers

### Dietary
- Alcohol (especially red wine)
- Caffeine (too much or too little)
- Aged cheeses
- Processed foods
- Artificial sweeteners
- Skipping meals

### Environmental
- Bright or flickering lights
- Strong odors
- Weather changes
- Loud noises

### Lifestyle
- Stress or post-stress relaxation
- Irregular sleep
- Physical exhaustion
- Dehydration

### Hormonal (in Women)
- Menstrual cycle
- Pregnancy
- Menopause
- Birth control pills

## Trigger Diary
Keep a diary to identify your triggers:
- What did you eat/drink?
- How many hours did you sleep?
- What was your stress level?
- What was the weather like?''',
                'content_type': 'text',
                'category': categories['prevention'],
                'order': 2,
                'estimated_duration_minutes': 7,
            },
            {
                'slug': 'migraine-treatment',
                'title_tr': 'Migren Tedavisi',
                'title_en': 'Migraine Treatment',
                'body_tr': '''Migren tedavisi, atak tedavisi ve önleyici tedavi olmak üzere iki ana yaklaşımı içerir.

## Atak Tedavisi
Atak başladığında kullanılan ilaçlar:

### Ağrı Kesiciler
- Parasetamol
- İbuprofen
- Naproksen
- Aspirin

### Triptanlar
- Sumatriptan
- Rizatriptan
- Zolmitriptan
Migrene özel, damarları daraltır ve ağrı sinyallerini engeller.

### Anti-emetikler
Bulantı ve kusma için metoklopramid gibi ilaçlar.

## Önleyici Tedavi
Sık atak geçirenlerde (ayda 4+):
- Beta blokerler
- Antidepresanlar
- Antikonvülzanlar
- CGRP inhibitörleri (yeni nesil)
- Botoks enjeksiyonları

## İlaç Dışı Tedaviler
- Akupunktur
- Biofeedback
- Bilişsel davranışçı terapi
- Gevşeme teknikleri
- Düzenli egzersiz

⚠️ **Önemli**: Tüm tedaviler doktorunuz tarafından belirlenmelidir.''',
                'body_en': '''Migraine treatment includes two main approaches: acute treatment and preventive treatment.

## Acute Treatment
Medications used when an attack starts:

### Pain Relievers
- Paracetamol
- Ibuprofen
- Naproxen
- Aspirin

### Triptans
- Sumatriptan
- Rizatriptan
- Zolmitriptan
Migraine-specific, constrict blood vessels and block pain signals.

### Anti-emetics
Medications like metoclopramide for nausea and vomiting.

## Preventive Treatment
For frequent attacks (4+ per month):
- Beta blockers
- Antidepressants
- Anticonvulsants
- CGRP inhibitors (new generation)
- Botox injections

## Non-Drug Treatments
- Acupuncture
- Biofeedback
- Cognitive behavioral therapy
- Relaxation techniques
- Regular exercise

⚠️ **Important**: All treatments should be determined by your doctor.''',
                'content_type': 'text',
                'category': categories['treatment'],
                'order': 3,
                'estimated_duration_minutes': 8,
            },
            {
                'slug': 'migraine-lifestyle',
                'title_tr': 'Migrenle Yaşam',
                'title_en': 'Living with Migraine',
                'body_tr': '''Migren kronik bir durumdur, ancak doğru yaşam tarzı değişiklikleri ile kontrol altına alınabilir.

## Uyku Düzeni
- Her gün aynı saatte yatın ve kalkın
- 7-8 saat uyuyun
- Hafta sonu bile düzeni bozmayın
- Uyku öncesi ekranlardan kaçının

## Beslenme
- Düzenli öğünler yiyin, asla atlama
- Bol su için (günde 8-10 bardak)
- Tetikleyici gıdalardan kaçının
- Kafein tüketimini sınırlayın

## Stres Yönetimi
- Düzenli egzersiz yapın
- Meditasyon ve derin nefes teknikleri
- Hobiler edinin
- Sosyal destek alın

## Çalışma Ortamı
- Ekran parlaklığını ayarlayın
- Düzenli mola verin
- Ergonomik oturma
- Florasan ışıklardan kaçının

## Atak Sırasında
1. Karanlık, sessiz bir odaya gidin
2. Soğuk kompres uygulayın
3. Bol su için
4. İlacınızı erken alın
5. Dinlenin''',
                'body_en': '''Migraine is a chronic condition, but it can be controlled with the right lifestyle changes.

## Sleep Schedule
- Go to bed and wake up at the same time every day
- Sleep 7-8 hours
- Don't break the routine even on weekends
- Avoid screens before bed

## Nutrition
- Eat regular meals, never skip
- Drink plenty of water (8-10 glasses daily)
- Avoid trigger foods
- Limit caffeine intake

## Stress Management
- Exercise regularly
- Meditation and deep breathing techniques
- Find hobbies
- Get social support

## Work Environment
- Adjust screen brightness
- Take regular breaks
- Ergonomic seating
- Avoid fluorescent lights

## During an Attack
1. Go to a dark, quiet room
2. Apply cold compress
3. Drink plenty of water
4. Take your medication early
5. Rest''',
                'content_type': 'text',
                'category': categories['lifestyle'],
                'order': 4,
                'estimated_duration_minutes': 6,
            },
        ]

        for item_data in education_items:
            category = item_data.pop('category')
            EducationItem.objects.update_or_create(
                slug=item_data['slug'],
                defaults={
                    **item_data,
                    'disease_module': module,
                    'category': category,
                    'is_published': True,
                }
            )
            self.stdout.write(f'  Education: {item_data["title_en"]}')

    def create_dementia_content(self, module, categories):
        if not module:
            self.stdout.write(self.style.WARNING('Dementia module not found'))
            return

        self.stdout.write('Creating dementia content...')

        education_items = [
            {
                'slug': 'dementia-what-is',
                'title_tr': 'Demans Nedir?',
                'title_en': 'What is Dementia?',
                'body_tr': '''Demans, hafıza, düşünme ve sosyal yetenekleri etkileyen belirtiler grubudur.

## Demans Nedir?
Demans tek bir hastalık değil, birçok farklı durumun neden olduğu bir belirtiler topluluğudur. Beyin hücrelerinin hasar görmesi sonucu ortaya çıkar.

## Belirtiler
### Bilişsel
- Hafıza kaybı (özellikle yakın geçmiş)
- Dil güçlükleri
- Yön bulma zorluğu
- Planlama ve organizasyon problemleri
- Karar verme güçlüğü

### Davranışsal
- Kişilik değişiklikleri
- Depresyon ve anksiyete
- Ajitasyon
- Sosyal geri çekilme
- Uyku bozuklukları

## Demans Türleri
1. **Alzheimer Hastalığı**: En yaygın tip (%60-80)
2. **Vasküler Demans**: İnme sonrası görülür
3. **Lewy Cisimcikli Demans**: Parkinson benzeri belirtiler
4. **Frontotemporal Demans**: Davranış ve dil değişiklikleri

## Risk Faktörleri
- İleri yaş
- Aile öyküsü
- Kalp hastalıkları
- Diyabet
- Hareketsiz yaşam
- Sosyal izolasyon''',
                'body_en': '''Dementia is a group of symptoms affecting memory, thinking and social abilities.

## What is Dementia?
Dementia is not a single disease but a collection of symptoms caused by various conditions. It occurs when brain cells are damaged.

## Symptoms
### Cognitive
- Memory loss (especially recent past)
- Language difficulties
- Disorientation
- Planning and organization problems
- Decision-making difficulties

### Behavioral
- Personality changes
- Depression and anxiety
- Agitation
- Social withdrawal
- Sleep disorders

## Types of Dementia
1. **Alzheimer's Disease**: Most common type (60-80%)
2. **Vascular Dementia**: Occurs after stroke
3. **Lewy Body Dementia**: Parkinson-like symptoms
4. **Frontotemporal Dementia**: Behavior and language changes

## Risk Factors
- Advanced age
- Family history
- Heart disease
- Diabetes
- Sedentary lifestyle
- Social isolation''',
                'content_type': 'text',
                'category': categories['basics'],
                'order': 1,
                'estimated_duration_minutes': 8,
            },
            {
                'slug': 'dementia-cognitive-exercises',
                'title_tr': 'Bilişsel Egzersizler',
                'title_en': 'Cognitive Exercises',
                'body_tr': '''Düzenli bilişsel egzersizler beyin sağlığını korumaya yardımcı olabilir.

## Hafıza Egzersizleri
- **Liste Ezberleme**: Alışveriş listeleri yazıp ezberlemeye çalışın
- **Hikaye Anlatma**: Günlük olayları detaylı anlatın
- **Fotoğraf İnceleme**: Eski fotoğraflara bakıp anıları hatırlayın
- **İsim-Yüz Eşleştirme**: Tanıştığınız kişilerin isimlerini tekrarlayın

## Dikkat Egzersizleri
- **Bulmaca Çözme**: Sudoku, çengel bulmaca
- **Farklı Bul**: İki resim arasındaki farkları bulun
- **Sıralama Oyunları**: Nesneleri belirli kriterlere göre sıralayın

## Dil Egzersizleri
- **Kelime Oyunları**: Scrabble, kelime avı
- **Yeni Kelimeler**: Her gün yeni bir kelime öğrenin
- **Hikaye Yazma**: Kısa hikayeler yazın
- **Okuma**: Günlük gazete veya kitap okuyun

## Günlük Öneriler
1. Her gün farklı bir bilişsel aktivite yapın
2. Zorluk seviyesini kademeli artırın
3. Sosyal aktivitelerle birleştirin
4. Sabah saatlerinde yapın
5. 15-30 dakika ile başlayın

## Uygulamamızdaki Oyunlar
Norosera uygulamasında size özel hazırlanmış bilişsel oyunları oynayabilirsiniz:
- Hafıza Kartları
- Kelime Eşleştirme
- Sıralama Oyunları
- Dikkat Testleri''',
                'body_en': '''Regular cognitive exercises can help maintain brain health.

## Memory Exercises
- **List Memorization**: Write shopping lists and try to memorize them
- **Storytelling**: Describe daily events in detail
- **Photo Review**: Look at old photos and recall memories
- **Name-Face Matching**: Repeat names of people you meet

## Attention Exercises
- **Puzzle Solving**: Sudoku, crossword puzzles
- **Spot the Difference**: Find differences between two pictures
- **Sorting Games**: Sort objects by specific criteria

## Language Exercises
- **Word Games**: Scrabble, word search
- **New Words**: Learn a new word every day
- **Story Writing**: Write short stories
- **Reading**: Read daily newspaper or books

## Daily Recommendations
1. Do a different cognitive activity each day
2. Gradually increase difficulty level
3. Combine with social activities
4. Do in the morning hours
5. Start with 15-30 minutes

## Games in Our App
You can play cognitive games specially prepared for you in the Norosera app:
- Memory Cards
- Word Matching
- Sorting Games
- Attention Tests''',
                'content_type': 'text',
                'category': categories['exercises'],
                'order': 2,
                'estimated_duration_minutes': 10,
            },
            {
                'slug': 'dementia-caregiver-guide',
                'title_tr': 'Bakıcı Rehberi',
                'title_en': 'Caregiver Guide',
                'body_tr': '''Demans hastasına bakım vermek zorlu ama anlamlı bir süreçtir.

## İletişim
- Basit ve net cümleler kullanın
- Göz teması kurun
- Sabırlı olun, acele etmeyin
- Eleştiriden kaçının
- Seçenekleri sınırlı tutun

## Günlük Rutin
- Tutarlı bir program oluşturun
- Aktiviteleri basit adımlara bölün
- Görsel ipuçları kullanın
- Bağımsızlığı destekleyin
- Esnek olun

## Güvenlik
- Kesici aletleri kaldırın
- İlaçları kilitleyin
- Gaz ve elektriği kontrol edin
- Kayma önleyici paspaslar kullanın
- Kapı alarmları düşünün

## Davranış Değişiklikleri
### Ajitasyon
- Tetikleyiciyi bulun
- Dikkat dağıtın
- Müzik çalın
- Yürüyüşe çıkın

### Gündüz Batımı Sendromu
- Akşam rutini oluşturun
- Işıkları parlak tutun
- Kafein ve şekeri azaltın
- Gündüz aktivitelerini artırın

## Kendinize Bakım
- Yardım isteyin
- Destek gruplarına katılın
- Mola verin
- Sağlığınızı ihmal etmeyin
- Duygularınızı ifade edin

⚠️ Bakıcı tükenmişliği ciddi bir durumdur. Kendinizi ihmal etmeyin.''',
                'body_en': '''Caring for a dementia patient is a challenging but meaningful process.

## Communication
- Use simple and clear sentences
- Make eye contact
- Be patient, don't rush
- Avoid criticism
- Keep options limited

## Daily Routine
- Create a consistent schedule
- Break activities into simple steps
- Use visual cues
- Support independence
- Be flexible

## Safety
- Remove sharp objects
- Lock medications
- Check gas and electricity
- Use non-slip mats
- Consider door alarms

## Behavioral Changes
### Agitation
- Find the trigger
- Distract attention
- Play music
- Go for a walk

### Sundowning Syndrome
- Create evening routine
- Keep lights bright
- Reduce caffeine and sugar
- Increase daytime activities

## Self-Care
- Ask for help
- Join support groups
- Take breaks
- Don't neglect your health
- Express your feelings

⚠️ Caregiver burnout is serious. Don't neglect yourself.''',
                'content_type': 'text',
                'category': categories['lifestyle'],
                'order': 3,
                'estimated_duration_minutes': 12,
            },
            {
                'slug': 'dementia-nutrition',
                'title_tr': 'Demans ve Beslenme',
                'title_en': 'Dementia and Nutrition',
                'body_tr': '''Doğru beslenme beyin sağlığını destekler ve demans ilerlemesini yavaşlatabilir.

## MIND Diyeti
Akdeniz ve DASH diyetlerinin birleşimi:

### Önerilen Gıdalar
- **Yeşil yapraklı sebzeler**: Günde 1+ porsiyon
- **Diğer sebzeler**: Günde 1+ porsiyon
- **Kuruyemişler**: Günde 1 avuç
- **Yaban mersini**: Haftada 2+ porsiyon
- **Fasulye/Baklagil**: Haftada 3+ porsiyon
- **Tam tahıllar**: Günde 3+ porsiyon
- **Balık**: Haftada 1+ porsiyon
- **Tavuk**: Haftada 2+ porsiyon
- **Zeytinyağı**: Ana yağ olarak

### Sınırlanması Gerekenler
- Kırmızı et: Haftada 4'ten az
- Tereyağı: Günde 1 yemek kaşığından az
- Peynir: Haftada 1'den az
- Pasta/tatlı: Haftada 5'ten az
- Kızartma/fast food: Haftada 1'den az

## Hidrasyon
- Günde 6-8 bardak su
- Kafeinli içecekleri sınırlayın
- Alkol tüketimini azaltın

## Beslenme Zorlukları
Demans ilerledikçe:
- Küçük, sık öğünler sunun
- Parmakla yenebilir gıdalar hazırlayın
- Renkli tabaklar kullanın
- Dikkat dağıtıcıları azaltın
- Yutma güçlüğünde yumuşak gıdalar tercih edin''',
                'body_en': '''Proper nutrition supports brain health and may slow dementia progression.

## MIND Diet
Combination of Mediterranean and DASH diets:

### Recommended Foods
- **Green leafy vegetables**: 1+ serving daily
- **Other vegetables**: 1+ serving daily
- **Nuts**: 1 handful daily
- **Blueberries**: 2+ servings weekly
- **Beans/Legumes**: 3+ servings weekly
- **Whole grains**: 3+ servings daily
- **Fish**: 1+ serving weekly
- **Poultry**: 2+ servings weekly
- **Olive oil**: As main oil

### Foods to Limit
- Red meat: Less than 4 per week
- Butter: Less than 1 tbsp daily
- Cheese: Less than 1 per week
- Pastries/sweets: Less than 5 per week
- Fried/fast food: Less than 1 per week

## Hydration
- 6-8 glasses of water daily
- Limit caffeinated drinks
- Reduce alcohol consumption

## Eating Challenges
As dementia progresses:
- Offer small, frequent meals
- Prepare finger foods
- Use colorful plates
- Reduce distractions
- Prefer soft foods for swallowing difficulties''',
                'content_type': 'text',
                'category': categories['nutrition'],
                'order': 4,
                'estimated_duration_minutes': 8,
            },
        ]

        for item_data in education_items:
            category = item_data.pop('category')
            EducationItem.objects.update_or_create(
                slug=item_data['slug'],
                defaults={
                    **item_data,
                    'disease_module': module,
                    'category': category,
                    'is_published': True,
                }
            )
            self.stdout.write(f'  Education: {item_data["title_en"]}')

    def create_epilepsy_content(self, module, categories):
        if not module:
            self.stdout.write(self.style.WARNING('Epilepsy module not found'))
            return

        self.stdout.write('Creating epilepsy content...')

        education_items = [
            {
                'slug': 'epilepsy-what-is',
                'title_tr': 'Epilepsi Nedir?',
                'title_en': 'What is Epilepsy?',
                'body_tr': '''Epilepsi, beyindeki anormal elektriksel aktiviteden kaynaklanan nöbetlerle karakterize kronik bir nörolojik hastalıktır.

## Nöbet Nedir?
Nöbet, beyin hücrelerinde ani ve aşırı elektriksel aktivite sonucu ortaya çıkar. Bu durum:
- Bilinç değişiklikleri
- Kasılmalar
- Duyusal değişiklikler
- Davranış değişiklikleri oluşturabilir.

## Nöbet Türleri

### Fokal (Parsiyel) Nöbetler
Beynin bir bölgesinde başlar:
- **Basit Fokal**: Bilinç açık, tek taraf etkilenir
- **Kompleks Fokal**: Bilinç etkilenir, otomatik hareketler

### Jeneralize Nöbetler
Tüm beyin etkilenir:
- **Absans**: Kısa süreli boş bakış
- **Tonik-Klonik**: Kasılma ve sarsılmalar
- **Atonik**: Ani kas tonusu kaybı
- **Miyoklonik**: Ani kas sıçramaları

## Tetikleyiciler
- Uyku eksikliği
- Stres
- Alkol
- Adet döngüsü
- Yanıp sönen ışıklar
- İlaç unutma

## Tanı
- EEG (elektroensefalografi)
- MRI
- Kan testleri
- Nörolojik muayene''',
                'body_en': '''Epilepsy is a chronic neurological condition characterized by seizures caused by abnormal electrical activity in the brain.

## What is a Seizure?
A seizure occurs when there is sudden, excessive electrical activity in brain cells. This can cause:
- Changes in consciousness
- Convulsions
- Sensory changes
- Behavioral changes

## Types of Seizures

### Focal (Partial) Seizures
Starts in one area of the brain:
- **Simple Focal**: Consciousness intact, one side affected
- **Complex Focal**: Consciousness affected, automatic movements

### Generalized Seizures
Entire brain affected:
- **Absence**: Brief blank stare
- **Tonic-Clonic**: Stiffening and jerking
- **Atonic**: Sudden loss of muscle tone
- **Myoclonic**: Sudden muscle jerks

## Triggers
- Sleep deprivation
- Stress
- Alcohol
- Menstrual cycle
- Flashing lights
- Missing medication

## Diagnosis
- EEG (electroencephalography)
- MRI
- Blood tests
- Neurological examination''',
                'content_type': 'text',
                'category': categories['basics'],
                'order': 1,
                'estimated_duration_minutes': 10,
            },
            {
                'slug': 'epilepsy-first-aid',
                'title_tr': 'Nöbet İlk Yardım',
                'title_en': 'Seizure First Aid',
                'body_tr': '''Nöbet geçiren birine yardım etmek hayat kurtarabilir.

## Yapılması Gerekenler ✓

1. **Sakin kalın** ve zamanı not edin
2. **Tehlikeli nesneleri** uzaklaştırın
3. **Baş altına** yumuşak bir şey koyun
4. **Yan yatırın** (nöbet durduğunda)
5. **Rahat nefes almasını** sağlayın
6. **Yanında kalın** bilinç geri gelene kadar

## Yapılmaması Gerekenler ✗

- **Ağzına bir şey koymayın** (kaşık, parmak vb.)
- **Tutmaya/bastırmaya** çalışmayın
- **Su veya ilaç** vermeyin
- **Hareket ettirmeyin** (tehlike yoksa)
- **Yapay solunum** yapmayın (nefes alıyorsa)

## Ne Zaman 112'yi Aramalı?

- Nöbet 5 dakikadan uzun sürerse
- İlk kez nöbet geçiriyorsa
- Nefes almakta zorlanıyorsa
- Suda nöbet geçirdiyse
- Hamile ise
- Diyabetik ise
- Yaralanma varsa
- Bilinç geri gelmiyorsa
- İkinci nöbet başlarsa

## Nöbet Sonrası

- Kişi yorgun ve kafası karışık olabilir
- Sakin ve destekleyici olun
- Ne olduğunu açıklayın
- Dinlenmesine izin verin
- Yalnız bırakmayın''',
                'body_en': '''Helping someone having a seizure can save their life.

## Do's ✓

1. **Stay calm** and note the time
2. **Remove dangerous objects** nearby
3. **Put something soft** under their head
4. **Turn them on their side** (after seizure stops)
5. **Ensure they can breathe** easily
6. **Stay with them** until consciousness returns

## Don'ts ✗

- **Don't put anything in their mouth** (spoon, finger, etc.)
- **Don't try to hold/restrain** them
- **Don't give water or medication**
- **Don't move them** (unless in danger)
- **Don't give CPR** (if breathing)

## When to Call Emergency

- Seizure lasts more than 5 minutes
- First-time seizure
- Difficulty breathing
- Seizure in water
- Person is pregnant
- Person is diabetic
- Injury occurred
- Consciousness doesn't return
- Second seizure starts

## After the Seizure

- Person may be tired and confused
- Be calm and supportive
- Explain what happened
- Let them rest
- Don't leave them alone''',
                'content_type': 'text',
                'category': categories['basics'],
                'order': 2,
                'estimated_duration_minutes': 7,
            },
        ]

        for item_data in education_items:
            category = item_data.pop('category')
            EducationItem.objects.update_or_create(
                slug=item_data['slug'],
                defaults={
                    **item_data,
                    'disease_module': module,
                    'category': category,
                    'is_published': True,
                }
            )
            self.stdout.write(f'  Education: {item_data["title_en"]}')

    def create_parkinson_content(self, module, categories):
        if not module:
            self.stdout.write(self.style.WARNING('Parkinson module not found'))
            return

        self.stdout.write('Creating parkinson content...')

        education_items = [
            {
                'slug': 'parkinson-what-is',
                'title_tr': 'Parkinson Hastalığı Nedir?',
                'title_en': 'What is Parkinson\'s Disease?',
                'body_tr': '''Parkinson hastalığı, hareket kontrolünü etkileyen ilerleyici bir nörolojik hastalıktır.

## Nasıl Oluşur?
Beyindeki dopamin üreten hücrelerin kaybı sonucu ortaya çıkar. Dopamin, hareketin düzgün koordinasyonu için gerekli bir nörotransmiterdir.

## Ana Belirtiler (Motor)

### Titreme (Tremor)
- Dinlenme halinde görülür
- Genellikle bir elde başlar
- "Hap yuvarlama" hareketi

### Bradikinezi (Yavaşlama)
- Hareketlerde yavaşlama
- Yüz ifadesinin azalması
- Yazının küçülmesi

### Rijidite (Sertlik)
- Kas sertliği
- Eklem hareketlerinde direnç
- Ağrı ve kramplar

### Postüral İnstabilite
- Denge bozukluğu
- Düşme riski
- Öne eğik duruş

## Motor Dışı Belirtiler
- Uyku bozuklukları
- Depresyon ve anksiyete
- Koku alma kaybı
- Kabızlık
- Bilişsel değişiklikler

## Risk Faktörleri
- İleri yaş (60+)
- Erkek cinsiyet
- Aile öyküsü
- Çevresel faktörler
- Kafa travması''',
                'body_en': '''Parkinson's disease is a progressive neurological condition affecting movement control.

## How Does It Develop?
It occurs due to loss of dopamine-producing cells in the brain. Dopamine is a neurotransmitter needed for smooth coordination of movement.

## Main Symptoms (Motor)

### Tremor
- Occurs at rest
- Usually starts in one hand
- "Pill-rolling" movement

### Bradykinesia (Slowness)
- Slowness of movement
- Decreased facial expression
- Handwriting becomes smaller

### Rigidity (Stiffness)
- Muscle stiffness
- Resistance in joint movements
- Pain and cramps

### Postural Instability
- Balance problems
- Risk of falling
- Forward-leaning posture

## Non-Motor Symptoms
- Sleep disorders
- Depression and anxiety
- Loss of smell
- Constipation
- Cognitive changes

## Risk Factors
- Advanced age (60+)
- Male gender
- Family history
- Environmental factors
- Head trauma''',
                'content_type': 'text',
                'category': categories['basics'],
                'order': 1,
                'estimated_duration_minutes': 9,
            },
            {
                'slug': 'parkinson-exercises',
                'title_tr': 'Parkinson Egzersizleri',
                'title_en': 'Parkinson Exercises',
                'body_tr': '''Düzenli egzersiz Parkinson belirtilerini yönetmede çok önemlidir.

## Egzersizin Faydaları
- Hareket yeteneğini korur
- Denge ve koordinasyonu geliştirir
- Kas gücünü artırır
- Ruh halini iyileştirir
- Uyku kalitesini artırır

## Önerilen Egzersizler

### Yürüyüş
- Günde 30 dakika
- Büyük adımlar atın
- Kolları sallayın
- Düz bir yüzeyde başlayın

### Denge Egzersizleri
- Tek ayak üzerinde durma
- Topuktan parmak ucuna yürüme
- Yan adımlar
- Sandalye desteği ile çömelme

### Esneklik
- Boyun germe
- Omuz dönüşleri
- Gövde rotasyonları
- Bacak germeleri

### Güç Egzersizleri
- Sandalyede oturma-kalkma
- Duvar şınavı
- Hafif ağırlık kaldırma
- Direnç bandı egzersizleri

## Özel Aktiviteler
- **Dans**: Tango özellikle faydalı
- **Tai Chi**: Denge ve esneklik
- **Yüzme**: Düşük etkili, tam vücut
- **Bisiklet**: Zorunlu pedallama hareketi

## Önemli İpuçları
- Güvenli bir ortamda yapın
- Düşme önlemlerini alın
- Küçük başlayıp artırın
- İlaç etkili olduğunda egzersiz yapın
- Fizyoterapistinize danışın''',
                'body_en': '''Regular exercise is crucial in managing Parkinson's symptoms.

## Benefits of Exercise
- Maintains mobility
- Improves balance and coordination
- Increases muscle strength
- Improves mood
- Enhances sleep quality

## Recommended Exercises

### Walking
- 30 minutes daily
- Take big steps
- Swing your arms
- Start on flat surface

### Balance Exercises
- Standing on one foot
- Heel-to-toe walking
- Side steps
- Chair-supported squats

### Flexibility
- Neck stretches
- Shoulder rolls
- Trunk rotations
- Leg stretches

### Strength Exercises
- Chair sit-to-stand
- Wall push-ups
- Light weight lifting
- Resistance band exercises

## Special Activities
- **Dance**: Tango especially beneficial
- **Tai Chi**: Balance and flexibility
- **Swimming**: Low impact, full body
- **Cycling**: Forced pedaling movement

## Important Tips
- Exercise in a safe environment
- Take fall precautions
- Start small and increase
- Exercise when medication is effective
- Consult your physiotherapist''',
                'content_type': 'text',
                'category': categories['exercises'],
                'order': 2,
                'estimated_duration_minutes': 8,
            },
        ]

        for item_data in education_items:
            category = item_data.pop('category')
            EducationItem.objects.update_or_create(
                slug=item_data['slug'],
                defaults={
                    **item_data,
                    'disease_module': module,
                    'category': category,
                    'is_published': True,
                }
            )
            self.stdout.write(f'  Education: {item_data["title_en"]}')

    def create_general_articles(self, categories):
        self.stdout.write('Creating general articles...')

        articles = [
            {
                'slug': 'brain-health-tips',
                'title_tr': 'Beyin Sağlığı İçin 10 Altın Kural',
                'title_en': '10 Golden Rules for Brain Health',
                'excerpt_tr': 'Beyin sağlığınızı korumak için günlük hayatta uygulayabileceğiniz basit ama etkili öneriler.',
                'excerpt_en': 'Simple but effective tips you can apply in daily life to protect your brain health.',
                'body_tr': '''Beyin sağlığınızı korumak için bu 10 altın kuralı takip edin.

## 1. Düzenli Egzersiz Yapın
Haftada en az 150 dakika orta yoğunlukta aerobik egzersiz beyin kan akışını artırır.

## 2. Kaliteli Uyku Alın
7-9 saat uyku beyninizin toksinleri temizlemesi için gereklidir.

## 3. Sağlıklı Beslenin
Akdeniz diyeti beyin sağlığı için en çok araştırılmış beslenme şeklidir.

## 4. Sosyal Bağlar Kurun
Sosyal etkileşim bilişsel gerilemeyi yavaşlatır.

## 5. Yeni Şeyler Öğrenin
Yeni dil, enstrüman veya hobi beyni aktif tutar.

## 6. Stresi Yönetin
Kronik stres beyin hücrelerine zarar verir.

## 7. Alkol ve Sigaradan Uzak Durun
Her ikisi de beyin sağlığını olumsuz etkiler.

## 8. Kalp Sağlığına Dikkat Edin
Kalp için iyi olan beyin için de iyidir.

## 9. Kafa Travmalarından Kaçının
Spor yaparken kask takın, emniyet kemeri kullanın.

## 10. Düzenli Sağlık Kontrolü
Kan basıncı, şeker ve kolesterolü takip edin.''',
                'body_en': '''Follow these 10 golden rules to protect your brain health.

## 1. Exercise Regularly
At least 150 minutes of moderate aerobic exercise per week increases brain blood flow.

## 2. Get Quality Sleep
7-9 hours of sleep is necessary for your brain to clear toxins.

## 3. Eat Healthy
Mediterranean diet is the most researched diet for brain health.

## 4. Build Social Connections
Social interaction slows cognitive decline.

## 5. Learn New Things
New language, instrument or hobby keeps the brain active.

## 6. Manage Stress
Chronic stress damages brain cells.

## 7. Avoid Alcohol and Smoking
Both negatively affect brain health.

## 8. Take Care of Heart Health
What's good for the heart is good for the brain.

## 9. Avoid Head Injuries
Wear helmet during sports, use seatbelt.

## 10. Regular Health Check-ups
Monitor blood pressure, sugar and cholesterol.''',
                'category': categories['lifestyle'],
                'is_featured': True,
            },
        ]

        for article_data in articles:
            category = article_data.pop('category')
            Article.objects.update_or_create(
                slug=article_data['slug'],
                defaults={
                    **article_data,
                    'category': category,
                    'status': 'published',
                    'published_at': timezone.now(),
                }
            )
            self.stdout.write(f'  Article: {article_data["title_en"]}')
