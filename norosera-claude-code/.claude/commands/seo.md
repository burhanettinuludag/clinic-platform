# /seo — Kapsamlı SEO Taraması

Norosera web sitesinin tam SEO denetimini yap.

## Adımlar:

### 1. Kırık Link Taraması
Tüm published blog postlarını ve hizmet sayfalarını tara:
- İçerikteki tüm `<a href>` linklerini çıkar
- Internal linkleri Django test client ile kontrol et
- External linkleri HTTP HEAD request ile kontrol et
- Sonuçları raporla: çalışan, 301 redirect, 404, timeout

### 2. Meta Tag Audit
Her public sayfa için kontrol et:
- `title` tag: 30-60 karakter, benzersiz, anahtar kelime içeriyor mu
- `meta description`: 120-160 karakter, benzersiz
- `og:title`, `og:description`, `og:image` mevcut mu
- `canonical` URL doğru mu
- `robots` meta tag uygun mu

Spawn sub-agent: Frontend dosyalarını tara
```bash
grep -rn "export const metadata" frontend/src/app/ --include="*.tsx"
```

### 3. Schema.org Kontrolü
Her sayfa tipi için doğru structured data var mı:
- Ana sayfa: `MedicalBusiness` schema
- Blog: `MedicalWebPage` + `Article` schema
- Hizmetler: `MedicalProcedure` schema
- SSS: `FAQPage` schema
- İletişim: `ContactPoint` schema

### 4. Sitemap Kontrolü
- `sitemap.xml` mevcut ve erişilebilir mi
- Tüm published sayfalar sitemap'te mi
- `lastmod` tarihleri güncel mi
- `robots.txt` sitemap'e referans veriyor mu

### 5. Performans SEO
- Core Web Vitals (LCP, CLS, INP) kontrol et
- Mobile-friendly test
- Görsel boyutları ve alt text'ler
- Sayfa yüklenme hızı

### 6. Sonuç Raporu
```
📊 NOROSERA SEO RAPORU
═══════════════════════════════

🔗 Kırık Linkler: X/Y link kırık
📝 Meta Tag: X/Y sayfa eksik
🏗️ Schema.org: X/Y sayfa eksik
🗺️ Sitemap: Durum
⚡ Performans: Skor

🔴 ACİL (hemen düzelt):
- ...

🟡 ÖNEMLİ (bu hafta):
- ...

🟢 İYİLEŞTİRME (backlog):
- ...
```
