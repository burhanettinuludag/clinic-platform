"""
VPS'te üretilen 8 yeni haberin başlık, özet ve içeriklerini
düzgün Türkçe karakterler ile güncelle.
"""
from django.core.management.base import BaseCommand
from apps.content.models import NewsArticle


FIXES = {
    # 1) GDUFA Raporu
    '300cf6e0-464d-425e-a16f-21d627803b17': {
        'title_tr': '2024 Mali Yılı GDUFA Bilim ve Araştırma Raporu',
        'title_en': 'FY 2024 GDUFA Science and Research Report',
        'excerpt_tr': 'FDA tarafından yayınlanan GDUFA raporu, jenerik ilaçlar konusunda aktif araştırma projelerini ve sonuçlarını sekiz öncelikli alanda sunuyor.',
        'excerpt_en': 'The FY 2024 GDUFA Science and Research report describes active research projects and outcomes in eight priority areas for generic drugs.',
        'meta_title': '2024 GDUFA Bilim ve Araştırma Raporu | Norosera',
        'meta_description': 'FDA jenerik ilaç araştırma raporu: kalite, güvenlik, biyoeşdeğerlilik ve yeni teknolojiler.',
    },
    # 2) OMUFA
    'f4a798ee-c23c-4e27-8e7d-aec890be19c5': {
        'title_tr': 'Reçetesiz İlaçlar İçin Kullanıcı Ücreti Programı (OMUFA)',
        'title_en': 'Over-The-Counter Monograph Drug User Fee Program (OMUFA)',
        'excerpt_tr': 'FDA, reçetesiz ilaçların üretim ve pazarlanmasının daha etkili denetlenmesi için OMUFA programını geliştiriyor.',
        'excerpt_en': 'FDA is developing the OMUFA program for more effective oversight of OTC drug manufacturing and marketing.',
        'meta_title': 'Reçetesiz İlaç Kullanıcı Ücreti Programı (OMUFA) | Norosera',
        'meta_description': 'FDA reçetesiz ilaç denetim programı OMUFA hakkında güncel bilgiler.',
    },
    # 3) Metformin
    '74bd4c67-dd8b-4d09-8c5c-7f3efb777ef9': {
        'title_tr': 'Metformin\'in Gizli Beyin Yolu 60 Yıl Sonra Açığa Çıktı',
        'title_en': 'Metformin\'s hidden brain pathway revealed after 60 years',
        'excerpt_tr': 'Yeni bir keşif, metforminin sadece vücutta değil beyinde de etkili olduğunu gösterdi. İlaç, bir anahtar proteini devre dışı bırakarak ve belirli nöronları aktive ederek kan şekerini düşürüyor.',
        'excerpt_en': 'A major discovery reveals that metformin works not just in the body, but in the brain, lowering blood sugar through a previously unknown pathway.',
        'meta_title': 'Metforminin Gizli Beyin Yolu Keşfedildi | Norosera',
        'meta_description': 'Metforminin beyindeki gizli mekanizması 60 yıl sonra keşfedildi. Hipotalamustaki nöronları aktive ederek kan şekerini düşürüyor.',
    },
    # 4) Vivid Rüyalar
    'd137c3a2-cc5e-450a-990d-ce4b740c67bd': {
        'title_tr': 'Canlı Rüyalar Daha Derin ve Dinlendirici Uykunun Sırrı Olabilir',
        'title_en': 'Vivid dreams may be the secret to deeper, more restful sleep',
        'excerpt_tr': 'Araştırmacılar, yoğun rüya deneyimlerinin uykunun daha derin ve dinlendirici hissedilmesini sağlayabileceğini keşfetti.',
        'excerpt_en': 'Researchers found that immersive dreaming can actually make sleep feel deeper and more refreshing.',
        'meta_title': 'Canlı Rüyalar ve Uyku Kalitesi | Norosera',
        'meta_description': 'Canlı rüyaların daha derin ve dinlendirici uykuya katkısı: yeni araştırma sonuçları.',
    },
    # 5) CDERLearn
    '222e6c7b-831a-4253-8b61-eb3cefc21738': {
        'title_tr': 'FDA\'dan Yeni Eğitim Platformu: CDERLearn',
        'title_en': 'CDERLearn: Training and Education from FDA',
        'excerpt_tr': 'FDA\'nın İlaç Değerlendirme Merkezi (CDER), sağlık profesyonelleri ve araştırmacılar için yeni eğitim platformu CDERLearn\'i tanıttı.',
        'excerpt_en': 'Training and education for healthcare professionals, academia, and consumers from FDA\'s Center for Drug Evaluation and Research.',
        'meta_title': 'FDA CDERLearn Eğitim Platformu | Norosera',
        'meta_description': 'FDA İlaç Değerlendirme Merkezi eğitim platformu CDERLearn hakkında bilgiler.',
    },
    # 6) Novel Drug Approvals 2025
    '8232804d-5808-442f-8d7f-f8630e202d4c': {
        'title_tr': '2025 Yılı FDA Yeni İlaç Onayları',
        'title_en': 'Novel Drug Approvals for 2025',
        'excerpt_tr': 'FDA\'nın 2025 yılında onayladığı yenilikçi ilaçlar, hastalar için yeni tedavi seçenekleri ve sağlık alanında önemli gelişmeler sunuyor.',
        'excerpt_en': 'Innovative drugs approved by FDA in 2025 mean new treatment options for patients and advances in health care.',
        'meta_title': '2025 Yılı FDA Yeni İlaç Onayları | Norosera',
        'meta_description': 'FDA 2025 yeni ilaç onayları: Lixisenatide ve diğer yenilikçi tedaviler.',
    },
    # 7) What's New Related to Drugs
    '7b6b8bdd-2762-4415-8833-119909a3a2f3': {
        'title_tr': 'FDA İlaç Haberleri: Lumakras (Sotorasib) Onayı',
        'title_en': 'FDA Drug News: Lumakras (Sotorasib) Approval',
        'excerpt_tr': 'FDA, KRAS G12C mutasyonu olan küçük hücreli dışı akciğer kanseri tedavisinde Lumakras (sotorasib) ilacını onayladı.',
        'excerpt_en': 'FDA approved Lumakras (sotorasib) for KRAS G12C mutated non-small cell lung cancer treatment.',
        'meta_title': 'FDA Lumakras (Sotorasib) İlaç Onayı | Norosera',
        'meta_description': 'FDA, KRAS G12C mutasyonlu akciğer kanseri için Lumakras ilacını onayladı. Etki mekanizması ve klinik sonuçlar.',
    },
    # 8) Erenumab REFORM
    '280c42bd-169a-4b32-82ab-35b9ece760b5': {
        'title_tr': 'Erenumabın Migren Aurası Sıklığına Etkileri: REFORM Çalışması',
        'title_en': 'Effects of erenumab on migraine aura frequency: a REFORM study',
        'excerpt_tr': 'CGRP karşıtı monoklonal antikor erenumabın migren aurası sıklığını azaltabileceği REFORM çalışmasıyla gösterildi.',
        'excerpt_en': 'Anti-CGRP monoclonal antibody erenumab may reduce migraine aura frequency, as shown by the REFORM study.',
        'meta_title': 'Erenumab ve Migren Aurası: REFORM Çalışması | Norosera',
        'meta_description': 'CGRP karşıtı erenumabın migren aurası üzerindeki etkileri: REFORM çalışma sonuçları.',
    },
}

