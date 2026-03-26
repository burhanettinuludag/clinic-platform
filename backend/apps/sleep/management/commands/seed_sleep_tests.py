"""
4 özgün uyku farkındalık testi oluşturur.
Telif sorunu olmayan, klinik bilgiye dayalı farkındalık anketleri.

Testler:
1. Uyku Kalitesi Farkındalık Anketi (10 soru)
2. Gündüz Uykululuk Farkındalık Anketi (8 soru)
3. Uykusuzluk Risk Değerlendirmesi (10 soru)
4. Uyku Apnesi Risk Farkındalık Anketi (10 soru)
"""

from django.core.management.base import BaseCommand
from apps.sleep.models import (
    SleepScreeningTest,
    SleepScreeningQuestion,
    SleepScreeningOption,
    SleepScreeningResultRange,
)


class Command(BaseCommand):
    help = 'Uyku farkındalık testleri seed data'

    def handle(self, *args, **options):
        # Temizle
        SleepScreeningTest.objects.all().delete()

        self._create_sleep_quality_test()
        self._create_daytime_sleepiness_test()
        self._create_insomnia_risk_test()
        self._create_apnea_risk_test()

        count = SleepScreeningTest.objects.count()
        self.stdout.write(self.style.SUCCESS(f'{count} farkındalık testi oluşturuldu!'))

    # ─── 1. Uyku Kalitesi Farkındalık Anketi ───────────────────────────

    def _create_sleep_quality_test(self):
        test = SleepScreeningTest.objects.create(
            slug='uyku-kalitesi',
            title_tr='Uyku Kalitesi Farkındalık Anketi',
            title_en='Sleep Quality Awareness Questionnaire',
            description_tr='Son bir ay içindeki uyku alışkanlıklarınızı değerlendirerek uyku kaliteniz hakkında farkındalık kazanın.',
            description_en='Gain awareness about your sleep quality by evaluating your sleep habits over the past month.',
            instructions_tr='Her soruyu son bir aydaki tipik uyku deneyiminize göre yanıtlayın. En uygun seçeneği işaretleyin.',
            instructions_en='Answer each question based on your typical sleep experience over the past month. Select the most appropriate option.',
            icon='moon',
            duration_minutes=3,
            order=1,
        )

        questions = [
            {
                'q_tr': 'Geceleri uykuya dalma süreniz genellikle ne kadardır?',
                'q_en': 'How long does it generally take you to fall asleep at night?',
                'help_tr': 'Yatağa girip ışıkları kapattıktan sonraki süreyi düşünün.',
                'help_en': 'Think about the time after you get into bed and turn off the lights.',
                'options': [
                    ('15 dakikadan az', 'Less than 15 minutes', 0),
                    ('15-30 dakika', '15-30 minutes', 1),
                    ('30-60 dakika', '30-60 minutes', 2),
                    ('60 dakikadan fazla', 'More than 60 minutes', 3),
                ],
            },
            {
                'q_tr': 'Gece boyunca kaç kez uyanırsınız?',
                'q_en': 'How many times do you wake up during the night?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hiç uyanmam veya 1 kez', 'Never or once', 0),
                    ('2-3 kez', '2-3 times', 1),
                    ('4-5 kez', '4-5 times', 2),
                    ('5 kereden fazla', 'More than 5 times', 3),
                ],
            },
            {
                'q_tr': 'Sabah uyandığınızda kendinizi dinlenmiş hissediyor musunuz?',
                'q_en': 'Do you feel rested when you wake up in the morning?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Her zaman dinlenmiş hissederim', 'I always feel rested', 0),
                    ('Çoğunlukla dinlenmiş hissederim', 'I mostly feel rested', 1),
                    ('Nadiren dinlenmiş hissederim', 'I rarely feel rested', 2),
                    ('Hiçbir zaman dinlenmiş hissetmem', 'I never feel rested', 3),
                ],
            },
            {
                'q_tr': 'Hafta içi ve hafta sonu uyku saatleriniz arasında fark var mı?',
                'q_en': 'Is there a difference between your weekday and weekend sleep times?',
                'help_tr': 'Sosyal jet lag olarak bilinen bu durum uyku kalitenizi etkileyebilir.',
                'help_en': 'This condition, known as social jet lag, can affect your sleep quality.',
                'options': [
                    ('Fark yok veya 30 dakikadan az', 'No difference or less than 30 minutes', 0),
                    ('30 dakika - 1 saat fark', '30 minutes - 1 hour difference', 1),
                    ('1-2 saat fark', '1-2 hours difference', 2),
                    ('2 saatten fazla fark', 'More than 2 hours difference', 3),
                ],
            },
            {
                'q_tr': 'Yatmadan önce ekran (telefon, tablet, bilgisayar) kullanıyor musunuz?',
                'q_en': 'Do you use screens (phone, tablet, computer) before bed?',
                'help_tr': 'Mavi ışık melatonin üretimini baskılayabilir.',
                'help_en': 'Blue light can suppress melatonin production.',
                'options': [
                    ('Yatmadan en az 1 saat önce bırakırım', 'I stop at least 1 hour before bed', 0),
                    ('Yatmadan 30 dakika - 1 saat önce bırakırım', 'I stop 30 min - 1 hour before bed', 1),
                    ('Yatağa girerken hâlâ kullanırım', 'I still use it when I get into bed', 2),
                    ('Yatakta uykum gelene kadar kullanırım', 'I use it in bed until I feel sleepy', 3),
                ],
            },
            {
                'q_tr': 'Uyku ortamınız (yatak odanız) nasıl?',
                'q_en': 'How is your sleep environment (bedroom)?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Karanlık, sessiz ve serin', 'Dark, quiet and cool', 0),
                    ('Çoğunlukla uygun ama bazen sorunlu', 'Mostly suitable but sometimes problematic', 1),
                    ('Gürültü veya ışık sorunu var', 'There are noise or light issues', 2),
                    ('Birden fazla çevresel sorun var', 'There are multiple environmental issues', 3),
                ],
            },
            {
                'q_tr': 'Kafein (çay, kahve, enerji içeceği) tüketiminiz nasıl?',
                'q_en': 'How is your caffeine consumption (tea, coffee, energy drinks)?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Öğleden sonra kafein almam', 'I don\'t consume caffeine after noon', 0),
                    ('Akşam saatlerinde bazen kafein alırım', 'I sometimes consume caffeine in the evening', 1),
                    ('Akşam saatlerinde sıklıkla kafein alırım', 'I frequently consume caffeine in the evening', 2),
                    ('Yatmadan kısa süre önce bile kafein alırım', 'I consume caffeine even shortly before bed', 3),
                ],
            },
            {
                'q_tr': 'Düzenli bir uyku saatiniz var mı?',
                'q_en': 'Do you have a regular sleep schedule?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Her gece aynı saatte yatar ve kalkarım', 'I go to bed and wake up at the same time every night', 0),
                    ('Çoğunlukla düzenli ama bazen değişir', 'Mostly regular but sometimes varies', 1),
                    ('Saatlerim oldukça düzensiz', 'My schedule is quite irregular', 2),
                    ('Her gece farklı saatte yatarım', 'I go to bed at a different time every night', 3),
                ],
            },
            {
                'q_tr': 'Gündüz uyku ihtiyacı (şekerleme) hissediyor musunuz?',
                'q_en': 'Do you feel the need for daytime naps?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır, gündüz dinç olurum', 'No, I feel alert during the day', 0),
                    ('Ara sıra kısa bir şekerleme yaparım', 'I occasionally take a short nap', 1),
                    ('Hemen her gün şekerlemeye ihtiyaç duyarım', 'I need a nap almost every day', 2),
                    ('Gündüz dayanılmaz uyku hali oluşur', 'I experience irresistible daytime sleepiness', 3),
                ],
            },
            {
                'q_tr': 'Uyku kalitenizi genel olarak nasıl değerlendirirsiniz?',
                'q_en': 'How would you rate your overall sleep quality?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Çok iyi', 'Very good', 0),
                    ('İyi', 'Good', 1),
                    ('Kötü', 'Poor', 2),
                    ('Çok kötü', 'Very poor', 3),
                ],
            },
        ]

        self._create_questions(test, questions)

        # Sonuç aralıkları (0-30 toplam puan)
        ranges = [
            ('low', 0, 7, 'İyi Uyku Kalitesi', 'Good Sleep Quality',
             'Uyku alışkanlıklarınız genel olarak sağlıklı görünüyor. Mevcut düzeninizi sürdürmeye devam edin.',
             'Your sleep habits appear generally healthy. Continue maintaining your current routine.',
             'Mevcut uyku düzeninizi koruyun. Düzenli egzersiz ve sağlıklı beslenme ile uyku kalitenizi daha da artırabilirsiniz.',
             'Maintain your current sleep routine. You can further improve your sleep quality with regular exercise and healthy nutrition.',
             'green'),
            ('moderate', 8, 15, 'Orta Düzey Uyku Sorunları', 'Moderate Sleep Issues',
             'Bazı uyku alışkanlıklarınızda iyileştirme yapılabilir. Uyku hijyeni kurallarına dikkat etmeniz önerilir.',
             'Some of your sleep habits could be improved. Paying attention to sleep hygiene rules is recommended.',
             'Uyku saatlerinizi düzenleyin, yatmadan önce ekran kullanımını azaltın ve yatak odanızın uyku için uygun olduğundan emin olun.',
             'Regulate your sleep schedule, reduce screen use before bed, and ensure your bedroom is suitable for sleep.',
             'yellow'),
            ('high', 16, 22, 'Belirgin Uyku Sorunları', 'Significant Sleep Issues',
             'Uyku kalitenizde belirgin sorunlar mevcut. Bu durum günlük yaşamınızı ve sağlığınızı olumsuz etkileyebilir.',
             'There are significant issues with your sleep quality. This may negatively affect your daily life and health.',
             'Bir uyku uzmanına veya nöroloji doktoruna başvurmanız önerilir. Uyku günlüğü tutmaya başlayın.',
             'Consulting a sleep specialist or neurologist is recommended. Start keeping a sleep diary.',
             'orange'),
            ('severe', 23, 30, 'Ciddi Uyku Sorunları', 'Severe Sleep Issues',
             'Uyku kalitenizde ciddi sorunlar tespit edildi. Bu durum fiziksel ve ruhsal sağlığınızı önemli ölçüde etkileyebilir.',
             'Serious issues with your sleep quality have been identified. This may significantly affect your physical and mental health.',
             'En kısa sürede bir uyku uzmanına başvurmanız şiddetle önerilir. Profesyonel değerlendirme ve tedavi planı gereklidir.',
             'It is strongly recommended that you consult a sleep specialist as soon as possible. Professional evaluation and treatment plan is required.',
             'red'),
        ]
        self._create_ranges(test, ranges)

    # ─── 2. Gündüz Uykululuk Farkındalık Anketi ───────────────────────

    def _create_daytime_sleepiness_test(self):
        test = SleepScreeningTest.objects.create(
            slug='gunduz-uykululuk',
            title_tr='Gündüz Uykululuk Farkındalık Anketi',
            title_en='Daytime Sleepiness Awareness Questionnaire',
            description_tr='Gündüz saatlerinde yaşadığınız uykululuk düzeyini değerlendirin. Aşırı gündüz uykululuğu birçok uyku bozukluğunun belirtisi olabilir.',
            description_en='Evaluate your level of daytime sleepiness. Excessive daytime sleepiness can be a symptom of various sleep disorders.',
            instructions_tr='Son bir ay içinde aşağıdaki durumlarda uyuklama veya uyuyakalma olasılığınızı değerlendirin.',
            instructions_en='Rate your likelihood of dozing off or falling asleep in the following situations over the past month.',
            icon='sun',
            duration_minutes=2,
            order=2,
        )

        questions = [
            {
                'q_tr': 'Oturarak kitap okurken veya belge incelerken uyuklama olasılığınız nedir?',
                'q_en': 'What is the likelihood of you dozing off while sitting and reading a book or reviewing a document?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Asla uyuklamam', 'I never doze off', 0),
                    ('Nadiren uyuklarım', 'I rarely doze off', 1),
                    ('Sıklıkla uyuklarım', 'I frequently doze off', 2),
                    ('Neredeyse her zaman uyuklarım', 'I almost always doze off', 3),
                ],
            },
            {
                'q_tr': 'Televizyon izlerken uyuklama olasılığınız nedir?',
                'q_en': 'What is the likelihood of you dozing off while watching television?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Asla uyuklamam', 'I never doze off', 0),
                    ('Nadiren uyuklarım', 'I rarely doze off', 1),
                    ('Sıklıkla uyuklarım', 'I frequently doze off', 2),
                    ('Neredeyse her zaman uyuklarım', 'I almost always doze off', 3),
                ],
            },
            {
                'q_tr': 'Toplantıda veya konferansta pasif olarak otururken uyuklama olasılığınız nedir?',
                'q_en': 'What is the likelihood of you dozing off while sitting passively in a meeting or conference?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Asla uyuklamam', 'I never doze off', 0),
                    ('Nadiren uyuklarım', 'I rarely doze off', 1),
                    ('Sıklıkla uyuklarım', 'I frequently doze off', 2),
                    ('Neredeyse her zaman uyuklarım', 'I almost always doze off', 3),
                ],
            },
            {
                'q_tr': 'Öğle yemeğinden sonra uyku hali yaşıyor musunuz?',
                'q_en': 'Do you experience sleepiness after lunch?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır, öğleden sonra da dinç olurum', 'No, I stay alert in the afternoon', 0),
                    ('Hafif bir uyku hali olur ama geçer', 'I feel slightly sleepy but it passes', 1),
                    ('Belirgin uyku hali olur, işime odaklanamam', 'I feel noticeably sleepy and can\'t focus', 2),
                    ('Dayanılmaz uyku hali olur', 'I experience irresistible sleepiness', 3),
                ],
            },
            {
                'q_tr': 'Araba yolculuğunda (yolcu olarak) 1 saatten fazla otururken uyuklama olasılığınız nedir?',
                'q_en': 'What is the likelihood of you dozing off as a passenger in a car for more than 1 hour?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Asla uyuklamam', 'I never doze off', 0),
                    ('Nadiren uyuklarım', 'I rarely doze off', 1),
                    ('Sıklıkla uyuklarım', 'I frequently doze off', 2),
                    ('Neredeyse her zaman uyuklarım', 'I almost always doze off', 3),
                ],
            },
            {
                'q_tr': 'İş veya okul performansınız gündüz uykululuktan etkileniyor mu?',
                'q_en': 'Is your work or school performance affected by daytime sleepiness?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır, performansım etkilenmiyor', 'No, my performance is not affected', 0),
                    ('Hafif etkileniyor', 'Slightly affected', 1),
                    ('Belirgin şekilde etkileniyor', 'Noticeably affected', 2),
                    ('Ciddi şekilde etkileniyor', 'Severely affected', 3),
                ],
            },
            {
                'q_tr': 'Gündüz uyanık kalmak için kahve veya enerji içeceğine ihtiyaç duyuyor musunuz?',
                'q_en': 'Do you need coffee or energy drinks to stay awake during the day?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır, doğal olarak uyanık kalırım', 'No, I stay awake naturally', 0),
                    ('Sabahları bir fincan kahve yeterli', 'One cup of coffee in the morning is enough', 1),
                    ('Gün içinde birden fazla kafeinli içeceğe ihtiyaç duyarım', 'I need multiple caffeinated drinks during the day', 2),
                    ('Sürekli kafein alsam bile uyanık kalamam', 'Even with constant caffeine, I can\'t stay awake', 3),
                ],
            },
            {
                'q_tr': 'Hafta sonları veya tatil günlerinde normalden çok daha fazla mı uyursunuz?',
                'q_en': 'Do you sleep much more on weekends or holidays than usual?',
                'help_tr': 'Bu "uyku borcu" olarak bilinir.',
                'help_en': 'This is known as "sleep debt".',
                'options': [
                    ('Hayır, benzer saatlerde uyanırım', 'No, I wake up at similar times', 0),
                    ('1-2 saat fazla uyurum', 'I sleep 1-2 hours more', 1),
                    ('2-4 saat fazla uyurum', 'I sleep 2-4 hours more', 2),
                    ('4 saatten fazla uyurum', 'I sleep more than 4 hours extra', 3),
                ],
            },
        ]

        self._create_questions(test, questions)

        ranges = [
            ('low', 0, 6, 'Normal Gündüz Uyanıklığı', 'Normal Daytime Alertness',
             'Gündüz uyanıklık düzeyiniz normal görünüyor. Yeterli ve kaliteli uyku aldığınızı gösteriyor.',
             'Your daytime alertness level appears normal. This suggests you are getting enough quality sleep.',
             'Mevcut uyku düzeninizi korumaya devam edin.',
             'Continue maintaining your current sleep routine.',
             'green'),
            ('moderate', 7, 12, 'Hafif Gündüz Uykululuğu', 'Mild Daytime Sleepiness',
             'Hafif düzeyde gündüz uykululuğu yaşıyorsunuz. Uyku sürenizi veya kalitenizi gözden geçirmeniz yararlı olabilir.',
             'You are experiencing mild daytime sleepiness. Reviewing your sleep duration or quality may be beneficial.',
             'Uyku sürenizi artırmayı ve uyku hijyeni kurallarına dikkat etmeyi deneyin.',
             'Try increasing your sleep duration and paying attention to sleep hygiene rules.',
             'yellow'),
            ('high', 13, 18, 'Belirgin Gündüz Uykululuğu', 'Significant Daytime Sleepiness',
             'Belirgin düzeyde gündüz uykululuğu yaşıyorsunuz. Bu durum altta yatan bir uyku bozukluğunun belirtisi olabilir.',
             'You are experiencing significant daytime sleepiness. This may be a symptom of an underlying sleep disorder.',
             'Bir uyku uzmanına danışmanız önerilir. Uyku apnesi veya diğer uyku bozuklukları değerlendirilmelidir.',
             'Consulting a sleep specialist is recommended. Sleep apnea or other sleep disorders should be evaluated.',
             'orange'),
            ('severe', 19, 24, 'Ciddi Gündüz Uykululuğu', 'Severe Daytime Sleepiness',
             'Ciddi düzeyde gündüz uykululuğu yaşıyorsunuz. Bu durum güvenliğinizi ve yaşam kalitenizi önemli ölçüde etkileyebilir.',
             'You are experiencing severe daytime sleepiness. This can significantly affect your safety and quality of life.',
             'En kısa sürede bir nöroloji veya uyku uzmanına başvurunuz. Araç kullanırken dikkatli olunuz.',
             'Please consult a neurologist or sleep specialist as soon as possible. Be careful when driving.',
             'red'),
        ]
        self._create_ranges(test, ranges)

    # ─── 3. Uykusuzluk Risk Değerlendirmesi ───────────────────────────

    def _create_insomnia_risk_test(self):
        test = SleepScreeningTest.objects.create(
            slug='uykusuzluk-riski',
            title_tr='Uykusuzluk Risk Değerlendirmesi',
            title_en='Insomnia Risk Assessment',
            description_tr='Uykusuzluk (insomni) belirtilerinizi ve risk faktörlerinizi değerlendirin. DSM-5 tanı kriterlerine dayalı farkındalık anketi.',
            description_en='Evaluate your insomnia symptoms and risk factors. An awareness questionnaire based on DSM-5 diagnostic criteria.',
            instructions_tr='Son üç ay içindeki uyku deneyiminize göre yanıtlayın. Bu anketteki sorular uykusuzluğun farklı boyutlarını değerlendirir.',
            instructions_en='Answer based on your sleep experience over the past three months. Questions in this survey evaluate different dimensions of insomnia.',
            icon='alert-circle',
            duration_minutes=3,
            order=3,
        )

        questions = [
            {
                'q_tr': 'Uykuya dalmakta güçlük çekiyor musunuz?',
                'q_en': 'Do you have difficulty falling asleep?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Hafif güçlük (haftada 1-2 gece)', 'Slight difficulty (1-2 nights per week)', 1),
                    ('Orta düzeyde güçlük (haftada 3-4 gece)', 'Moderate difficulty (3-4 nights per week)', 2),
                    ('Ciddi güçlük (hemen her gece)', 'Severe difficulty (almost every night)', 3),
                ],
            },
            {
                'q_tr': 'Gece ortasında uyanıp tekrar uyuyamama sorunu yaşıyor musunuz?',
                'q_en': 'Do you wake up in the middle of the night and have trouble falling back asleep?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Hafif sorun (haftada 1-2 gece)', 'Slight problem (1-2 nights per week)', 1),
                    ('Orta düzeyde sorun (haftada 3-4 gece)', 'Moderate problem (3-4 nights per week)', 2),
                    ('Ciddi sorun (hemen her gece)', 'Severe problem (almost every night)', 3),
                ],
            },
            {
                'q_tr': 'Sabah istediğinizden erken uyanıyor musunuz?',
                'q_en': 'Do you wake up earlier than desired in the morning?',
                'help_tr': 'Alarm saatinizden veya planladığınızdan erken uyanma durumu.',
                'help_en': 'Waking up before your alarm or planned time.',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Bazen (haftada 1-2 gün)', 'Sometimes (1-2 days per week)', 1),
                    ('Sıklıkla (haftada 3-4 gün)', 'Often (3-4 days per week)', 2),
                    ('Her gün', 'Every day', 3),
                ],
            },
            {
                'q_tr': 'Uyku sorununuz gündüz işlevselliğinizi nasıl etkiliyor?',
                'q_en': 'How does your sleep problem affect your daytime functioning?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Etkilemiyor', 'It doesn\'t affect me', 0),
                    ('Hafif etkiliyor (dikkat dağınıklığı)', 'Slightly affects (attention issues)', 1),
                    ('Belirgin şekilde etkiliyor (iş/okul performansı düşüyor)', 'Noticeably affects (work/school performance decreases)', 2),
                    ('Ciddi şekilde etkiliyor (günlük aktiviteleri yapamıyorum)', 'Severely affects (I can\'t perform daily activities)', 3),
                ],
            },
            {
                'q_tr': 'Yatağa gittiğinizde uyuyamama endişesi yaşıyor musunuz?',
                'q_en': 'Do you experience anxiety about not being able to sleep when you go to bed?',
                'help_tr': 'Bu durum "uyku kaygısı" olarak bilinir ve uykusuzluğu pekiştirebilir.',
                'help_en': 'This is known as "sleep anxiety" and can reinforce insomnia.',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Bazen endişelenirim', 'I sometimes worry', 1),
                    ('Sıklıkla endişelenirim', 'I often worry', 2),
                    ('Her gece yoğun kaygı yaşarım', 'I experience intense anxiety every night', 3),
                ],
            },
            {
                'q_tr': 'Stres, kaygı veya depresyon belirtileri yaşıyor musunuz?',
                'q_en': 'Are you experiencing symptoms of stress, anxiety, or depression?',
                'help_tr': 'Ruh sağlığı sorunları uykusuzluğun en önemli risk faktörlerinden biridir.',
                'help_en': 'Mental health issues are among the most important risk factors for insomnia.',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Hafif düzeyde', 'Mild level', 1),
                    ('Orta düzeyde', 'Moderate level', 2),
                    ('Ciddi düzeyde', 'Severe level', 3),
                ],
            },
            {
                'q_tr': 'Yatağı uyku dışında aktiviteler için kullanıyor musunuz?',
                'q_en': 'Do you use the bed for activities other than sleep?',
                'help_tr': 'Telefon kullanma, televizyon izleme, çalışma, yemek yeme gibi.',
                'help_en': 'Such as using phone, watching TV, working, eating.',
                'options': [
                    ('Hayır, yatağımı yalnızca uyku için kullanırım', 'No, I only use my bed for sleep', 0),
                    ('Bazen kitap okurum', 'I sometimes read books', 1),
                    ('Sıklıkla telefon/tablet kullanırım', 'I frequently use phone/tablet', 2),
                    ('Yatakta uzun süre telefon, bilgisayar, TV kullanırım', 'I use phone, computer, TV in bed for long periods', 3),
                ],
            },
            {
                'q_tr': 'Düzensiz çalışma saatleri veya vardiyalı çalışma yapıyor musunuz?',
                'q_en': 'Do you work irregular hours or shift work?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır, düzenli mesai saatlerim var', 'No, I have regular working hours', 0),
                    ('Bazen fazla mesai yaparım', 'I sometimes work overtime', 1),
                    ('Düzensiz çalışma saatlerim var', 'I have irregular working hours', 2),
                    ('Gece vardiyası veya dönüşümlü vardiya çalışıyorum', 'I work night shifts or rotating shifts', 3),
                ],
            },
            {
                'q_tr': 'Bu uyku sorununuz ne kadar süredir devam ediyor?',
                'q_en': 'How long has this sleep problem been going on?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Uyku sorunum yok', 'I don\'t have a sleep problem', 0),
                    ('1 aydan az', 'Less than 1 month', 1),
                    ('1-3 ay', '1-3 months', 2),
                    ('3 aydan fazla', 'More than 3 months', 3),
                ],
            },
            {
                'q_tr': 'Uyku ilacı veya alkol kullanarak uyumaya çalışıyor musunuz?',
                'q_en': 'Do you try to sleep using sleep medication or alcohol?',
                'help_tr': '',
                'help_en': '',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Nadiren (ayda birkaç kez)', 'Rarely (a few times a month)', 1),
                    ('Sıklıkla (haftada birkaç kez)', 'Often (a few times a week)', 2),
                    ('Her gece', 'Every night', 3),
                ],
            },
        ]

        self._create_questions(test, questions)

        ranges = [
            ('low', 0, 7, 'Düşük Uykusuzluk Riski', 'Low Insomnia Risk',
             'Uykusuzluk belirtileriniz minimal düzeyde. Uyku alışkanlıklarınız genel olarak sağlıklı görünüyor.',
             'Your insomnia symptoms are at a minimal level. Your sleep habits appear generally healthy.',
             'Sağlıklı uyku alışkanlıklarınızı sürdürmeye devam edin.',
             'Continue maintaining your healthy sleep habits.',
             'green'),
            ('moderate', 8, 15, 'Orta Düzey Uykusuzluk Riski', 'Moderate Insomnia Risk',
             'Bazı uykusuzluk belirtileri mevcut. Uyku hijyeni önlemlerinin alınması önerilir.',
             'Some insomnia symptoms are present. Sleep hygiene measures are recommended.',
             'Uyku hijyeni kurallarını uygulayın: düzenli uyku saatleri, ekran sınırlaması, rahat uyku ortamı. Belirtiler devam ederse doktora başvurun.',
             'Apply sleep hygiene rules: regular sleep schedule, screen limitation, comfortable sleep environment. Consult a doctor if symptoms persist.',
             'yellow'),
            ('high', 16, 22, 'Yüksek Uykusuzluk Riski', 'High Insomnia Risk',
             'Belirgin uykusuzluk belirtileri mevcut. Kronik uykusuzluk gelişme riski yüksek.',
             'Significant insomnia symptoms are present. Risk of developing chronic insomnia is high.',
             'Bir uyku uzmanına veya psikiyatriste başvurmanız önerilir. Bilişsel davranışçı terapi (BDT-I) uykusuzluk tedavisinde en etkili yöntemdir.',
             'Consulting a sleep specialist or psychiatrist is recommended. Cognitive behavioral therapy (CBT-I) is the most effective method for insomnia treatment.',
             'orange'),
            ('severe', 23, 30, 'Çok Yüksek Uykusuzluk Riski', 'Very High Insomnia Risk',
             'Ciddi uykusuzluk belirtileri mevcut. Bu durum fiziksel ve ruhsal sağlığınızı önemli ölçüde tehdit edebilir.',
             'Serious insomnia symptoms are present. This may significantly threaten your physical and mental health.',
             'En kısa sürede bir uyku uzmanına başvurunuz. Profesyonel değerlendirme ve kapsamlı tedavi planı acil olarak gereklidir.',
             'Please consult a sleep specialist as soon as possible. Professional evaluation and comprehensive treatment plan is urgently needed.',
             'red'),
        ]
        self._create_ranges(test, ranges)

    # ─── 4. Uyku Apnesi Risk Farkındalık Anketi ───────────────────────

    def _create_apnea_risk_test(self):
        test = SleepScreeningTest.objects.create(
            slug='uyku-apnesi-riski',
            title_tr='Uyku Apnesi Risk Farkındalık Anketi',
            title_en='Sleep Apnea Risk Awareness Questionnaire',
            description_tr='Obstrüktif uyku apnesi (OUA) risk faktörlerinizi değerlendirin. Genel klinik bilgiye dayalı farkındalık anketi.',
            description_en='Evaluate your risk factors for obstructive sleep apnea (OSA). An awareness questionnaire based on general clinical knowledge.',
            instructions_tr='Aşağıdaki soruları kendiniz veya yatak partnerinizin gözlemlerine göre yanıtlayın.',
            instructions_en='Answer the following questions based on your own observations or those of your bed partner.',
            icon='wind',
            duration_minutes=3,
            order=4,
        )

        questions = [
            {
                'q_tr': 'Horlama durumunuz nedir?',
                'q_en': 'What is your snoring status?',
                'help_tr': 'Yatak partnerinize veya aile üyelerinize sorabilirsiniz.',
                'help_en': 'You can ask your bed partner or family members.',
                'options': [
                    ('Horlamam', 'I don\'t snore', 0),
                    ('Hafif horlarım (kapı kapalıyken duyulmaz)', 'I snore lightly (not heard through closed door)', 1),
                    ('Orta düzeyde horlarım (kapı kapalıyken duyulur)', 'I snore moderately (heard through closed door)', 2),
                    ('Çok gürültülü horlarım (diğer odalardan duyulur)', 'I snore very loudly (heard from other rooms)', 3),
                ],
            },
            {
                'q_tr': 'Uyku sırasında nefesinizin durduğu veya tıkandığı söyleniyor mu?',
                'q_en': 'Have you been told that your breathing stops or gets blocked during sleep?',
                'help_tr': 'Bu durum "apne" olarak adlandırılır ve tanı için çok önemlidir.',
                'help_en': 'This condition is called "apnea" and is very important for diagnosis.',
                'options': [
                    ('Hayır, böyle bir durumum yok', 'No, I don\'t have this issue', 0),
                    ('Nadiren söylendi', 'It\'s been mentioned rarely', 1),
                    ('Sıklıkla söyleniyor', 'It\'s mentioned frequently', 2),
                    ('Her gece gözlemleniyor', 'It\'s observed every night', 3),
                ],
            },
            {
                'q_tr': 'Sabah uyandığınızda ağız kuruluğu veya boğaz ağrısı yaşıyor musunuz?',
                'q_en': 'Do you experience dry mouth or sore throat when you wake up in the morning?',
                'help_tr': 'Ağızdan nefes alma, uyku apnesinin yaygın belirtilerindendir.',
                'help_en': 'Mouth breathing is a common sign of sleep apnea.',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Bazen', 'Sometimes', 1),
                    ('Sıklıkla', 'Often', 2),
                    ('Her sabah', 'Every morning', 3),
                ],
            },
            {
                'q_tr': 'Sabah baş ağrısı yaşıyor musunuz?',
                'q_en': 'Do you experience morning headaches?',
                'help_tr': 'Uyku apnesinde gece oksijen düşüşü sabah baş ağrısına neden olabilir.',
                'help_en': 'Nighttime oxygen drops in sleep apnea can cause morning headaches.',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Ayda birkaç kez', 'A few times a month', 1),
                    ('Haftada birkaç kez', 'A few times a week', 2),
                    ('Her sabah', 'Every morning', 3),
                ],
            },
            {
                'q_tr': 'Vücut kitle indeksiniz (BMI) ne kadardır?',
                'q_en': 'What is your body mass index (BMI)?',
                'help_tr': 'BMI = kilo(kg) / boy(m)². Örnek: 80kg, 1.75m → BMI = 26.1',
                'help_en': 'BMI = weight(kg) / height(m)². Example: 80kg, 1.75m → BMI = 26.1',
                'options': [
                    ('25\'ten az (normal kilolu)', 'Less than 25 (normal weight)', 0),
                    ('25-29.9 (fazla kilolu)', '25-29.9 (overweight)', 1),
                    ('30-34.9 (obez)', '30-34.9 (obese)', 2),
                    ('35 ve üzeri (ileri obez)', '35 and above (severely obese)', 3),
                ],
            },
            {
                'q_tr': 'Boyun çevreniz ne kadardır?',
                'q_en': 'What is your neck circumference?',
                'help_tr': 'Boyun çevresi büyüklüğü üst hava yolu daralması riskiyle ilişkilidir.',
                'help_en': 'Neck circumference is associated with upper airway narrowing risk.',
                'options': [
                    ('Erkek: <40cm / Kadın: <35cm', 'Male: <40cm / Female: <35cm', 0),
                    ('Erkek: 40-43cm / Kadın: 35-38cm', 'Male: 40-43cm / Female: 35-38cm', 1),
                    ('Erkek: 43-48cm / Kadın: 38-43cm', 'Male: 43-48cm / Female: 38-43cm', 2),
                    ('Erkek: >48cm / Kadın: >43cm', 'Male: >48cm / Female: >43cm', 3),
                ],
            },
            {
                'q_tr': 'Yaşınız kaçtır?',
                'q_en': 'How old are you?',
                'help_tr': 'Yaş ilerledikçe uyku apnesi riski artar.',
                'help_en': 'Sleep apnea risk increases with age.',
                'options': [
                    ('40 yaş altı', 'Under 40', 0),
                    ('40-49 yaş', '40-49 years', 1),
                    ('50-59 yaş', '50-59 years', 2),
                    ('60 yaş ve üzeri', '60 years and above', 3),
                ],
            },
            {
                'q_tr': 'Yüksek tansiyon (hipertansiyon) tedavisi alıyor musunuz?',
                'q_en': 'Are you receiving treatment for high blood pressure (hypertension)?',
                'help_tr': 'Uyku apnesi ve hipertansiyon arasında güçlü bir ilişki vardır.',
                'help_en': 'There is a strong relationship between sleep apnea and hypertension.',
                'options': [
                    ('Hayır, tansiyonum normal', 'No, my blood pressure is normal', 0),
                    ('Sınırda yüksek ama ilaç kullanmıyorum', 'Borderline high but not on medication', 1),
                    ('Tansiyon ilacı kullanıyorum, kontrol altında', 'On blood pressure medication, controlled', 2),
                    ('Birden fazla tansiyon ilacı kullanıyorum', 'Using multiple blood pressure medications', 3),
                ],
            },
            {
                'q_tr': 'Gece sık idrara kalkıyor musunuz?',
                'q_en': 'Do you frequently get up to urinate at night?',
                'help_tr': 'Noktüri (gece idrara kalkma) uyku apnesinin az bilinen belirtilerinden biridir.',
                'help_en': 'Nocturia is one of the lesser known symptoms of sleep apnea.',
                'options': [
                    ('Hayır veya nadiren', 'No or rarely', 0),
                    ('Gecede 1 kez', 'Once per night', 1),
                    ('Gecede 2-3 kez', '2-3 times per night', 2),
                    ('Gecede 3 kereden fazla', 'More than 3 times per night', 3),
                ],
            },
            {
                'q_tr': 'Ailenizde uyku apnesi tanısı alan biri var mı?',
                'q_en': 'Has anyone in your family been diagnosed with sleep apnea?',
                'help_tr': 'Genetik yatkınlık uyku apnesi riskini artırır.',
                'help_en': 'Genetic predisposition increases the risk of sleep apnea.',
                'options': [
                    ('Hayır', 'No', 0),
                    ('Uzak akrabada var', 'In a distant relative', 1),
                    ('Anne veya babada var', 'In mother or father', 2),
                    ('Birden fazla aile üyesinde var', 'In multiple family members', 3),
                ],
            },
        ]

        self._create_questions(test, questions)

        ranges = [
            ('low', 0, 7, 'Düşük Uyku Apnesi Riski', 'Low Sleep Apnea Risk',
             'Uyku apnesi risk faktörleriniz minimal düzeyde. Mevcut sağlıklı alışkanlıklarınızı sürdürün.',
             'Your sleep apnea risk factors are at a minimal level. Maintain your current healthy habits.',
             'Sağlıklı kilonuzu koruyun ve düzenli egzersiz yapın.',
             'Maintain a healthy weight and exercise regularly.',
             'green'),
            ('moderate', 8, 15, 'Orta Düzey Uyku Apnesi Riski', 'Moderate Sleep Apnea Risk',
             'Bazı uyku apnesi risk faktörleri mevcut. Belirtilerinizi takip etmeniz önerilir.',
             'Some sleep apnea risk factors are present. Monitoring your symptoms is recommended.',
             'Kilo kontrolü, alkol kısıtlaması ve sırt üstü yatmaktan kaçınma önerilir. Belirtiler artarsa doktora başvurun.',
             'Weight control, alcohol restriction, and avoiding sleeping on your back are recommended. Consult a doctor if symptoms increase.',
             'yellow'),
            ('high', 16, 22, 'Yüksek Uyku Apnesi Riski', 'High Sleep Apnea Risk',
             'Uyku apnesi açısından yüksek risk grubundasınız. Profesyonel değerlendirme önerilir.',
             'You are in a high-risk group for sleep apnea. Professional evaluation is recommended.',
             'Bir uyku uzmanına başvurarak polisomnografi (uyku testi) yaptırmanız önerilir. Tedavi edilmeyen uyku apnesi kalp ve damar hastalıkları riskini artırır.',
             'It is recommended to consult a sleep specialist for polysomnography (sleep test). Untreated sleep apnea increases the risk of cardiovascular diseases.',
             'orange'),
            ('severe', 23, 30, 'Çok Yüksek Uyku Apnesi Riski', 'Very High Sleep Apnea Risk',
             'Uyku apnesi açısından çok yüksek risk grubundasınız. Acil değerlendirme gereklidir.',
             'You are in a very high-risk group for sleep apnea. Urgent evaluation is required.',
             'En kısa sürede uyku laboratuvarında polisomnografi yaptırınız. CPAP veya diğer tedavi seçenekleri değerlendirilmelidir.',
             'Have a polysomnography done at a sleep laboratory as soon as possible. CPAP or other treatment options should be evaluated.',
             'red'),
        ]
        self._create_ranges(test, ranges)

    # ─── Helper Methods ────────────────────────────────────────────────

    def _create_questions(self, test, questions):
        for idx, q in enumerate(questions, start=1):
            question = SleepScreeningQuestion.objects.create(
                test=test,
                question_tr=q['q_tr'],
                question_en=q['q_en'],
                help_text_tr=q.get('help_tr', ''),
                help_text_en=q.get('help_en', ''),
                order=idx,
            )
            for opt_idx, (text_tr, text_en, score) in enumerate(q['options']):
                SleepScreeningOption.objects.create(
                    question=question,
                    text_tr=text_tr,
                    text_en=text_en,
                    score=score,
                    order=opt_idx,
                )

    def _create_ranges(self, test, ranges):
        for level, min_s, max_s, title_tr, title_en, desc_tr, desc_en, rec_tr, rec_en, color in ranges:
            SleepScreeningResultRange.objects.create(
                test=test,
                level=level,
                min_score=min_s,
                max_score=max_s,
                title_tr=title_tr,
                title_en=title_en,
                description_tr=desc_tr,
                description_en=desc_en,
                recommendation_tr=rec_tr,
                recommendation_en=rec_en,
                color=color,
            )
