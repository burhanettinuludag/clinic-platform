"""
Gerçek haber kaynağı toplayıcı.

PubMed, FDA, EMA ve nöroloji haber RSS feed'lerinden güncel haberleri çeker,
news_agent'a besleyerek Türkçe haber ürettirir.

Kaynaklar:
- PubMed E-utilities API (nöroloji araştırmaları)
- FDA Drug Approvals RSS
- Medscape Neurology RSS
- Neurology Today RSS
- WHO Newsroom RSS

Kullanım:
    from services.news_fetcher import NewsFetcher
    fetcher = NewsFetcher()
    items = fetcher.fetch_all(max_per_source=3)
"""

import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

FETCH_TIMEOUT = 15  # saniye


@dataclass
class NewsItem:
    """Dış kaynaktan çekilen ham haber."""
    title: str
    summary: str = ''
    url: str = ''
    source_name: str = ''
    source_type: str = ''  # pubmed, fda, rss
    published_at: Optional[datetime] = None
    authors: str = ''
    journal: str = ''
    category: str = 'popular_science'
    keywords: list = field(default_factory=list)
    disease_tags: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════
# PubMed E-utilities (ücretsiz, API key opsiyonel)
# ═══════════════════════════════════════════════════════

PUBMED_SEARCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
PUBMED_FETCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

PUBMED_QUERIES = [
    {
        'query': 'migraine treatment 2025:2026[dp]',
        'disease': 'migraine',
        'category': 'clinical_trial',
    },
    {
        'query': 'epilepsy seizure therapy 2025:2026[dp]',
        'disease': 'epilepsy',
        'category': 'clinical_trial',
    },
    {
        'query': 'alzheimer dementia treatment 2025:2026[dp]',
        'disease': 'dementia',
        'category': 'clinical_trial',
    },
    {
        'query': 'neurology breakthrough 2025:2026[dp]',
        'disease': '',
        'category': 'popular_science',
    },
]


def fetch_pubmed(query: str, max_results: int = 3, disease: str = '', category: str = 'clinical_trial') -> list[NewsItem]:
    """PubMed'den araştırma makaleleri çeker."""
    items = []
    try:
        # 1. Arama — PMID listesi al
        search_resp = requests.get(PUBMED_SEARCH_URL, params={
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'sort': 'date',
            'retmode': 'json',
        }, timeout=FETCH_TIMEOUT)
        search_resp.raise_for_status()
        id_list = search_resp.json().get('esearchresult', {}).get('idlist', [])

        if not id_list:
            return items

        # 2. Detay çek — XML
        fetch_resp = requests.get(PUBMED_FETCH_URL, params={
            'db': 'pubmed',
            'id': ','.join(id_list),
            'retmode': 'xml',
        }, timeout=FETCH_TIMEOUT)
        fetch_resp.raise_for_status()

        root = ET.fromstring(fetch_resp.text)
        for article_el in root.findall('.//PubmedArticle'):
            try:
                title_el = article_el.find('.//ArticleTitle')
                abstract_el = article_el.find('.//AbstractText')
                journal_el = article_el.find('.//Journal/Title')
                year_el = article_el.find('.//PubDate/Year')
                pmid_el = article_el.find('.//PMID')

                title = title_el.text if title_el is not None and title_el.text else ''
                abstract = abstract_el.text if abstract_el is not None and abstract_el.text else ''
                journal = journal_el.text if journal_el is not None and journal_el.text else ''
                pmid = pmid_el.text if pmid_el is not None and pmid_el.text else ''

                # Yazarlar
                authors = []
                for author_el in article_el.findall('.//Author'):
                    last = author_el.findtext('LastName', '')
                    first = author_el.findtext('ForeName', '')
                    if last:
                        authors.append(f"{last} {first}".strip())

                if not title:
                    continue

                disease_tags = [disease] if disease else []
                # Hastalık tespiti
                text_lower = (title + ' ' + abstract).lower()
                if 'migrain' in text_lower and 'migraine' not in disease_tags:
                    disease_tags.append('migraine')
                if 'epilep' in text_lower or 'seizure' in text_lower:
                    if 'epilepsy' not in disease_tags:
                        disease_tags.append('epilepsy')
                if 'alzheimer' in text_lower or 'dementia' in text_lower:
                    if 'dementia' not in disease_tags:
                        disease_tags.append('dementia')

                items.append(NewsItem(
                    title=title,
                    summary=abstract[:1000],
                    url=f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/' if pmid else '',
                    source_name='PubMed',
                    source_type='pubmed',
                    authors=', '.join(authors[:5]),
                    journal=journal,
                    category=category,
                    disease_tags=disease_tags,
                    keywords=[disease] if disease else [],
                ))
            except Exception as e:
                logger.warning(f"PubMed makale parse hatası: {e}")
                continue

    except Exception as e:
        logger.error(f"PubMed fetch hatası [{query[:40]}]: {e}")

    return items


# ═══════════════════════════════════════════════════════
# RSS Feed Parser (XML tabanlı, feedparser gerektirmez)
# ═══════════════════════════════════════════════════════

