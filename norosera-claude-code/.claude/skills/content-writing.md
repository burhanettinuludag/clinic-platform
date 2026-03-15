# Skill: İçerik Yazımı — Norosera

## Trigger
makale, article, blog, yazı, içerik yaz, post yaz, medikal içerik, sağlık yazısı, hakkında yaz

## Minimum Uzunluk Kuralları (ZORUNLU)

| İçerik Türü | Minimum Karakter | Yaklaşık Kelime |
|-------------|-----------------|-----------------|
| Blog yazısı | 3000 | ~450 kelime |
| Medikal makale | 5000 | ~750 kelime |
| Kapsamlı rehber | 8000 | ~1200 kelime |
| Sosyal medya caption | 500 | ~75 kelime |
| Kısa bilgi notu | 1500 | ~225 kelime |

## ÖNEMLİ: Uzunluk doğrulama prosedürü

İçerik üretildikten sonra MUTLAKA şu kontrolü yap:

```python
content = "..." # üretilen içerik
char_count = len(content)
word_count = len(content.split())

if char_count < MINIMUM_FOR_TYPE:
    # İçeriği genişlet:
    # 1. Alt başlıklar ekle
    # 2. Klinik örnekler ekle
    # 3. "Ne zaman doktora başvurmalı?" bölümü ekle
    # 4. Sık Sorulan Sorular (SSS) bölümü ekle
    # 5. Kaynak/referans bölümü ekle
```

## Kısa kalırsa genişletme stratejisi

Aşağıdaki bölümlerden eksik olanları ekleyerek minimum uzunluğa ulaş:

1. **Giriş paragrafı** — Konunun önemi, kimleri ilgilendirdiği (min 200 karakter)
2. **Tanım/Açıklama** — Nedir, nasıl oluşur (min 400 karakter)
3. **Belirtiler/Bulgular** — Klinik tablo (min 400 karakter)
4. **Tanı yöntemleri** — EMG, EEG, MR vb. (min 300 karakter)
5. **Tedavi seçenekleri** — İlaç, fizik tedavi, cerrahi (min 400 karakter)
6. **Günlük yaşamda dikkat edilecekler** — Pratik tavsiyeler (min 300 karakter)
7. **Ne zaman doktora başvurmalı?** — Acil durumlar (min 200 karakter)
8. **Sık Sorulan Sorular (SSS)** — 3-5 soru-cevap (min 500 karakter)
9. **Sonuç** — Özet ve çağrı (min 200 karakter)

## Yazım Kuralları

- Dil: Türkçe, hasta/halk için anlaşılır ama bilimsel doğru
- Ton: Profesyonel, güven veren, paternalist olmayan
- Medikal terimler kullanılınca parantez içinde Türkçe açıklama ver
- Her makale sonunda:
  ```
  ---
  Prof. Dr. Burhanettin Uludağ
  Nöroloji ve Klinik Nörofizyoloji Uzmanı
  Norosera Nöroloji Kliniği, İzmir
  ```
- UYDURMA BİLGİ YASAK — emin olmadığın medikal bilgiyi yazma
- Kaynak belirt (mümkünse DOI veya guideline adı)

## SEO Entegrasyonu

Her makale için otomatik üret:
- `meta_title`: max 60 karakter, anahtar kelime içermeli
- `meta_description`: 150-160 karakter
- `slug`: Türkçe karaktersiz, kebab-case
- `keywords`: 5-8 anahtar kelime listesi
- İçerikte H2/H3 başlıklar kullan (SEO Agent ile koordineli)
