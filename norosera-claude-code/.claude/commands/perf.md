# /perf — Performans Denetimi

Norosera'nın frontend ve backend performansını kapsamlı denetle.

## Adımlar:

### 1. Frontend Performans
```bash
cd frontend
npm run build 2>&1 | tail -20  # Build çıktısı ve boyutlar
```

Spawn sub-agent: Bundle analizi yap
- Her route'un JS boyutunu kontrol et
- 50KB üstü chunk'ları raporla
- Tree-shaking yapılmamış import'ları bul
- Kullanılmayan dependency'leri tespit et

### 2. Görsel Audit
```bash
# Optimize edilmemiş görselleri bul
find frontend/public -type f \( -name "*.png" -o -name "*.jpg" \) -size +200k -exec ls -lh {} \;

# WebP olmayan görseller
find frontend/public -name "*.png" -o -name "*.jpg" | while read f; do
    test -f "${f%.*}.webp" || echo "❌ WebP yok: $f"
done

# next/image kullanmayan img tag'leri
grep -rn "<img " frontend/src/ --include="*.tsx" --include="*.jsx"
```

### 3. Backend Performans
Spawn sub-agent: Django query analizi
- `select_related` / `prefetch_related` eksik olan queryset'leri bul
- `len(queryset)` yerine `.count()` kullanılması gereken yerleri bul
- `queryset.all()` döngüleri içindeki N+1 pattern'leri tespit et
- Index eksik olabilecek sık sorgulanan alanları belirle

### 4. API Yanıt Süresi
```bash
# Kritik endpoint'leri test et
for url in "/api/v1/services/" "/api/v1/blog/" "/api/v1/appointments/"; do
    TIME=$(curl -o /dev/null -s -w '%{time_total}' "http://localhost:8000$url")
    echo "$url: ${TIME}s"
done
```

### 5. Sonuç Raporu
Hedef skorlarla karşılaştır ve aksiyon listesi oluştur.