RSS_FEEDS = [
    {
        'name': 'FDA Drug Approvals',
        'url': 'https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/drugs/rss.xml',
        'category': 'fda_approval',
        'diseases': [],
    },
    {
        'name': 'Nature Neuroscience',
        'url': 'https://www.nature.com/neuro.rss',
        'category': 'clinical_trial',
        'diseases': [],
    },
    {
        'name': 'JAMA Neurology',
        'url': 'https://jamanetwork.com/rss/site_3/67.xml',
        'category': 'clinical_trial',
        'diseases': [],
    },
    {
        'name': 'ScienceDaily Neuroscience',
        'url': 'https://www.sciencedaily.com/rss/mind_brain/neuroscience.xml',
        'category': 'popular_science',
        'diseases': [],
    },
    {
        'name': 'WHO Newsroom',
        'url': 'https://www.who.int/rss-feeds/news-english.xml',
        'category': 'popular_science',
        'diseases': [],
    },
]


def fetch_rss_feed(feed_config: dict, max_items: int = 3) -> list[NewsItem]:
    """Tek bir RSS feed'den haber çeker (stdlib XML parser)."""
    items = []
    name = feed_config['name']
    url = feed_config['url']

    try:
        resp = requests.get(url, timeout=FETCH_TIMEOUT, headers={
            'User-Agent': 'Norosera/1.0 (Neurology Platform; +https://norosera.com)',
        })
        resp.raise_for_status()

        root = ET.fromstring(resp.text)

        # RSS 2.0 items
        entries = root.findall('.//item')
        if not entries:
            # Atom format
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('.//atom:entry', ns)

        for entry in entries[:max_items]:
            title = (
                entry.findtext('title')
                or entry.findtext('{http://www.w3.org/2005/Atom}title')
                or ''
            ).strip()

            description = (
                entry.findtext('description')
                or entry.findtext('{http://www.w3.org/2005/Atom}summary')
                or ''
            ).strip()
            # HTML tag temizle
            description = re.sub(r'<[^>]+>', '', description).strip()

            link = (
                entry.findtext('link')
                or ''
            ).strip()
            if not link:
                link_el = entry.find('{http://www.w3.org/2005/Atom}link')
                if link_el is not None:
                    link = link_el.get('href', '')

            pub_date_str = (
                entry.findtext('pubDate')
                or entry.findtext('{http://www.w3.org/2005/Atom}published')
                or ''
            )

            if not title:
                continue

            # Nöroloji ile ilgili mi kontrol et
            text_lower = (title + ' ' + description).lower()
            neuro_keywords = [
                'neurol', 'brain', 'migrain', 'epilep', 'seizure', 'alzheimer',
                'dementia', 'cognitive', 'headache', 'stroke', 'parkinson',
                'nöroloji', 'beyin', 'migren', 'nöbet',
            ]

            # FDA feed'i her zaman dahil et, diğerleri nöroloji filtresi uygula
            is_neuro = feed_config['category'] == 'fda_approval' or any(
                kw in text_lower for kw in neuro_keywords
            )
            if not is_neuro:
                continue

            # Hastalık tag'leri
            disease_tags = list(feed_config.get('diseases', []))
            if 'migrain' in text_lower or 'headache' in text_lower:
                disease_tags.append('migraine')
            if 'epilep' in text_lower or 'seizure' in text_lower:
                disease_tags.append('epilepsy')
            if 'alzheimer' in text_lower or 'dementia' in text_lower or 'cognitive' in text_lower:
                disease_tags.append('dementia')

            items.append(NewsItem(
                title=title,
                summary=description[:1000],
                url=link,
                source_name=name,
                source_type='rss',
                category=feed_config['category'],
                disease_tags=list(set(disease_tags)),
            ))

    except Exception as e:
        logger.error(f"RSS fetch hatası [{name}]: {e}")

    return items


# ═══════════════════════════════════════════════════════
# Ana Fetcher sınıfı
# ═══════════════════════════════════════════════════════

