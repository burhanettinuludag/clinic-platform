"""
Noroloji odaklı görsel kaynakları:

1) Servier Medical Art (SMART) - Tıbbi illüstrasyonlar
   Lisans: CC BY 4.0 | https://smart.servier.com/
   Atıf: "Servier Medical Art by Servier, licensed under CC BY 4.0"

2) Unsplash - Fotoğraflar
   Lisans: Unsplash License (ücretsiz ticari kullanım)
   https://unsplash.com/license

Her kategoride SMART illüstrasyonları + Unsplash fotoğrafları karışık
olarak sunulur. Deterministic seçim (seed) ile aynı haber her zaman
aynı görseli alır.

Kullanım:
    from services.stock_images import get_medical_image
    result = get_medical_image(category='fda_approval', diseases=['migraine'])
    # result = {'url': '...', 'alt': '...', 'credit': '...'}
"""

import random
import hashlib
import logging

logger = logging.getLogger(__name__)

SMART_CREDIT = 'Servier Medical Art (CC BY 4.0)'
UNSPLASH_CREDIT = 'Unsplash'

# ============================================================
# SMART - Tıbbi İllüstrasyonlar (PNG)
# ============================================================
_S = 'https://smart.servier.com/wp-content/uploads'

# ============================================================
# Unsplash - Fotoğraflar (CDN, API key gerektirmez)
# ============================================================
def _u(photo_id: str, w: int = 800, h: int = 450) -> str:
    return f'https://images.unsplash.com/{photo_id}?w={w}&h={h}&fit=crop&q=80&auto=format'


# ---------- MİGREN ----------
MIGRAINE_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2024/01/Pain-and-migraines.png',
        'alt': 'Ağrı ve migren illüstrasyonu',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Cerveau_beau.png',
        'alt': 'Beyin anatomisi - nörolojik değerlendirme',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Cerveau_01.png',
        'alt': 'Beyin illüstrasyonu - migren araştırması',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/cerveau_zones.png',
        'alt': 'Beyin bölgeleri - ağrı lokalizasyonu',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Arteres_cerveau.png',
        'alt': 'Beyin arterleri - vasküler migren',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Neurone012.png',
        'alt': 'Nöron hücresi - sinirsel iletim',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Renkli beyin MRI görüntülemesi',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1617791160505-6f00504e3519'),
        'alt': 'Nöron ağları ve sinirsel bağlantılar',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1614935151651-0bea6508db6b'),
        'alt': 'Dijital beyin illüstrasyonu - nöroloji',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1576091160550-2173dba999ef'),
        'alt': 'Nörolojik ilaç tedavisi',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- EPİLEPSİ ----------
EPILEPSY_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/EEG_face.png',
        'alt': 'EEG elektroensefalografi - epilepsi tanısı',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/EEG_profil.png',
        'alt': 'EEG elektrot yerleşimi - nöbet izleme',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/EEG_bonhomme.png',
        'alt': 'EEG beyin dalgası ölçümü',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/synapse_06.png',
        'alt': 'Sinaps - nöral iletim mekanizması',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/neuromed_01.png',
        'alt': 'Nöromediatör salınımı - sinaptik iletim',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/synapse_bombee_1.png',
        'alt': 'Sinaptik bağlantı - nöral aktivite',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1559757148-5c350d0d3c56'),
        'alt': 'EEG beyin dalgaları ölçümü',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1516549655169-df83a0774514'),
        'alt': 'Nöron hücresi - mikroskop görüntüsü',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1581093806997-124204d9fa9d'),
        'alt': 'Sinir hücreleri ve nöron ağları',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1620641788421-7a1c342ea42e'),
        'alt': 'Beyin aktivitesi ve nöroloji',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- DEMANS / ALZHEİMER ----------
