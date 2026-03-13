"""
Broken Link Checker & Auto-Fixer

Tum iceriklerdeki (Article, NewsArticle, EducationItem) linkleri tarar,
kirik olanlari tespit eder ve mumkunse otomatik tamir eder.

Akis:
1. HTML iceriklerden ve URL alanlarindan linkleri cikar
2. Her linki HTTP HEAD ile kontrol et
3. Kirik linkleri BrokenLink modeline kaydet
4. Dahili linkler icin otomatik tamir dene (slug eslestirme)
5. Tarama sonuclarini BrokenLinkScan'e kaydet
"""

import re
import time
import logging
from urllib.parse import urlparse

import requests
from celery import shared_task
from django.db import models
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)

# Link cikarma regex - HTML href ve src
HREF_PATTERN = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
SRC_PATTERN = re.compile(r'src=["\']([^"\']+)["\']', re.IGNORECASE)

# Atlanacak linkler
SKIP_PREFIXES = (
    'mailto:', 'tel:', 'javascript:', '#', 'data:',
    'blob:', 'about:', 'chrome:', 'file:',
)
SKIP_DOMAINS = ('localhost', '127.0.0.1', '0.0.0.0')

# Dahili domain
INTERNAL_DOMAINS = ('norosera.com', 'www.norosera.com')

# HTTP timeout
REQUEST_TIMEOUT = 10
# Max links per scan to avoid overwhelming
MAX_LINKS_PER_SCAN = 500

USER_AGENT = 'Norosera-LinkChecker/1.0 (+https://norosera.com)'


def extract_links_from_html(html_content):
    """HTML icerikten tum linkleri cikar."""
    if not html_content:
        return []

    links = set()
    for match in HREF_PATTERN.finditer(html_content):
        url = match.group(1).strip()
        if url and not url.startswith(SKIP_PREFIXES):
            links.add(url)

    for match in SRC_PATTERN.finditer(html_content):
        url = match.group(1).strip()
        if url and not url.startswith(SKIP_PREFIXES):
            links.add(url)

    return list(links)


def classify_link(url):
    """Linkin turunu belirle: internal, external, image, video."""
    parsed = urlparse(url)
    domain = parsed.hostname or ''

    # Gorsel kontrolu
    path_lower = (parsed.path or '').lower()
    if any(path_lower.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico')):
        return 'image'

    # Video kontrolu
    if any(path_lower.endswith(ext) for ext in ('.mp4', '.webm', '.avi')) or \
       'youtube.com' in domain or 'youtu.be' in domain or 'vimeo.com' in domain:
        return 'video'

    # Dahili kontrolu
    if not domain or domain in INTERNAL_DOMAINS:
        return 'internal'

    return 'external'


def check_url(url):
    """
    URL'nin erisilebilirligini kontrol et.
    Returns: (is_broken, http_status, error_message)
    """
    try:
        # Once HEAD dene (daha hizli)
        resp = requests.head(
            url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            headers={'User-Agent': USER_AGENT},
        )

        # Bazi siteler HEAD'i reddeder, GET ile tekrar dene
        if resp.status_code in (403, 405, 406):
            resp = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                headers={'User-Agent': USER_AGENT},
                stream=True,  # Body'yi indirme
            )
            resp.close()

        if resp.status_code >= 400:
            return True, resp.status_code, f'HTTP {resp.status_code}'
        return False, resp.status_code, ''

    except requests.exceptions.Timeout:
        return True, None, 'Timeout'
    except requests.exceptions.ConnectionError:
        return True, None, 'Connection Error'
    except requests.exceptions.TooManyRedirects:
        return True, None, 'Too Many Redirects'
    except requests.exceptions.SSLError:
        return True, None, 'SSL Error'
    except Exception as e:
        return True, None, str(e)[:200]


def try_auto_fix_internal(broken_url):
    """
    Dahili kirik link icin otomatik tamir dene.
    Slug eslestirme ile yeni URL bul.
    """
    from apps.content.models import Article, NewsArticle, EducationItem

    parsed = urlparse(broken_url)
    path = parsed.path.rstrip('/')
    slug = path.split('/')[-1] if path else ''

    if not slug:
        return None

    # Blog yazisi slug'i kontrol et
    article = Article.objects.filter(
        Q(slug_tr=slug) | Q(slug_en=slug),
        status='published',
    ).first()
    if article:
        return f'/blog/{article.slug_tr}'

    # Haber slug'i
    news = NewsArticle.objects.filter(
        Q(slug_tr=slug) | Q(slug_en=slug),
        status='published',
    ).first()
    if news:
        return f'/news/{news.slug_tr}'

    return None