class NewsFetcher:
    """Tüm kaynaklardan haber toplar ve news_agent'a besler."""

    def fetch_all(self, max_per_source: int = 3) -> list[NewsItem]:
        """Tüm kaynaklardan haber çeker."""
        all_items: list[NewsItem] = []

        # PubMed
        for pq in PUBMED_QUERIES:
            items = fetch_pubmed(
                query=pq['query'],
                max_results=max_per_source,
                disease=pq['disease'],
                category=pq['category'],
            )
            all_items.extend(items)
            logger.info(f"PubMed [{pq['disease'] or 'general'}]: {len(items)} makale")

        # RSS Feeds
        for feed in RSS_FEEDS:
            items = fetch_rss_feed(feed, max_items=max_per_source)
            all_items.extend(items)
            logger.info(f"RSS [{feed['name']}]: {len(items)} haber")

        logger.info(f"Toplam {len(all_items)} haber kaynağı toplandı")
        return all_items

    def fetch_and_generate(self, max_per_source: int = 2, max_news: int = 5) -> list[dict]:
        """
        Kaynakları çek → news_agent ile Türkçe haber üret → NewsArticle kaydet.
        Dönen liste: [{news_id, title, source, success}, ...]
        """
        from apps.content.models import NewsArticle
        from apps.patients.models import DiseaseModule
        from django.utils.text import slugify
        from services.registry import agent_registry
        from services.base_agent import BaseAgent
        import uuid

        raw_items = self.fetch_all(max_per_source=max_per_source)

        if not raw_items:
            logger.warning("Hiçbir kaynak bulunamadı")
            return []

        # Önceliğe göre sırala: pubmed > fda > rss
        source_priority = {'pubmed': 0, 'fda': 1, 'rss': 2}
        raw_items.sort(key=lambda x: source_priority.get(x.source_type, 9))

        # Tekrar kontrol: aynı başlıkla daha önce haber var mı
        existing_titles = set(
            NewsArticle.objects.values_list('title_en', flat=True)
        )

        # FeatureFlag bypass
        original_is_enabled = BaseAgent.is_enabled
        BaseAgent.is_enabled = lambda self: True

        results = []
        generated = 0

        try:
            news_agent = agent_registry.get('news_agent')
            if not news_agent:
                logger.error("news_agent bulunamadı")
                return []

            disease_map = {dm.slug: dm for dm in DiseaseModule.objects.all()}

            for item in raw_items:
                if generated >= max_news:
                    break

                # Başlık benzerliği kontrolü (basit)
                if item.title in existing_titles:
                    continue

                try:
                    # news_agent'a kaynak bilgisini besle
                    agent_input = {
                        'topic': item.title,
                        'source': item.url,
                        'type': _detect_news_type(item),
                        'study': item.title,
                        'journal': item.journal,
                        'summary': item.summary[:500],
                        'source_name': item.source_name,
                    }

                    agent_result = news_agent.run(agent_input)

                    if not agent_result.success:
                        logger.warning(f"news_agent başarısız: {item.title[:60]}")
                        results.append({
                            'title': item.title[:80],
                            'source': item.source_name,
                            'success': False,
                            'error': agent_result.error,
                        })
                        continue

                    data = agent_result.data or {}
                    title_tr = data.get('title_tr', '') or item.title
                    body_tr = data.get('body_tr', '')

                    if not body_tr:
                        continue

                    # Slug oluştur
                    slug_base = slugify(title_tr[:80]) or f'haber-{uuid.uuid4().hex[:8]}'
                    slug = slug_base
                    counter = 1
                    while NewsArticle.objects.filter(slug=slug).exists():
                        slug = f'{slug_base}-{counter}'
                        counter += 1

                    # Kategori
                    category = data.get('category', item.category)
                    valid_cats = [c[0] for c in NewsArticle.CATEGORY_CHOICES]
                    if category not in valid_cats:
                        category = 'popular_science'

                    # Kaydet
                    news = NewsArticle.objects.create(
                        slug=slug,
                        title_tr=title_tr,
                        title_en=data.get('title_en', item.title),
                        excerpt_tr=data.get('excerpt_tr', item.summary[:200]),
                        excerpt_en=data.get('excerpt_en', item.summary[:200]),
                        body_tr=body_tr,
                        body_en=data.get('body_en', ''),
                        category=category,
                        priority='medium',
                        status='published',
                        published_at=timezone.now(),
                        is_auto_generated=True,
                        source_urls=[{'url': item.url, 'title': item.source_name}] if item.url else [],
                        meta_title=title_tr[:200],
                        meta_description=data.get('excerpt_tr', '')[:300],
                    )

                    # Hastalık ilişkilendir
                    for dtag in item.disease_tags:
                        dm = disease_map.get(dtag)
                        if dm:
                            news.related_diseases.add(dm)

                    existing_titles.add(item.title)
                    generated += 1

                    results.append({
                        'news_id': str(news.id),
                        'title': title_tr[:80],
                        'source': item.source_name,
                        'source_url': item.url,
                        'category': category,
                        'success': True,
                    })
                    logger.info(f"Haber üretildi: {title_tr[:60]} [{item.source_name}]")

                except Exception as e:
                    logger.error(f"Haber üretim hatası [{item.title[:40]}]: {e}")
                    results.append({
                        'title': item.title[:80],
                        'source': item.source_name,
                        'success': False,
                        'error': str(e),
                    })

        finally:
            BaseAgent.is_enabled = original_is_enabled

        logger.info(f"Haber üretimi tamamlandı: {generated}/{len(raw_items)} başarılı")
        return results


def _detect_news_type(item: NewsItem) -> str:
    """Kaynak bilgisinden haber tipini belirle."""
    text = (item.title + ' ' + item.summary).lower()
    if 'fda' in text or 'approv' in text:
        return 'fda_approval'
    if 'clinical trial' in text or 'phase' in text or 'randomized' in text:
        return 'clinical_trial'
    return 'general'
