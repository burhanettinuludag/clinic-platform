"""
Mevcut haberlere ucretsiz stok gorsel ata.
API key gerektirmez - onceden secilmis Unsplash CDN URL'lerini kullanir.

Kullanim:
    python3 manage.py assign_news_images           # Gorselsiz tum haberlere ata
    python3 manage.py assign_news_images --limit 5  # Sadece 5 habere ata
    python3 manage.py assign_news_images --force     # Mevcut gorselleri de guncelle
    python3 manage.py assign_news_images --dry-run   # Degisiklik yapmadan goster
"""
from django.core.management.base import BaseCommand
from apps.content.models import NewsArticle
from services.stock_images import get_medical_image


class Command(BaseCommand):
    help = 'Haberlere ucretsiz stok gorsel ata (API key gerektirmez)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=0,
            help='Maksimum kac habere gorsel atanacak (0 = hepsi)',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Mevcut gorseli olan haberlere de yeniden ata',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Degisiklik yapmadan ne yapilacagini goster',
        )

    def handle(self, *args, **options):
        force = options['force']
        limit = options['limit']
        dry_run = options['dry_run']

        qs = NewsArticle.objects.filter(status='published').order_by('-published_at')

        if not force:
            qs = qs.filter(featured_image_url='')

        if limit:
            qs = qs[:limit]

        articles = list(qs)
        total = len(articles)

        if total == 0:
            self.stdout.write(self.style.WARNING('Gorsel atanacak haber bulunamadi.'))
            return

        self.stdout.write(f'\n{total} habere gorsel atanacak...\n')
        success_count = 0

        for i, article in enumerate(articles, 1):
            diseases = list(article.related_diseases.values_list('slug', flat=True))
            disease_str = ', '.join(diseases) if diseases else '-'

            result = get_medical_image(
                category=article.category,
                diseases=diseases,
                seed=article.slug,
            )

            self.stdout.write(
                f'  [{i}/{total}] {article.title_tr[:55]}...\n'
                f'           Kategori: {article.category} | Hastalik: {disease_str}'
            )

            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f'           -> DRY RUN: {result["url"][:60]}...'
                ))
                success_count += 1
                continue

            article.featured_image_url = result['url']
            if not article.featured_image_alt or force:
                article.featured_image_alt = result['alt'][:200]
            article.save(update_fields=['featured_image_url', 'featured_image_alt'])

            self.stdout.write(self.style.SUCCESS(
                f'           -> OK: {result["alt"][:50]}'
            ))
            success_count += 1

        self.stdout.write(f'\n--- Sonuc ---')
        self.stdout.write(self.style.SUCCESS(f'Atanan: {success_count}/{total}'))
        self.stdout.write('')
