# /linkcheck — Kırık Link Taraması

Tüm published içeriklerdeki linkleri kontrol et ve kırık olanları düzelt.

## Adımlar:

### 1. Internal Link Taraması
```bash
# Blog postlarındaki linkleri çıkar
cd backend
python manage.py shell -c "
from apps.blog.models import BlogPost
import re
for post in BlogPost.objects.filter(status='published'):
    urls = re.findall(r'href=[\"\\']([^\"\\'>]+)', post.content)
    for url in urls:
        print(f'{post.slug}|{url}')
" > /tmp/norosera-links.txt
```

### 2. Her linki kontrol et
```bash
# HTTP status kontrol (internal)
while IFS='|' read -r slug url; do
    if [[ "$url" == /* ]]; then
        STATUS=$(curl -o /dev/null -s -w '%{http_code}' "http://localhost:8000$url")
        echo "$STATUS|$slug|$url"
    fi
done < /tmp/norosera-links.txt
```

### 3. External link kontrol
External linkleri HEAD request ile kontrol et.
Timeout: 10 saniye. Retry: 1 kez.

### 4. Sonuçları raporla
```
🔗 LİNK KONTROL RAPORU
══════════════════════

✅ Çalışan: X link
⚠️  Redirect (301/302): X link → son URL'ye güncelle
❌ Kırık (404): X link → düzelt veya kaldır
⏱️ Timeout: X link → tekrar kontrol et

Detaylı liste:
- [blog-slug] /eski-url → 404 — Öneri: /yeni-url
- [blog-slug] https://... → timeout
```

### 5. Otomatik düzeltme
Kullanıcıya sor: kırık linkleri otomatik düzelteyim mi?
- 301 redirect → son URL'ye güncelle
- 404 internal → doğru URL'yi bul, güncelle
- 404 external → kaldır veya alternatif kaynak bul
