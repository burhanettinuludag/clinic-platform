"""
Gerçek kaynaklardan haber topla ve AI ile Türkçe haber üret.

Kaynaklar: PubMed, FDA RSS, Medscape, ScienceDaily, WHO
Kullanım: python3 manage.py fetch_news [--max-per-source 2] [--max-news 5] [--dry-run]
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Gerçek kaynaklardan nöroloji haberleri topla ve AI ile Türkçe haber üret'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-per-source', type=int, default=2,
            help='Her kaynaktan maksimum çekilecek haber sayısı (varsayılan: 2)',
        )
        parser.add_argument(
            '--max-news', type=int, default=5,
            help='Toplam üretilecek maksimum haber sayısı (varsayılan: 5)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Sadece kaynakları çek, haber üretme',
        )
        parser.add_argument(
            '--source', type=str, default='all',
            choices=['all', 'pubmed', 'rss'],
            help='Hangi kaynaklardan çekilecek (varsayılan: all)',
        )

    def handle(self, *args, **options):
        from services.news_fetcher import NewsFetcher, fetch_pubmed, fetch_rss_feed, PUBMED_QUERIES, RSS_FEEDS

        fetcher = NewsFetcher()
        max_per_source = options['max_per_source']
        max_news = options['max_news']
        dry_run = options['dry_run']
        source_filter = options['source']

        self.stdout.write(self.style.NOTICE(
            f'\nKaynak tarama başlıyor... (max_per_source={max_per_source}, max_news={max_news})\n'
        ))

        if dry_run:
            # Sadece kaynakları çek ve göster
            all_items = []

            if source_filter in ('all', 'pubmed'):
                self.stdout.write('─── PubMed Araştırmaları ───')
                for pq in PUBMED_QUERIES:
                    items = fetch_pubmed(
                        query=pq['query'],
                        max_results=max_per_source,
                        disease=pq['disease'],
                        category=pq['category'],
                    )
                    for item in items:
                        self.stdout.write(f'  [{item.source_name}] {item.title[:80]}')
                        self.stdout.write(f'    → {item.url}')
                        if item.journal:
                            self.stdout.write(f'    → Dergi: {item.journal}')
                        self.stdout.write(f'    → Hastalık: {", ".join(item.disease_tags) or "-"}')
                    all_items.extend(items)

            if source_filter in ('all', 'rss'):
                self.stdout.write('\n─── RSS Feed\'leri ───')
                for feed in RSS_FEEDS:
                    items = fetch_rss_feed(feed, max_items=max_per_source)
                    for item in items:
                        self.stdout.write(f'  [{item.source_name}] {item.title[:80]}')
                        self.stdout.write(f'    → {item.url}')
                    all_items.extend(items)

            self.stdout.write(self.style.SUCCESS(
                f'\nToplam {len(all_items)} haber kaynağı bulundu (dry-run, kayıt yapılmadı)'
            ))
            return

        # Gerçek üretim
        results = fetcher.fetch_and_generate(
            max_per_source=max_per_source,
            max_news=max_news,
        )

        succeeded = sum(1 for r in results if r.get('success'))
        failed = sum(1 for r in results if not r.get('success'))

        self.stdout.write('\n─── Sonuçlar ───')
        for r in results:
            if r.get('success'):
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ {r["title"][:70]} [{r["source"]}]'
                ))
                if r.get('source_url'):
                    self.stdout.write(f'    → {r["source_url"]}')
            else:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ {r.get("title", "?")[:70]} [{r.get("source", "?")}]'
                ))
                if r.get('error'):
                    self.stdout.write(f'    → Hata: {r["error"][:100]}')

        self.stdout.write(self.style.SUCCESS(
            f'\nTamamlandı: {succeeded} başarılı, {failed} başarısız (taslak olarak kaydedildi)'
        ))
