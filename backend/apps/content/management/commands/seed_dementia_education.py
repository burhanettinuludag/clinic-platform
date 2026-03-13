"""
Demans Egitim Seti - 5 modul x 5 kart = 25 egitim icerigi + 5 quiz + rozetler.
Kullanim: python3 manage.py seed_dementia_education
"""
from django.core.management.base import BaseCommand
from apps.content.models import (
    ContentCategory, EducationItem, EducationQuiz, QuizQuestion,
)
from apps.patients.models import DiseaseModule
from apps.gamification.models import Badge


class Command(BaseCommand):
    help = 'Demans egitim seti: 25 kart, 5 quiz, 7 rozet'

    def handle(self, *args, **options):
        dementia_module = DiseaseModule.objects.filter(slug='dementia').first()
        if not dementia_module:
            self.stderr.write('Demans modulu bulunamadi!')
            return

        # --- Kategoriler ---
        categories = {}
        cat_data = [
            ('dementia-basics', 'Demansi Taniyalim', 'Understanding Dementia', 1),
            ('dementia-types', 'Demans Turleri', 'Types of Dementia', 2),
            ('dementia-signs', 'Erken Belirtiler ve Uyari Isareti', 'Early Signs & Red Flags', 3),
            ('dementia-diagnosis', 'Tani ve Degerlendirme', 'Diagnosis & Assessment', 4),
            ('dementia-care', 'Bakim, Destek ve Yasam Kalitesi', 'Care, Support & Quality of Life', 5),
        ]
        for slug, name_tr, name_en, order in cat_data:
            cat, _ = ContentCategory.objects.update_or_create(
                slug=slug,
                defaults={'name_tr': name_tr, 'name_en': name_en, 'order': order + 200},
            )
            categories[slug] = cat

        # --- 25 Egitim Karti ---
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
                    'disease_module': dementia_module,
                    'category': cat,
                    'order': card['order'],
                    'is_published': True,
                    'estimated_duration_minutes': card.get('duration', 4),
                },
            )
            if created:
                created_cards += 1

        self.stdout.write(f'EducationItem: {created_cards} yeni, {len(cards) - created_cards} guncellendi.')

        # --- 5 Quiz ---
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
                    'disease_module': dementia_module,
                    'category': cat,
                    'passing_score_percent': 60,
                    'points_reward': 10,
                    'is_published': True,
                    'order': qd['order'],
                },
            )
            if created:
                created_quizzes += 1

            quiz_items = EducationItem.objects.filter(
                category=cat, disease_module=dementia_module
            )
            quiz.education_items.set(quiz_items)

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

        # --- Rozetler ---
        badges = [
            {
                'name_tr': 'Demans Ogrencisi',
                'name_en': 'Dementia Learner',
                'description_tr': '5 demans egitim kartini tamamladiniz',
                'description_en': 'Completed 5 dementia education cards',
                'icon': 'brain',
                'color': 'teal',
                'category': 'education',
                'rarity': 'common',
                'points_reward': 10,
                'requirement_type': 'dementia_education_completed',
                'requirement_value': 5,
                'is_active': True,
            },
            {
                'name_tr': 'Demans Bilgi Avcisi',
                'name_en': 'Dementia Knowledge Hunter',
                'description_tr': '15 demans egitim kartini tamamladiniz',
                'description_en': 'Completed 15 dementia education cards',
                'icon': 'target',
                'color': 'indigo',
                'category': 'education',
                'rarity': 'uncommon',
                'points_reward': 25,
                'requirement_type': 'dementia_education_completed',
                'requirement_value': 15,
                'is_active': True,
            },
            {
                'name_tr': 'Demans Egitim Ustasi',
                'name_en': 'Dementia Education Master',
                'description_tr': '25 demans egitim kartini tamamladiniz - tam program',
                'description_en': 'Completed all 25 dementia education cards - full program',
                'icon': 'graduation-cap',
                'color': 'amber',
                'category': 'education',
                'rarity': 'rare',
                'points_reward': 50,
                'requirement_type': 'dementia_education_completed',
                'requirement_value': 25,
                'is_active': True,
            },
            {
                'name_tr': 'Demans Quiz Sampiyonu',
                'name_en': 'Dementia Quiz Champion',
                'description_tr': '3 demans quizini basariyla gectin',
                'description_en': 'Successfully passed 3 dementia quizzes',
                'icon': 'trophy',
                'color': 'yellow',
                'category': 'education',
                'rarity': 'uncommon',
                'points_reward': 20,
                'requirement_type': 'dementia_quizzes_passed',
                'requirement_value': 3,
                'is_active': True,
            },
            {
                'name_tr': 'Demans Seri Ogretici',
                'name_en': 'Dementia Streak Learner',
                'description_tr': '7 gun ust uste demans egitimi yaptin',
                'description_en': '7-day dementia education streak',
                'icon': 'flame',
                'color': 'orange',
                'category': 'streak',
                'rarity': 'uncommon',
                'points_reward': 25,
                'requirement_type': 'dementia_education_streak',
                'requirement_value': 7,
                'is_active': True,
            },
        ]
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
        self.stdout.write(self.style.SUCCESS('Demans egitim seti basariyla yuklendi!'))

    # =========================================================================
    # MODUL 1: DEMANSI TANIYALIM
    # =========================================================================
    def _get_cards(self):
        return [
            # --- Modul 1: Demansi Taniyalim ---
            {
                'slug': 'dementia-basics-what-is',
                'category': 'dementia-basics',
                'order': 1,
                'duration': 4,
                'title_tr': 'Demans Nedir?',
                'title_en': 'What Is Dementia?',
                'body_tr': (
                    '## Demans: Genel Bakis\n\n'
                    'Demans, **tek bir hastalik degil**, bilissel islevlerde (dusunme, hatirlama, karar verme) '
                    'ciddi kayba yol acan bir **belirtiler toplulugudur**. Gunluk yasamda bagimsiz islevsellige '
                    'engel olacak duzeyde bilissel bozulmaya isaret eder.\n\n'
                    '### Onemli Noktalar\n\n'
                    '- Demans yaslanmanin dogal bir sonucu **degildir**\n'
                    '- Beyindeki sinir hucreleri hasar gorur veya olur\n'
                    '- Dunya genelinde 55 milyondan fazla kisiyi etkiler\n'
                    '- Erken tani ile hastalik sureci yavaslatilabilir\n\n'
                    '> **Bilinmesi Gereken:** Her unutkanlik demans degildir, ancak her demans baslangicinda '
                    'unutkanlik vardir. Aradaki farki anlamak kritik oneme sahiptir.'
                ),
                'body_en': (
                    '## Dementia: An Overview\n\n'
                    'Dementia is **not a single disease** but a **group of symptoms** that cause serious '
                    'decline in cognitive functions (thinking, remembering, decision-making). It interferes '
                    'with independent daily functioning.\n\n'
                    '### Key Points\n\n'
                    '- Dementia is **not** a natural part of aging\n'
                    '- Nerve cells in the brain are damaged or die\n'
                    '- Over 55 million people worldwide are affected\n'
                    '- Early diagnosis can slow disease progression\n\n'
                    '> **Important:** Not every forgetfulness is dementia, but every dementia starts with '
                    'memory issues. Understanding the difference is critical.'
                ),
            },
            {
                'slug': 'dementia-basics-brain-changes',
                'category': 'dementia-basics',
                'order': 2,
                'duration': 5,
                'title_tr': 'Beyinde Neler Degisiyor?',
                'title_en': 'What Changes in the Brain?',
                'body_tr': (
                    '## Demansta Beyin Degisiklikleri\n\n'
                    'Saglikli bir beyinde sinir hucreleri (noronlar) birbirleriyle surekli iletisim kurar. '
                    'Demansta bu iletisim aglari bozulur.\n\n'
                    '### Temel Degisiklikler\n\n'
                    '- **Protein birikimi:** Amiloid plaklar ve tau yumaklari beyin hucreleri arasinda birikir\n'
                    '- **Noronal kayip:** Sinir hucreleri olur ve yerine yenileri olusturulamaz\n'
                    '- **Sinaptik bozulma:** Hucrelerin birbiriyle haberlesmesi zorlanir\n'
                    '- **Beyin hacmi azalmasi:** Ozellikle hipokampus (hafiza merkezi) kuculur\n\n'
                    '### Etkilenen Bolgeler\n\n'
                    '| Beyin Bolgesi | Islevi | Demans Etkisi |\n'
                    '|---|---|---|\n'
                    '| Hipokampus | Hafiza olusturma | Yeni bilgileri ogrenme zorluklugu |\n'
                    '| Temporal lob | Dil ve anlama | Kelime bulma guclugu |\n'
                    '| Frontal lob | Planlama, karar | Organizasyon bozuklugu |\n'
                    '| Parietal lob | Mekansal algi | Yon bulma guclugu |'
                ),
                'body_en': (
                    '## Brain Changes in Dementia\n\n'
                    'In a healthy brain, nerve cells (neurons) constantly communicate with each other. '
                    'In dementia, these communication networks break down.\n\n'
                    '### Key Changes\n\n'
                    '- **Protein buildup:** Amyloid plaques and tau tangles accumulate between brain cells\n'
                    '- **Neuronal loss:** Nerve cells die and cannot be replaced\n'
                    '- **Synaptic disruption:** Cell-to-cell communication becomes difficult\n'
                    '- **Brain volume reduction:** Especially the hippocampus (memory center) shrinks\n\n'
                    '### Affected Regions\n\n'
                    '| Brain Region | Function | Dementia Impact |\n'
                    '|---|---|---|\n'
                    '| Hippocampus | Memory formation | Difficulty learning new information |\n'
                    '| Temporal lobe | Language & understanding | Word-finding difficulty |\n'
                    '| Frontal lobe | Planning & decisions | Organizational problems |\n'
                    '| Parietal lobe | Spatial awareness | Navigation difficulty |'
                ),
            },
            {
                'slug': 'dementia-basics-normal-vs-dementia',
                'category': 'dementia-basics',
                'order': 3,
                'duration': 4,
                'title_tr': 'Normal Unutkanlik mi, Demans mi?',
                'title_en': 'Normal Forgetfulness or Dementia?',
                'body_tr': (
                    '## Normal Yaslanma vs. Demans\n\n'
                    'Yas ilerledikce hafif unutkanlik normaldir. Ancak demans bundan cok farklidir.\n\n'
                    '### Karsilastirma Tablosu\n\n'
                    '| Normal Yaslanma | Demans Belirtisi |\n'
                    '|---|---|\n'
                    '| Anahtar nereye koydugunuzu unutmak | Anahtarin ne ise yaradigini unutmak |\n'
                    '| Bir ismi gecici olarak hatirlayamamak | Yakin aile uyelerini taniyamamak |\n'
                    '| Randevuyu kacirup sonra hatirlamak | Randevulari surekli unutmak |\n'
                    '| Ara sira hesaplama hatasi yapmak | Basit matematik islemlerini yapamamak |\n'
                    '| TV kumandasini karistirmak | Tanidik ev aletlerini kullanamamak |\n\n'
                    '### Ne Zaman Endiselenilmeli?\n\n'
                    '- Unutkanlik **gunluk yasami** etkiliyor mu?\n'
                    '- Ayni soruyu defalarca soruyor mu?\n'
                    '- Bilinen yollarda kaybolma var mi?\n'
                    '- Kisilik ve davranis degisiklikleri gozleniyor mu?\n\n'
                    '> Bu belirtiler varsa **mutlaka** bir noroloji uzmanina basvurun.'
                ),
                'body_en': (
                    '## Normal Aging vs. Dementia\n\n'
                    'Mild forgetfulness with age is normal. However, dementia is very different.\n\n'
                    '### Comparison Table\n\n'
                    '| Normal Aging | Dementia Symptom |\n'
                    '|---|---|\n'
                    '| Forgetting where you put your keys | Forgetting what keys are for |\n'
                    '| Temporarily not remembering a name | Not recognizing close family |\n'
                    '| Missing an appointment then remembering | Constantly forgetting appointments |\n'
                    '| Occasional calculation mistakes | Unable to do simple math |\n'
                    '| Confusing the TV remote | Unable to use familiar appliances |\n\n'
                    '### When to Worry?\n\n'
                    '- Does forgetfulness affect **daily life**?\n'
                    '- Asking the same question repeatedly?\n'
                    '- Getting lost on familiar routes?\n'
                    '- Personality and behavior changes?\n\n'
                    '> If these signs are present, **always** consult a neurologist.'
                ),
            },
            {
                'slug': 'dementia-basics-risk-factors',
                'category': 'dementia-basics',
                'order': 4,
                'duration': 4,
                'title_tr': 'Risk Faktorleri',
                'title_en': 'Risk Factors',
                'body_tr': (
                    '## Demans Risk Faktorleri\n\n'
                    'Bazi risk faktorleri degistirilemez, ancak bircok faktor yasam tarzi degisiklikleriyle '
                    'kontrol altina alinabilir.\n\n'
                    '### Degistirilemez Faktorler\n\n'
                    '- **Yas:** 65 yas sonrasi risk her 5 yilda iki katina cikar\n'
                    '- **Genetik:** Aile gecmisinde demans olmasi riski arttirir\n'
                    '- **APOE-e4 geni:** Alzheimer riskini 3-12 kat arttirir\n\n'
                    '### Degistirilebilir Faktorler\n\n'
                    '- **Hipertansiyon:** Orta yasta yuksek tansiyon riski %60 arttirir\n'
                    '- **Diyabet:** Tip 2 diyabet riski neredeyse ikiye katlar\n'
                    '- **Sigara:** Damarsal hasar ve oksidatif stres yaratir\n'
                    '- **Fiziksel hareketsizlik:** Duzenli egzersiz riski %30 azaltir\n'
                    '- **Sosyal izolasyon:** Sosyal iliskiler beyni korur\n'
                    '- **Isitme kaybi:** Tedavi edilmemis isitme kaybi onemli risk faktorudur\n'
                    '- **Depresyon:** Kronik depresyon demans riskini arttirir\n\n'
                    '> **Iyi Haber:** Degistirilebilir faktorlere mudahale ederek demans riskinin yaklasik '
                    '**%40\'i** onlenebilir!'
                ),
                'body_en': (
                    '## Dementia Risk Factors\n\n'
                    'Some risk factors cannot be changed, but many can be controlled through lifestyle changes.\n\n'
                    '### Non-Modifiable Factors\n\n'
                    '- **Age:** Risk doubles every 5 years after age 65\n'
                    '- **Genetics:** Family history increases risk\n'
                    '- **APOE-e4 gene:** Increases Alzheimer risk 3-12 fold\n\n'
                    '### Modifiable Factors\n\n'
                    '- **Hypertension:** Midlife high blood pressure increases risk by 60%\n'
                    '- **Diabetes:** Type 2 diabetes nearly doubles the risk\n'
                    '- **Smoking:** Causes vascular damage and oxidative stress\n'
                    '- **Physical inactivity:** Regular exercise reduces risk by 30%\n'
                    '- **Social isolation:** Social connections protect the brain\n'
                    '- **Hearing loss:** Untreated hearing loss is a significant risk factor\n'
                    '- **Depression:** Chronic depression increases dementia risk\n\n'
                    '> **Good News:** By addressing modifiable factors, approximately **40%** of '
                    'dementia cases could be prevented!'
                ),
            },
            {
                'slug': 'dementia-basics-statistics',
                'category': 'dementia-basics',
                'order': 5,
                'duration': 3,
                'title_tr': 'Demans Sayilarla',
                'title_en': 'Dementia in Numbers',
                'body_tr': (
                    '## Turkiye ve Dunyada Demans\n\n'
                    '### Dunya Istatistikleri\n\n'
                    '- **55+ milyon** kisi demansla yasiyor\n'
                    '- Her yil **10 milyon** yeni vaka\n'
                    '- 2050\'de bu sayi **139 milyon** olacak\n'
                    '- Toplam maliyet: Yilda **1.3 trilyon dolar**\n\n'
                    '### Turkiye\'de Durum\n\n'
                    '- Tahmini **600.000 - 1 milyon** demans hastasi\n'
                    '- 65 yas ustu nufusun %6-8\'ini etkiler\n'
                    '- Tani oraninin dusuk oldugu tahmin ediliyor\n'
                    '- Bakim yukunu cogunlukla aile uyeleri tasir\n\n'
                    '### Onemli Gercekler\n\n'
                    '- Kadinlarda gorulme sikligi erkeklere gore daha yuksek\n'
                    '- Bakicilarin %60\'inda stres ve tukenmislik gorulur\n'
                    '- Erken tani ile 5 yila kadar bagimsiz yasam uzatilabilir\n'
                    '- Beyin egzersizleri bilissel gerilemeyi yavaslatir'
                ),
                'body_en': (
                    '## Dementia Worldwide and in Turkey\n\n'
                    '### Global Statistics\n\n'
                    '- **55+ million** people live with dementia\n'
                    '- **10 million** new cases every year\n'
                    '- By 2050, this number will reach **139 million**\n'
                    '- Total cost: **$1.3 trillion** per year\n\n'
                    '### Turkey\n\n'
                    '- Estimated **600,000 - 1 million** dementia patients\n'
                    '- Affects 6-8% of the population over 65\n'
                    '- Diagnosis rates are estimated to be low\n'
                    '- Care burden mostly falls on family members\n\n'
                    '### Key Facts\n\n'
                    '- Women have a higher incidence than men\n'
                    '- 60% of caregivers experience stress and burnout\n'
                    '- Early diagnosis can extend independent living by up to 5 years\n'
                    '- Brain exercises slow cognitive decline'
                ),
            },

            # --- Modul 2: Demans Turleri ---
            {
                'slug': 'dementia-types-alzheimer',
                'category': 'dementia-types',
                'order': 1,
                'duration': 5,
                'title_tr': 'Alzheimer Hastaligi',
                'title_en': 'Alzheimer\'s Disease',
                'body_tr': (
                    '## Alzheimer Hastaligi\n\n'
                    'Alzheimer, tum demans vakalarinin **%60-70**\'ini olusturan en yaygin demans turudur.\n\n'
                    '### Temel Ozellikler\n\n'
                    '- Yavas ve sinsi baslar, yillar icinde ilerler\n'
                    '- Beyinde amiloid plaklar ve tau protein yumaklari birikir\n'
                    '- Ilk belirti genellikle **yakin gecmis hafiza kaybi**dir\n'
                    '- Ortalama sure: Tanidan sonra 8-12 yil\n\n'
                    '### Evreler\n\n'
                    '1. **Erken Evre (2-4 yil):** Hafif unutkanlik, kelime bulma guclugu, planlama sorunlari\n'
                    '2. **Orta Evre (2-10 yil):** Artan unutkanlik, davranis degisiklikleri, gunluk isler icin yardim gereksinimi\n'
                    '3. **Ileri Evre (1-3 yil):** Tam bagimlililk, iletisim kaybi, fiziksel islevlerde azalma\n\n'
                    '> Alzheimer tani ve tedavisinde son yillarda onemli gelismeler kaydedilmektedir. '
                    'Erken tani buyuk oneme sahiptir.'
                ),
                'body_en': (
                    '## Alzheimer\'s Disease\n\n'
                    'Alzheimer\'s is the most common type of dementia, accounting for **60-70%** of all cases.\n\n'
                    '### Key Features\n\n'
                    '- Starts slowly and insidiously, progresses over years\n'
                    '- Amyloid plaques and tau protein tangles accumulate in the brain\n'
                    '- First symptom is usually **recent memory loss**\n'
                    '- Average duration: 8-12 years after diagnosis\n\n'
                    '### Stages\n\n'
                    '1. **Early Stage (2-4 years):** Mild forgetfulness, word-finding difficulty, planning issues\n'
                    '2. **Middle Stage (2-10 years):** Increasing forgetfulness, behavior changes, need help with daily tasks\n'
                    '3. **Late Stage (1-3 years):** Full dependency, loss of communication, physical decline\n\n'
                    '> Significant advances have been made in Alzheimer\'s diagnosis and treatment in recent years. '
                    'Early diagnosis is crucial.'
                ),
            },
            {
                'slug': 'dementia-types-vascular',
                'category': 'dementia-types',
                'order': 2,
                'duration': 4,
                'title_tr': 'Vaskuler Demans',
                'title_en': 'Vascular Dementia',
                'body_tr': (
                    '## Vaskuler Demans\n\n'
                    'Beyin kan damarlarindaki sorunlardan kaynaklanan, **ikinci en yaygin** demans turudur (%15-20).\n\n'
                    '### Nasil Olusur?\n\n'
                    '- Inme (felc) sonrasi beyine yeterli kan gitmez\n'
                    '- Kucuk damar hastaligi beyinde sessiz hasarlara yol acar\n'
                    '- Beyin dokusu oksijensiz kalarak olur\n\n'
                    '### Ayirt Edici Ozellikler\n\n'
                    '- **Basamakli ilerleme:** Ani kotulesme, sonra stabil donem\n'
                    '- Yururme bozuklugu ve denge sorunlari erken gorulur\n'
                    '- Dikkat ve planlama zorlugu (hafiza nispeten korunabilir)\n'
                    '- Duygusal dalgalanmalar sik yasanir\n\n'
                    '### Onleme\n\n'
                    '- Tansiyon kontrolu (%50 risk azalmasi)\n'
                    '- Kolesterol ve seker kontrolu\n'
                    '- Sigara birakmak\n'
                    '- Duzenli fiziksel aktivite'
                ),
                'body_en': (
                    '## Vascular Dementia\n\n'
                    'Caused by problems in brain blood vessels, the **second most common** dementia type (15-20%).\n\n'
                    '### How Does It Develop?\n\n'
                    '- After a stroke, insufficient blood reaches the brain\n'
                    '- Small vessel disease causes silent brain damage\n'
                    '- Brain tissue dies from lack of oxygen\n\n'
                    '### Distinguishing Features\n\n'
                    '- **Stepwise progression:** Sudden decline, then stable period\n'
                    '- Walking and balance problems appear early\n'
                    '- Attention and planning difficulty (memory relatively preserved)\n'
                    '- Emotional fluctuations are common\n\n'
                    '### Prevention\n\n'
                    '- Blood pressure control (50% risk reduction)\n'
                    '- Cholesterol and blood sugar control\n'
                    '- Quit smoking\n'
                    '- Regular physical activity'
                ),
            },
            {
                'slug': 'dementia-types-lewy',
                'category': 'dementia-types',
                'order': 3,
                'duration': 4,
                'title_tr': 'Lewy Cisimcikli Demans',
                'title_en': 'Lewy Body Dementia',
                'body_tr': (
                    '## Lewy Cisimcikli Demans (LCD)\n\n'
                    'Beyinde alfa-sinuklein proteini birikimi sonucu gelisen, **ucuncu en yaygin** demans turudur.\n\n'
                    '### Belirgin Ozellikleri\n\n'
                    '- **Dalgalanan bilissel durum:** Iyi ve kotu gunler, hatta saatler arasi degisim\n'
                    '- **Gorsel halusinasyonlar:** Canli, ayrintili goruntuler gorme (kisi, hayvan)\n'
                    '- **Parkinsonizm:** Kas serti, titreme, yavas hareket\n'
                    '- **REM uyku bozuklugu:** Uykuda hareket etme, bagirma\n\n'
                    '### Dikkat Edilmesi Gerekenler\n\n'
                    '- Bazi ilaclar (antipsikotikler) **tehlikeli** olabilir\n'
                    '- Alzheimer\'dan farkli olarak hafiza kaybi ilk belirti olmayabilir\n'
                    '- Gorsel-mekansal yetenekler erken bozulur\n'
                    '- Parkinson hastaligi ile yakin iliskilidir'
                ),
                'body_en': (
                    '## Lewy Body Dementia (LBD)\n\n'
                    'Develops from accumulation of alpha-synuclein protein in the brain, the **third most common** type.\n\n'
                    '### Key Features\n\n'
                    '- **Fluctuating cognition:** Good and bad days, even hour-to-hour changes\n'
                    '- **Visual hallucinations:** Vivid, detailed visual experiences (people, animals)\n'
                    '- **Parkinsonism:** Muscle rigidity, tremor, slow movement\n'
                    '- **REM sleep disorder:** Acting out dreams, shouting during sleep\n\n'
                    '### Important Considerations\n\n'
                    '- Some medications (antipsychotics) can be **dangerous**\n'
                    '- Unlike Alzheimer\'s, memory loss may not be the first symptom\n'
                    '- Visual-spatial abilities deteriorate early\n'
                    '- Closely related to Parkinson\'s disease'
                ),
            },
            {
                'slug': 'dementia-types-frontotemporal',
                'category': 'dementia-types',
                'order': 4,
                'duration': 4,
                'title_tr': 'Frontotemporal Demans',
                'title_en': 'Frontotemporal Dementia',
                'body_tr': (
                    '## Frontotemporal Demans (FTD)\n\n'
                    'Beynin on (frontal) ve yan (temporal) loplarina etki eder. Genellikle **45-65 yas** '
                    'arasinda baslar, genc basta demans sebebidir.\n\n'
                    '### Uc Ana Alt Tipi\n\n'
                    '1. **Davranissal FTD:** Kisilik degisikligi, sosyal kurallari ihmal, durtuselluk\n'
                    '2. **Semantik demans:** Kelimelerin anlamini kaybetme\n'
                    '3. **Progresif afazi:** Konusma ve dil uretiminde bozulma\n\n'
                    '### Ayirt Edici Ozellikler\n\n'
                    '- Hafiza genellikle **korunur** (basta)\n'
                    '- **Kisilik degisiklikleri** on planda\n'
                    '- Empati kaybi, uygunsuz davranislar\n'
                    '- Yeme aliskanliklari degisir (asiri yeme, tatli duskumlugu)\n'
                    '- Tekrarlayici davranislar ve rituel olusturma\n\n'
                    '> Genc yasta baslayan demans semptomlarinda FTD mutlaka dusunulmelidir.'
                ),
                'body_en': (
                    '## Frontotemporal Dementia (FTD)\n\n'
                    'Affects the front (frontal) and side (temporal) lobes of the brain. Usually starts '
                    'between **ages 45-65**, a cause of young-onset dementia.\n\n'
                    '### Three Main Subtypes\n\n'
                    '1. **Behavioral FTD:** Personality changes, ignoring social norms, impulsivity\n'
                    '2. **Semantic dementia:** Loss of word meaning\n'
                    '3. **Progressive aphasia:** Deterioration in speech production\n\n'
                    '### Distinguishing Features\n\n'
                    '- Memory is usually **preserved** (initially)\n'
                    '- **Personality changes** are prominent\n'
                    '- Loss of empathy, inappropriate behavior\n'
                    '- Eating habits change (overeating, sweet cravings)\n'
                    '- Repetitive behaviors and ritual formation\n\n'
                    '> FTD should always be considered in young-onset dementia symptoms.'
                ),
            },
            {
                'slug': 'dementia-types-other',
                'category': 'dementia-types',
                'order': 5,
                'duration': 4,
                'title_tr': 'Diger Demans Turleri ve Karisik Demans',
                'title_en': 'Other Types & Mixed Dementia',
                'body_tr': (
                    '## Diger Demans Turleri\n\n'
                    '### Karisik Demans\n\n'
                    'Birden fazla demans turunun birlikte gorulmesidir. Ozellikle Alzheimer + vaskuler '
                    'demans kombinasyonu yaygindi. Otopsi calismalarinda vakalarin **%50\'sinden fazlasinda** '
                    'karisik patoloji saptanmistir.\n\n'
                    '### Nadir Gorulen Turler\n\n'
                    '- **Posterior kortikal atrofi:** Gorsel-mekansal problemler on planda\n'
                    '- **Huntington hastaligi:** Genetik, hareket bozukluklariyla birlikte\n'
                    '- **Creutzfeldt-Jakob hastaligi:** Hizli seyir, prion kaynakli\n'
                    '- **Normal basinc hidrosefalisi:** Tedavi edilebilir; yurume bozuklugu + idrar kacirma + demans\n\n'
                    '### Geri Donusturulebilenler\n\n'
                    'Bazi durumlar demans benzeri belirtiler verir ama **tedavi edilebilir**:\n\n'
                    '- Vitamin B12 eksikligi\n'
                    '- Tiroid fonksiyon bozukluklari\n'
                    '- Depresyon (psoddemans)\n'
                    '- Normal basinc hidrosefalisi\n'
                    '- Ilac yan etkileri\n\n'
                    '> Bu nedenle demans benzeri belirtilerde kapsamli bir tibbi degerlendirme **sart**tir.'
                ),
                'body_en': (
                    '## Other Types of Dementia\n\n'
                    '### Mixed Dementia\n\n'
                    'Two or more types occurring together. The Alzheimer + vascular dementia combination '
                    'is especially common. Autopsy studies found mixed pathology in **over 50%** of cases.\n\n'
                    '### Rare Types\n\n'
                    '- **Posterior cortical atrophy:** Visual-spatial problems prominent\n'
                    '- **Huntington\'s disease:** Genetic, with movement disorders\n'
                    '- **Creutzfeldt-Jakob disease:** Rapid progression, prion-caused\n'
                    '- **Normal pressure hydrocephalus:** Treatable; gait + incontinence + dementia\n\n'
                    '### Reversible Conditions\n\n'
                    'Some conditions mimic dementia but are **treatable**:\n\n'
                    '- Vitamin B12 deficiency\n'
                    '- Thyroid disorders\n'
                    '- Depression (pseudodementia)\n'
                    '- Normal pressure hydrocephalus\n'
                    '- Medication side effects\n\n'
                    '> This is why comprehensive medical evaluation is **essential** for dementia-like symptoms.'
                ),
            },

            # --- Modul 3: Erken Belirtiler ve Uyari Isareti ---
            {
                'slug': 'dementia-signs-10-warnings',
                'category': 'dementia-signs',
                'order': 1,
                'duration': 5,
                'title_tr': 'Demansın 10 Uyari Isareti',
                'title_en': '10 Warning Signs of Dementia',
                'body_tr': (
                    '## Demans Icin 10 Kritik Uyari Isareti\n\n'
                    '1. **Hafiza kaybi:** Yeni ogrenilen bilgilerin unutulmasi, onemli tarihlerin hatirlanaması\n'
                    '2. **Planlama guclugu:** Faturalari odeme, yemek tarifi takip etme sorunlari\n'
                    '3. **Alisilmis isleri tamamlayamama:** Tanidik gorevlerde zorlanma\n'
                    '4. **Zaman ve yer kafa karisikligi:** Tarihleri, mevsimleri karistirma\n'
                    '5. **Gorsel-mekansal algi sorunlari:** Mesafe tahmininde zorluk, renk ayirt etmede gucluk\n'
                    '6. **Kelime bulma guclugu:** Konusma ortasinda durma, yanlis kelime kullanma\n'
                    '7. **Esyalari kaybetme:** Esyalari alisilagelmadik yerlere koyma\n'
                    '8. **Karar verme bozuklugu:** Parayla ilgili kotu kararlar, kisisel bakimi ihmal\n'
                    '9. **Sosyal cekilme:** Hobilerden, sosyal aktivitelerden uzaklasma\n'
                    '10. **Ruh hali degisiklikleri:** Supheci, kaygi, depresyon, uygunsuz duygusal tepkiler\n\n'
                    '> Bu belirtilerden **iki veya daha fazlasi** varsa bir uzmana basvurun.'
                ),
                'body_en': (
                    '## 10 Critical Warning Signs of Dementia\n\n'
                    '1. **Memory loss:** Forgetting newly learned information, important dates\n'
                    '2. **Planning difficulty:** Problems with bills, following recipes\n'
                    '3. **Inability to complete familiar tasks:** Difficulty with known activities\n'
                    '4. **Time and place confusion:** Mixing up dates, seasons\n'
                    '5. **Visual-spatial perception issues:** Difficulty judging distance, distinguishing colors\n'
                    '6. **Word-finding difficulty:** Stopping mid-conversation, using wrong words\n'
                    '7. **Misplacing items:** Putting things in unusual places\n'
                    '8. **Poor judgment:** Bad financial decisions, neglecting personal care\n'
                    '9. **Social withdrawal:** Pulling away from hobbies, social activities\n'
                    '10. **Mood changes:** Suspicious, anxious, depressed, inappropriate emotional reactions\n\n'
                    '> If **two or more** of these signs are present, consult a specialist.'
                ),
            },
            {
                'slug': 'dementia-signs-memory-changes',
                'category': 'dementia-signs',
                'order': 2,
                'duration': 4,
                'title_tr': 'Hafiza Degisikliklerini Anlamak',
                'title_en': 'Understanding Memory Changes',
                'body_tr': (
                    '## Hafiza Turleri ve Demans\n\n'
                    '### Hafiza Turleri\n\n'
                    '- **Epizodik hafiza:** Kisisel deneyimler (dun ne yediginiz) - *En erken etkilenen*\n'
                    '- **Semantik hafiza:** Genel bilgiler (baskentin adi) - *Daha gec etkilenir*\n'
                    '- **Prosedural hafiza:** Motor beceriler (bisiklet surme) - *En son etkilenen*\n'
                    '- **Calisma hafizasi:** Anlik bilgi isleme (telefon numarasi tutma)\n\n'
                    '### Demansta Hafiza Degisimi Sureci\n\n'
                    '1. Yeni bilgi kaydetme zorlasir\n'
                    '2. Yakin gecmis hatiralari kaybolur\n'
                    '3. Uzak gecmis (cocukluk) daha uzun korunur\n'
                    '4. Tanidik yuzleri tanimada zorluk baslar\n'
                    '5. Ilerleyen evrelerde kimlik bilinci etkilenir\n\n'
                    '### Ipuclari ve Teknikler\n\n'
                    '- Ajanda ve takvim kullanin\n'
                    '- Gunluk rutinler olusturun\n'
                    '- Hatirlama ipuclari (fotograflar, notlar) kullanin\n'
                    '- Onemli bilgileri gorunur yerlere yapin'
                ),
                'body_en': (
                    '## Memory Types and Dementia\n\n'
                    '### Types of Memory\n\n'
                    '- **Episodic memory:** Personal experiences (what you ate yesterday) - *Earliest affected*\n'
                    '- **Semantic memory:** General knowledge (capital city) - *Affected later*\n'
                    '- **Procedural memory:** Motor skills (riding a bicycle) - *Last affected*\n'
                    '- **Working memory:** Immediate information processing (holding a phone number)\n\n'
                    '### Memory Change Process in Dementia\n\n'
                    '1. Difficulty recording new information\n'
                    '2. Recent memories fade\n'
                    '3. Distant past (childhood) is preserved longer\n'
                    '4. Difficulty recognizing familiar faces begins\n'
                    '5. In advanced stages, identity awareness is affected\n\n'
                    '### Tips and Techniques\n\n'
                    '- Use planners and calendars\n'
                    '- Create daily routines\n'
                    '- Use memory cues (photos, notes)\n'
                    '- Place important information in visible locations'
                ),
            },
            {
                'slug': 'dementia-signs-behavior-changes',
                'category': 'dementia-signs',
                'order': 3,
                'duration': 4,
                'title_tr': 'Davranis ve Kisilik Degisiklikleri',
                'title_en': 'Behavior and Personality Changes',
                'body_tr': (
                    '## Demansta Davranis Degisiklikleri\n\n'
                    'Bilissel kaybin yaninda davranissal ve psikolojik belirtiler de demansin onemli bir '
                    'parcasidir.\n\n'
                    '### Sik Gorulen Degisiklikler\n\n'
                    '- **Apati:** Ilgisizlik, motivasyon kaybi (en yaygin belirti)\n'
                    '- **Ajitasyon:** Huzursuzluk, sinirlilik, agresyon\n'
                    '- **Kaygi ve korku:** Yalniz kalma korkusu, panik ataklar\n'
                    '- **Depresyon:** Uzuntu, umutsuzluk, yasam sevinci kaybi\n'
                    '- **Sundowning:** Aksam saatlerinde artan kafa karisikligi ve huzursuzluk\n'
                    '- **Tekrarlayici davranislar:** Ayni soruyu sorma, ayni hareketi yapma\n\n'
                    '### Aile Icin Rehber\n\n'
                    '- Degisikliklerin **hastalik kaynakli** oldugunu hatirlatin\n'
                    '- Tartisma veya duzeltme yerine **yonlendirme** yapin\n'
                    '- Guvenli ve sakin bir ortam saglayin\n'
                    '- Tetikleyicileri (yorgunluk, gurultu) belirlemeye calisin\n'
                    '- Kendinize de bakmak icin destek alin'
                ),
                'body_en': (
                    '## Behavioral Changes in Dementia\n\n'
                    'Alongside cognitive decline, behavioral and psychological symptoms are an important '
                    'part of dementia.\n\n'
                    '### Common Changes\n\n'
                    '- **Apathy:** Lack of interest, loss of motivation (most common symptom)\n'
                    '- **Agitation:** Restlessness, irritability, aggression\n'
                    '- **Anxiety and fear:** Fear of being alone, panic attacks\n'
                    '- **Depression:** Sadness, hopelessness, loss of joy\n'
                    '- **Sundowning:** Increased confusion and restlessness in evening hours\n'
                    '- **Repetitive behaviors:** Asking the same question, repeating actions\n\n'
                    '### Guide for Families\n\n'
                    '- Remember that changes are **caused by the disease**\n'
                    '- **Redirect** instead of arguing or correcting\n'
                    '- Provide a safe and calm environment\n'
                    '- Try to identify triggers (fatigue, noise)\n'
                    '- Seek support for your own well-being'
                ),
            },
            {
                'slug': 'dementia-signs-when-to-see-doctor',
                'category': 'dementia-signs',
                'order': 4,
                'duration': 4,
                'title_tr': 'Ne Zaman Doktora Gitmeli?',
                'title_en': 'When to See a Doctor?',
                'body_tr': (
                    '## Doktora Basvuru Zamani\n\n'
                    '### Hemen Basvurun Eger:\n\n'
                    '- Unutkanlik **son 6 ayda belirgin** arttiysa\n'
                    '- **Gunluk isler** (yemek yapma, alisveris) aksiyorsa\n'
                    '- Bilinen yollarda **kaybolma** yasandiysa\n'
                    '- **Kisilik degisiklikleri** cevre tarafindan fark edildiyse\n'
                    '- **Ilac yonetimi** yapilamiyorsa\n'
                    '- **Mali kararlar** bozulduysa\n\n'
                    '### Hangi Doktora Gidilir?\n\n'
                    '- **Noroloji uzmani:** Birincil basvuru\n'
                    '- **Geriatri uzmani:** 65 yas ustu hastalar icin\n'
                    '- **Psikiyatri uzmani:** Davranissal belirtiler on plandaysa\n'
                    '- **Hafiza klinikleri:** Multidisipliner degerlendirme\n\n'
                    '### Ziyaret Oncesi Hazirlik\n\n'
                    '- Belirtilerin ne zaman basladigini not edin\n'
                    '- Kullanilan tum ilaclarin listesini getirin\n'
                    '- Mumkunse bir yakinla birlikte gidin\n'
                    '- Gunluk yasam ornekleri ile anlatim yapin'
                ),
                'body_en': (
                    '## Time to See a Doctor\n\n'
                    '### Seek help immediately if:\n\n'
                    '- Forgetfulness has **significantly increased in the last 6 months**\n'
                    '- **Daily activities** (cooking, shopping) are disrupted\n'
                    '- **Getting lost** on familiar routes\n'
                    '- **Personality changes** noticed by others\n'
                    '- **Medication management** has become impossible\n'
                    '- **Financial decisions** have deteriorated\n\n'
                    '### Which Doctor to Visit?\n\n'
                    '- **Neurologist:** Primary referral\n'
                    '- **Geriatrician:** For patients over 65\n'
                    '- **Psychiatrist:** When behavioral symptoms are prominent\n'
                    '- **Memory clinics:** Multidisciplinary assessment\n\n'
                    '### Before Your Visit\n\n'
                    '- Note when symptoms started\n'
                    '- Bring a list of all medications\n'
                    '- Go with a family member if possible\n'
                    '- Describe with daily life examples'
                ),
            },
            {
                'slug': 'dementia-signs-progression',
                'category': 'dementia-signs',
                'order': 5,
                'duration': 4,
                'title_tr': 'Hastalik Ilerleme Sureci',
                'title_en': 'Disease Progression',
                'body_tr': (
                    '## Demans Nasil Ilerler?\n\n'
                    '### Genel Ilerleme Evreleri\n\n'
                    '**Erken Evre:**\n'
                    '- Hafif unutkanlik, tarihleri karistirma\n'
                    '- Is ve sosyal yasam henuz surdurulebilir\n'
                    '- Kisi durumun farkinda olabilir\n\n'
                    '**Orta Evre:**\n'
                    '- Gunluk isler icin yardim gerekir\n'
                    '- Gece-gunduz karisikligi\n'
                    '- Kaybolma, dolasmma davranisi\n'
                    '- Iletisim zorlasiyor\n\n'
                    '**Ileri Evre:**\n'
                    '- Tam bagimlililk\n'
                    '- Yutma guclugu, enfeksiyon riski\n'
                    '- Iletisim minimuma iniyor\n'
                    '- Fiziksel bakim gereksinimleri artiyor\n\n'
                    '### Onemli Not\n\n'
                    'Her hasta farkli ilerler. Bazi kisilerde yavaslatmak mumkundur:\n'
                    '- Bilissel stimulasyon (beyin egzersizleri)\n'
                    '- Fiziksel aktivite\n'
                    '- Sosyal etkilesim\n'
                    '- Uygun medikal tedavi\n'
                    '- Iyi beslenme ve uyku duzeni'
                ),
                'body_en': (
                    '## How Does Dementia Progress?\n\n'
                    '### General Progression Stages\n\n'
                    '**Early Stage:**\n'
                    '- Mild forgetfulness, date confusion\n'
                    '- Work and social life still manageable\n'
                    '- Person may be aware of the condition\n\n'
                    '**Middle Stage:**\n'
                    '- Help needed for daily tasks\n'
                    '- Day-night confusion\n'
                    '- Wandering behavior, getting lost\n'
                    '- Communication becomes difficult\n\n'
                    '**Late Stage:**\n'
                    '- Full dependency\n'
                    '- Swallowing difficulty, infection risk\n'
                    '- Communication minimized\n'
                    '- Increased physical care needs\n\n'
                    '### Important Note\n\n'
                    'Every patient progresses differently. Slowing is possible with:\n'
                    '- Cognitive stimulation (brain exercises)\n'
                    '- Physical activity\n'
                    '- Social interaction\n'
                    '- Appropriate medical treatment\n'
                    '- Good nutrition and sleep'
                ),
            },

            # --- Modul 4: Tani ve Degerlendirme ---
            {
                'slug': 'dementia-diagnosis-process',
                'category': 'dementia-diagnosis',
                'order': 1,
                'duration': 5,
                'title_tr': 'Tani Sureci Nasil Isler?',
                'title_en': 'How Does Diagnosis Work?',
                'body_tr': (
                    '## Demans Tani Sureci\n\n'
                    'Demans tanisi cok yonlu bir degerlendirme gerektirir.\n\n'
                    '### Tani Adimlari\n\n'
                    '1. **Detayli oykü:** Hasta ve yakinindan belirtilerin seyri\n'
                    '2. **Norolojik muayene:** Refleksler, motor beceriler, duyu degerlendirmesi\n'
                    '3. **Bilissel testler:** MMSE, MoCA, saat cizme testi\n'
                    '4. **Kan testleri:** B12, tiroid, karaciger, bobrek, seker\n'
                    '5. **Beyin goruntuleme:** MRI (yapisal), PET (islevsel)\n'
                    '6. **Ek testler:** EEG, BOS analizi (gerektiginde)\n\n'
                    '### Tani Kriterleri\n\n'
                    '- En az **iki bilissel alanda** bozulma\n'
                    '- Gunluk **islevsellikte** azalma\n'
                    '- Diger nedenlerin (depresyon, deliryum) dislanmasi\n'
                    '- Belirtilerin en az **6 ay** surmesi\n\n'
                    '> Erken ve dogru tani, tedavi plani ve gelecek planlamasi icin kritik oneme sahiptir.'
                ),
                'body_en': (
                    '## Dementia Diagnosis Process\n\n'
                    'Dementia diagnosis requires a multi-faceted evaluation.\n\n'
                    '### Diagnostic Steps\n\n'
                    '1. **Detailed history:** Course of symptoms from patient and caregiver\n'
                    '2. **Neurological exam:** Reflexes, motor skills, sensory assessment\n'
                    '3. **Cognitive tests:** MMSE, MoCA, clock drawing test\n'
                    '4. **Blood tests:** B12, thyroid, liver, kidney, glucose\n'
                    '5. **Brain imaging:** MRI (structural), PET (functional)\n'
                    '6. **Additional tests:** EEG, CSF analysis (if needed)\n\n'
                    '### Diagnostic Criteria\n\n'
                    '- Impairment in at least **two cognitive domains**\n'
                    '- Decline in daily **functioning**\n'
                    '- Exclusion of other causes (depression, delirium)\n'
                    '- Symptoms lasting at least **6 months**\n\n'
                    '> Early and accurate diagnosis is critical for treatment planning and future preparations.'
                ),
            },
            {
                'slug': 'dementia-diagnosis-cognitive-tests',
                'category': 'dementia-diagnosis',
                'order': 2,
                'duration': 5,
                'title_tr': 'Bilissel Tarama Testleri',
                'title_en': 'Cognitive Screening Tests',
                'body_tr': (
                    '## Bilissel Tarama ve Degerlendirme Testleri\n\n'
                    '### Klinik Tarama Testleri\n\n'
                    '**Mini Mental Durum Testi (MMSE):**\n'
                    '- 30 puan uzerinden degerlendirilir\n'
                    '- Oryantasyon, kayit, dikkat, hatirlama, dil alanlarini olcer\n'
                    '- 24 alti skup suphelidir\n\n'
                    '**Montreal Bilissel Degerlendirme (MoCA):**\n'
                    '- 30 puan, MMSE\'den daha hassas\n'
                    '- Yurutme islevi, gorsel-mekansal yetiler de test edilir\n'
                    '- 26 alti skup suphelidir\n\n'
                    '**Saat Cizme Testi:**\n'
                    '- Basit ama cok bilgilendirici\n'
                    '- Gorsel-mekansal yetiyi, planlamayi ve sayisal anlayisi olcer\n\n'
                    '### Norosera Bilissel Tarama\n\n'
                    'Bu uygulamada sunulan tarama testi 5 bilissel alani degerlendirir:\n'
                    '- Oryantasyon (zaman ve yer farkindailigi)\n'
                    '- Hafiza (kisa sureli bellek)\n'
                    '- Dikkat (odaklanma ve konsantrasyon)\n'
                    '- Dil (isimlendirme ve anlama)\n'
                    '- Yurutme islevi (planlama ve problem cozme)\n\n'
                    '> Bu testler **tani koyma araci degildir**, ancak uzman degerlendirmesi icin yol gostericidir.'
                ),
                'body_en': (
                    '## Cognitive Screening and Assessment Tests\n\n'
                    '### Clinical Screening Tests\n\n'
                    '**Mini-Mental State Examination (MMSE):**\n'
                    '- Scored out of 30\n'
                    '- Measures orientation, registration, attention, recall, language\n'
                    '- Score below 24 is suspicious\n\n'
                    '**Montreal Cognitive Assessment (MoCA):**\n'
                    '- 30 points, more sensitive than MMSE\n'
                    '- Also tests executive function, visuospatial abilities\n'
                    '- Score below 26 is suspicious\n\n'
                    '**Clock Drawing Test:**\n'
                    '- Simple but very informative\n'
                    '- Measures visuospatial ability, planning, and numerical understanding\n\n'
                    '### Norosera Cognitive Screening\n\n'
                    'The screening test in this app evaluates 5 cognitive domains:\n'
                    '- Orientation (time and place awareness)\n'
                    '- Memory (short-term memory)\n'
                    '- Attention (focus and concentration)\n'
                    '- Language (naming and comprehension)\n'
                    '- Executive function (planning and problem solving)\n\n'
                    '> These tests are **not diagnostic tools**, but guide specialist evaluation.'
                ),
            },
            {
                'slug': 'dementia-diagnosis-frontal-tests',
                'category': 'dementia-diagnosis',
                'order': 3,
                'duration': 5,
                'title_tr': 'Frontal Lob Testleri ve Unutkanlık Degerlendirmesi',
                'title_en': 'Frontal Lobe Tests & Forgetfulness Assessment',
                'body_tr': (
                    '## Frontal Lob Islevlerini Degerlendirme\n\n'
                    'Frontal lob, beynimizin "yonetici merkezi"dir. Planlama, karar verme, durtü kontrolu '
                    've sosyal davranislari yonetir.\n\n'
                    '### Frontal Degerlendirme Bataryasi (FAB)\n\n'
                    '6 alt testten olusur:\n'
                    '1. **Benzerlikler:** Soyut dusunce (muz-portakal arasi benzerlik)\n'
                    '2. **Sozel akicilik:** 1 dakikada hayvan ismi sayma\n'
                    '3. **Motor seriler:** El sira hareketleri (yumruk-kenar-duz)\n'
                    '4. **Catisma talimatlari:** Karsi talimata uyma (ben 1 vurursam sen 2 vur)\n'
                    '5. **Git-Gitme:** Durtü kontrolu\n'
                    '6. **Kavrama refleksi:** Primitif refleks varliginin kontrolu\n\n'
                    '### Unutkanlik Degerlendirme Ipuclari\n\n'
                    '**Kendinize Sorun:**\n'
                    '- Alisveris listesi olmadan market alisverisi yapabiliyor musunuz?\n'
                    '- Tanidik insanlarin isimlerini hatirliyor musunuz?\n'
                    '- Dun aksam ne yediginizi hatirliyorsunuz?\n'
                    '- Randevularinizi takip edebiliyor musunuz?\n'
                    '- Para ustu hesaplayabiliyor musunuz?\n\n'
                    '> Bu uygulamadaki bilissel egzersizler frontal lob islevlerini guclendirmeye yardimci olur.'
                ),
                'body_en': (
                    '## Assessing Frontal Lobe Functions\n\n'
                    'The frontal lobe is our brain\'s "executive center." It manages planning, decision-making, '
                    'impulse control, and social behavior.\n\n'
                    '### Frontal Assessment Battery (FAB)\n\n'
                    'Consists of 6 subtests:\n'
                    '1. **Similarities:** Abstract thinking (banana-orange similarity)\n'
                    '2. **Verbal fluency:** Naming animals in 1 minute\n'
                    '3. **Motor series:** Hand sequence (fist-edge-palm)\n'
                    '4. **Conflicting instructions:** Following opposite commands\n'
                    '5. **Go-No Go:** Impulse control\n'
                    '6. **Grasp reflex:** Checking for primitive reflexes\n\n'
                    '### Forgetfulness Assessment Tips\n\n'
                    '**Ask Yourself:**\n'
                    '- Can you shop without a list?\n'
                    '- Do you remember familiar people\'s names?\n'
                    '- Do you remember what you ate last night?\n'
                    '- Can you track your appointments?\n'
                    '- Can you calculate change?\n\n'
                    '> Cognitive exercises in this app help strengthen frontal lobe functions.'
                ),
            },
            {
                'slug': 'dementia-diagnosis-imaging',
                'category': 'dementia-diagnosis',
                'order': 4,
                'duration': 4,
                'title_tr': 'Beyin Goruntuleme Yontemleri',
                'title_en': 'Brain Imaging Methods',
                'body_tr': (
                    '## Demansta Beyin Goruntuleme\n\n'
                    '### MRI (Manyetik Rezonans Goruntuleme)\n\n'
                    '- **Amac:** Beyin yapisini detayli gostermek\n'
                    '- Hipokampus atrofisi (kuculme) gorulur\n'
                    '- Vaskuler lezyonlar ve inme izleri saptanir\n'
                    '- Tumor gibi diger nedenleri dislar\n\n'
                    '### PET (Pozitron Emisyon Tomografisi)\n\n'
                    '- **Amiloid PET:** Beyindeki amiloid plak birikimini gosterir\n'
                    '- **FDG-PET:** Beyin metabolizma haritasi cikarir\n'
                    '- **Tau PET:** Tau protein dagiliminı gosterir\n\n'
                    '### BT (Bilgisayarli Tomografi)\n\n'
                    '- Hizli, kolay erisilen yontem\n'
                    '- Buyuk yapisal sorunlari (kanama, tumor) gosterir\n'
                    '- MRI kadar detayli degildir\n\n'
                    '### Goruntuleme Ne Zaman Gerekli?\n\n'
                    '- Ilk demans degerlendirmesinde mutlaka\n'
                    '- Ani veya beklenmedik kotulesmelerde\n'
                    '- Tani belirsizliginde ayirici tani icin\n'
                    '- Tedavi yanitini degerlendirmede'
                ),
                'body_en': (
                    '## Brain Imaging in Dementia\n\n'
                    '### MRI (Magnetic Resonance Imaging)\n\n'
                    '- **Purpose:** Show detailed brain structure\n'
                    '- Hippocampal atrophy (shrinkage) visible\n'
                    '- Vascular lesions and stroke signs detected\n'
                    '- Rules out other causes like tumors\n\n'
                    '### PET (Positron Emission Tomography)\n\n'
                    '- **Amyloid PET:** Shows amyloid plaque buildup\n'
                    '- **FDG-PET:** Maps brain metabolism\n'
                    '- **Tau PET:** Shows tau protein distribution\n\n'
                    '### CT (Computed Tomography)\n\n'
                    '- Fast, easily accessible method\n'
                    '- Shows major structural issues (bleeding, tumor)\n'
                    '- Not as detailed as MRI\n\n'
                    '### When Is Imaging Needed?\n\n'
                    '- Always in initial dementia evaluation\n'
                    '- With sudden or unexpected deterioration\n'
                    '- For differential diagnosis when uncertain\n'
                    '- In evaluating treatment response'
                ),
            },
            {
                'slug': 'dementia-diagnosis-blood-tests',
                'category': 'dementia-diagnosis',
                'order': 5,
                'duration': 3,
                'title_tr': 'Kan Testleri ve Laboratuvar Degerlendirmesi',
                'title_en': 'Blood Tests and Lab Evaluation',
                'body_tr': (
                    '## Demans Tanisinda Kan Testleri\n\n'
                    'Kan testleri, tedavi edilebilir nedenleri dismak icin zorunludur.\n\n'
                    '### Temel Testler\n\n'
                    '| Test | Amac |\n'
                    '|---|---|\n'
                    '| Tam kan sayimi | Anemi, enfeksiyon |\n'
                    '| B12 vitamini | Eksikligi demans benzeri tabloya neden olur |\n'
                    '| Folik asit | B12 ile birlikte degerlendirilir |\n'
                    '| Tiroid islevleri | Hipotiroidi bilissel yavashlamaya yol acar |\n'
                    '| Aclik seker, HbA1c | Diyabet demans riskini arttirir |\n'
                    '| Karaciger-bobrek | Metabolik nedenleri dislar |\n'
                    '| Kalsiyum | Kalsiyum bozukluklari bilinc degisikliklerine yol acar |\n'
                    '| Sifiliz serolojisi | Nadir ama tedavi edilebilir neden |\n\n'
                    '### Yeni Biyobelirtecler\n\n'
                    '- **Plazma amiloid:** Kan testiyle Alzheimer ongorusu (gelismekte)\n'
                    '- **P-tau 217:** Erken Alzheimer saptamada umut verici\n'
                    '- **Nörofilaman hafif zincir (NfL):** Noronal hasari gosteren belirtec\n\n'
                    '> Kan testlerinde **B12 ve tiroid** sonuclari ozellikle onemlidir; '
                    'duzeltilmeleri belirtileri tersine cevirebilir.'
                ),
                'body_en': (
                    '## Blood Tests in Dementia Diagnosis\n\n'
                    'Blood tests are mandatory to exclude treatable causes.\n\n'
                    '### Essential Tests\n\n'
                    '| Test | Purpose |\n'
                    '|---|---|\n'
                    '| Complete blood count | Anemia, infection |\n'
                    '| Vitamin B12 | Deficiency causes dementia-like symptoms |\n'
                    '| Folic acid | Evaluated together with B12 |\n'
                    '| Thyroid function | Hypothyroidism causes cognitive slowing |\n'
                    '| Fasting glucose, HbA1c | Diabetes increases dementia risk |\n'
                    '| Liver-kidney | Excludes metabolic causes |\n'
                    '| Calcium | Calcium disorders cause consciousness changes |\n'
                    '| Syphilis serology | Rare but treatable cause |\n\n'
                    '### New Biomarkers\n\n'
                    '- **Plasma amyloid:** Blood-based Alzheimer prediction (developing)\n'
                    '- **P-tau 217:** Promising for early Alzheimer detection\n'
                    '- **Neurofilament light chain (NfL):** Marker for neuronal damage\n\n'
                    '> **B12 and thyroid** results are especially important; '
                    'correction may reverse symptoms.'
                ),
            },

            # --- Modul 5: Bakim, Destek ve Yasam Kalitesi ---
            {
                'slug': 'dementia-care-caregiver-guide',
                'category': 'dementia-care',
                'order': 1,
                'duration': 5,
                'title_tr': 'Bakici Rehberi: Temel Ilkeler',
                'title_en': 'Caregiver Guide: Basic Principles',
                'body_tr': (
                    '## Demans Bakici Rehberi\n\n'
                    '### Altin Kurallar\n\n'
                    '1. **Sabir ve anlayis:** Hastalik kaynakli davranislara karsı\n'
                    '2. **Rutin olusturun:** Duzenli program guvenlik hissi yaratir\n'
                    '3. **Basite indirgeyin:** Tek adimli talimatlar verin\n'
                    '4. **Secenekler sunun:** "Ne giymek istersin?" yerine iki secenek gosterin\n'
                    '5. **Guvenligi saglayin:** Ev icinde dusme, yanma, kaybolma risklerini azaltin\n\n'
                    '### Iletisim Teknikleri\n\n'
                    '- Goz temasi kurun ve yavas konusun\n'
                    '- Kisa, net cumleler kullanin\n'
                    '- Dokunarak iletisimi destekleyin\n'
                    '- Duzeltme yerine onaylama yapin\n'
                    '- "Hatirliyor musun?" sorusundan kacinin\n\n'
                    '### Bakicinin Bakimi\n\n'
                    'Bakicilar yuksek risk altindadir:\n'
                    '- **Tukenmislik sendromu** sik gorulur\n'
                    '- Duzenli molalar alin (mola vermek sucluluk degildir)\n'
                    '- Destek gruplarina katilin\n'
                    '- Profesyonel yardim isteyin\n'
                    '- Kendi sagliginizi ihmal etmeyin'
                ),
                'body_en': (
                    '## Dementia Caregiver Guide\n\n'
                    '### Golden Rules\n\n'
                    '1. **Patience and understanding:** Towards disease-caused behaviors\n'
                    '2. **Create routines:** Regular schedules provide security\n'
                    '3. **Simplify:** Give one-step instructions\n'
                    '4. **Offer choices:** Show two options instead of "What do you want?"\n'
                    '5. **Ensure safety:** Reduce fall, burn, and wandering risks at home\n\n'
                    '### Communication Techniques\n\n'
                    '- Make eye contact and speak slowly\n'
                    '- Use short, clear sentences\n'
                    '- Support communication with touch\n'
                    '- Validate instead of correcting\n'
                    '- Avoid asking "Do you remember?"\n\n'
                    '### Caregiver Self-Care\n\n'
                    'Caregivers are at high risk:\n'
                    '- **Burnout syndrome** is common\n'
                    '- Take regular breaks (taking breaks is not guilt)\n'
                    '- Join support groups\n'
                    '- Seek professional help\n'
                    '- Don\'t neglect your own health'
                ),
            },
            {
                'slug': 'dementia-care-observation-notes',
                'category': 'dementia-care',
                'order': 2,
                'duration': 4,
                'title_tr': 'Bakici Gozlem Notlari: Nasil Tutulur?',
                'title_en': 'Caregiver Observation Notes: How to Keep',
                'body_tr': (
                    '## Etkili Gozlem Notu Tutma\n\n'
                    'Duzgun tutulan gozlem notlari doktorun tedavi planini optimize etmesine yardimci olur.\n\n'
                    '### Neleri Kaydetmeli?\n\n'
                    '- **Davranis degisiklikleri:** Ajitasyon, apati, agresyon epizodlari\n'
                    '- **Uyku duzeni:** Gece uyanmalari, gunduz uykulugu\n'
                    '- **Beslenme:** Istahtaki degisiklikler, yutma guclugu\n'
                    '- **Bilisssel durum:** Iyi ve kotu gunler, kafa karisikligi\n'
                    '- **Guvenlik olaylari:** Dusmeler, kaybolma, ilac atlama\n'
                    '- **Ruh hali:** Aglamaklilk, sinirlilik, korku\n\n'
                    '### Not Sablonu\n\n'
                    '**Tarih - Saat - Olay - Surusu - Tetikleyici - Mudahale - Sonuc**\n\n'
                    'Ornek: "12 Mart, 15:00 - Ajitasyon - 30 dk - Misafir gelmesi - '
                    'Sessiz odaya gecis - 10 dk sonra sakinlesti"\n\n'
                    '### Norosera\'da Gozlem Notu\n\n'
                    'Bu uygulamada gozlem notu ozelligini kullanarak:\n'
                    '- Not tipi secin (gozlem, endise, iyilesme, olay)\n'
                    '- Ciddiyet seviyesi belirleyin\n'
                    '- Doktora bayrakla isaretleyin\n'
                    '- Tum notlar doktor panelinde goruntulenir'
                ),
                'body_en': (
                    '## Effective Observation Note-Keeping\n\n'
                    'Well-kept observation notes help doctors optimize treatment plans.\n\n'
                    '### What to Record?\n\n'
                    '- **Behavior changes:** Agitation, apathy, aggression episodes\n'
                    '- **Sleep patterns:** Night wakings, daytime sleepiness\n'
                    '- **Nutrition:** Appetite changes, swallowing difficulty\n'
                    '- **Cognitive status:** Good and bad days, confusion\n'
                    '- **Safety incidents:** Falls, wandering, missed medications\n'
                    '- **Mood:** Tearfulness, irritability, fear\n\n'
                    '### Note Template\n\n'
                    '**Date - Time - Event - Duration - Trigger - Intervention - Outcome**\n\n'
                    'Example: "March 12, 3:00 PM - Agitation - 30 min - Visitor arrival - '
                    'Moved to quiet room - Calmed down after 10 min"\n\n'
                    '### Observation Notes in Norosera\n\n'
                    'Using the observation note feature in this app:\n'
                    '- Select note type (observation, concern, improvement, incident)\n'
                    '- Set severity level\n'
                    '- Flag for doctor attention\n'
                    '- All notes visible in the doctor panel'
                ),
            },
            {
                'slug': 'dementia-care-daily-activities',
                'category': 'dementia-care',
                'order': 3,
                'duration': 4,
                'title_tr': 'Gunluk Yasam Aktivitelerini Destekleme',
                'title_en': 'Supporting Daily Living Activities',
                'body_tr': (
                    '## Gunluk Yasam Aktiviteleri (GYA)\n\n'
                    '### Yemek Yeme\n\n'
                    '- Basit, parmakla yenebilir yiyecekler sunun\n'
                    '- Renkli tabaklar kullanin (kontrast yardimci olur)\n'
                    '- Sessiz, dikkat dagitici olmayan ortam saglayin\n'
                    '- Yeterli sivi alimini takip edin\n\n'
                    '### Giyinme\n\n'
                    '- Iki secenek sunun (daha fazla kafa karistirir)\n'
                    '- Giysileri siraya dizin\n'
                    '- Fermuar yerine lastikli pantolon tercih edin\n'
                    '- Yardim ederken onurunu koruyun\n\n'
                    '### Banyo ve Kisisel Bakim\n\n'
                    '- Guvenlik barlari ve kayma onleyici paspas kullanin\n'
                    '- Su sicakligini onceden ayarlayin\n'
                    '- Adim adim yonlendirin\n'
                    '- Mahremiyete saygi gosterin\n\n'
                    '### Hareket ve Aktivite\n\n'
                    '- Gunluk yuruyus (15-30 dk) tesvik edin\n'
                    '- Basit ev isleri yapmasina izin verin\n'
                    '- Muzik dinleme, bahce isleri gibi keyifli aktiviteler\n'
                    '- Sosyal etkilesimi surdurun'
                ),
                'body_en': (
                    '## Activities of Daily Living (ADL)\n\n'
                    '### Eating\n\n'
                    '- Offer simple, finger-friendly foods\n'
                    '- Use colorful plates (contrast helps)\n'
                    '- Provide a quiet, distraction-free environment\n'
                    '- Monitor adequate fluid intake\n\n'
                    '### Dressing\n\n'
                    '- Offer two choices (more causes confusion)\n'
                    '- Lay out clothes in order\n'
                    '- Prefer elastic waistbands over zippers\n'
                    '- Preserve dignity when helping\n\n'
                    '### Bathing and Personal Care\n\n'
                    '- Use safety bars and non-slip mats\n'
                    '- Pre-set water temperature\n'
                    '- Guide step by step\n'
                    '- Respect privacy\n\n'
                    '### Movement and Activity\n\n'
                    '- Encourage daily walks (15-30 min)\n'
                    '- Allow simple household tasks\n'
                    '- Enjoyable activities like music, gardening\n'
                    '- Maintain social interaction'
                ),
            },
            {
                'slug': 'dementia-care-safety',
                'category': 'dementia-care',
                'order': 4,
                'duration': 4,
                'title_tr': 'Ev Guvenligi ve Onlemler',
                'title_en': 'Home Safety Measures',
                'body_tr': (
                    '## Demans Hastasi Icin Ev Guvenligi\n\n'
                    '### Genel Onlemler\n\n'
                    '- Kaymaz halilar ve aydinlik ortam saglayin\n'
                    '- Elektrikli aletlere guvenlik kilidi koyun\n'
                    '- Ilaclari kilitli dolaplarda saklayin\n'
                    '- Bicak, makas gibi kesici aletleri guvenli yere kaldirin\n\n'
                    '### Kaybolma Onleme\n\n'
                    '- Kapi alarmlari veya zil sistemi kurun\n'
                    '- GPS takip cihazi veya akilli saat kullanin\n'
                    '- Kimlik bilgisi tasimalarini saglayin\n'
                    '- Komsulari bilgilendirin\n\n'
                    '### Gece Guvenligi\n\n'
                    '- Gece isiklari kullanin (koridor, banyo)\n'
                    '- Yatak kenar korkuluklari degerlendirin\n'
                    '- Gece dolasmasi icin guvenli alan olusturun\n\n'
                    '### Mutfak Guvenligi\n\n'
                    '- Ocak kilidi veya otomatik kapanma sistemi\n'
                    '- Sicak su sicakligini sinirlayin\n'
                    '- Temizlik malzemelerini kilitli dolaplara koyun\n\n'
                    '### Acil Durum Plani\n\n'
                    '- Acil numaralari gorunur yere yapin\n'
                    '- Komsu ve aile uyelerinin iletisim bilgileri\n'
                    '- Tibbi bilgilerin ozeti (ilaclar, alerjiler)'
                ),
                'body_en': (
                    '## Home Safety for Dementia Patients\n\n'
                    '### General Precautions\n\n'
                    '- Provide non-slip rugs and well-lit spaces\n'
                    '- Add safety locks to electrical appliances\n'
                    '- Store medications in locked cabinets\n'
                    '- Remove sharp objects to safe locations\n\n'
                    '### Wandering Prevention\n\n'
                    '- Install door alarms or bell systems\n'
                    '- Use GPS tracking device or smartwatch\n'
                    '- Ensure they carry ID information\n'
                    '- Inform neighbors\n\n'
                    '### Night Safety\n\n'
                    '- Use night lights (hallway, bathroom)\n'
                    '- Consider bed rails\n'
                    '- Create safe areas for night wandering\n\n'
                    '### Kitchen Safety\n\n'
                    '- Stove lock or auto-off system\n'
                    '- Limit hot water temperature\n'
                    '- Lock cleaning supplies in cabinets\n\n'
                    '### Emergency Plan\n\n'
                    '- Post emergency numbers visibly\n'
                    '- Neighbor and family contact information\n'
                    '- Medical information summary (medications, allergies)'
                ),
            },
            {
                'slug': 'dementia-care-brain-health',
                'category': 'dementia-care',
                'order': 5,
                'duration': 4,
                'title_tr': 'Beyin Sagligini Koruma ve Bilissel Egzersizler',
                'title_en': 'Brain Health Protection and Cognitive Exercises',
                'body_tr': (
                    '## Beyin Sagligini Koruma\n\n'
                    '### Bilissel Stimulasyon\n\n'
                    '- **Bulmacalar ve oyunlar:** Sudoku, kelime oyunlari, hafiza kartlari\n'
                    '- **Yeni beceriler:** Yeni bir hobi, enstruman, dil ogrenme\n'
                    '- **Okuma ve yazma:** Kitap okuma, gunluk tutma\n'
                    '- **Sosyal aktiviteler:** Sohbet, grup oyunlari, dernekler\n\n'
                    '### Fiziksel Aktivite\n\n'
                    '- Haftada en az 150 dakika orta siddette aktivite\n'
                    '- Yuruyus, yuzme, dans, bahce isleri\n'
                    '- Denge egzersizleri (dusme onleme)\n'
                    '- Fiziksel aktivite beyine kan akisini arttirir\n\n'
                    '### Beslenme (Akdeniz Diyeti)\n\n'
                    '- Bol sebze, meyve, tam tahil\n'
                    '- Zeytinyagi, balik (omega-3)\n'
                    '- Kirmizi et ve islenmisinler gida sinirli\n'
                    '- Yeterli su icmek (gunde 8 bardak)\n\n'
                    '### Uyku Kalitesi\n\n'
                    '- Duzenli uyku saatleri (7-8 saat)\n'
                    '- Karanlik ve sessiz uyku ortami\n'
                    '- Uyku bozukluklari tedavi edilmeli\n\n'
                    '### Norosera Bilissel Egzersizleri\n\n'
                    'Bu uygulamada 6 farkli bilissel alanda 20+ egzersiz mevcuttur:\n'
                    '- Hafiza, Dikkat, Dil, Problem Cozme, Oryantasyon, Hesaplama'
                ),
                'body_en': (
                    '## Protecting Brain Health\n\n'
                    '### Cognitive Stimulation\n\n'
                    '- **Puzzles and games:** Sudoku, word games, memory cards\n'
                    '- **New skills:** New hobby, instrument, language learning\n'
                    '- **Reading and writing:** Book reading, journaling\n'
                    '- **Social activities:** Conversation, group games, associations\n\n'
                    '### Physical Activity\n\n'
                    '- At least 150 minutes of moderate activity per week\n'
                    '- Walking, swimming, dancing, gardening\n'
                    '- Balance exercises (fall prevention)\n'
                    '- Physical activity increases brain blood flow\n\n'
                    '### Nutrition (Mediterranean Diet)\n\n'
                    '- Plenty of vegetables, fruits, whole grains\n'
                    '- Olive oil, fish (omega-3)\n'
                    '- Limited red meat and processed foods\n'
                    '- Adequate water intake (8 glasses daily)\n\n'
                    '### Sleep Quality\n\n'
                    '- Regular sleep schedule (7-8 hours)\n'
                    '- Dark and quiet sleep environment\n'
                    '- Sleep disorders should be treated\n\n'
                    '### Norosera Cognitive Exercises\n\n'
                    'This app offers 20+ exercises in 6 cognitive domains:\n'
                    '- Memory, Attention, Language, Problem Solving, Orientation, Calculation'
                ),
            },
        ]

    # =========================================================================
    # QUIZLER
    # =========================================================================
    def _get_quizzes(self):
        return [
            {
                'slug': 'dementia-quiz-basics',
                'category': 'dementia-basics',
                'order': 1,
                'title_tr': 'Demansi Taniyalim Quizi',
                'title_en': 'Understanding Dementia Quiz',
                'description_tr': 'Demans hakkindaki temel bilgilerinizi test edin.',
                'description_en': 'Test your basic knowledge about dementia.',
                'questions': [
                    {
                        'question_tr': 'Demans nedir?',
                        'question_en': 'What is dementia?',
                        'options': [
                            {'text_tr': 'Yaslanmanin dogal bir sonucu', 'text_en': 'A natural result of aging', 'is_correct': False},
                            {'text_tr': 'Bilissel islevlerde ciddi kayba yol acan belirtiler toplulugu', 'text_en': 'A group of symptoms causing serious cognitive decline', 'is_correct': True},
                            {'text_tr': 'Sadece hafiza kaybi', 'text_en': 'Only memory loss', 'is_correct': False},
                            {'text_tr': 'Bulasici bir hastalik', 'text_en': 'A contagious disease', 'is_correct': False},
                        ],
                        'explanation_tr': 'Demans tek bir hastalik degil, bilissel islevlerde ciddi kayba yol acan belirtiler toplulugudur.',
                        'explanation_en': 'Dementia is not a single disease but a group of symptoms causing serious cognitive decline.',
                    },
                    {
                        'question_tr': 'Demans riskinin yaklasik yuzde kaci degistirilebilir faktorlerle onlenebilir?',
                        'question_en': 'What percentage of dementia risk can be prevented with modifiable factors?',
                        'options': [
                            {'text_tr': '%10', 'text_en': '10%', 'is_correct': False},
                            {'text_tr': '%25', 'text_en': '25%', 'is_correct': False},
                            {'text_tr': '%40', 'text_en': '40%', 'is_correct': True},
                            {'text_tr': '%80', 'text_en': '80%', 'is_correct': False},
                        ],
                        'explanation_tr': 'Arastirmalara gore degistirilebilir faktorlere mudahale ile demans riskinin yaklasik %40\'i onlenebilir.',
                        'explanation_en': 'Research shows approximately 40% of dementia cases could be prevented by addressing modifiable factors.',
                    },
                    {
                        'question_tr': 'Asagidakilerden hangisi demansta en erken etkilenen beyin bolgesidir?',
                        'question_en': 'Which brain region is affected earliest in dementia?',
                        'options': [
                            {'text_tr': 'Frontal lob', 'text_en': 'Frontal lobe', 'is_correct': False},
                            {'text_tr': 'Hipokampus', 'text_en': 'Hippocampus', 'is_correct': True},
                            {'text_tr': 'Beyincik', 'text_en': 'Cerebellum', 'is_correct': False},
                        ],
                        'explanation_tr': 'Hipokampus hafiza olusturma merkezidir ve Alzheimer tipi demansta en erken etkilenen bolgedir.',
                        'explanation_en': 'The hippocampus is the memory formation center and is the earliest affected region in Alzheimer-type dementia.',
                    },
                ],
            },
            {
                'slug': 'dementia-quiz-types',
                'category': 'dementia-types',
                'order': 2,
                'title_tr': 'Demans Turleri Quizi',
                'title_en': 'Types of Dementia Quiz',
                'description_tr': 'Farkli demans turlerini ne kadar iyi taniyorsunuz?',
                'description_en': 'How well do you know the different types of dementia?',
                'questions': [
                    {
                        'question_tr': 'En yaygin demans turu hangisidir?',
                        'question_en': 'What is the most common type of dementia?',
                        'options': [
                            {'text_tr': 'Vaskuler demans', 'text_en': 'Vascular dementia', 'is_correct': False},
                            {'text_tr': 'Alzheimer hastaligi', 'text_en': "Alzheimer's disease", 'is_correct': True},
                            {'text_tr': 'Lewy cisimcikli demans', 'text_en': 'Lewy body dementia', 'is_correct': False},
                            {'text_tr': 'Frontotemporal demans', 'text_en': 'Frontotemporal dementia', 'is_correct': False},
                        ],
                        'explanation_tr': 'Alzheimer hastaligi tum demans vakalarinin %60-70\'ini olusturur.',
                        'explanation_en': "Alzheimer's disease accounts for 60-70% of all dementia cases.",
                    },
                    {
                        'question_tr': 'Frontotemporal demans tipik olarak hangi yas grubunda baslar?',
                        'question_en': 'At what age does frontotemporal dementia typically start?',
                        'options': [
                            {'text_tr': '30-45 yas', 'text_en': 'Ages 30-45', 'is_correct': False},
                            {'text_tr': '45-65 yas', 'text_en': 'Ages 45-65', 'is_correct': True},
                            {'text_tr': '65-75 yas', 'text_en': 'Ages 65-75', 'is_correct': False},
                            {'text_tr': '75 yas ustu', 'text_en': 'Over 75', 'is_correct': False},
                        ],
                        'explanation_tr': 'Frontotemporal demans genellikle 45-65 yas arasinda baslar ve genc basta demans sebeplerinden biridir.',
                        'explanation_en': 'Frontotemporal dementia typically starts between ages 45-65 and is a cause of young-onset dementia.',
                    },
                    {
                        'question_tr': 'Lewy cisimcikli demansin ayirt edici ozelligi hangisidir?',
                        'question_en': 'What is the distinguishing feature of Lewy body dementia?',
                        'options': [
                            {'text_tr': 'Basamakli ilerleme', 'text_en': 'Stepwise progression', 'is_correct': False},
                            {'text_tr': 'Gorsel halusinasyonlar ve dalgalanan bilissel durum', 'text_en': 'Visual hallucinations and fluctuating cognition', 'is_correct': True},
                            {'text_tr': 'Sadece hafiza kaybi', 'text_en': 'Only memory loss', 'is_correct': False},
                        ],
                        'explanation_tr': 'Lewy cisimcikli demans gorsel halusinasyonlar, dalgalanan bilissel durum ve parkinsonizm ile karakterizedir.',
                        'explanation_en': 'Lewy body dementia is characterized by visual hallucinations, fluctuating cognition, and parkinsonism.',
                    },
                    {
                        'question_tr': 'Asagidakilerden hangisi tedavi edilebilir demans benzeri bir durumdur?',
                        'question_en': 'Which is a treatable condition that mimics dementia?',
                        'options': [
                            {'text_tr': 'Alzheimer hastaligi', 'text_en': "Alzheimer's disease", 'is_correct': False},
                            {'text_tr': 'Vitamin B12 eksikligi', 'text_en': 'Vitamin B12 deficiency', 'is_correct': True},
                            {'text_tr': 'Frontotemporal demans', 'text_en': 'Frontotemporal dementia', 'is_correct': False},
                        ],
                        'explanation_tr': 'Vitamin B12 eksikligi, tiroid bozukluklari ve normal basinc hidrosefalisi tedavi edilebilir demans benzeri durumlardandir.',
                        'explanation_en': 'Vitamin B12 deficiency, thyroid disorders, and normal pressure hydrocephalus are treatable conditions mimicking dementia.',
                    },
                ],
            },
            {
                'slug': 'dementia-quiz-signs',
                'category': 'dementia-signs',
                'order': 3,
                'title_tr': 'Erken Belirtiler Quizi',
                'title_en': 'Early Signs Quiz',
                'description_tr': 'Demans uyari isretlerini taniyabiliyor musunuz?',
                'description_en': 'Can you recognize dementia warning signs?',
                'questions': [
                    {
                        'question_tr': 'Asagidakilerden hangisi normal yaslanmanin bir parcasidir?',
                        'question_en': 'Which of the following is a normal part of aging?',
                        'options': [
                            {'text_tr': 'Yakin aile uyelerini taniyamamak', 'text_en': 'Not recognizing close family members', 'is_correct': False},
                            {'text_tr': 'Bir ismi gecici olarak hatirlayamamak', 'text_en': 'Temporarily not remembering a name', 'is_correct': True},
                            {'text_tr': 'Bilinen yollarda surekli kaybolmak', 'text_en': 'Constantly getting lost on familiar routes', 'is_correct': False},
                            {'text_tr': 'Basit matematik islemlerini yapamamak', 'text_en': 'Unable to do simple math', 'is_correct': False},
                        ],
                        'explanation_tr': 'Bir ismi gecici olarak hatirlayamama normal yaslanmanin bir parcasidir. Diger secenekler demans belirtileridir.',
                        'explanation_en': 'Temporarily not remembering a name is part of normal aging. The other options are dementia symptoms.',
                    },
                    {
                        'question_tr': 'Sundowning (gunes batimi sendromu) ne anlama gelir?',
                        'question_en': 'What does sundowning mean?',
                        'options': [
                            {'text_tr': 'Sabah saatlerinde uyku hali', 'text_en': 'Sleepiness in the morning', 'is_correct': False},
                            {'text_tr': 'Aksam saatlerinde artan kafa karisikligi ve huzursuzluk', 'text_en': 'Increased confusion and restlessness in the evening', 'is_correct': True},
                            {'text_tr': 'Gunes isigina duyarlilik', 'text_en': 'Sensitivity to sunlight', 'is_correct': False},
                        ],
                        'explanation_tr': 'Sundowning, demans hastalarinda aksam saatlerinde artan kafa karisikligi, huzursuzluk ve ajitasyon durumudur.',
                        'explanation_en': 'Sundowning refers to increased confusion, restlessness, and agitation in dementia patients during evening hours.',
                    },
                    {
                        'question_tr': 'Demansta en erken etkilenen hafiza turu hangisidir?',
                        'question_en': 'Which type of memory is affected earliest in dementia?',
                        'options': [
                            {'text_tr': 'Prosedural hafiza (bisiklet surme)', 'text_en': 'Procedural memory (riding a bicycle)', 'is_correct': False},
                            {'text_tr': 'Epizodik hafiza (kisisel deneyimler)', 'text_en': 'Episodic memory (personal experiences)', 'is_correct': True},
                            {'text_tr': 'Semantik hafiza (genel bilgiler)', 'text_en': 'Semantic memory (general knowledge)', 'is_correct': False},
                        ],
                        'explanation_tr': 'Epizodik hafiza (kisisel deneyimler, yakin gecmis) demansta en erken etkilenen hafiza turudur.',
                        'explanation_en': 'Episodic memory (personal experiences, recent past) is the earliest affected memory type in dementia.',
                    },
                ],
            },
            {
                'slug': 'dementia-quiz-diagnosis',
                'category': 'dementia-diagnosis',
                'order': 4,
                'title_tr': 'Tani ve Degerlendirme Quizi',
                'title_en': 'Diagnosis & Assessment Quiz',
                'description_tr': 'Demans tanisi ve degerlendirme yontemlerini test edin.',
                'description_en': 'Test your knowledge of dementia diagnosis and assessment.',
                'questions': [
                    {
                        'question_tr': 'Demans tanisi icin en az kac bilissel alanda bozulma olmalidir?',
                        'question_en': 'How many cognitive domains must be impaired for dementia diagnosis?',
                        'options': [
                            {'text_tr': '1 alan', 'text_en': '1 domain', 'is_correct': False},
                            {'text_tr': '2 alan', 'text_en': '2 domains', 'is_correct': True},
                            {'text_tr': '4 alan', 'text_en': '4 domains', 'is_correct': False},
                            {'text_tr': 'Tum alanlar', 'text_en': 'All domains', 'is_correct': False},
                        ],
                        'explanation_tr': 'Demans tanisi icin en az iki bilissel alanda bozulma ve gunluk islevsellikte azalma olmalidir.',
                        'explanation_en': 'For dementia diagnosis, impairment in at least two cognitive domains and decline in daily functioning is required.',
                    },
                    {
                        'question_tr': 'Frontal Degerlendirme Bataryasi (FAB) kac alt testten olusur?',
                        'question_en': 'How many subtests does the Frontal Assessment Battery (FAB) consist of?',
                        'options': [
                            {'text_tr': '3', 'text_en': '3', 'is_correct': False},
                            {'text_tr': '6', 'text_en': '6', 'is_correct': True},
                            {'text_tr': '10', 'text_en': '10', 'is_correct': False},
                        ],
                        'explanation_tr': 'FAB 6 alt testten olusur: Benzerlikler, sozel akicilik, motor seriler, catisma talimatlari, git-gitme ve kavrama refleksi.',
                        'explanation_en': 'FAB consists of 6 subtests: Similarities, verbal fluency, motor series, conflicting instructions, go-no go, and grasp reflex.',
                    },
                    {
                        'question_tr': 'Kan testlerinde hangi sonuc ozellikle onemlidir ve belirtileri tersine cevirebilir?',
                        'question_en': 'Which blood test result is especially important and can reverse symptoms?',
                        'options': [
                            {'text_tr': 'Tam kan sayimi', 'text_en': 'Complete blood count', 'is_correct': False},
                            {'text_tr': 'B12 vitamini ve tiroid', 'text_en': 'Vitamin B12 and thyroid', 'is_correct': True},
                            {'text_tr': 'Kalsiyum', 'text_en': 'Calcium', 'is_correct': False},
                        ],
                        'explanation_tr': 'B12 eksikligi ve tiroid bozukluklari demans benzeri belirtilere neden olabilir ve tedavi ile belirtiler tersine donebilir.',
                        'explanation_en': 'B12 deficiency and thyroid disorders can cause dementia-like symptoms and treatment can reverse symptoms.',
                    },
                ],
            },
            {
                'slug': 'dementia-quiz-care',
                'category': 'dementia-care',
                'order': 5,
                'title_tr': 'Bakim ve Destek Quizi',
                'title_en': 'Care & Support Quiz',
                'description_tr': 'Demans bakimi ve yasam kalitesi hakkindaki bilgilerinizi test edin.',
                'description_en': 'Test your knowledge about dementia care and quality of life.',
                'questions': [
                    {
                        'question_tr': 'Demans hastasina soru sorarken en uygun yaklasim hangisidir?',
                        'question_en': 'What is the most appropriate approach when asking questions to a dementia patient?',
                        'options': [
                            {'text_tr': '"Hatirliyor musun?" diye sormak', 'text_en': 'Asking "Do you remember?"', 'is_correct': False},
                            {'text_tr': 'Iki secenek sunmak', 'text_en': 'Offering two choices', 'is_correct': True},
                            {'text_tr': 'Uzun ve detayli sorular sormak', 'text_en': 'Asking long and detailed questions', 'is_correct': False},
                            {'text_tr': 'Cevabi beklemeden kendiniz yapmak', 'text_en': 'Doing it yourself without waiting for an answer', 'is_correct': False},
                        ],
                        'explanation_tr': 'Iki secenek sunmak hastanin karar vermesini kolaylastirir. "Hatirliyor musun?" sorusu hayal kirikligi yaratabilir.',
                        'explanation_en': 'Offering two choices makes decision-making easier. "Do you remember?" can create frustration.',
                    },
                    {
                        'question_tr': 'Beyin sagligi icin haftada en az kac dakika fiziksel aktivite onerilir?',
                        'question_en': 'How many minutes of physical activity per week is recommended for brain health?',
                        'options': [
                            {'text_tr': '30 dakika', 'text_en': '30 minutes', 'is_correct': False},
                            {'text_tr': '60 dakika', 'text_en': '60 minutes', 'is_correct': False},
                            {'text_tr': '150 dakika', 'text_en': '150 minutes', 'is_correct': True},
                        ],
                        'explanation_tr': 'Haftada en az 150 dakika orta siddette fiziksel aktivite beyin sagligi icin onerilir.',
                        'explanation_en': 'At least 150 minutes of moderate physical activity per week is recommended for brain health.',
                    },
                    {
                        'question_tr': 'Gozlem notu tutarken asagidakilerden hangisi kayit edilmelidir?',
                        'question_en': 'Which of the following should be recorded in observation notes?',
                        'options': [
                            {'text_tr': 'Sadece kotu gunler', 'text_en': 'Only bad days', 'is_correct': False},
                            {'text_tr': 'Sadece guvenlik olaylari', 'text_en': 'Only safety incidents', 'is_correct': False},
                            {'text_tr': 'Davranis degisiklikleri, uyku, beslenme, bilissel durum ve guvenlik olaylari', 'text_en': 'Behavior changes, sleep, nutrition, cognitive status, and safety incidents', 'is_correct': True},
                        ],
                        'explanation_tr': 'Kapsamli gozlem notlari davranis, uyku, beslenme, bilissel durum ve guvenlik olaylarini icermelidir.',
                        'explanation_en': 'Comprehensive observation notes should include behavior, sleep, nutrition, cognitive status, and safety incidents.',
                    },
                    {
                        'question_tr': 'Bakicilarin kendileri icin en onemli yapmalari gereken sey nedir?',
                        'question_en': 'What is the most important thing caregivers should do for themselves?',
                        'options': [
                            {'text_tr': 'Hic mola vermeden bakim yapmak', 'text_en': 'Provide care without any breaks', 'is_correct': False},
                            {'text_tr': 'Duygularini bastirmak', 'text_en': 'Suppress their emotions', 'is_correct': False},
                            {'text_tr': 'Duzenli mola almak ve destek aramak', 'text_en': 'Take regular breaks and seek support', 'is_correct': True},
                        ],
                        'explanation_tr': 'Bakicilarin tukenmislik sendromunu onlemek icin duzenli mola almasi ve destek gruplarina katilmasi cok onemlidir.',
                        'explanation_en': 'It is crucial for caregivers to take regular breaks and join support groups to prevent burnout syndrome.',
                    },
                ],
            },
        ]
