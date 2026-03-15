# Skill: SEO Audit & Onarım — Norosera

## Trigger
SEO, kırık link, broken link, 404, meta tag, sitemap, schema, arama motoru, Google, indexleme, canonical, robots

## Kırık Link Tarama

### Otomatik tarama komutu
```bash
# Tüm internal linkleri tara
cd backend
python manage.py shell -c "
from apps.blog.models import BlogPost
from apps.services.models import Service
from django.test import Client
import re

client = Client()
broken = []

# Blog postlarındaki linkleri tara
for post in BlogPost.objects.filter(status='published'):
    urls = re.findall(r'href=[\"\\']([^\"\\'>]+)', post.content)
    for url in urls:
        if url.startswith('/') or url.startswith('http'):
            try:
                if url.startswith('/'):
                    resp = client.get(url)
                    if resp.status_code >= 400:
                        broken.append({'post': post.title, 'url': url, 'status': resp.status_code})
            except Exception as e:
                broken.append({'post': post.title, 'url': url, 'error': str(e)})

for b in broken:
    print(f'❌ {b}')
print(f'\\nToplam kırık link: {len(broken)}')
"
```

### Kırık link düzeltme stratejisi
1. 404 internal link → Doğru URL'yi bul ve güncelle
2. 404 external link → Web Archive'dan kontrol et, alternatif kaynak bul
3. 301/302 redirect → Direkt son URL'ye güncelle (redirect zinciri kır)
4. Timeout → URL'yi kontrol et, gerekirse kaldır

### Django management command oluştur
```python
# apps/seo/management/commands/check_links.py
from django.core.management.base import BaseCommand
import requests
from apps.blog.models import BlogPost

class Command(BaseCommand):
    help = "Tüm yayınlanmış içeriklerdeki linkleri kontrol eder"

    def handle(self, *args, **options):
        broken_count = 0
        for post in BlogPost.objects.filter(status="published"):
            # link extraction and checking logic
            pass
        self.stdout.write(f"Tarama tamamlandı. Kırık link: {broken_count}")
```

## Meta Tag Audit

### Her sayfa için kontrol listesi
```python
# Otomatik meta tag doğrulama
REQUIRED_META = {
    "title": {"min": 30, "max": 60, "required": True},
    "description": {"min": 120, "max": 160, "required": True},
    "og:title": {"required": True},
    "og:description": {"required": True},
    "og:image": {"required": True},
    "og:locale": {"value": "tr_TR", "required": True},
    "canonical": {"required": True},
    "robots": {"required": False},
}
```

### Next.js metadata kontrolü
Her `page.tsx` dosyasında şunları doğrula:
- `export const metadata: Metadata` var mı?
- `title` 30-60 karakter arasında mı?
- `description` 120-160 karakter arasında mı?
- `openGraph` objesi tanımlı mı?
- `alternates.canonical` tanımlı mı?

## Schema.org Yapılandırılmış Veri

### Medikal pratik için zorunlu schema'lar
```typescript
// lib/schema.ts

// Ana sayfa: MedicalBusiness
export function clinicSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "MedicalBusiness",
    "name": "Norosera Nöroloji Kliniği",
    "description": "Prof. Dr. Burhanettin Uludağ - Nöroloji ve Klinik Nörofizyoloji",
    "url": "https://norosera.com",
    "telephone": "+905323829031",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Ankara Caddesi No 243/2",
      "addressLocality": "Bornova",
      "addressRegion": "İzmir",
      "addressCountry": "TR"
    },
    "medicalSpecialty": "Neurology",
    "availableService": [
      {"@type": "MedicalProcedure", "name": "EEG"},
      {"@type": "MedicalProcedure", "name": "EMG"},
      {"@type": "MedicalProcedure", "name": "Nörolojik Muayene"}
    ],
    "physician": {
      "@type": "Physician",
      "name": "Prof. Dr. Burhanettin Uludağ",
      "medicalSpecialty": ["Neurology", "Clinical Neurophysiology"]
    }
  };
}

// Blog yazıları: MedicalWebPage
export function articleSchema(post: BlogPost) {
  return {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    "headline": post.title,
    "author": {
      "@type": "Physician",
      "name": "Prof. Dr. Burhanettin Uludağ"
    },
    "datePublished": post.published_at,
    "dateModified": post.updated_at,
    "medicalAudience": {
      "@type": "PatientAudience"
    }
  };
}

// Hizmet sayfaları: MedicalProcedure
export function serviceSchema(service: Service) {
  return {
    "@context": "https://schema.org",
    "@type": "MedicalProcedure",
    "name": service.title,
    "description": service.description,
    "howPerformed": service.details,
    "bodyLocation": service.body_area,
    "procedureType": "http://schema.org/DiagnosticProcedure"
  };
}

// SSS: FAQPage
export function faqSchema(faqs: FAQ[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };
}
```

## Sitemap Yönetimi

### Otomatik sitemap kontrolü
- `sitemap.xml` her deploy'da yeniden üretilmeli
- Tüm published blog postları dahil
- Tüm hizmet sayfaları dahil
- `lastmod` tarihleri doğru olmalı
- `priority`: ana sayfa 1.0, hizmetler 0.8, blog 0.6
- Google Search Console'a ping at: `https://www.google.com/ping?sitemap=URL`

### robots.txt kontrolü
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /dashboard/
Sitemap: https://norosera.com/sitemap.xml
```