def collect_content_links():
    """
    Tum iceriklerden link topla.
    Returns: list of (url, source_type, source_id, source_title, source_field, language)
    """
    from apps.content.models import Article, NewsArticle, EducationItem
    from apps.common.models import Announcement, SocialLink

    all_links = []

    # 1. Articles (published)
    for article in Article.objects.filter(status='published').only(
        'id', 'title_tr', 'body_tr', 'body_en'
    ):
        for field_name, lang in [('body_tr', 'tr'), ('body_en', 'en')]:
            html = getattr(article, field_name, '')
            for url in extract_links_from_html(html):
                all_links.append((url, 'article', article.id, article.title_tr, field_name, lang))

    # 2. News Articles (published)
    for news in NewsArticle.objects.filter(status='published').only(
        'id', 'title_tr', 'body_tr', 'body_en', 'source_urls'
    ):
        for field_name, lang in [('body_tr', 'tr'), ('body_en', 'en')]:
            html = getattr(news, field_name, '')
            for url in extract_links_from_html(html):
                all_links.append((url, 'news', news.id, news.title_tr, field_name, lang))

        # source_urls JSON alanindaki linkler
        if news.source_urls and isinstance(news.source_urls, list):
            for url in news.source_urls:
                if isinstance(url, str) and url.startswith('http'):
                    all_links.append((url, 'news', news.id, news.title_tr, 'source_urls', ''))

    # 3. Education Items
    for edu in EducationItem.objects.filter(is_active=True).only(
        'id', 'title_tr', 'body_tr', 'body_en', 'video_url'
    ):
        for field_name, lang in [('body_tr', 'tr'), ('body_en', 'en')]:
            html = getattr(edu, field_name, '')
            for url in extract_links_from_html(html):
                all_links.append((url, 'education', edu.id, edu.title_tr, field_name, lang))

        if edu.video_url:
            all_links.append((edu.video_url, 'education', edu.id, edu.title_tr, 'video_url', ''))

    # 4. Announcements
    for ann in Announcement.objects.filter(is_active=True).only('id', 'title_tr', 'link_url'):
        if ann.link_url:
            all_links.append((ann.link_url, 'announcement', ann.id, ann.title_tr, 'link_url', ''))

    # 5. Social Links
    for sl in SocialLink.objects.filter(is_active=True).only('id', 'platform', 'url'):
        all_links.append((sl.url, 'social_link', sl.id, sl.get_platform_display(), 'url', ''))

    return all_links


def apply_fix_to_content(source_type, source_id, source_field, broken_url, new_url):
    """
    Icerik icindeki kirik linki yeni URL ile degistir.
    Returns: True if fix applied.
    """
    from apps.content.models import Article, NewsArticle, EducationItem
    from apps.common.models import Announcement

    MODEL_MAP = {
        'article': Article,
        'news': NewsArticle,
        'education': EducationItem,
        'announcement': Announcement,
    }

    model_class = MODEL_MAP.get(source_type)
    if not model_class:
        return False

    try:
        obj = model_class.objects.get(id=source_id)
    except model_class.DoesNotExist:
        return False

    # JSON alan (source_urls gibi)
    if source_field == 'source_urls':
        urls = getattr(obj, source_field, [])
        if isinstance(urls, list) and broken_url in urls:
            urls = [new_url if u == broken_url else u for u in urls]
            setattr(obj, source_field, urls)
            obj.save(update_fields=[source_field])
            return True
        return False

    # URL alan (video_url, link_url)
    if source_field in ('video_url', 'link_url', 'url'):
        current_val = getattr(obj, source_field, '')
        if current_val == broken_url:
            setattr(obj, source_field, new_url)
            obj.save(update_fields=[source_field])
            return True
        return False

    # HTML alan (body_tr, body_en)
    html = getattr(obj, source_field, '')
    if broken_url in html:
        html = html.replace(broken_url, new_url)
        setattr(obj, source_field, html)
        obj.save(update_fields=[source_field])
        return True

    return False