DEMENTIA_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/Alzheimer1.png',
        'alt': 'Alzheimer hastalığı - beyin değişiklikleri',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Alzheimer2.png',
        'alt': 'Alzheimer hastalığı - koronal kesit',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/hypocampe.png',
        'alt': 'Hipokampüs - bellek ve öğrenme merkezi',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Astrocyte01.png',
        'alt': 'Astrosit hücresi - nöroglial destek',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Astrocyte03.png',
        'alt': 'Astrosit - beyin koruyucu hücre',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Cerveau_02.png',
        'alt': 'Beyin anatomisi - kognitif sağlık',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1530497610245-94d3c16cda28'),
        'alt': 'Anatomik beyin modeli - demans araştırması',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1566438480900-0609be27a4be'),
        'alt': 'Beyin modeli - kognitif sağlık',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1611532736597-de2d4265fba3'),
        'alt': 'Beyin aktivite haritalaması',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1573497620053-ea5300f94f21'),
        'alt': 'Kognitif sağlık ve destek hizmetleri',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- İLAÇ ONAYI / FDA ----------
FDA_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/gelule.png',
        'alt': 'İlaç kapsülü - farmakolojik tedavi',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/blister.png',
        'alt': 'İlaç blisteri - nörolojik ilaç onayı',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/boite.png',
        'alt': 'İlaç kutusu - tedavi protokolü',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/neuromed_02.png',
        'alt': 'Nöromediatör - ilaç hedef mekanizması',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1576091160550-2173dba999ef'),
        'alt': 'Nörolojik ilaç tedavisi ve onayı',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1471864190281-a93a3070b6de'),
        'alt': 'İlaç molekülleri ve nörolojik araştırma',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1606112219348-204d7d8b94ee'),
        'alt': 'Nörolojik ilaç geliştirme süreci',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- KLİNİK ARAŞTIRMA ----------
CLINICAL_TRIAL_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/Neuroblaste02.png',
        'alt': 'Nöroblast - nörolojik araştırma',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Neurone012.png',
        'alt': 'Nöron yapısı - klinik çalışma',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/synapse_06.png',
        'alt': 'Sinaps detayı - nörolojik araştırma',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Astrocyte01.png',
        'alt': 'Astrosit araştırması - sinir bilimi',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1581595220892-b0739db3ba8c'),
        'alt': 'Beyin araştırması - klinik çalışma',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1579684385127-1ef15d508118'),
        'alt': 'Nöroloji laboratuvar çalışması',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1530026405186-ed1f139313f8'),
        'alt': 'Beyin bilimi laboratuvarı',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- TIBBİ CİHAZ ----------
DEVICE_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/EEG_face.png',
        'alt': 'EEG cihazı - beyin dalgası ölçümü',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/EEG_profil.png',
        'alt': 'EEG elektrotları - nörolojik tanı',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/EEG_dessus.png',
        'alt': 'EEG elektrot yerleşimi - üstten görünüm',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Circu_cerebrale1.png',
        'alt': 'Serebral dolaşım - tanı görüntüleme',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1576091160399-112ba8d25d1d'),
        'alt': 'Nörolojik tanı teknolojisi',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1589279003513-467d320f47eb'),
        'alt': 'Yapay zeka ve beyin teknolojisi',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1628595351029-c2bf17511435'),
        'alt': 'Nörolojik görüntüleme teknolojisi',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- KONGRE ----------
CONGRESS_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/cerveau_zones2.png',
        'alt': 'Beyin fonksiyonel bölgeleri - bilimsel sunum',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/cerveau_zones.png',
        'alt': 'Beyin haritalama - nöroloji kongresi',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1475721027785-f74eccf877e2'),
        'alt': 'Nöroloji kongresi ve bilimsel sunum',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1505373877841-8d25f7d46678'),
        'alt': 'Nöroloji akademik konferansı',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- POPÜLER BİLİM ----------
