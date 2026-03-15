# /doc — Dokümantasyon Oluştur

Projenin mevcut durumuna göre otomatik dokümantasyon üret.

## Adımlar:

1. Backend API endpoint'lerini tara:
```bash
cd backend && python manage.py show_urls 2>/dev/null || grep -r "path(" config/urls.py apps/*/urls.py
```

2. Model yapısını çıkar:
```bash
cd backend && python manage.py inspectdb --include-views 2>/dev/null || grep -rn "class.*models.Model" apps/
```

3. Spawn sub-agents:
   - **API Doc Agent:** Her endpoint için method, permission, request/response format
   - **Model Doc Agent:** Her model için field açıklamaları, ilişkiler
   - **Setup Doc Agent:** Kurulum ve development ortamı talimatları

4. Çıktıları birleştir ve `docs/` klasörüne yaz:
   - `docs/API.md` — REST API referansı
   - `docs/MODELS.md` — Veritabanı modelleri
   - `docs/SETUP.md` — Geliştirici kurulum rehberi
   - `docs/ARCHITECTURE.md` — Sistem mimarisi

5. Değişen dosyaları raporla.
