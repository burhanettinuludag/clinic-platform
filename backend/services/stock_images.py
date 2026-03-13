"""
Ucretsiz tibbi stok gorseller - API key gerektirmez.

Unsplash CDN URL'leri herkese acik ve ucretsizdir.
Unsplash License: https://unsplash.com/license
- Ucretsiz ticari kullanim
- Atifta bulunmak zorunlu degil ama tavsiye edilir

Her kategori ve hastalik icin onceden secilmis, yuksek kaliteli
tibbi gorsellerin URL'lerini icerir. Haber/makale olusturulurken
ilgili kategori ve hastaliga gore random bir gorsel atanir.

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
# Unsplash CDN'den secilmis tibbi gorseller
# Tumunu dogrudan kullanabiliriz, API key gerekmez
# URL format: https://images.unsplash.com/photo-{id}?w=800&h=450&fit=crop&q=80
# ============================================================

def _u(photo_id: str, w: int = 800, h: int = 450) -> str:
    """Unsplash CDN URL olustur. API key gerektirmez."""
    return f'https://images.unsplash.com/{photo_id}?w={w}&h={h}&fit=crop&q=80&auto=format'


# ---------- MIGREN ----------
MIGRAINE_IMAGES = [
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin goruntulemesi - norolojik arastirma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1530026405186-ed1f139313f8'),
        'alt': 'Tibbi arastirma - laboratuvar ortami',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1576091160550-2173dba999ef'),
        'alt': 'Ilac ve tedavi arastirmasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1579684385127-1ef15d508118'),
        'alt': 'Tibbi laboratuvar arastirmasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1551076805-e1869033e561'),
        'alt': 'Noroloji ve beyin bilimi',
        'credit': 'Unsplash',
    },
]

# ---------- EPILEPSI ----------
EPILEPSY_IMAGES = [
    {
        'url': _u('photo-1559757148-5c350d0d3c56'),
        'alt': 'EEG ve beyin dalgalari olcumu',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1532187863486-abf9dbad1b69'),
        'alt': 'Tibbi muayene ve tani',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1631549916768-4f9f5e5b4578'),
        'alt': 'Norolojik tani ve tedavi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1581595220892-b0739db3ba8c'),
        'alt': 'Beyin arastirmasi ve noroloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1516549655169-df83a0774514'),
        'alt': 'Sinir bilimi ve noron arastirmasi',
        'credit': 'Unsplash',
    },
]

# ---------- DEMANS ----------
DEMENTIA_IMAGES = [
    {
        'url': _u('photo-1576765608535-5f04d1e3f289'),
        'alt': 'Kognitif saglik ve hafiza',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1573497620053-ea5300f94f21'),
        'alt': 'Yasli bakim ve saglik hizmetleri',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin goruntulemesi - demans arastirmasi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1587854692152-cbe660dbde88'),
        'alt': 'Saglik bakimi ve destek',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1544991875-5dc1b05f607d'),
        'alt': 'Hafiza ve bilissel egzersizler',
        'credit': 'Unsplash',
    },
]

# ---------- FDA / ILAC ONAYI ----------
FDA_IMAGES = [
    {
        'url': _u('photo-1585435557343-3f684f1d2e2f'),
        'alt': 'Farmasotik ilac gelistirme',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1471864190281-a93a3070b6de'),
        'alt': 'Ilac molekulleri ve arastirma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1576091160550-2173dba999ef'),
        'alt': 'Ilac tedavisi ve onay sureci',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1587854692152-cbe660dbde88'),
        'alt': 'Klinik ilac calismasi',
        'credit': 'Unsplash',
    },
]

# ---------- KLINIK ARASTIRMA ----------
CLINICAL_TRIAL_IMAGES = [
    {
        'url': _u('photo-1532187863486-abf9dbad1b69'),
        'alt': 'Klinik arastirma ve calisma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1579684385127-1ef15d508118'),
        'alt': 'Tibbi arastirma laboratuvari',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1581595220892-b0739db3ba8c'),
        'alt': 'Bilimsel arastirma ve deney',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1530026405186-ed1f139313f8'),
        'alt': 'Laboratuvar ortaminda calisma',
        'credit': 'Unsplash',
    },
]

# ---------- TIBBI CIHAZ ----------
DEVICE_IMAGES = [
    {
        'url': _u('photo-1576091160399-112ba8d25d1d'),
        'alt': 'Tibbi teknoloji ve cihazlar',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1551076805-e1869033e561'),
        'alt': 'Medikal teknoloji inovasyonu',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1530026405186-ed1f139313f8'),
        'alt': 'Saglik teknolojisi arastirmasi',
        'credit': 'Unsplash',
    },
]

# ---------- KONGRE ----------
CONGRESS_IMAGES = [
    {
        'url': _u('photo-1540575467063-178a50e2fd60'),
        'alt': 'Tibbi kongre ve konferans',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1475721027785-f74eccf877e2'),
        'alt': 'Bilimsel sunum ve kongre',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1505373877841-8d25f7d46678'),
        'alt': 'Akademik konferans ve toplanti',
        'credit': 'Unsplash',
    },
]

# ---------- POPULER BILIM ----------
POPULAR_SCIENCE_IMAGES = [
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin bilimi ve noroloji',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1507413245164-6160d8298b31'),
        'alt': 'Bilimsel kesif ve arastirma',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1516549655169-df83a0774514'),
        'alt': 'Noron ve sinir bilimi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1551076805-e1869033e561'),
        'alt': 'Beyin arastirmasi ve kesfler',
        'credit': 'Unsplash',
    },
]

# ---------- GENEL SAGLIK ----------
GENERAL_IMAGES = [
    {
        'url': _u('photo-1576091160550-2173dba999ef'),
        'alt': 'Saglik ve tip bilimi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1579684385127-1ef15d508118'),
        'alt': 'Tibbi arastirma ve saglik',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1532187863486-abf9dbad1b69'),
        'alt': 'Doktor muayenesi ve tani',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Noroloji ve beyin sagligi',
        'credit': 'Unsplash',
    },
    {
        'url': _u('photo-1551076805-e1869033e561'),
        'alt': 'Tibbi bilim ve saglik hizmetleri',
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
    Kategori ve hastaliga uygun tibbi gorsel sec.

    API key gerektirmez - onceden secilmis Unsplash CDN URL'lerini kullanir.

    Args:
        category: Haber kategorisi (fda_approval, clinical_trial, vb.)
        diseases: Iliskili hastalik slug listesi (['migraine', 'epilepsy'])
        seed: Deterministic secim icin seed (ornegin slug).
              Ayni seed her zaman ayni gorseli dondurur.

    Returns:
        dict: {'url': str, 'alt': str, 'credit': str}
    """
    # Hastalik bazli gorsel havuzu
    pool = []
    if diseases:
        for disease in diseases:
            pool.extend(DISEASE_IMAGES.get(disease, []))

    # Kategori bazli gorsel havuzu
    pool.extend(CATEGORY_IMAGES.get(category, []))

    # Fallback: genel havuz
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


def assign_image_to_news(news_article) -> bool:
    """
    Bir NewsArticle'a otomatik gorsel ata.
    Zaten gorseli varsa atlamaz.
    API key gerektirmez.
    """
    if news_article.featured_image_url or news_article.featured_image:
        return False

    diseases = list(news_article.related_diseases.values_list('slug', flat=True))

    result = get_medical_image(
        category=news_article.category,
        diseases=diseases,
        seed=news_article.slug,  # Ayni slug = ayni gorsel
    )

    if result:
        news_article.featured_image_url = result['url']
        if not news_article.featured_image_alt:
            news_article.featured_image_alt = result['alt'][:200]
        news_article.save(update_fields=['featured_image_url', 'featured_image_alt'])
        logger.info(f'Gorsel atandi: {news_article.slug}')
        return True

    return False
