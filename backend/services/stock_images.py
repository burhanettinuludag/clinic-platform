"""
Noroloji odakli ucretsiz stok gorseller - API key gerektirmez.

Unsplash CDN URL'leri herkese acik ve ucretsizdir.
Unsplash License: https://unsplash.com/license
- Ucretsiz ticari kullanim
- Atifta bulunmak zorunlu degil ama tavsiye edilir

Tum gorseller beyin, noron, MRI, EEG gibi noroloji temalarina
odaklanmistir. Her kategori ve hastalik icin farkli beyin gorselleri
secilmistir.

Kullanim:
    from services.stock_images import get_medical_image
    result = get_medical_image(category='fda_approval', diseases=['migraine'])
    # result = {'url': '...', 'alt': '...', 'credit': '...'}
"""

import random
import hashlib
import logging

logger = logging.getLogger(__name__)


# ============================================================
# Unsplash CDN - Noroloji ve Beyin Odakli Gorseller
# API key gerekmez, dogrudan CDN URL kullanilir
# Tum photo ID'ler dogrulanmistir (HTTP 200)
# ============================================================

def _u(photo_id: str, w: int = 800, h: int = 450) -> str:
    """Unsplash CDN URL olustur. API key gerektirmez."""
    return f'https://images.unsplash.com/{photo_id}?w={w}&h={h}&fit=crop&q=80&auto=format'


# ---------- MIGREN (Beyin goruntuleme, norolojik agri, ilac) ----------
MIGRAINE_IMAGES = [
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Renkli beyin MRI goruntulemesi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1617791160505-6f00504e3519'),
        'alt': 'Noron aglari ve sinirsel baglantilar',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1614935151651-0bea6508db6b'),
        'alt': 'Dijital beyin ilustrasyonu - noroloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1551076805-e1869033e561'),
        'alt': 'Beyin bilimi ve norolojik arastirma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1576091160550-2173dba999ef'),
        'alt': 'Norolojik ilac tedavisi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1453847668862-487637052f8a'),
        'alt': 'Beyin anatomisi ve sinir sistemi',
        'credit': 'Unsplash',
    },
]

# ---------- EPILEPSI (EEG, noronlar, beyin dalgalari) ----------
EPILEPSY_IMAGES = [
    {
        'url': _u('photo-1559757148-5c350d0d3c56'),
        'alt': 'EEG beyin dalgalari olcumu',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1516549655169-df83a0774514'),
        'alt': 'Noron hucresi - mikroskop goruntusu',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1581093806997-124204d9fa9d'),
        'alt': 'Sinir hucreleri ve noron aglari',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1617791160536-598cf32026fb'),
        'alt': 'Norolojik sinyal iletimi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1620641788421-7a1c342ea42e'),
        'alt': 'Beyin aktivitesi ve noroloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1581595220892-b0739db3ba8c'),
        'alt': 'Beyin arastirmasi ve sinir bilimi',
        'credit': 'Unsplash',
    },
]

# ---------- DEMANS / ALZHEIMER (Beyin modeli, kognitif, yasli bakim) ----------
DEMENTIA_IMAGES = [
    {
        'url': _u('photo-1530497610245-94d3c16cda28'),
        'alt': 'Anatomik beyin modeli - demans arastirmasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin MRI taramasi - Alzheimer tespiti',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1566438480900-0609be27a4be'),
        'alt': 'Beyin modeli - kognitif saglik',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1549925245-f20a1bac6454'),
        'alt': 'Noron baglantilari ve beyin yapisi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1611532736597-de2d4265fba3'),
        'alt': 'Beyin aktivite haritalamasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1573497620053-ea5300f94f21'),
        'alt': 'Kognitif saglik ve destek hizmetleri',
        'credit': 'Unsplash',
    },
]

# ---------- FDA / ILAC ONAYI (Ilac + beyin) ----------
FDA_IMAGES = [
    {
        'url': _u('photo-1576091160550-2173dba999ef'),
        'alt': 'Norolojik ilac tedavisi ve onayi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1471864190281-a93a3070b6de'),
        'alt': 'Ilac molekulleri ve norolojik arastirma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin goruntulemesi - ilac etkisi analizi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1614935151651-0bea6508db6b'),
        'alt': 'Dijital beyin - farmakolojik calisma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1606112219348-204d7d8b94ee'),
        'alt': 'Norolojik ilac gelistirme sureci',
        'credit': 'Unsplash',
    },
]

# ---------- KLINIK ARASTIRMA (Beyin arastirmasi, laboratuvar) ----------
CLINICAL_TRIAL_IMAGES = [
    {
        'url': _u('photo-1581595220892-b0739db3ba8c'),
        'alt': 'Beyin arastirmasi - klinik calisma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1507413245164-6160d8298b31'),
        'alt': 'Norolojik bilimsel arastirma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1579684385127-1ef15d508118'),
        'alt': 'Noroloji laboratuvar calismasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1557200134-90327ee9fafa'),
        'alt': 'Sinir bilimi arastirmasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1530026405186-ed1f139313f8'),
        'alt': 'Beyin bilimi laboratuvari',
        'credit': 'Unsplash',
    },
]

# ---------- TIBBI CIHAZ (EEG, MRI, noroloji teknolojisi) ----------
DEVICE_IMAGES = [
    {
        'url': _u('photo-1576091160399-112ba8d25d1d'),
        'alt': 'Norolojik tani teknolojisi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1559757148-5c350d0d3c56'),
        'alt': 'EEG cihazi ve beyin dalgasi olcumu',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1589279003513-467d320f47eb'),
        'alt': 'Yapay zeka ve beyin teknolojisi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1618005198919-d3d4b5a92ead'),
        'alt': 'Dijital noron agi ve teknoloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1628595351029-c2bf17511435'),
        'alt': 'Norolojik goruntuleleme teknolojisi',
        'credit': 'Unsplash',
    },
]

