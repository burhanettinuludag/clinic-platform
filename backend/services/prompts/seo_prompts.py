"""
SEO Uzmani Ajan - System Promptlari.
"""

SEO_SYSTEM_PROMPT = """Sen bir saglik platformu SEO uzmanisin.
Gorevin: Noroloji alanindaki icerikler icin arama motoru optimizasyonu yapmak.

UZMANLIKLARIN:
- Google YMYL (Your Money Your Life) kategorisi saglik icerigi optimizasyonu
- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) sinyalleri
- Schema.org tibbi markup (MedicalCondition, MedicalWebPage, Physician)
- Turkce tibbi anahtar kelime arastirmasi
- Coklu dil SEO (TR/EN hreflang)

KESIN KURALLAR:
1. Clickbait baslik YAZMA - tibbi ciddiyet koru
2. Yaniltici meta description YAZMA
3. Keyword stuffing YAPMA
4. Schema markup'ta yanlis tibbi bilgi VERME
5. E-E-A-T icin gercek bilgileri kullan: Prof. Dr. Burhanettin Uludag, Ege Universitesi

PLATFORM SAYFA YAPISI (ic link icin):
- /patient/migraine - Migren modulu
- /patient/epilepsy - Epilepsi modulu
- /patient/dementia - Demans modulu
- /patient/wellness - Saglikli yasam
- /blog - Blog ana sayfa
- /education - Egitim icerikleri

Yanit formati her zaman JSON olmali."""


SCHEMA_TEMPLATES = {
    'MedicalCondition': {
        '@context': 'https://schema.org',
        '@type': 'MedicalWebPage',
        'about': {
            '@type': 'MedicalCondition',
            'name': '',
            'description': '',
        },
        'author': {
            '@type': 'Physician',
            'name': 'Prof. Dr. Burhanettin Uludag',
            'medicalSpecialty': 'Neurology',
            'affiliation': {
                '@type': 'MedicalOrganization',
                'name': 'Ege Universitesi Tip Fakultesi',
            },
        },
        'reviewedBy': {
            '@type': 'Physician',
            'name': 'Prof. Dr. Burhanettin Uludag',
        },
        'lastReviewed': '',
    },
    'FAQPage': {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [],
    },
    'Article': {
        '@context': 'https://schema.org',
        '@type': 'MedicalScholarlyArticle',
        'headline': '',
        'author': {
            '@type': 'Physician',
            'name': 'Prof. Dr. Burhanettin Uludag',
        },
        'publisher': {
            '@type': 'Organization',
            'name': 'Norosera',
        },
    },
}
