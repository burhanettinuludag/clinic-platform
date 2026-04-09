"""
Mevcut haberleri doğru Türkçe karakterlerle günceller.
seed_news.py'deki verileri slug eşleşmesiyle günceller.
Kullanım: python3 manage.py reseed_news
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify


# seed_news.py ile aynı veri — doğru Türkçe karakterlerle
NEWS_DATA = [
    {
        'title_tr': 'FDA, Kronik Migren İçin Yeni CGRP Antagonisti İlacı Onayladı',
        'title_en': 'FDA Approves New CGRP Antagonist Drug for Chronic Migraine',
        'excerpt_tr': 'ABD Gıda ve İlaç Dairesi (FDA), kronik migren tedavisinde kullanılacak yeni nesil CGRP reseptör antagonisti ilacın kullanımını onayladı. İlaç, ayda 15 ve üzeri migren günü yaşayan hastalar için umut vaat ediyor.',
        'excerpt_en': 'The FDA has approved a new generation CGRP receptor antagonist for chronic migraine treatment. The drug promises hope for patients experiencing 15 or more migraine days per month.',
        'body_tr': '<h2>Yeni Tedavi Seçeneği</h2><p>FDA tarafından onaylanan yeni CGRP antagonisti ilaç, kronik migren hastalarında atak sıklığını ortalama %50 azaltıyor. Faz 3 klinik çalışmalarda 2.500 hasta üzerinde test edilen ilaç, plaseboya kıyasla anlamlı sonuçlar gösterdi.</p><h3>Klinik Çalışma Sonuçları</h3><p>12 haftalık tedavi sürecinde hastaların %65\'inde aylık migren gün sayısı yarısına indi. En sık görülen yan etkiler hafif bulantı ve enjeksiyon bölgesinde kızarıklıktı.</p><h3>Türkiye\'de Erişilebilirlik</h3><p>İlacın Türkiye\'de ruhsat süreci 2026 yılının ikinci yarısında başlaması bekleniyor. Uzmanlar, bu ilacın özellikle mevcut tedavilere yanıt vermeyen hastalarda önemli bir seçenek olacağını belirtiyor.</p>',
        'body_en': '<h2>New Treatment Option</h2><p>The newly FDA-approved CGRP antagonist reduces attack frequency by an average of 50% in chronic migraine patients. The drug was tested on 2,500 patients in Phase 3 clinical trials and showed significant results compared to placebo.</p>',
    },
    {
        'title_tr': 'Migren Aurasının Beyindeki Mekanizması İlk Kez Görüntülendi',
        'title_en': 'Brain Mechanism of Migraine Aura Imaged for First Time',
        'excerpt_tr': 'Harvard ve MIT araştırmacıları, migren aurasının beyinde nasıl yayıldığını ilk kez canlı olarak görüntülemeyi başardı. Bulgular yeni tedavi hedeflerinin önünü açıyor.',
        'excerpt_en': 'Harvard and MIT researchers have successfully imaged how migraine aura spreads in the brain for the first time. Findings open the door to new treatment targets.',
        'body_tr': '<h2>Çığır Açan Araştırma</h2><p>Nature Medicine dergisinde yayınlanan çalışma, kortikal yayılan depresyon (CSD) olarak bilinen migren aurasının beyindeki hareketini ultrasonografik yöntemlerle görüntüledi. Araştırma, auranın beyin kabuğunda dakikada 3-5 mm hızla yayıldığını doğruladı.</p><p>Bu keşif, özellikle auralı migren hastalarına yönelik hedefe yönelik tedavilerin geliştirilmesinde kilit rol oynayabilir.</p>',
        'body_en': '<h2>Groundbreaking Research</h2><p>Published in Nature Medicine, the study imaged cortical spreading depression (CSD) movement using ultrasonographic methods.</p>',
    },
    {
        'title_tr': 'Türkiye\'de Migren Prevalansı Araştırması: Her 5 Kadından 1\'i Etkileniyor',
        'title_en': 'Migraine Prevalence Study in Turkey: 1 in 5 Women Affected',
        'excerpt_tr': 'Türk Nöroloji Derneği\'nin 15 ilde gerçekleştirdiği kapsamlı araştırma, Türkiye\'deki migren prevalansının beklenenin üzerinde olduğunu ortaya koydu.',
        'excerpt_en': 'A comprehensive study by the Turkish Neurological Society across 15 provinces revealed that migraine prevalence in Turkey is higher than expected.',
        'body_tr': '<h2>Çalışma Detayları</h2><p>25.000 kişilik örneklem üzerinde gerçekleştirilen çalışma, genel popülasyonda migren prevalansının %16.4 olduğunu belirledi. Kadınlarda bu oran %21.8\'e yükselirken, erkeklerde %10.2 olarak saptandı.</p><p>Araştırma ayrıca migren hastalarının yalnızca %30\'unun düzenli tedavi gördüğünün altını çizdi.</p>',
        'body_en': '<h2>Study Details</h2><p>The study of 25,000 people found migraine prevalence in the general population to be 16.4%.</p>',
    },
    {
        'title_tr': '2026 Avrupa Baş Ağrısı Kongresi: Önemli Sonuçlar',
        'title_en': '2026 European Headache Congress: Key Findings',
        'excerpt_tr': 'Barcelona\'da düzenlenen kongrede sunulan yeni çalışmalar, migren tedavisinde nöral stimülasyon yöntemlerinin etkinliğini doğruladı.',
        'excerpt_en': 'New studies presented at the Barcelona congress confirmed the efficacy of neural stimulation methods in migraine treatment.',
        'body_tr': '<p>2026 Avrupa Baş Ağrısı Kongresi\'nde sunulan en dikkat çekici çalışmalardan biri, vagus siniri stimülasyonunun (VNS) episodik migrende atak sıklığını %40 azalttığını gösterdi.</p>',
        'body_en': '<p>One of the most notable studies presented showed vagus nerve stimulation (VNS) reduced attack frequency by 40% in episodic migraine.</p>',
    },
    {
        'title_tr': 'Epilepside Yapay Zekâ Destekli Nöbet Tahmini: Yeni Giyilebilir Cihaz',
        'title_en': 'AI-Powered Seizure Prediction in Epilepsy: New Wearable Device',
        'excerpt_tr': 'MIT mühendisleri, epilepsi nöbetlerini ortalama 45 dakika önceden tahmin edebilen yapay zekâ destekli yeni bir giyilebilir cihaz geliştirdi.',
        'excerpt_en': 'MIT inventors have developed a new AI-powered wearable device that can predict epileptic seizures an average of 45 minutes in advance.',
        'body_tr': '<h2>Devrimci Teknoloji</h2><p>Bileklik formundaki cihaz, EEG sinyallerini, kalp hızı değişkenliğini ve deri iletkenliğini sürekli izleyerek yapay zekâ algoritması ile nöbet öncesi değişiklikleri tespit ediyor. Klinik testlerde %89 doğruluk oranına ulaşılan cihaz, 2027\'de ticarileşmesi bekleniyor.</p><p>Bu teknoloji özellikle kontrolsüz epilepsi hastalarına büyük özgürlük sağlayabilir.</p>',
        'body_en': '<h2>Revolutionary Technology</h2><p>The wristband-form device continuously monitors EEG signals, heart rate variability and skin conductance using AI algorithms to detect pre-seizure changes.</p>',
    },
    {
        'title_tr': 'EMA, Dirençli Epilepsi İçin Cenobamat\'ı Onayladı',
        'title_en': 'EMA Approves Cenobamate for Drug-Resistant Epilepsy',
        'excerpt_tr': 'Avrupa İlaç Ajansı (EMA), dirençli fokal epilepsi tedavisi için cenobamat etken maddeli ilacın kullanımını onayladı.',
        'excerpt_en': 'The European Medicines Agency has approved cenobamate for the treatment of drug-resistant focal epilepsy.',
        'body_tr': '<h2>Dirençli Epilepside Umut</h2><p>Cenobamat, sodyum kanal blokeri mekanizmasına ek olarak GABA-A reseptörlerini pozitif yönde modüle ederek etki gösteriyor. Klinik çalışmalarda dirençli fokal epilepsi hastalarının %20\'sinde tam nöbet kontrolü sağlandı.</p>',
        'body_en': '<h2>Hope for Drug-Resistant Epilepsy</h2><p>Cenobamate works through sodium channel blocking plus positive modulation of GABA-A receptors.</p>',
    },
    {
        'title_tr': 'Çocukluk Çağı Epilepsisinde Erken Tedavinin Önemi: Yeni Kılavuz',
        'title_en': 'Importance of Early Treatment in Childhood Epilepsy: New Guideline',
        'excerpt_tr': 'ILAE\'nin yayınladığı yeni kılavuz, çocukluk çağı epilepsisinde erken ve agresif tedavinin uzun vadeli sonuçları iyileştirdiğini vurguluyor.',
        'excerpt_en': 'ILAE\'s new guideline emphasizes that early and aggressive treatment in childhood epilepsy improves long-term outcomes.',
        'body_tr': '<p>Uluslararası Epilepsi Ligi (ILAE) tarafından yayınlanan güncellenmiş kılavuz, ilk nöbetin ardından 6 ay içinde tedaviye başlanmasının, 10 yıllık nöbet kontrolü oranlarını %35 artırdığını gösteriyor.</p>',
        'body_en': '<p>The updated guideline by ILAE shows that starting treatment within 6 months of the first seizure increases 10-year seizure control rates by 35%.</p>',
    },
    {
        'title_tr': 'Alzheimer Kan Testi Erken Tanıda Çığırları Açıyor',
        'title_en': 'Alzheimer Blood Test Opens Breakthrough in Early Diagnosis',
        'excerpt_tr': 'Yeni geliştirilen kan testi, Alzheimer hastalığını semptomlar başlamadan 15 yıl öncesinden tespit edebiliyor. Test, fosforile tau 217 proteinini ölçüyor.',
        'excerpt_en': 'A newly developed blood test can detect Alzheimer\'s disease up to 15 years before symptoms appear by measuring phosphorylated tau 217 protein.',
        'body_tr': '<h2>Erken Tanı Devrimi</h2><p>Lund Üniversitesi\'nden araştırmacıların geliştirdiği kan testi, fosforile tau 217 (p-tau217) seviyesini ölçerek Alzheimer hastalığını %96 doğrulukla tespit edebiliyor. Bu, şu anda kullanılan beyin-omurilik sıvısı testleri ve PET taramalarından çok daha pratik ve ucuz bir yöntem.</p><h3>Klinik Önemi</h3><p>Erken tanı, hastaların henüz bilişsel gerileme başlamadan tedaviye başlayabilmesini sağlıyor. 2026 yılı içinde bu testin klinik kullanıma girmesi bekleniyor.</p>',
        'body_en': '<h2>Early Diagnosis Revolution</h2><p>The blood test developed by Lund University researchers can detect Alzheimer\'s disease with 96% accuracy by measuring phosphorylated tau 217 levels.</p>',
    },
    {
        'title_tr': 'Lecanemab Türkiye\'de Ruhsat Aldı: Erken Evre Alzheimer Tedavisi',
        'title_en': 'Lecanemab Receives Approval in Turkey: Early Stage Alzheimer Treatment',
        'excerpt_tr': 'Amiloid plak temizleyici antikor tedavisi lecanemab, TİTCK tarafından erken evre Alzheimer hastalığı için onay aldı.',
        'excerpt_en': 'Amyloid plaque-clearing antibody therapy lecanemab has been approved by TITCK for early-stage Alzheimer\'s disease.',
        'body_tr': '<h2>Türkiye\'de İlk</h2><p>Lecanemab, beyindeki amiloid plakları temizleyerek Alzheimer hastalığının ilerlemesini yavaşlatıyor. Faz 3 klinik çalışmalarda bilişsel gerilemeyi %27 azalttığı gösterildi. İlaç, ayda 2 kez intravenöz olarak uygulanacak.</p><p>TİTCK, ilacın sınırlı merkezlerde ve uzman gözetiminde kullanılması şartını koydu.</p>',
        'body_en': '<h2>First in Turkey</h2><p>Lecanemab slows Alzheimer\'s progression by clearing amyloid plaques in the brain. Phase 3 trials showed 27% reduction in cognitive decline.</p>',
    },
    {
        'title_tr': 'Günlük 30 Dakika Yürüyüşün Demans Riskini %40 Azalttığı Kanıtlandı',
        'title_en': 'Daily 30-Minute Walking Proven to Reduce Dementia Risk by 40%',
        'excerpt_tr': 'Lancet\'te yayınlanan büyük ölçekli çalışma, düzenli fiziksel aktivitenin demans riskini önemli ölçüde azalttığını doğruladı.',
        'excerpt_en': 'A large-scale study published in The Lancet confirmed that regular physical activity significantly reduces dementia risk.',
        'body_tr': '<p>78.000 kişiyi 12 yıl boyunca takip eden çalışma, haftada en az 150 dakika orta yoğunlukta fiziksel aktivitenin tüm-neden demans riskini %40 azalttığını belirledi. Etki özellikle vasküler demans tipinde daha belirgin görülüyor.</p>',
        'body_en': '<p>A study following 78,000 people for 12 years found that at least 150 minutes of moderate physical activity per week reduces all-cause dementia risk by 40%.</p>',
    },
    {
        'title_tr': 'Bilişsel Oyunların Hafif Bilişsel Bozuklukta Etkisi: Meta-Analiz Sonuçları',
        'title_en': 'Effect of Cognitive Games on Mild Cognitive Impairment: Meta-Analysis Results',
        'excerpt_tr': '42 çalışmayı kapsayan meta-analiz, dijital bilişsel egzersizlerin hafif bilişsel bozuklukta dikkat ve çalışma belleğini iyileştirdiğini ortaya koydu.',
        'excerpt_en': 'A meta-analysis covering 42 studies revealed that digital cognitive exercises improve attention and working memory in mild cognitive impairment.',
        'body_tr': '<p>JAMA Neurology\'de yayınlanan meta-analiz, düzenli bilişsel oyun oynamanın (haftada 3+ seans) hafif bilişsel bozukluk hastalarında dikkat (%18 iyileşme), çalışma belleği (%22 iyileşme) ve işleme hızı (%15 iyileşme) alanlarında anlamlı kazanımlar sağladığını gösterdi.</p>',
        'body_en': '<p>Published in JAMA Neurology, the meta-analysis showed that regular cognitive gaming (3+ sessions per week) provides significant gains in attention (18%), working memory (22%) and processing speed (15%).</p>',
    },
    {
        'title_tr': 'Nörolojik Hastalıklarda Bağırsak-Beyin Ekseni: Mikrobiyom Tedavisi İçin Yeni Kanıtlar',
        'title_en': 'Gut-Brain Axis in Neurological Diseases: New Evidence for Microbiome Therapy',
        'excerpt_tr': 'Nature Neuroscience\'ta yayınlanan derleme, bağırsak mikrobiyomunun migren, epilepsi ve demans dahil birden fazla nörolojik hastalıkta rol oynadığını gösteriyor.',
        'excerpt_en': 'A review in Nature Neuroscience shows gut microbiome plays a role in multiple neurological diseases including migraine, epilepsy and dementia.',
        'body_tr': '<p>Derleme, spesifik bağırsak bakterilerinin nörotransmitter üretimine doğrudan katkıları olduğunu ve disbiyozis durumunun nörolojik hastalık riskini artırdığını özetliyor. Probiyotik müdahalelerin her üç hastalıkta da faydalı etkileri kanıtlanmıştır.</p>',
        'body_en': '<p>The review summarizes that specific gut bacteria directly contribute to neurotransmitter production and dysbiosis increases neurological disease risk.</p>',
    },
    {
        'title_tr': 'Yeni Nesil Nörostimülasyon Cihazı Üç Hastalıkta Birden Etkili',
        'title_en': 'Next-Gen Neurostimulation Device Effective in Three Diseases',
        'excerpt_tr': 'Programlanabilir nörostimülasyon cihazı, migren, epilepsi ve hafif bilişsel bozuklukta klinik denemelerde başarılı sonuçlar veriyor.',
        'excerpt_en': 'Programmable neurostimulation device shows successful results in clinical trials for migraine, epilepsy and mild cognitive impairment.',
        'body_tr': '<p>Boston merkezli startup\'ın geliştirdiği minyatürize nörostimülasyon cihazı, farklı frekanslarda stimülasyon uygulayarak üç farklı nörolojik tabloda da etkili olabiliyor. FDA onay süreci başlamış durumda.</p>',
        'body_en': '<p>The miniaturized neurostimulation device can be effective in three different neurological conditions by applying stimulation at different frequencies.</p>',
    },
    {
        'title_tr': 'Türkiye Nöroloji Haftası 2026: Farkındalığın Önemi',
        'title_en': 'Turkey Neurology Week 2026: Importance of Awareness',
        'excerpt_tr': 'Türk Nöroloji Derneği, 2026 Nöroloji Haftası kapsamında ülke genelinde ücretsiz nörolojik muayene kampanyası başlattı.',
        'excerpt_en': 'Turkish Neurological Society launched a free neurological examination campaign nationwide as part of 2026 Neurology Week.',
        'body_tr': '<p>10-17 Mart tarihleri arasında düzenlenen etkinlikte 81 ilde ücretsiz nörolojik muayene imkânı sunuluyor. Kampanya özellikle migren, epilepsi ve demans farkındalığına odaklanıyor.</p>',
        'body_en': '<p>The event held March 10-17 offers free neurological examinations in all 81 provinces, focusing on migraine, epilepsy and dementia awareness.</p>',
    },
]


class Command(BaseCommand):
    help = 'Mevcut haber içeriklerini doğru Türkçe karakterlerle günceller'

    def handle(self, *args, **options):
        from apps.content.models import NewsArticle

        updated = 0
        not_found = 0

        for news in NEWS_DATA:
            slug = slugify(news['title_en'][:180], allow_unicode=True)

            try:
                article = NewsArticle.objects.get(slug=slug)
            except NewsArticle.DoesNotExist:
                not_found += 1
                self.stdout.write(self.style.WARNING(f'  Bulunamadı: {slug}'))
                continue

            article.title_tr = news['title_tr']
            article.excerpt_tr = news['excerpt_tr']
            article.body_tr = news['body_tr']
            article.title_en = news['title_en']
            article.excerpt_en = news['excerpt_en']
            article.body_en = news['body_en']
            article.save(update_fields=[
                'title_tr', 'excerpt_tr', 'body_tr',
                'title_en', 'excerpt_en', 'body_en',
                'updated_at',
            ])

            updated += 1
            self.stdout.write(self.style.SUCCESS(f'  Güncellendi: {article.title_tr[:60]}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Tamamlandı: {updated} güncellendi, {not_found} bulunamadı.'))