# Body içindeki yabancı kelime/karakter düzeltmeleri
BODY_REPLACEMENTS = [
    # Almanca/Çince/Vietnamca/Malezce karışan kelimeler
    ('Qualitätini', 'kalitesini'),
    ('Qualität', 'kalite'),
    ('影响', 'etki'),
    ('masih', 'hâlâ'),
    ('phức', 'karmaşık'),
    ('chăm sóc', 'bakım'),
    ('Various', 'Çeşitli'),
    ('various', 'çeşitli'),
    ('prospectif', 'prospektif'),
    # İngilizce karışan kelimeler
    ('birHidden beyin yolunun', 'bir gizli beyin yolunun'),
    ('Qualitätini artırarakVarious', 'kalitesini artırarak çeşitli'),
    ('klinik.performansı', 'klinik performansı'),
    ('non-small hücreli', 'küçük hücreli dışı'),
    # Türkçe karakter düzeltmeleri
    ('arastirma', 'araştırma'),
    ('calisma', 'çalışma'),
    ('baslama', 'başlama'),
    ('norolojik', 'nörolojik'),
    ('uzerinde', 'üzerinde'),
    ('goruntulen', 'görüntülen'),
    ('arasi ', 'arası '),
    ('basinda', 'başında'),
    ('arasinda', 'arasında'),
    ('Uluslararasi', 'Uluslararası'),
]


class Command(BaseCommand):
    help = 'VPS te üretilen yeni haberlerin başlık ve özetlerini Türkçeye çevir'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Değişiklik yapmadan göster')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        updated = 0

        for article_id, fixes in FIXES.items():
            try:
                article = NewsArticle.objects.get(id=article_id)
            except NewsArticle.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Bulunamadı: {article_id}'))
                continue

            self.stdout.write(f'\n--- {article.title_tr[:60]} ---')

            # Başlık, özet, meta güncellemeleri
            fields_to_update = []
            for field, value in fixes.items():
                old_value = getattr(article, field, '')
                if old_value != value:
                    self.stdout.write(f'  {field}: {(old_value or "")[:50]} -> {value[:50]}')
                    if not dry_run:
                        setattr(article, field, value)
                    fields_to_update.append(field)

            # Body içi düzeltmeler
            body = article.body_tr or ''
            original_body = body
            for old, new in BODY_REPLACEMENTS:
                body = body.replace(old, new)

            if body != original_body:
                changes = sum(1 for old, new in BODY_REPLACEMENTS if old in original_body)
                self.stdout.write(f'  body_tr: {changes} düzeltme yapıldı')
                if not dry_run:
                    article.body_tr = body
                fields_to_update.append('body_tr')

            if fields_to_update and not dry_run:
                article.save(update_fields=list(set(fields_to_update)))
                self.stdout.write(self.style.SUCCESS(f'  -> Güncellendi ({len(fields_to_update)} alan)'))
                updated += 1
            elif fields_to_update and dry_run:
                self.stdout.write(self.style.WARNING(f'  -> DRY RUN: {len(fields_to_update)} alan güncellenecek'))
                updated += 1
            else:
                self.stdout.write(self.style.SUCCESS(f'  -> Değişiklik yok'))

        self.stdout.write(f'\n=== Sonuç: {updated}/{len(FIXES)} haber güncellendi ===\n')
