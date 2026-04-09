"""
VPS'teki 3 yayınlanmış haberin body içeriklerini tamamen temiz Türkçe HTML ile güncelle.
"""
from django.core.management.base import BaseCommand
from apps.content.models import NewsArticle


BODY_FIXES = {
    # 1) Erenumab REFORM
    '280c42bd-169a-4b32-82ab-35b9ece760b5': """<h2>Migren Aurası Sıklığında Erenumabın Etkileri</h2>

<p>Migren, dünya çapında milyonlarca insanı etkileyen yaygın bir nörolojik bozukluktur. Migrenin bir alt türü olan <strong>migren aurası</strong>, genellikle parlak ışıklar, renkli desenler veya diğer görsel bulgular gibi duyusal değişikliklerle kendini gösterir. Son yıllarda, kalsitonin geniyle ilişkili peptid (CGRP) karşıtı monoklonal antikorlar, migren ağrısını önlemede etkili olduğu kanıtlanmıştır. Ancak bu tedavilerin migren aurası üzerindeki etkileri henüz netlik kazanmamıştır.</p>

<h2>REFORM Çalışması</h2>

<p>REFORM çalışması kapsamında bilim insanları, <strong>erenumab</strong> adlı CGRP karşıtı monoklonal antikorun sık migren aurası yaşayan yetişkinlerdeki etkilerini incelemiştir. Çalışmada katılımcıların migren aurası sıklığı, erenumab tedavisi süresince ve sonrasında prospektif olarak değerlendirilmiştir.</p>

<h2>CGRP ve Migren İlişkisi</h2>

<p>Kalsitonin geniyle ilişkili peptid (CGRP), migren ağrısının oluşumunda kilit rol oynayan bir peptiddir. CGRP karşıtı monoklonal antikorlar bu peptidi hedefleyerek migren ağrısını önler. Erenumab, bu sınıftaki ilk onaylı ilaçtır ve ayda bir kez deri altı enjeksiyon şeklinde uygulanır.</p>

<h2>Çalışma Sonuçları</h2>

<p>Araştırmanın sonuçları, erenumabın migren aurası sıklığını anlamlı ölçüde azaltabileceğini göstermiştir. Bu bulgular, migren aurası yaşayan hastalar için yeni tedavi seçenekleri sunabilir.</p>

<h2>Türkiye'deki Durum</h2>

<p>Türkiye'de migren ve migren aurası sık görülen nörolojik bozukluklardandır. Ülkemizde migren tedavisi genellikle ağrı kesiciler ve önleyici ilaçlarla yapılmaktadır. CGRP karşıtı monoklonal antikorların Türkiye'deki kullanımı giderek yaygınlaşmaktadır. Erenumab, Türkiye İlaç ve Tıbbi Cihaz Kurumu (TİTCK) tarafından onaylanmış olup erişkin kronik migren hastalarında kullanılmaktadır.</p>

<p><strong>Kaynak:</strong> <a href="https://pubmed.ncbi.nlm.nih.gov/41888647/" target="_blank" rel="noopener">PubMed - REFORM Çalışması</a></p>""",

    # 2) FDA 2025 İlaç Onayları
    '8232804d-5808-442f-8d7f-f8630e202d4c': """<h2>2025 Yılında FDA Tarafından Onaylanan Yeni İlaçlar</h2>

<p>Amerikan Gıda ve İlaç Dairesi (FDA), 2025 yılında çeşitli hastalıkların tedavisine yönelik yenilikçi ilaçları onaylamıştır. Bu yeni ilaçlar, hastalar için önemli tedavi seçenekleri sunmakta ve sağlık alanında önemli gelişmelere imza atmaktadır.</p>

<h2>Öne Çıkan Onay: Lixisenatide (Adlyxin)</h2>

<ul>
<li><strong>Jenerik İsim:</strong> Lixisenatide</li>
<li><strong>Ticari İsim:</strong> Adlyxin</li>
<li><strong>Endikasyon:</strong> Tip 2 Diyabet</li>
<li><strong>İlaç Sınıfı:</strong> GLP-1 reseptör agonisti</li>
</ul>

<h2>Etki Mekanizması</h2>

<p>Lixisenatide, GLP-1 (glukagon benzeri peptid-1) reseptörlerine bağlanarak insülin salgılanmasını artırır ve glukagon salgılanmasını azaltır. Böylece kan şekeri düzeylerinin düşürülmesine yardımcı olur. Ayrıca mide boşalmasını geciktirerek tokluk hissini artırır ve açlık duygusunu azaltır.</p>

<h2>Klinik Çalışma Sonuçları</h2>

<p>Lixisenatide'nin etkinliği ve güvenliği çeşitli klinik çalışmalarda değerlendirilmiştir. Çalışmalarda lixisenatide kullanan hastaların kan şekeri düzeylerinde anlamlı düşüş sağlanmıştır. Ayrıca kilo kaybı ve kan basıncı düşüşü gibi ek yararlar da gözlemlenmiştir.</p>

<h2>Yan Etkiler</h2>

<p>En sık görülen yan etkiler şunlardır:</p>
<ul>
<li>Bulantı</li>
<li>İshal</li>
<li>Baş ağrısı</li>
<li>Enfeksiyon</li>
</ul>

<h2>Türkiye'deki Durum</h2>

<p>Türkiye İlaç ve Tıbbi Cihaz Kurumu (TİTCK), FDA onaylı yeni ilaçların ülkemizde ruhsatlandırılması sürecini yakından takip etmektedir. GLP-1 reseptör agonistleri Türkiye'de tip 2 diyabet tedavisinde giderek daha yaygın kullanılmaktadır.</p>

<p><strong>Kaynak:</strong> <a href="http://www.fda.gov/drugs/novel-drug-approvals-fda/novel-drug-approvals-2025" target="_blank" rel="noopener">FDA - 2025 Yeni İlaç Onayları</a></p>""",

    # 3) Canlı Rüyalar ve Uyku
    'd137c3a2-cc5e-450a-990d-ce4b740c67bd': """<h2>Canlı Rüyalar Uyku Kalitesini Artırabilir</h2>

<p>Uykumuz sırasında gördüğümüz canlı ve renkli rüyalar, yalnızca zihnimizi eğlendirmekle kalmayıp aslında daha derin ve dinlendirici bir uykuya ulaşmamızı sağlayabilir. Yeni bir araştırma, yoğun rüya deneyimlerinin uykunun daha derin ve yenileyici hissedilmesini sağlayabileceğini ortaya koymuştur.</p>

<h2>Araştırma Bulguları</h2>

<p>Şaşırtıcı bir şekilde katılımcılar, en derin uykularını yoğun rüya deneyimlerinden sonra rapor etmiştir. Bu bulgu, rüyaların gerçekten dinlenmiş hissetmemizde kritik bir rol oynadığını düşündürmektedir.</p>

<p>Araştırmacılar, uykunun kalitesini belirlemede beyin aktivitesinin yüksek veya düşük olmasının tek başına yeterli olmadığını saptamıştır. İnsanlar, rüya deneyimlerinin yoğunluğuna bağlı olarak uykularının derinliğini farklı değerlendirmektedir.</p>

<h2>Beyin Dalgaları ve REM Uykusu</h2>

<p>Rüyaların uykuya etkisini anlamak için araştırmacılar, beyin aktivitesini ölçen çeşitli teknikler kullanmıştır. Elektroensefalografi (EEG) ile yapılan ölçümler, uykunun farklı evrelerinde beyin aktivitesinin nasıl değiştiğini göstermiştir. Rüyalar özellikle <strong>REM (Hızlı Göz Hareketi) uykusu</strong> sırasında oluşmaktadır. REM uykusu, uykunun en aktif evresi olup en canlı rüya deneyimlerinin yaşandığı dönemdir.</p>

<h2>Türkiye'deki Çalışmalar</h2>

<p>Türkiye'de de uykunun kalitesi ve rüyaların önemi konusunda çalışmalar sürdürülmektedir. Türk nörologlar, uyku kalitesinin artırılmasıyla çeşitli nörolojik hastalıkların önlenmesi ve tedavisi üzerine araştırmalar yürütmektedir. Bu araştırmalar, uyku bozuklukları ve nörolojik hastalıklar arasındaki ilişkinin daha iyi anlaşılmasına katkı sağlamaktadır.</p>

<p><strong>Kaynak:</strong> <a href="https://www.sciencedaily.com/releases/2026/03/260326011458.htm" target="_blank" rel="noopener">ScienceDaily</a></p>""",
}


class Command(BaseCommand):
    help = 'Yayınlanmış 3 haberin body içeriklerini temiz Türkçe HTML ile güncelle'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        updated = 0

        for article_id, new_body in BODY_FIXES.items():
            try:
                article = NewsArticle.objects.get(id=article_id)
            except NewsArticle.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Bulunamadı: {article_id}'))
                continue

            self.stdout.write(f'\n{article.title_tr[:60]}')
            self.stdout.write(f'  Eski body: {len(article.body_tr or "")} karakter')
            self.stdout.write(f'  Yeni body: {len(new_body)} karakter')

            if not dry_run:
                article.body_tr = new_body
                article.save(update_fields=['body_tr'])
                self.stdout.write(self.style.SUCCESS('  -> Güncellendi'))
            else:
                self.stdout.write(self.style.WARNING('  -> DRY RUN'))
            updated += 1

        self.stdout.write(f'\n=== {updated}/{len(BODY_FIXES)} haber güncellendi ===')