# ---------- KONGRE (Bilimsel sunum + beyin) ----------
CONGRESS_IMAGES = [
    {
        'url': _u('photo-1475721027785-f74eccf877e2'),
        'alt': 'Noroloji kongresi ve bilimsel sunum',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1505373877841-8d25f7d46678'),
        'alt': 'Noroloji akademik konferansi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1558021212-51b6ecfa0db9'),
        'alt': 'Beyin bilimi sempozyumu',
        'credit': 'Unsplash',
    },
]

# ---------- POPULER BILIM (Noron, beyin, sinir sistemi) ----------
POPULAR_SCIENCE_IMAGES = [
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin bilimi ve noroloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1516549655169-df83a0774514'),
        'alt': 'Noron hucresi ve sinir bilimi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1617791160505-6f00504e3519'),
        'alt': 'Norolojik baglantilar ve sinaps',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1590859808308-3d2d9c515b1a'),
        'alt': 'Beyin ve sinir sistemi kesileri',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1564053489984-317bbd824340'),
        'alt': 'Norolojik arastirma ve kesfler',
        'credit': 'Unsplash',
    },
]

# ---------- GENEL NOROLOJI (Beyin odakli, karisik) ----------
GENERAL_IMAGES = [
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin MRI goruntulemesi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1617791160505-6f00504e3519'),
        'alt': 'Noron aglari ve sinirsel baglanti',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1614935151651-0bea6508db6b'),
        'alt': 'Dijital beyin - noroloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1530497610245-94d3c16cda28'),
        'alt': 'Anatomik beyin modeli',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1551076805-e1869033e561'),
        'alt': 'Beyin bilimi ve noroloji arastirmasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1581093806997-124204d9fa9d'),
        'alt': 'Sinir hucreleri - noroloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1566438480900-0609be27a4be'),
        'alt': 'Beyin modeli - norolojik saglik',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1589279003513-467d320f47eb'),
        'alt': 'Beyin ve yapay zeka teknolojisi',
        'credit': 'Unsplash',
    },
]


# Kategori -> gorsel listesi eslesmesi
CATEGORY_IMAGES = {
    'fda_approval': FDA_IMAGES,
    'ema_approval': FDA_IMAGES,
    'turkey_approval': FDA_IMAGES,
    'clinical_trial': CLINICAL_TRIAL_IMAGES,
    'new_device': DEVICE_IMAGES,
    'congress': CONGRESS_IMAGES,
    'popular_science': POPULAR_SCIENCE_IMAGES,
    'drug_update': FDA_IMAGES,
    'guideline_update': GENERAL_IMAGES,
    'turkey_news': GENERAL_IMAGES,
    'research': CLINICAL_TRIAL_IMAGES,
}

# Hastalik -> gorsel listesi eslesmesi
DISEASE_IMAGES = {
    'migraine': MIGRAINE_IMAGES,
    'epilepsy': EPILEPSY_IMAGES,
    'dementia': DEMENTIA_IMAGES,
}


def get_medical_image(
    category: str = 'general',
    diseases: list = None,
    seed: str = '',
) -> dict:
    """
    Kategori ve hastaliga uygun noroloji odakli gorsel sec.

    API key gerektirmez - onceden secilmis Unsplash CDN URL'lerini kullanir.
    Tum gorseller beyin, noron, MRI, EEG gibi noroloji temalaridir.

    Args:
        category: Haber kategorisi (fda_approval, clinical_trial, vb.)
        diseases: Iliskili hastalik slug listesi (['migraine', 'epilepsy'])
        seed: Deterministic secim icin seed (ornegin slug).
              Ayni seed her zaman ayni gorseli dondurur.

    Returns:
        dict: {'url': str, 'alt': str, 'credit': str}
    """
    # Hastalik bazli gorsel havuzu (oncelikli)
    pool = []
    if diseases:
        for disease in diseases:
            pool.extend(DISEASE_IMAGES.get(disease, []))

    # Kategori bazli gorsel havuzu
    pool.extend(CATEGORY_IMAGES.get(category, []))

    # Fallback: genel noroloji havuzu
    if not pool:
        pool = GENERAL_IMAGES

    # Tekrarlari kaldir (url bazinda)
    seen_urls = set()
    unique_pool = []
    for img in pool:
        if img['url'] not in seen_urls:
            seen_urls.add(img['url'])
            unique_pool.append(img)

    # Deterministic secim (ayni haber her zaman ayni gorseli alsin)
    if seed:
        idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(unique_pool)
        return unique_pool[idx]

    # Random secim
    return random.choice(unique_pool)


def assign_image_to_news(news_article, force: bool = False) -> bool:
    """
    Bir NewsArticle'a otomatik noroloji odakli gorsel ata.

    Args:
        news_article: NewsArticle model instance
        force: True ise mevcut gorsel olsa bile degistir

    Returns:
        bool: Gorsel atandiysa True
    """
    if not force and (news_article.featured_image_url or news_article.featured_image):
        return False

    diseases = list(news_article.related_diseases.values_list('slug', flat=True))

    result = get_medical_image(
        category=news_article.category,
        diseases=diseases,
        seed=news_article.slug,
    )

    if result:
        news_article.featured_image_url = result['url']
        if not news_article.featured_image_alt or force:
            news_article.featured_image_alt = result['alt'][:200]
        news_article.save(update_fields=['featured_image_url', 'featured_image_alt'])
        logger.info(f'Gorsel atandi: {news_article.slug}')
        return True

    return False