POPULAR_SCIENCE_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/Neurone012.png',
        'alt': 'Nöron hücresi - sinir bilimi',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/synapse_bombee_1.png',
        'alt': 'Sinaptik bağlantı - beyin iletişimi',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/neuromed_01.png',
        'alt': 'Nöromediatör - beyin kimyası',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/cerveau_06.png',
        'alt': 'Beyin sagital kesit - nöroanatomi',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1559757175-5700dde675bc'),
        'alt': 'Beyin bilimi ve nöroloji',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1516549655169-df83a0774514'),
        'alt': 'Nöron hücresi ve sinir bilimi',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1590859808308-3d2d9c515b1a'),
        'alt': 'Beyin ve sinir sistemi kesitleri',
        'credit': UNSPLASH_CREDIT,
    },
]

# ---------- GENEL NÖROLOJİ ----------
GENERAL_IMAGES = [
    # SMART
    {
        'url': f'{_S}/2016/10/Cerveau_01.png',
        'alt': 'Beyin illüstrasyonu - nöroloji',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Cerveau_02.png',
        'alt': 'Beyin anatomisi - genel nöroloji',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/Cerveau_beau.png',
        'alt': 'Beyin yapısı - tıbbi illüstrasyon',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/cerveau_tronc.png',
        'alt': 'Beyin sapı - nöroanatomi',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/hypocampe.png',
        'alt': 'Hipokampüs - bellek yapısı',
        'credit': SMART_CREDIT,
    },
    {
        'url': f'{_S}/2016/10/cerveau_willis.png',
        'alt': 'Willis poligonu - serebral dolaşım',
        'credit': SMART_CREDIT,
    },
    # Unsplash
    {
        'url': _u('photo-1617791160505-6f00504e3519'),
        'alt': 'Nöron ağları ve sinirsel bağlantı',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1614935151651-0bea6508db6b'),
        'alt': 'Dijital beyin - nöroloji',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1551076805-e1869033e561'),
        'alt': 'Beyin bilimi ve nöroloji araştırması',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1581093806997-124204d9fa9d'),
        'alt': 'Sinir hücreleri - nöroloji',
        'credit': UNSPLASH_CREDIT,
    },
    {
        'url': _u('photo-1589279003513-467d320f47eb'),
        'alt': 'Beyin ve yapay zeka teknolojisi',
        'credit': UNSPLASH_CREDIT,
    },
]


# Kategori -> görsel listesi eşlemesi
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

# Hastalık -> görsel listesi eşlemesi
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
    Kategori ve hastalığa uygun görsel seç.

    SMART tıbbi illüstrasyonları + Unsplash fotoğrafları karma havuzundan seçer.
    Deterministic seçim (seed) ile aynı haber her zaman aynı görseli alır.

    Args:
        category: Haber kategorisi (fda_approval, clinical_trial, vb.)
        diseases: İlişkili hastalık slug listesi (['migraine', 'epilepsy'])
        seed: Deterministic seçim için seed (örneğin slug).

    Returns:
        dict: {'url': str, 'alt': str, 'credit': str}
    """
    # Hastalık bazlı görsel havuzu (öncelikli)
    pool = []
    if diseases:
        for disease in diseases:
            pool.extend(DISEASE_IMAGES.get(disease, []))

    # Kategori bazlı görsel havuzu
    pool.extend(CATEGORY_IMAGES.get(category, []))

    # Fallback: genel nöroloji havuzu
    if not pool:
        pool = GENERAL_IMAGES

    # Tekrarları kaldır (url bazında)
    seen_urls = set()
    unique_pool = []
    for img in pool:
        if img['url'] not in seen_urls:
            seen_urls.add(img['url'])
            unique_pool.append(img)

    # Deterministic seçim (aynı haber her zaman aynı görseli alsın)
    if seed:
        idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(unique_pool)
        return unique_pool[idx]

    # Random seçim
    return random.choice(unique_pool)


def assign_image_to_news(news_article, force: bool = False) -> bool:
    """
    Bir NewsArticle'a otomatik görsel ata (SMART + Unsplash karma).

    Args:
        news_article: NewsArticle model instance
        force: True ise mevcut görsel olsa bile değiştir

    Returns:
        bool: Görsel atandıysa True
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
        logger.info(f'Görsel atandı ({result["credit"]}): {news_article.slug}')
        return True

    return False
