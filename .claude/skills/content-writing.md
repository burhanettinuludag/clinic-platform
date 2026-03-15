# Content Writing Skill

## Triggers
article, blog, content, makale, icerik, yazilar, education, egitim, rehber, guide

## Minimum Content Length (ZORUNLU)

| Tip | Minimum Karakter | Yaklasik Kelime |
|-----|-----------------|-----------------|
| Blog yazisi | 3.000 | ~450 |
| Tibbi makale | 5.000 | ~750 |
| Kapsamli rehber | 8.000 | ~1.200 |
| Sosyal medya caption | 500 | ~75 |
| Kisa not/ozet | 1.500 | ~225 |

Bu sinirlar ZORUNLUDUR. Daha kisa icerik uretme.

## Icerik Kisa Kalirsa Genisletme Stratejisi

Asagidaki bolumleri ekleyerek icerigi genislet:
1. **Giris** — konunun onemi, kime hitap ettigi
2. **Tanim** — hastalik/konu nedir, epidemiyoloji
3. **Belirtiler** — detayli semptom listesi
4. **Tani yontemleri** — EEG, EMG, MR vb.
5. **Tedavi secenekleri** — ilac, cerrahi, yasam tarzi
6. **Gunluk yasam ipuclari** — pratik oneriler
7. **Ne zaman doktora basvurulmali** — acil durumlar
8. **Sikca Sorulan Sorular (SSS)** — 5-8 soru-cevap
9. **Sonuc** — ozet ve yonlendirme

## Yazim Kurallari

1. **Dil:** Kullaniciya yonelik icerik TURKCE, kod/yorum INGILIZCE
2. **Uslup:** Profesyonel ama hastaya snobca davranmayan ton
3. **Tibbi terimler:** Ilk kullanimda aciklama: "Elektroensefalografi (EEG, beyin dalgalarini olcen test)"
4. **Yazar imzasi:** Her makalenin sonunda:
   ```
   Prof. Dr. Burhanettin Uludag
   Noroloji Uzmani
   ```
5. **Kaynak:** Uydurma tibbi bilgi yazma. Bilmiyorsan belirt
6. **Yasal uyari:** Icerik bilgilendirme amaclidir, tibbi teshis/tedavi yerine gecmez

## SEO Entegrasyonu

Her icerik su alanlari icermeli:
- `seo_title_tr` — max 60 karakter
- `seo_description_tr` — 150-160 karakter
- `slug` — Turkce uyumlu URL slug
- `keywords` — 5-8 anahtar kelime
- Basliklar H2/H3 hiyerarsisinde

## Article Model Alanlari
```python
# backend/apps/content/models.py
title_tr, title_en          # Baslik
body_tr, body_en            # Govde (HTML/Markdown)
excerpt_tr, excerpt_en      # Ozet
seo_title_tr, seo_title_en  # SEO basligi
seo_description_tr/en       # Meta description
category                    # ContentCategory FK
module                      # DiseaseModule FK (migraine/epilepsy/dementia)
status                      # draft/published/archived
author                      # DoctorAuthor FK
```
