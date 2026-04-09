"""
UpToDate nöroloji haberlerinden ilham alınarak oluşturulmuş orijinal haberler.
Kullanım: python3 manage.py seed_uptodate_news
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

NEWS_DATA = [
    # 1 - DEMANS: Semaglutid ve Alzheimer
    {
        'title_tr': 'Semaglutid Alzheimer Hastalığının İlerlemesini Yavaşlatmıyor: Faz 3 Sonuçları',
        'title_en': 'Semaglutide Does Not Slow Alzheimer Disease Progression: Phase 3 Results',
        'excerpt_tr': 'GLP-1 reseptör agonisti semaglutid ile yapılan iki büyük Faz 3 klinik çalışma, erken evre Alzheimer hastalarında iki yıllık tedavinin hastalık ilerlemesini yavaşlatmadığını gösterdi.',
        'excerpt_en': 'Two large Phase 3 clinical trials of the GLP-1 receptor agonist semaglutide showed that two years of treatment did not slow disease progression in patients with early-stage Alzheimer disease.',
        'body_tr': (
            '<h2>Gözlemsel Çalışmalar Umut Vermişti</h2>'
            '<p>Daha önce yapılan gözlemsel çalışmalar, diyabet tedavisinde yaygın olarak kullanılan GLP-1 reseptör agonistlerinin bilişsel gerilemeyi yavaşlatabileceğini ve demans insidansını azaltabileceğini düşündürmüştü. Bu bulgular, kontrollü klinik çalışmalarla doğrulanması gereken heyecan verici hipotezler ortaya koymuştu.</p>'
            '<h2>EVOKE ve EVOKE+ Çalışmaları</h2>'
            '<p>Amiloid testi ile doğrulanmış erken evre Alzheimer hastalığı olan bireylerde gerçekleştirilen iki randomize kontrollü çalışmada (EVOKE ve EVOKE+), oral semaglutid 14 mg ile tedavi edilen hastalar iki yıl boyunca takip edildi. Sonuçlar, semaglutid alan hastaların plasebo grubuna kıyasla benzer klinik ilerleme oranlarına sahip olduğunu ortaya koydu.</p>'
            '<h3>Vasküler Risk Faktörü Yönetimi Hâlâ Önemli</h3>'
            '<p>Bu çalışma, semaglutid\'in doğrudan Alzheimer hastalığı üzerindeki etkisini değerlendirmesine rağmen, diyabet ve diğer vasküler risk faktörlerinin yönetiminin Alzheimer hastalarında hâlâ önerildiğini vurguladı. Kan şekeri kontrolü, hipertansiyon tedavisi ve kardiyovasküler sağlığın korunması bilişsel sağlık için kritik olmaya devam etmektedir.</p>'
            '<h3>Klinik Önemi</h3>'
            '<p>Bu sonuçlar, Alzheimer hastalığının karmaşık patofizyolojisini bir kez daha vurguluyor. Tek bir mekanizmayı hedef alan tedavilerin yetersiz kalabileceği ve çok yönlü yaklaşımların gerekebileceği anlaşılmaktadır.</p>'
        ),
        'body_en': (
            '<h2>Observational Studies Had Raised Hope</h2>'
            '<p>Previous observational studies had suggested that GLP-1 receptor agonists, widely used in diabetes treatment, might slow cognitive decline and reduce dementia incidence. These findings raised exciting hypotheses that needed validation through controlled clinical trials.</p>'
            '<h2>EVOKE and EVOKE+ Trials</h2>'
            '<p>In two randomized controlled trials (EVOKE and EVOKE+) conducted in individuals with amyloid-confirmed early-stage Alzheimer disease, patients treated with oral semaglutide 14 mg were followed for two years. Results showed that semaglutide-treated patients had similar rates of clinical progression compared to the placebo group.</p>'
            '<h3>Vascular Risk Factor Management Still Important</h3>'
            '<p>Despite these results, the management of diabetes and other vascular risk factors in Alzheimer patients is still recommended. Blood sugar control, hypertension treatment, and cardiovascular health remain critical for cognitive well-being.</p>'
        ),
        'category': 'clinical_trial',
        'priority': 'high',
        'diseases': ['dementia'],
        'source': 'Cummings JL, et al. Lancet 2026',
    },
    # 2 - DEMANS: Kafein ve demans riski
    {
        'title_tr': 'Düzenli Kafein Tüketimi Demans Riskini Azaltabilir: Büyük Kohort Çalışması',
        'title_en': 'Regular Caffeine Consumption May Lower Dementia Risk: Large Cohort Study',
        'excerpt_tr': 'İki büyük prospektif kohort çalışmasının sonuçları, günde 2-3 fincan kahve tüketiminin demans riskinde anlamlı azalmayla ilişkili olduğunu ortaya koydu.',
        'excerpt_en': 'Results from two large prospective cohort studies revealed that consuming 2-3 cups of coffee per day is associated with a significant reduction in dementia risk.',
        'body_tr': (
            '<h2>Nurses\' Health Study ve Health Professionals Follow-up Study</h2>'
            '<p>Uzun süreli takip edilen bu iki büyük prospektif kohort çalışmasında, kafeinli kahve tüketiminin en yüksek çeyreğinde yer alan katılımcılarda demans insidansı, en düşük çeyreğe kıyasla belirgin şekilde daha düşük bulundu.</p>'
            '<h2>Önemli Bulgular</h2>'
            '<p>Çalışmada dikkat çeken noktalar şunlardır:</p>'
            '<ul>'
            '<li>Kafeinli kahve tüketimi ile demans riski arasında ters ilişki saptandı</li>'
            '<li>Çay tüketimi için de benzer koruyucu etkiler gözlemlendi</li>'
            '<li>Kafeinsiz kahve tüketiminde ise bu koruyucu etki görülmedi</li>'
            '<li>Günde 2-3 fincan kahve tüketimi optimal aralık olarak belirlendi</li>'
            '</ul>'
            '<h3>Pratik Öneriler</h3>'
            '<p>Araştırmacılar, ılımlı kafein tüketiminin (günde 2-3 fincan kahve) zararlı olmadığını ve demans riskini azaltabileceğini belirtiyor. Ancak bunun bir tedavi değil, yaşam tarzı faktörü olduğu unutulmamalıdır. Yeterli uyku, düzenli egzersiz ve sosyal aktiviteler de bilişsel sağlık için kritik öneme sahiptir.</p>'
        ),
        'body_en': (
            '<h2>Nurses\' Health Study and Health Professionals Follow-up Study</h2>'
            '<p>In these two large prospective cohort studies with long-term follow-up, participants in the highest quartile of caffeinated coffee intake had notably lower dementia incidence compared to the lowest quartile.</p>'
            '<h2>Key Findings</h2>'
            '<ul>'
            '<li>An inverse relationship was found between caffeinated coffee consumption and dementia risk</li>'
            '<li>Similar protective effects were observed for tea consumption</li>'
            '<li>Decaffeinated coffee did not show this protective effect</li>'
            '<li>2-3 cups of coffee per day was identified as the optimal range</li>'
            '</ul>'
            '<h3>Practical Recommendations</h3>'
            '<p>Moderate caffeine consumption of 2-3 cups per day is unlikely to be harmful and may lower dementia risk. However, adequate sleep, regular exercise, and social activities remain critical for cognitive health.</p>'
        ),
        'category': 'popular_science',
        'priority': 'medium',
        'diseases': ['dementia'],
        'source': 'Zhang Y, et al. JAMA 2026; 335:961',
    },
    # 3 - MİGREN: Oksipital sinir bloğu
    {
        'title_tr': 'Akut Migren Ataklarında Oksipital Sinir Bloğu Etkili Bulundu',
        'title_en': 'Occipital Nerve Block Found Effective in Acute Migraine Attacks',
        'excerpt_tr': 'Randomize kontrollü bir çalışma, standart tedaviye dirençli şiddetli akut migren ataklarında büyük oksipital sinir bloğunun ağrıda belirgin azalma sağladığını gösterdi.',
        'excerpt_en': 'A randomized controlled trial showed that greater occipital nerve block provides significant pain reduction in severe acute migraine attacks resistant to standard treatment.',
        'body_tr': (
            '<h2>Dirençli Migren Atakları İçin Yeni Seçenek</h2>'
            '<p>Standart farmakolojik tedavilere yanıt vermeyen şiddetli akut migren atakları, hastaların yaşam kalitesini ciddi ölçüde etkileyen önemli bir klinik sorundur. Yeni bir randomize kontrollü çalışma, bu hasta grubunda büyük oksipital sinir (BON) bloğunun umut verici sonuçlar ortaya koyduğunu gösterdi.</p>'
            '<h2>Çalışma Tasarımı ve Sonuçları</h2>'
            '<p>Çalışmaya şiddetli ve dirençli akut migreni olan 42 hasta dahil edildi. Tüm hastalara intravenöz ketorolak, parasetamol ve metoklopramid uygulandı. Ek olarak BON bloğu uygulanan grupta dikkat çekici sonuçlar elde edildi:</p>'
            '<ul>'
            '<li>2 saatte anlamlı ağrı rahatlaması: BON grubu %95, kontrol grubu %48</li>'
            '<li>30 günlük takipte aylık migren günü: BON grubu 3 gün, kontrol grubu 7 gün</li>'
            '</ul>'
            '<h3>Klinik Uygulamada Yeri</h3>'
            '<p>Bu bulgular, BON bloğunun dirençli akut migren ataklarında etkili bir ek tedavi seçeneği olabileceğini göstermektedir. Özellikle acil serviste standart tedaviye yanıt vermeyen hastalarda düşünülmesi gereken bir yöntemdir.</p>'
        ),
        'body_en': (
            '<h2>A New Option for Refractory Migraine Attacks</h2>'
            '<p>Severe acute migraine attacks that do not respond to standard pharmacotherapies represent a significant clinical problem. A new randomized controlled trial demonstrated promising results for greater occipital nerve (GON) block in these patients.</p>'
            '<h2>Study Design and Results</h2>'
            '<p>The study included 42 patients with severe, refractory acute migraine. All received IV ketorolac, paracetamol, and metoclopramide. The group receiving adjunctive GON block showed remarkable results:</p>'
            '<ul>'
            '<li>Significant pain relief at 2 hours: GON group 95% vs control 48%</li>'
            '<li>Monthly migraine days at 30-day follow-up: GON group 3 vs control 7</li>'
            '</ul>'
        ),
        'category': 'clinical_trial',
        'priority': 'medium',
        'diseases': ['migraine'],
        'source': 'Tamayo de Leon CD, et al. Cephalalgia 2025',
    },
    # 4 - PARKİNSON: Alfa-sinüklein testleri
    {
        'title_tr': 'Parkinson Tanısında Alfa-Sinüklein Biyobelirteç Testleri: Uzman Değerlendirmesi',
        'title_en': 'Alpha-Synuclein Biomarker Tests in Parkinson Diagnosis: Expert Review',
        'excerpt_tr': 'Ticari olarak kullanılabilir alfa-sinüklein biyobelirteç testlerinin Parkinson hastalığı tanısındaki rolüne ilişkin kapsamlı bir uzman değerlendirmesi yayımlandı.',
        'excerpt_en': 'A comprehensive expert review on commercially available alpha-synuclein biomarker tests for Parkinson disease diagnosis has been published.',
        'body_tr': (
            '<h2>Parkinson Tanısında Yeni Dönem</h2>'
            '<p>Parkinson hastalığı ve diğer alfa-sinükleinopatilerin değerlendirilmesinde ticari olarak kullanılabilir alfa-sinüklein biyobelirteç testlerine ilişkin kapsamlı bir uzman değerlendirmesi yayımlandı. Bu gelişme, Parkinson tanısının daha erken ve daha doğru konulabilmesi yolunda önemli bir adımdır.</p>'
            '<h2>Mevcut Test Yöntemleri</h2>'
            '<p>Değerlendirme, iki ana test yöntemini inceledi:</p>'
            '<ul>'
            '<li><strong>BOS Tohum Amplifikasyon Analizi (SAA):</strong> Beyin-omurilik sıvısından yapılan bu test, klinik tanılarla karşılaştırıldığında alfa-sinüklein nörodejeneratif hastalıklar için yüksek duyarlılık göstermektedir.</li>'
            '<li><strong>Deri Biyopsisi İmmünofloresan Testi:</strong> Minimal invaziv bir yöntem olup, benzer şekilde yüksek duyarlılığa sahiptir.</li>'
            '</ul>'
            '<h3>Önemli Sınırlılıklar</h3>'
            '<p>Uzman paneli, testlerin bazı önemli sınırlılıklarını da vurguladı:</p>'
            '<ul>'
            '<li>Testler farklı alfa-sinüklein hastalıklarını birbirinden ayırt edemez</li>'
            '<li>Ayırıcı tanıda yer alan diğer hastalıklarda alfa-sinüklein kopatolojisi sık görülmektedir</li>'
            '<li>Sağlıklı bireylerde pozitif test oranları ve bunun klinik anlamı konusunda daha fazla araştırma gereklidir</li>'
            '</ul>'
            '<h3>Klinik Yorum</h3>'
            '<p>Değerlendirme, uygun kullanım konusunda klinik konsensüs kılavuzlarının geliştirilmesi çağrısında bulundu ve test sonuçlarının yorumlanmasında klinik muhakemenin önemini vurguladı. Testler tanıya yardımcı olabilir ancak tek başına tanı koydurmaz.</p>'
        ),
        'body_en': (
            '<h2>New Era in Parkinson Diagnosis</h2>'
            '<p>A comprehensive expert review on commercially available alpha-synuclein biomarker tests for evaluating Parkinson disease and other alpha-synucleinopathies has been published. This represents an important step toward earlier and more accurate diagnosis.</p>'
            '<h2>Current Test Methods</h2>'
            '<ul>'
            '<li><strong>CSF Seed Amplification Assay (SAA):</strong> This test shows high sensitivity for alpha-synuclein neurodegenerative disorders compared with clinical diagnoses.</li>'
            '<li><strong>Skin Biopsy Immunofluorescence Test:</strong> A minimally invasive method with similarly high sensitivity.</li>'
            '</ul>'
            '<h3>Important Limitations</h3>'
            '<p>The expert panel highlighted that tests cannot distinguish among various alpha-synuclein disorders, and more research is needed on positive test rates in healthy individuals.</p>'
        ),
        'category': 'new_device',
        'priority': 'high',
        'diseases': ['parkinson'],
        'source': 'Coughlin DG, et al. Neurology 2026; 106:e214648',
    },
    # 5 - SEREBROVASKÜLER: Tenekteplaz genişletilmiş pencere
    {
        'title_tr': 'Akut İskemik İnmede Tenekteplaz ile Genişletilmiş Zaman Penceresi: İki Yeni Çalışma',
        'title_en': 'Extended Time Window for Tenecteplase in Acute Ischemic Stroke: Two New Trials',
        'excerpt_tr': 'TRACE-5 ve OPTION çalışmaları, inme başlangıcından 4.5-24 saat sonra tenekteplaz ile intravenöz trombolizin seçilmiş hastalarda olumlu sonuçlar verdiğini gösterdi.',
        'excerpt_en': 'The TRACE-5 and OPTION trials showed that intravenous thrombolysis with tenecteplase 4.5-24 hours after stroke onset yielded favorable outcomes in selected patients.',
        'body_tr': (
            '<h2>İnme Tedavisinde Zaman Penceresi Genişliyor</h2>'
            '<p>İntravenöz tromboliz (İVT), akut iskemik inme başlangıcından sonraki 4.5 saat içindeki hastalar için standart tedavidir. Son yayımlanan iki çalışma, seçilmiş hastalarda bu zaman penceresinin 24 saate kadar genişletilebileceğine dair önemli kanıtlar sundu.</p>'
            '<h2>TRACE-5 Çalışması</h2>'
            '<p>Baziler arter oklüzyonu olan hastalarda yapılan bu çalışmada, genişletilmiş zaman penceresinde (4.5-24 saat) tenekteplaz (TNK) ile İVT uygulaması, mükemmel sonuç oranını iyileştirdi. Çalışmada klinisyenin tercihine göre mekanik trombektomiye de izin verildi.</p>'
            '<h2>OPTION Çalışması</h2>'
            '<p>Büyük damar oklüzyonu olmayan ancak ileri görüntülemede kurtarılabilir doku saptanan hastalarda gerçekleştirilen bu çalışma, genişletilmiş zaman penceresinde TNK ile İVT\'nin mükemmel sonuç oranını iyileştirdiğini gösterdi. Semptomatik intrakraniyal kanama oranında düşük ancak anlamlı bir artış gözlemlendi.</p>'
            '<h3>Klinik Önemi</h3>'
            '<p>Bu çalışmalar, inme tedavisinde "zaman beyin demektir" prensibini yeniden şekillendirmektedir. İleri görüntüleme teknikleri sayesinde, daha geç başvuran bazı hastaların da tromboliz tedavisinden fayda görebileceği anlaşılmaktadır. Ancak her iki çalışma da Çin\'de yapılmış olup, sonuçların diğer popülasyonlara genellenebilmesi için daha fazla veri gerekmektedir.</p>'
        ),
        'body_en': (
            '<h2>Expanding the Time Window for Stroke Treatment</h2>'
            '<p>Intravenous thrombolysis (IVT) is standard therapy within 4.5 hours of acute ischemic stroke. Two recent trials provided important evidence that this window may be extended to 24 hours in selected patients.</p>'
            '<h2>TRACE-5 Trial</h2>'
            '<p>In patients with basilar artery occlusion, IVT with tenecteplase in the extended time window (4.5-24 hours) improved the rate of excellent outcome.</p>'
            '<h2>OPTION Trial</h2>'
            '<p>In patients without large vessel occlusion but with salvageable tissue on advanced imaging, TNK in the extended window improved outcomes despite a low increased rate of symptomatic intracranial hemorrhage.</p>'
        ),
        'category': 'clinical_trial',
        'priority': 'high',
        'diseases': [],
        'source': 'Xiong Y, et al. Lancet 2026; 407:763 / Ma G, et al. JAMA 2026',
    },
    # 6 - SEREBROVASKÜLER: AHA/ASA güncel kılavuz
    {
        'title_tr': 'AHA/ASA Akut İskemik İnme Yönetimi Kılavuzu Güncellendi',
        'title_en': 'AHA/ASA Updates Guideline for Early Management of Acute Ischemic Stroke',
        'excerpt_tr': 'Amerikan Kalp Derneği ve Amerikan İnme Derneği, akut iskemik inme erken yönetimi için güncellenmiş kılavuzunu yayımladı. Kılavuz, tedavi erişimini genişleten önemli değişiklikler içeriyor.',
        'excerpt_en': 'The American Heart Association and American Stroke Association published updated guidelines for early management of acute ischemic stroke with important changes expanding treatment access.',
        'body_tr': (
            '<h2>Kılavuzdaki Önemli Güncellemeler</h2>'
            '<p>2026 yılında yayımlanan güncellenmiş kılavuz, son yıllardaki kanıtları ve yeni önerileri bir araya getirerek akut iskemik inme yönetimini önemli ölçüde yeniden şekillendirdi. Başlıca değişiklikler şunlardır:</p>'
            '<h3>Hastane Öncesi Değerlendirme ve Nakil</h3>'
            '<ul>'
            '<li>Mobil inme ünitelerinin kullanılabilir olduğu yerlerde rolü vurgulandı</li>'
            '<li>Telestroke ve teleradyoloji hizmetlerinin hızlı görüntüleme yorumlaması için kullanımı önerildi</li>'
            '</ul>'
            '<h3>Tedavi Yenilikleri</h3>'
            '<ul>'
            '<li>İleri görüntüleme ile intravenöz tromboliz için genişletilmiş zaman penceresi</li>'
            '<li>Trombolitik tedavide tenekteplaz veya alteplaz kullanımı</li>'
            '<li>Büyük çekirdek enfarktı veya baziler arter inmesi olan seçilmiş hastalar dahil endovasküler trombektomi için genişletilmiş uygunluk kriterleri</li>'
            '<li>İkili antiplatelet tedavinin kullanımı</li>'
            '</ul>'
            '<h3>Temel Mesaj</h3>'
            '<p>Bu güncellemeler, etkili akut iskemik inme tedavilerine hızlı ve geniş erişimi sağlamayı amaçlamaktadır. İnme belirtileri fark edildiğinde derhal acil yardım çağrılması hayat kurtarıcıdır.</p>'
        ),
        'body_en': (
            '<h2>Key Guideline Updates</h2>'
            '<p>The updated guideline incorporates recent evidence with major changes including:</p>'
            '<ul>'
            '<li>Support for mobile stroke units and telestroke services for rapid assessment</li>'
            '<li>Extended time window for IV thrombolysis with advanced imaging</li>'
            '<li>Use of either tenecteplase or alteplase for thrombolytic treatment</li>'
            '<li>Expanded eligibility for endovascular thrombectomy including large core infarcts and basilar artery stroke</li>'
            '<li>Use of dual antiplatelet therapy</li>'
            '</ul>'
        ),
        'category': 'guideline_update',
        'priority': 'high',
        'diseases': [],
        'source': 'Prabhakaran S, et al. Stroke 2026',
    },
    # 7 - MS: McDonald kriterleri güncellendi
    {
        'title_tr': 'Multipl Skleroz Tanısında McDonald Kriterleri Güncellendi: 2024 Revizyonu',
        'title_en': 'McDonald Criteria for Multiple Sclerosis Diagnosis Updated: 2024 Revision',
        'excerpt_tr': 'MS tanısında kullanılan McDonald kriterleri önemli değişikliklere uğradı. Optik sinir beşinci anatomik bölge olarak eklendi ve yeni biyobelirteçler tanıya dahil edildi.',
        'excerpt_en': 'The McDonald criteria for MS diagnosis underwent significant changes. The optic nerve was added as a fifth anatomic region and new biomarkers were incorporated.',
        'body_tr': (
            '<h2>MS Tanısında Köşe Taşı: McDonald Kriterleri</h2>'
            '<p>2001 yılından bu yana multipl skleroz (MS) tanısında temel araç olan McDonald kriterleri, zaman içinde önemli değişikliklerden geçmiştir. Son yayımlanan revizyon, tanıyı hızlandırırken özgüllüğü korumayı amaçlayan dikkat çekici yenilikler içermektedir.</p>'
            '<h2>Önemli Değişiklikler</h2>'
            '<h3>Optik Sinir: Beşinci Anatomik Bölge</h3>'
            '<p>Optik sinir, periventriküler, jukstakortikal, infratentoryal ve spinal kord bölgelerine ek olarak beşinci anatomik bölge olarak tanımlandı. Beş bölgeden ikisinde fokal MRG lezyonları, uzayda yayılım kriterini karşılayabilir.</p>'
            '<h3>Yeni Tanı Biyobelirteçleri</h3>'
            '<p>Güncelleme, üç yeni tanı biyobelirtecini ekledi:</p>'
            '<ul>'
            '<li><strong>Santral ven işareti (CVS):</strong> MRG\'de lezyon içindeki venöz yapıların gösterilmesi</li>'
            '<li><strong>Paramanyetik rim lezyonları (PRL):</strong> Kronik aktif enflamasyonun MRG göstergesi</li>'
            '<li><strong>Kappa serbest hafif zincirler:</strong> BOS\'ta saptanan yeni immünolojik biyobelirteç</li>'
            '</ul>'
            '<h3>Hastaların Bilmesi Gerekenler</h3>'
            '<p>Bu güncellemeler, MS\'in daha erken tanınmasını ve dolayısıyla daha erken tedavi başlanmasını mümkün kılmayı hedeflemektedir. Erken tanı ve tedavi, hastalığın uzun vadeli seyrini olumlu yönde etkileyebilir.</p>'
        ),
        'body_en': (
            '<h2>Cornerstone of MS Diagnosis: McDonald Criteria</h2>'
            '<p>The McDonald criteria, a pivotal diagnostic tool since 2001, have undergone significant revisions aimed at expediting diagnosis while maintaining specificity.</p>'
            '<h2>Key Changes</h2>'
            '<h3>Optic Nerve: Fifth Anatomic Region</h3>'
            '<p>The optic nerve has been added as a fifth region alongside periventricular, juxtacortical, infratentorial, and spinal cord regions.</p>'
            '<h3>New Diagnostic Biomarkers</h3>'
            '<ul>'
            '<li><strong>Central vein sign (CVS)</strong></li>'
            '<li><strong>Paramagnetic rim lesions (PRL)</strong></li>'
            '<li><strong>Kappa free light chains</strong> in cerebrospinal fluid</li>'
            '</ul>'
        ),
        'category': 'guideline_update',
        'priority': 'medium',
        'diseases': [],
        'source': 'Montalban X, et al. Lancet Neurol 2025; 24:850',
    },
    # 8 - NÖROMÜSKÜLER: İnebilizumab MG tedavisi
    {
        'title_tr': 'FDA Miyastenia Gravis Tedavisinde İnebilizumabu Onayladı',
        'title_en': 'FDA Approves Inebilizumab for Myasthenia Gravis Treatment',
        'excerpt_tr': 'Anti-CD19 monoklonal antikor inebilizumab, jeneralize asetilkolin reseptörü veya MuSK pozitif miyastenia gravis tedavisi için FDA onayı aldı.',
        'excerpt_en': 'The anti-CD19 monoclonal antibody inebilizumab received FDA approval for the treatment of generalized acetylcholine receptor or MuSK-positive myasthenia gravis.',
        'body_tr': (
            '<h2>MG Tedavisinde Yeni Biyolojik Ajan</h2>'
            '<p>Miyastenia gravis (MG) tedavisinde antikor bazlı biyolojik ajanlar, hızlı etki başlangıcı sunan genişleyen bir immünoterapi grubudur. İnebilizumab, otoantikor üreten B hücrelerini hedef alan bir anti-CD19 monoklonal antikordur.</p>'
            '<h2>Faz 3 Klinik Çalışma</h2>'
            '<p>238 asetilkolin reseptörü (AChR) pozitif veya kas-spesifik kinaz (MuSK) pozitif MG hastasının dahil edildiği randomize kontrollü çalışmada, inebilizumab alan hastalarda fonksiyonel semptomlarda 26 haftada plaseboya kıyasla anlamlı iyileşme gözlemlendi.</p>'
            '<h3>FDA Onayı</h3>'
            '<p>Bu sonuçlar, ABD Gıda ve İlaç Dairesi\'nin (FDA) inebilizumabı yetişkinlerde jeneralize AChR veya MuSK pozitif MG tedavisi için onaylamasına yol açtı.</p>'
            '<h3>MG Hastaları İçin Önemi</h3>'
            '<p>Bu onay, MG hastaları için ek bir immünoterapötik seçenek sunmaktadır. Özellikle mevcut tedavilere yeterli yanıt alınamayan hastalarda yeni bir umut kaynağıdır. Tedavi kararı, hastanın genel durumu, hastalık şiddeti ve diğer tedavilere yanıtı göz önünde bulundurularak verilmelidir.</p>'
        ),
        'body_en': (
            '<h2>New Biologic Agent for MG</h2>'
            '<p>Inebilizumab is an anti-CD19 monoclonal antibody that depletes autoantibody-producing B-cells, representing an expanding group of immunotherapies for myasthenia gravis.</p>'
            '<h2>Phase 3 Clinical Trial</h2>'
            '<p>In a randomized trial of 238 AChR-positive or MuSK-positive MG patients, inebilizumab showed greater improvement in functional symptoms versus placebo at 26 weeks, leading to FDA approval.</p>'
        ),
        'category': 'fda_approval',
        'priority': 'high',
        'diseases': [],
        'source': 'Nowak RJ, et al. N Engl J Med 2025; 392:2309',
    },
]


class Command(BaseCommand):
    help = 'UpToDate nöroloji haberlerinden ilham alınarak oluşturulmuş haberler'

    def handle(self, *args, **options):
        from apps.content.models import NewsArticle
        from apps.patients.models import DiseaseModule

        created = 0
        skipped = 0

        for news in NEWS_DATA:
            slug = slugify(news['title_en'][:180], allow_unicode=True)

            if NewsArticle.objects.filter(slug=slug).exists():
                self.stdout.write(f"  Var: {slug}")
                skipped += 1
                continue

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
                published_at=timezone.now(),
                is_auto_generated=False,
                source_urls=[news.get('source', '')],
                original_source='UpToDate - Whats New in Neurology',
                view_count=0,
                keywords=[],
            )

            # İlişkili hastalık modülleri
            for disease_slug in news.get('diseases', []):
                try:
                    dm = DiseaseModule.objects.get(slug=disease_slug)
                    article.related_diseases.add(dm)
                except DiseaseModule.DoesNotExist:
                    pass

            created += 1
            self.stdout.write(self.style.SUCCESS(f"  + {news['title_tr'][:60]}..."))

        self.stdout.write(self.style.SUCCESS(
            f"\n{created} yeni haber oluşturuldu, {skipped} atlandı"
        ))
