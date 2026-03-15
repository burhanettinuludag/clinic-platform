"""
Haberlere baslik ve icerikteki anahtar kelimelere gore hastalik modulu ata.

Migren ile ilgili haberler -> Migren modulu
Epilepsi ile ilgili haberler -> Epilepsi modulu
Demans/Alzheimer ile ilgili haberler -> Demans modulu

Kullanim:
    python3 manage.py assign_news_diseases           # Tum haberlere ata
    python3 manage.py assign_news_diseases --dry-run  # Degisiklik yapmadan goster
    python3 manage.py assign_news_diseases --create-modules  # DiseaseModule yoksa olustur
"""
import re
from django.core.management.base import BaseCommand
from apps.content.models import NewsArticle
from apps.patients.models import DiseaseModule


# Hastalik tespiti icin anahtar kelimeler (case-insensitive)
DISEASE_KEYWORDS = {
    'migraine': [
        r'migren', r'migraine', r'bas\s*agr[ıi]', r'headache',
        r'cgrp', r'aura', r'triptan', r'norostim[uü]lasyon',
        r'botox.*bas', r'bas.*botox',
    ],
    'epilepsy': [
        r'epilepsi', r'epilepsy', r'n[oö]bet', r'seizure',
        r'eeg', r'antiepilep', r'cenobamat', r'valproat',
        r'karbamazepin', r'levetirasetam', r'n[oö]bet\s*tahmin',
    ],
    'dementia': [
        r'demans', r'dementia', r'alzheimer', r'hafiza',
        r'bilis', r'kognitif', r'cognitive', r'lecanemab',
        r'aducanumab', r'bilissel', r'hafif\s*bilis',
        r'n[oö]rodejeneratif', r'neurodegen',
    ],
}


def detect_diseases(text: str) -> list[str]:
    """Metinde gecen hastaliklari tespit et."""
    text_lower = text.lower()
    found = []
    for disease, patterns in DISEASE_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found.append(disease)
                break
    return found


class Command(BaseCommand):
    help = 'Haberlere baslik/icerik analizi ile hastalik modulu ata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Degisiklik yapmadan ne yapilacagini goster',
        )
        parser.add_argument(
            '--create-modules', action='store_true',
            help='DiseaseModule kayitlari yoksa olustur',
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Mevcut hastalik iliskilerini temizleyip yeniden ata',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        create_modules = options['create_modules']
        clear = options['clear']

        # DiseaseModule var mi kontrol et
        existing_modules = {m.slug: m for m in DiseaseModule.objects.all()}

        if not existing_modules or create_modules:
            self._ensure_modules(existing_modules, dry_run)
            existing_modules = {m.slug: m for m in DiseaseModule.objects.all()}

        if not existing_modules:
            self.stdout.write(self.style.ERROR(
                'DiseaseModule bulunamadi! --create-modules ile calistirin.'
            ))
            return

        self.stdout.write(f'\nMevcut hastalik modulleri:')
        for slug, mod in existing_modules.items():
            self.stdout.write(f'  - {slug}: {mod.name_tr}')
        self.stdout.write('')

        # Haberleri isle
        articles = NewsArticle.objects.filter(status='published').order_by('-published_at')
        total = articles.count()
        assigned_count = 0
        disease_counts = {'migraine': 0, 'epilepsy': 0, 'dementia': 0}

        self.stdout.write(f'{total} yayinli haber analiz ediliyor...\n')

        for i, article in enumerate(articles, 1):
            # Baslik + ozet + body'de anahtar kelime ara
            search_text = ' '.join(filter(None, [
                article.title_tr or '',
                article.title_en or '',
                article.excerpt_tr or '',
                article.excerpt_en or '',
                (article.body_tr or '')[:500],  # Body'nin ilk 500 karakteri
            ]))

            diseases = detect_diseases(search_text)

            current_diseases = list(article.related_diseases.values_list('slug', flat=True))

            if not diseases:
                self.stdout.write(
                    f'  [{i}/{total}] {article.title_tr[:55]}...'
                    f'\n           -> Hastalik bulunamadi (genel noroloji)'
                )
                continue

            # Degisiklik gerekli mi?
            if set(diseases) == set(current_diseases) and not clear:
                self.stdout.write(
                    f'  [{i}/{total}] {article.title_tr[:55]}...'
                    f'\n           -> Zaten atanmis: {diseases}'
                )
                continue

            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f'  [{i}/{total}] {article.title_tr[:55]}...'
                    f'\n           -> DRY RUN: {diseases} atanacak'
                ))
            else:
                if clear:
                    article.related_diseases.clear()

                for disease_slug in diseases:
                    if disease_slug in existing_modules:
                        article.related_diseases.add(existing_modules[disease_slug])
                        disease_counts[disease_slug] += 1

                self.stdout.write(self.style.SUCCESS(
                    f'  [{i}/{total}] {article.title_tr[:55]}...'
                    f'\n           -> Atandi: {diseases}'
                ))

            assigned_count += 1

        self.stdout.write(f'\n--- Sonuc ---')
        self.stdout.write(self.style.SUCCESS(
            f'Islenen: {assigned_count}/{total} haber'
        ))
        for d, count in disease_counts.items():
            self.stdout.write(f'  {d}: {count} haber')
        self.stdout.write('')

    def _ensure_modules(self, existing, dry_run):
        """Eksik DiseaseModule kayitlarini olustur."""
        modules_data = [
            {
                'slug': 'migraine',
                'disease_type': 'migraine',
                'name_tr': 'Migren',
                'name_en': 'Migraine',
                'description_tr': 'Migren hastaligi takibi ve bilgilendirme',
                'description_en': 'Migraine disease tracking and information',
                'icon': 'brain',
                'is_active': True,
                'order': 1,
            },
            {
                'slug': 'epilepsy',
                'disease_type': 'epilepsy',
                'name_tr': 'Epilepsi',
                'name_en': 'Epilepsy',
                'description_tr': 'Epilepsi hastaligi takibi ve bilgilendirme',
                'description_en': 'Epilepsy disease tracking and information',
                'icon': 'zap',
                'is_active': True,
                'order': 2,
            },
            {
                'slug': 'dementia',
                'disease_type': 'dementia',
                'name_tr': 'Demans / Alzheimer',
                'name_en': 'Dementia / Alzheimer',
                'description_tr': 'Demans ve Alzheimer hastaligi takibi',
                'description_en': 'Dementia and Alzheimer disease tracking',
                'icon': 'activity',
                'is_active': True,
                'order': 3,
            },
        ]

        for data in modules_data:
            if data['slug'] not in existing:
                if dry_run:
                    self.stdout.write(self.style.WARNING(
                        f'DRY RUN: DiseaseModule olusturulacak: {data["slug"]}'
                    ))
                else:
                    obj, created = DiseaseModule.objects.get_or_create(
                        slug=data['slug'],
                        defaults=data,
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            f'DiseaseModule olusturuldu: {data["slug"]} ({data["name_tr"]})'
                        ))
                    else:
                        self.stdout.write(f'DiseaseModule zaten var: {data["slug"]}')
