# Skill: Erişilebilirlik (A11y) — Norosera

## Trigger
erişilebilirlik, accessibility, a11y, WCAG, screen reader, alt text, ARIA, kontrast, contrast, engelli, görme

## WCAG 2.1 AA Zorunlu Kontroller

### Otomatik tarama
```bash
# Frontend a11y taraması
cd frontend
npx pa11y-ci --sitemap http://localhost:3000/sitemap.xml --standard WCAG2AA

# Veya tek sayfa
npx pa11y http://localhost:3000/hizmetler --standard WCAG2AA --reporter cli
```

### Kontrol listesi — her component için

#### Görsel
- [ ] Tüm `<img>` ve `<Image>` elementlerinde anlamlı `alt` text var
- [ ] Dekoratif görsellerde `alt=""` (boş) ve `aria-hidden="true"`
- [ ] Renk kontrastı: normal text min 4.5:1, büyük text min 3:1
- [ ] Bilgi sadece renkle değil, şekil/text ile de iletiliyor

#### Form
- [ ] Her input'un `<label>` eşleştirmesi var (`htmlFor` + `id`)
- [ ] Hata mesajları `aria-describedby` ile bağlı
- [ ] Required alanlar `aria-required="true"` ve görsel işaret
- [ ] Focus sırası mantıklı (`tabIndex` doğru)

#### Navigasyon
- [ ] `<nav>` elementleri `aria-label` ile etiketli
- [ ] Skip-to-content linki var
- [ ] Keyboard ile tüm işlemler yapılabiliyor
- [ ] Focus visible (outline kaldırılmamış)

#### Dinamik içerik
- [ ] Modal/dialog'lar `role="dialog"` ve `aria-modal="true"`
- [ ] Live region'lar `aria-live="polite"` kullanıyor
- [ ] Loading state'leri `aria-busy="true"` ile işaretli

### Next.js Component Patterns
```typescript
// Erişilebilir button
<button
  onClick={handleClick}
  aria-label="Randevu al"
  className="focus:outline-2 focus:outline-blue-600 focus:outline-offset-2"
>
  Randevu Al
</button>

// Skip-to-content (layout.tsx'e ekle)
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 
             focus:z-50 focus:bg-white focus:px-4 focus:py-2 focus:rounded"
>
  İçeriğe geç
</a>
<main id="main-content">...</main>

// Erişilebilir form field
<div>
  <label htmlFor="patient-name" className="block text-sm font-medium">
    Ad Soyad <span aria-hidden="true" className="text-red-500">*</span>
  </label>
  <input
    id="patient-name"
    type="text"
    aria-required="true"
    aria-describedby={error ? "name-error" : undefined}
    aria-invalid={!!error}
  />
  {error && (
    <p id="name-error" role="alert" className="text-red-600 text-sm mt-1">
      {error}
    </p>
  )}
</div>
```

### AI Alt Text Üretimi
Blog/hizmet sayfalarındaki görseller için otomatik alt text:
```python
# apps/media_manager/services.py
def generate_alt_text(image_path: str) -> str:
    """AI ile görsel için Türkçe alt text üret"""
    # Claude API veya vision model ile
    # Format: "[Ne gösterildiği], [bağlam]"
    # Örnek: "EEG cihazı ile beyin dalgası kaydı yapılan hasta"
    pass
```

### Medikal erişilebilirlik özel kuralları
- Tıbbi terimler `<abbr title="açıklama">` ile açıklanmalı
- PDF formları erişilebilir olmalı (tagged PDF)
- Randevu formunda sesli yönlendirme desteği
- Telefon numarası `tel:` linki ile tıklanabilir olmalı
