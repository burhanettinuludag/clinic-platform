# Skill: Performans Optimizasyonu — Norosera

## Trigger
performans, hız, yavaş, Lighthouse, Core Web Vitals, LCP, CLS, FID, INP, N+1, query, bundle, görsel boyut, image optimize, WebP, lazy load, cache

## Lighthouse CI Otomasyonu

### GitHub Actions entegrasyonu
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on:
  pull_request:
    paths: ["frontend/**"]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: cd frontend && npm ci && npm run build
      - name: Lighthouse CI
        uses: treosh/lighthouse-ci-action@v11
        with:
          urls: |
            http://localhost:3000/
            http://localhost:3000/hizmetler
            http://localhost:3000/blog
          budgetPath: ./frontend/lighthouse-budget.json
          uploadArtifacts: true
```

### Minimum skorlar (ZORUNLU)
```json
// frontend/lighthouse-budget.json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:best-practices": ["error", {"minScore": 0.85}],
        "categories:seo": ["error", {"minScore": 0.95}]
      }
    }
  }
}
```

### Core Web Vitals hedefleri
| Metrik | İyi | Kötü | Norosera hedef |
|--------|-----|------|----------------|
| LCP | < 2.5s | > 4s | < 2.0s |
| FID/INP | < 100ms | > 300ms | < 80ms |
| CLS | < 0.1 | > 0.25 | < 0.05 |

## Görsel Optimizasyon

### Otomatik kontrol
```bash
# Optimize edilmemiş görselleri bul
find frontend/public -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) -size +200k | while read f; do
    echo "⚠️  Büyük görsel: $f ($(du -h "$f" | cut -f1))"
done

# WebP versiyonu olmayanları bul
find frontend/public -type f \( -name "*.png" -o -name "*.jpg" \) | while read f; do
    WEBP="${f%.*}.webp"
    if [ ! -f "$WEBP" ]; then
        echo "❌ WebP yok: $f"
    fi
done
```

### Next.js Image kuralları
```typescript
// DOĞRU — Next.js Image component ile
import Image from "next/image";
<Image src="/clinic.jpg" alt="Norosera Kliniği" width={800} height={600} />

// YANLIŞ — ham img tag
<img src="/clinic.jpg" />  // ❌ ASLA
```

### Görsel boyut standartları
| Kullanım | Max boyut | Format | Lazy load |
|----------|----------|--------|-----------|
| Hero/banner | 200KB | WebP | Hayır (priority) |
| Blog thumbnail | 80KB | WebP | Evet |
| Blog inline | 150KB | WebP | Evet |
| Logo/icon | 20KB | SVG/WebP | Hayır |
| OG image | 100KB | JPG | N/A |

## N+1 Query Tespiti

### Django QuerySet kontrol
```python
# Potansiyel N+1 pattern'leri ara
# KÖTÜ:
for post in BlogPost.objects.all():
    print(post.author.name)  # ❌ Her post için ayrı query

# İYİ:
for post in BlogPost.objects.select_related("author").all():
    print(post.author.name)  # ✅ Tek query

# KÖTÜ:
for post in BlogPost.objects.all():
    tags = post.tags.all()  # ❌ N+1

# İYİ:
for post in BlogPost.objects.prefetch_related("tags").all():
    tags = post.tags.all()  # ✅ 2 query toplam
```

### Otomatik N+1 tespit
```python
# settings/dev.py — Development ortamında otomatik tespit
INSTALLED_APPS += ["nplusone.ext.django"]
MIDDLEWARE += ["nplusone.ext.django.NPlusOneMiddleware"]
NPLUSONE_RAISE = True  # N+1 bulunca hata fırlat
```

## Bundle Size Analizi

### Frontend kontrol
```bash
cd frontend

# Bundle analyzer çalıştır
ANALYZE=true npm run build

# Büyük paketleri tespit et
npx @next/bundle-analyzer
```

### Hedef boyutlar
| Chunk | Max boyut |
|-------|----------|
| First Load JS | < 100KB |
| Shared chunk | < 80KB |
| Per-page JS | < 50KB |
| Total (gzipped) | < 300KB |

### Tree-shaking kontrol
```typescript
// KÖTÜ — tüm kütüphane import
import _ from "lodash";  // ❌ 72KB

// İYİ — sadece kullanılan fonksiyon
import debounce from "lodash/debounce";  // ✅ 1KB
```
