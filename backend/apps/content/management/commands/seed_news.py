"""
Ornek haber ve blog icerikleri olusturur.
Kullanim: python3 manage.py seed_news
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
import random


# ==================== HABER VERILERI ====================

NEWS_DATA = [
    # MIGREN HABERLERI
    {
        'title_tr': 'FDA, Kronik Migren Icin Yeni CGRP Antagonisti Ilaci Onayladi',
        'title_en': 'FDA Approves New CGRP Antagonist Drug for Chronic Migraine',
        'excerpt_tr': 'ABD Gida ve Ilac Dairesi (FDA), kronik migren tedavisinde kullanilacak yeni nesil CGRP reseptor antagonisti ilacin kullanimini onayladi. Ilac, ayda 15 ve uzeri migren gunu yasayan hastalar icin umut vaat ediyor.',
        'excerpt_en': 'The FDA has approved a new generation CGRP receptor antagonist for chronic migraine treatment. The drug promises hope for patients experiencing 15 or more migraine days per month.',
        'body_tr': '<h2>Yeni Tedavi Secenegi</h2><p>FDA tarafindan onaylanan yeni CGRP antagonisti ilac, kronik migren hastalarinda atak sikligini ortalama %50 azaltiyor. Faz 3 klinik calismalarda 2.500 hasta uzerinde test edilen ilac, plaseboya kiyasla anlamli sonuclar gosterdi.</p><h3>Klinik Calisma Sonuclari</h3><p>12 haftalik tedavi surecinde hastalarin %65\'inde aylik migren gun sayisi yarisina indi. En sik gorulen yan etkiler hafif bulanti ve enjeksiyon bolgesinde kizariklikti.</p><h3>Turkiye\'de Erisilebilirlik</h3><p>Ilacin Turkiye\'de ruhsat sureci 2026 yilinin ikinci yarisinda baslamasi bekleniyor. Uzmanlar, bu ilacin ozellikle mevcut tedavilere yanit vermeyen hastalarda onemli bir secenek olacagini belirtiyor.</p>',
        'body_en': '<h2>New Treatment Option</h2><p>The newly FDA-approved CGRP antagonist reduces attack frequency by an average of 50% in chronic migraine patients. The drug was tested on 2,500 patients in Phase 3 clinical trials and showed significant results compared to placebo.</p>',
        'category': 'fda_approval',
        'priority': 'urgent',
        'diseases': ['migraine'],
    },
    {
        'title_tr': 'Migren Aurasinin Beyindeki Mekanizmasi Ilk Kez Goruntulendi',
        'title_en': 'Brain Mechanism of Migraine Aura Imaged for First Time',
        'excerpt_tr': 'Harvard ve MIT arastirmacilari, migren aurasinin beyinde nasil yayildigini ilk kez canli olarak goruntulemeyi basardi. Bulgular yeni tedavi hedeflerinin onunu aciyor.',
        'excerpt_en': 'Harvard and MIT researchers have successfully imaged how migraine aura spreads in the brain for the first time. Findings open the door to new treatment targets.',
        'body_tr': '<h2>Cigirlara Arasturma</h2><p>Nature Medicine dergisinde yayinlanan calisma, kortikal yayilan depresyon (CSD) olarak bilinen migren aurasinin beyindeki hareketini ultrasonografik yontemlerle goruntuledi. Arastirma, auranin beyin kabugunda dakikada 3-5 mm hizla yayildigini dogruladi.</p><p>Bu kesif, ozellikle auralı migren hastalarina yonelik hedefe yonelik tedavilerin gelistirilmesinde kilit rol oynayabilir.</p>',
        'body_en': '<h2>Groundbreaking Research</h2><p>Published in Nature Medicine, the study imaged cortical spreading depression (CSD) movement using ultrasonographic methods.</p>',
        'category': 'clinical_trial',
        'priority': 'high',
        'diseases': ['migraine'],
    },
    {
        'title_tr': 'Turkiye\'de Migren Prevalansi Arastirmasi: Her 5 Kadindan 1\'i Etkileniyor',
        'title_en': 'Migraine Prevalence Study in Turkey: 1 in 5 Women Affected',
        'excerpt_tr': 'Turk Noroloji Dernegi\'nin 15 ilde gerceklestirdigi kapsamli arastirma, Turkiye\'deki migren prevalansinin beklenenin uzerinde oldugunu ortaya koydu.',
        'excerpt_en': 'A comprehensive study by the Turkish Neurological Society across 15 provinces revealed that migraine prevalence in Turkey is higher than expected.',
        'body_tr': '<h2>Calisma Detaylari</h2><p>25.000 kisilik orneklem uzerinde gerceklestirilen calisma, genel populasyonda migren prevalansinin %16.4 oldugunu belirledi. Kadinlarda bu oran %21.8\'e yukselerken, erkeklerde %10.2 olarak saptandi.</p><p>Arastirma ayrica migren hastalarinin yalnizca %30\'unun duzenli tedavi gordugunun altini cizdi.</p>',
        'body_en': '<h2>Study Details</h2><p>The study of 25,000 people found migraine prevalence in the general population to be 16.4%.</p>',
        'category': 'turkey_news',
        'priority': 'medium',
        'diseases': ['migraine'],
    },
    {
        'title_tr': '2026 Avrupa Bas Agrisi Kongresi: Onemli Sonuclar',
        'title_en': '2026 European Headache Congress: Key Findings',
        'excerpt_tr': 'Barcelona\'da duzenlenen kongrede sunulan yeni calismalar, migren tedavisinde noral stimulasyon yontemlerinin etkinligini dogruladi.',
        'excerpt_en': 'New studies presented at the Barcelona congress confirmed the efficacy of neural stimulation methods in migraine treatment.',
        'body_tr': '<p>2026 Avrupa Bas Agrisi Kongresi\'nde sunulan en dikkat cekici calismalardan biri, vagus siniri stimulasyonunun (VNS) episodik migrende atak sikligini %40 azalttigi gosterdi.</p>',
        'body_en': '<p>One of the most notable studies presented showed vagus nerve stimulation (VNS) reduced attack frequency by 40% in episodic migraine.</p>',
        'category': 'congress',
        'priority': 'medium',
        'diseases': ['migraine'],
    },

    # EPILEPSI HABERLERI
    {
        'title_tr': 'Epilepside Yapay Zeka Destekli Nobet Tahmini: Yeni Giyilebilir Cihaz',
        'title_en': 'AI-Powered Seizure Prediction in Epilepsy: New Wearable Device',
        'excerpt_tr': 'MIT mucitleri, epilepsi nobetlerini ortalama 45 dakika onceden tahmin edebilen yapay zeka destekli yeni bir giyilebilir cihaz gelistirdi.',
        'excerpt_en': 'MIT inventors have developed a new AI-powered wearable device that can predict epileptic seizures an average of 45 minutes in advance.',
        'body_tr': '<h2>Devrimci Teknoloji</h2><p>Bileklik formundaki cihaz, EEG sinyallerini, kalp hizi degiskenligini ve deri iletkenligini surekli izleyerek yapay zeka algoritmasi ile nobet oncesi degisiklikleri tespit ediyor. Klinik testlerde %89 dogruluk oranina ulasilan cihaz, 2027\'de ticarilesmesi bekleniyor.</p><p>Bu teknoloji ozellikle kontrolsuz epilepsi hastalarina buyuk ozgurluk saglayabilir.</p>',
        'body_en': '<h2>Revolutionary Technology</h2><p>The wristband-form device continuously monitors EEG signals, heart rate variability and skin conductance using AI algorithms to detect pre-seizure changes.</p>',
        'category': 'new_device',
        'priority': 'high',
        'diseases': ['epilepsy'],
    },
    {
        'title_tr': 'EMA, Direncli Epilepsi Icin Cenobamat\'i Onayladi',
        'title_en': 'EMA Approves Cenobamate for Drug-Resistant Epilepsy',
        'excerpt_tr': 'Avrupa Ilac Ajansi (EMA), direncli fokal epilepsi tedavisi icin cenobamat etken maddeli ilacin kullanimini onayladi.',
        'excerpt_en': 'The European Medicines Agency has approved cenobamate for the treatment of drug-resistant focal epilepsy.',
        'body_tr': '<h2>Direncli Epilepside Umut</h2><p>Cenobamat, sodyum kanal bloker mekanizmasina ek olarak GABA-A reseptorlerini pozitif yonde module ederek etki gosteriyor. Klinik calismalarda direncli fokal epilepsi hastalarinin %20\'sinde tam nobet kontrolu saglandi.</p>',
        'body_en': '<h2>Hope for Drug-Resistant Epilepsy</h2><p>Cenobamate works through sodium channel blocking plus positive modulation of GABA-A receptors.</p>',
        'category': 'ema_approval',
        'priority': 'urgent',
        'diseases': ['epilepsy'],
    },
    {
        'title_tr': 'Cocukluk Cagi Epilepsisinde Erken Tedavinin Onemi: Yeni Kilavuz',
        'title_en': 'Importance of Early Treatment in Childhood Epilepsy: New Guideline',
        'excerpt_tr': 'ILAE\'nin yayinladigi yeni kilavuz, cocukluk cagi epilepsisinde erken ve agresif tedavinin uzun vadeli sonuclari iyilestirdigini vurguluyor.',
        'excerpt_en': 'ILAE\'s new guideline emphasizes that early and aggressive treatment in childhood epilepsy improves long-term outcomes.',
        'body_tr': '<p>Uluslararasi Epilepsi Ligi (ILAE) tarafindan yayinlanan guncellenmis kilavuz, ilk nobetin ardindan 6 ay icinde tedaviye baslanmasinin, 10 yillik nobet kontrolu oranlarini %35 artirdigini gosteriyor.</p>',
        'body_en': '<p>The updated guideline by ILAE shows that starting treatment within 6 months of the first seizure increases 10-year seizure control rates by 35%.</p>',
        'category': 'guideline_update',
        'priority': 'medium',
        'diseases': ['epilepsy'],
    },

    # DEMANS HABERLERI
    {
        'title_tr': 'Alzheimer Kan Testi Erken Tanida Cigirlari Aciyor',
        'title_en': 'Alzheimer Blood Test Opens Breakthrough in Early Diagnosis',
        'excerpt_tr': 'Yeni gelistirilen kan testi, Alzheimer hastaligini semptomlar baslama dan 15 yil oncesinden tespit edebiliyor. Test, fosforile tau 217 proteinini olcuyor.',
        'excerpt_en': 'A newly developed blood test can detect Alzheimer\'s disease up to 15 years before symptoms appear by measuring phosphorylated tau 217 protein.',
        'body_tr': '<h2>Erken Tani Devrimi</h2><p>Lund Universitesi\'nden arastirmacilarin gelistirdigi kan testi, fosforile tau 217 (p-tau217) seviyesini olcerek Alzheimer hastaligini %96 dogrulukla tespit edebiliyor. Bu, su anda kullanilan beyin-omurilik sivisi testleri ve PET taramalarindan cok daha pratik ve ucuz bir yontem.</p><h3>Klinik Onemi</h3><p>Erken tani, hastalarin henuz bilissel gerileme baslamadan tedaviye baslayabilmesini sagliyor. 2026 yili icinde bu testin klinik kullanima girmesi bekleniyor.</p>',
        'body_en': '<h2>Early Diagnosis Revolution</h2><p>The blood test developed by Lund University researchers can detect Alzheimer\'s disease with 96% accuracy by measuring phosphorylated tau 217 levels.</p>',
        'category': 'clinical_trial',
        'priority': 'urgent',
        'diseases': ['dementia'],
    },
    {
        'title_tr': 'Lecanemab Turkiye\'de Ruhsat Aldi: Erken Evre Alzheimer Tedavisi',
        'title_en': 'Lecanemab Receives Approval in Turkey: Early Stage Alzheimer Treatment',
        'excerpt_tr': 'Amiloid plak temizleyici antikor tedavisi lecanemab, TITCK tarafindan erken evre Alzheimer hastaligi icin onay aldi.',
        'excerpt_en': 'Amyloid plaque-clearing antibody therapy lecanemab has been approved by TITCK for early-stage Alzheimer\'s disease.',
        'body_tr': '<h2>Turkiye\'de Ilk</h2><p>Lecanemab, beyindeki amiloid plaklari temizleyerek Alzheimer hastaliginin ilerlemesini yavaslatıyor. Faz 3 klinik calismalarda bilissel gerilemeyi %27 azalttigi gosterildi. Ilac, ayda 2 kez intravenoz olarak uygulanacak.</p><p>TITCK, ilacin sinirli merkezlerde ve uzman gozetiminde kullanilmasi sartini koydu.</p>',
        'body_en': '<h2>First in Turkey</h2><p>Lecanemab slows Alzheimer\'s progression by clearing amyloid plaques in the brain. Phase 3 trials showed 27% reduction in cognitive decline.</p>',
        'category': 'turkey_approval',
        'priority': 'urgent',
        'diseases': ['dementia'],
    },
    {
        'title_tr': 'Gunluk 30 Dakika Yuruyusun Demans Riskini %40 Azalttigi Kanitlandi',
        'title_en': 'Daily 30-Minute Walking Proven to Reduce Dementia Risk by 40%',
        'excerpt_tr': 'Lancet\'te yayinlanan buyuk olcekli calisma, duzenli fiziksel aktivitenin demans riskini onemli olcude azalttigi dogruladi.',
        'excerpt_en': 'A large-scale study published in The Lancet confirmed that regular physical activity significantly reduces dementia risk.',
        'body_tr': '<p>78.000 kisiyi 12 yil boyunca takip eden calisma, haftada en az 150 dakika orta yogunlukta fiziksel aktivitenin tum-neden demans riskini %40 azalttigi belirledi. Etki ozellikle vaskuler demans tipinde daha belirgin goruluyor.</p>',
        'body_en': '<p>A study following 78,000 people for 12 years found that at least 150 minutes of moderate physical activity per week reduces all-cause dementia risk by 40%.</p>',
        'category': 'popular_science',
        'priority': 'medium',
        'diseases': ['dementia'],
    },
    {
        'title_tr': 'Bilissel Oyunlarin Hafif Bilissel Bozuklukta Etkisi: Meta-Analiz Sonuclari',
        'title_en': 'Effect of Cognitive Games on Mild Cognitive Impairment: Meta-Analysis Results',
        'excerpt_tr': '42 calismayi kapsayan meta-analiz, dijital bilissel egzersizlerin hafif bilissel bozuklukta dikkat ve calisma bellegini iyilestirdigini ortaya koydu.',
        'excerpt_en': 'A meta-analysis covering 42 studies revealed that digital cognitive exercises improve attention and working memory in mild cognitive impairment.',
        'body_tr': '<p>JAMA Neurology\'de yayinlanan meta-analiz, duzenli bilissel oyun oynamanin (haftada 3+ seans) hafif bilissel bozukluk hastalarinda dikkat (%18 iyilesme), calisma bellegi (%22 iyilesme) ve isleme hizi (%15 iyilesme) alanlarinda anlamli kazanimlar sagladigini gosterdi.</p>',
        'body_en': '<p>Published in JAMA Neurology, the meta-analysis showed that regular cognitive gaming (3+ sessions per week) provides significant gains in attention (18%), working memory (22%) and processing speed (15%).</p>',
        'category': 'clinical_trial',
        'priority': 'high',
        'diseases': ['dementia'],
    },

    # COKLU HASTALIK HABERLERI
    {
        'title_tr': 'Norolojik Hastaliklarda Bagirsak-Beyin Ekseni: Mikrobiom Tedavisi Icin Yeni Kanitlar',
        'title_en': 'Gut-Brain Axis in Neurological Diseases: New Evidence for Microbiome Therapy',
        'excerpt_tr': 'Nature Neuroscience\'ta yayinlanan derleme, bagirsak mikrobiyomunun migren, epilepsi ve demans dahil birden fazla norolojik hastalikta rol oynadigini gosteriyor.',
        'excerpt_en': 'A review in Nature Neuroscience shows gut microbiome plays a role in multiple neurological diseases including migraine, epilepsy and dementia.',
        'body_tr': '<p>Derleme, spesifik bagirsak bakterilerinin norotransmitter uretimine dogrudan katkilari oldugunu ve disbiyozis durumunun norolojik hastalik riskini artirdigini ozetliyor. Probiyotik mudahalelerin her uc hastalikta da faydali etkileri kanitlanmistir.</p>',
        'body_en': '<p>The review summarizes that specific gut bacteria directly contribute to neurotransmitter production and dysbiosis increases neurological disease risk.</p>',
        'category': 'popular_science',
        'priority': 'high',
        'diseases': ['migraine', 'epilepsy', 'dementia'],
    },
    {
        'title_tr': 'Yeni Nesil Norostimulasyon Cihazi Uc Hastalikta Birden Etkili',
        'title_en': 'Next-Gen Neurostimulation Device Effective in Three Diseases',
        'excerpt_tr': 'Programlanabilir norostimulasyon cihazi, migren, epilepsi ve hafif bilissel bozuklukta klinik denemelerde basarili sonuclar veriyor.',
        'excerpt_en': 'Programmable neurostimulation device shows successful results in clinical trials for migraine, epilepsy and mild cognitive impairment.',
        'body_tr': '<p>Boston merkezli startup\'in gelistirdigi miniaturize norostimulasyon cihazi, farkli frekanslarda stimulasyon uygulayarak uc farkli norolojik tabloda da etkili olabiliyor. FDA onay sureci baslamis durumda.</p>',
        'body_en': '<p>The miniaturized neurostimulation device can be effective in three different neurological conditions by applying stimulation at different frequencies.</p>',
        'category': 'new_device',
        'priority': 'medium',
        'diseases': ['migraine', 'epilepsy', 'dementia'],
    },
    {
        'title_tr': 'Turkiye Noroloji Haftasi 2026: Farkindaligin Onemi',
        'title_en': 'Turkey Neurology Week 2026: Importance of Awareness',
        'excerpt_tr': 'Turk Noroloji Dernegi, 2026 Noroloji Haftasi kapsaminda ulke genelinde ucretsiz norolojik muayene kampanyasi baslatti.',
        'excerpt_en': 'Turkish Neurological Society launched a free neurological examination campaign nationwide as part of 2026 Neurology Week.',
        'body_tr': '<p>10-17 Mart tarihleri arasinda duzenlenen etkinlikte 81 ilde ucretsiz norolojik muayene imkani sunuluyor. Kampanya ozellikle migren, epilepsi ve demans farkindaliigina odaklaniyor.</p>',
        'body_en': '<p>The event held March 10-17 offers free neurological examinations in all 81 provinces, focusing on migraine, epilepsy and dementia awareness.</p>',
        'category': 'turkey_news',
        'priority': 'medium',
        'diseases': ['migraine', 'epilepsy', 'dementia'],
    },
]


class Command(BaseCommand):
    help = 'Ornek haber ve blog icerikleri olusturur'

    def handle(self, *args, **options):
        from apps.content.models import NewsArticle
        from apps.patients.models import DiseaseModule

        # DiseaseModule'leri cache'le
        disease_map = {dm.slug: dm for dm in DiseaseModule.objects.all()}

        created = 0
        skipped = 0
        now = timezone.now()

        for i, news in enumerate(NEWS_DATA):
            slug = slugify(news['title_en'][:180], allow_unicode=True)

            if NewsArticle.objects.filter(slug=slug).exists():
                skipped += 1
                self.stdout.write(f'  Zaten var: {slug}')
                continue

            # Tarihi daginik yap (son 30 gun icinde)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            pub_date = now - timedelta(days=days_ago, hours=hours_ago)

            article = NewsArticle.objects.create(
                slug=slug,
                title_tr=news['title_tr'],
                title_en=news['title_en'],
                excerpt_tr=news['excerpt_tr'],
                excerpt_en=news['excerpt_en'],
                body_tr=news['body_tr'],
                body_en=news['body_en'],
                category=news['category'],
                priority=news['priority'],
                status='published',
                published_at=pub_date,
                view_count=random.randint(50, 2000),
                is_auto_generated=False,
            )

            # Hastalik iliskilendirme
            for disease_slug in news.get('diseases', []):
                dm = disease_map.get(disease_slug)
                if dm:
                    article.related_diseases.add(dm)

            created += 1
            self.stdout.write(self.style.SUCCESS(
                f'  [{article.category}] {article.title_tr[:60]}... -> {news["diseases"]}'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Tamamlandi: {created} haber olusturuldu, {skipped} atlanildi.'
        ))
        self.stdout.write(f'  Migren: {sum(1 for n in NEWS_DATA if "migraine" in n["diseases"])} haber')
        self.stdout.write(f'  Epilepsi: {sum(1 for n in NEWS_DATA if "epilepsy" in n["diseases"])} haber')
        self.stdout.write(f'  Demans: {sum(1 for n in NEWS_DATA if "dementia" in n["diseases"])} haber')