@shared_task(name='apps.common.tasks.scan_broken_links')
def scan_broken_links():
    """
    Ana tarama gorevi. Tum iceriklerdeki linkleri kontrol eder.
    Haftalik Celery Beat ile calisir.
    """
    from apps.common.models import BrokenLink, BrokenLinkScan

    start_time = time.time()
    scan = BrokenLinkScan.objects.create(status='running')

    try:
        all_links = collect_content_links()
        logger.info(f"Link taramasi basladi: {len(all_links)} link bulundu")

        # Unique URL'lere indir (ayni URL birden fazla yerde olabilir)
        unique_urls = {}
        for url, src_type, src_id, src_title, src_field, lang in all_links:
            # URL normalize
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://norosera.com' + url

            parsed = urlparse(url)
            if not parsed.scheme or parsed.hostname in SKIP_DOMAINS:
                continue

            if url not in unique_urls:
                unique_urls[url] = []
            unique_urls[url].append((src_type, src_id, src_title, src_field, lang))

        total_checked = 0
        broken_found = 0
        auto_fixed = 0

        # Mevcut kirik linkleri "detected" durumunda birak
        # Sadece yeni kirik linkler ekle

        for url, sources in unique_urls.items():
            if total_checked >= MAX_LINKS_PER_SCAN:
                break

            is_broken, http_status, error_msg = check_url(url)
            total_checked += 1

            if not is_broken:
                # Eger onceden kirik olarak kayitliysa, otomatik tamamla
                BrokenLink.objects.filter(
                    broken_url=url,
                    status='detected',
                ).update(status='auto_fixed', fix_notes='Link tekrar erisilebilir', fixed_at=timezone.now())
                continue

            link_type = classify_link(url)

            # Dahili link icin otomatik tamir dene
            suggested = None
            if link_type == 'internal':
                suggested = try_auto_fix_internal(url)

            for src_type, src_id, src_title, src_field, lang in sources:
                obj, created = BrokenLink.objects.update_or_create(
                    broken_url=url,
                    source_type=src_type,
                    source_id=src_id,
                    source_field=src_field,
                    defaults={
                        'http_status': http_status,
                        'error_message': error_msg,
                        'link_type': link_type,
                        'source_title': src_title,
                        'source_language': lang,
                        'check_count': 1 if created else models.F('check_count') + 1,
                    },
                )

                if created:
                    broken_found += 1

                # Otomatik tamir uygula
                if suggested and obj.status == 'detected':
                    success = apply_fix_to_content(src_type, src_id, src_field, url, suggested)
                    if success:
                        obj.status = 'auto_fixed'
                        obj.suggested_url = suggested
                        obj.fix_notes = f'Dahili link otomatik tamir edildi: {suggested}'
                        obj.fixed_at = timezone.now()
                        obj.save(update_fields=['status', 'suggested_url', 'fix_notes', 'fixed_at'])
                        auto_fixed += 1
                    elif not obj.suggested_url:
                        obj.suggested_url = suggested
                        obj.save(update_fields=['suggested_url'])

            # Rate limiting - sunuculari baskiya sokmamak icin
            if total_checked % 10 == 0:
                time.sleep(0.5)

        duration = int(time.time() - start_time)
        scan.status = 'completed'
        scan.total_links_checked = total_checked
        scan.broken_links_found = broken_found
        scan.auto_fixed_count = auto_fixed
        scan.duration_seconds = duration
        scan.details = {
            'total_content_links': len(all_links),
            'unique_urls': len(unique_urls),
        }
        scan.save()

        logger.info(
            f"Link taramasi tamamlandi: {total_checked} kontrol, "
            f"{broken_found} kirik, {auto_fixed} otomatik tamir, "
            f"{duration}s sure"
        )

        return {
            'total_checked': total_checked,
            'broken_found': broken_found,
            'auto_fixed': auto_fixed,
            'duration_seconds': duration,
        }

    except Exception as e:
        scan.status = 'failed'
        scan.error_message = str(e)[:500]
        scan.duration_seconds = int(time.time() - start_time)
        scan.save()
        logger.error(f"Link taramasi basarisiz: {e}")
        raise


@shared_task(name='apps.common.tasks.fix_broken_link')
def fix_broken_link(broken_link_id, new_url, user_id=None):
    """
    Tek bir kirik linki manuel tamir et.
    Admin panelden tetiklenir.
    """
    from apps.common.models import BrokenLink
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        bl = BrokenLink.objects.get(id=broken_link_id)
    except BrokenLink.DoesNotExist:
        return {'error': 'Kirik link bulunamadi'}

    success = apply_fix_to_content(
        bl.source_type, bl.source_id, bl.source_field,
        bl.broken_url, new_url
    )

    if success:
        bl.status = 'manually_fixed'
        bl.suggested_url = new_url
        bl.fix_notes = f'Manuel tamir: {bl.broken_url} -> {new_url}'
        bl.fixed_at = timezone.now()
        if user_id:
            try:
                bl.fixed_by = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        bl.save()
        return {'success': True, 'message': 'Link tamir edildi'}
    else:
        return {'success': False, 'message': 'Link icerikte bulunamadi'}
