# Security & KVKK Skill

## Triggers
guvenlik, security, KVKK, hasta verisi, patient data, encryption, audit, consent, privacy

## KVKK Ozel Nitelikli Veri

Asagidaki veriler KVKK kapsaminda ozel nitelikli kisisel veridir:
- Hasta adi, soyadi, TC kimlik numarasi
- Telefon numarasi, e-posta
- Saglik verileri (teshis, tedavi, ilac, semptom)
- Biyometrik veriler

## Koruma Kurallari

### Backend API
1. **Kimlik dogrulama:** Tum hasta endpoint'leri `IsAuthenticated` + rol bazli permission
2. **Rate limiting:** Anonymous 10/min, Authenticated 30/min, Auth endpoint 5/min, AI agent 10/hour
3. **URL'de PII yok:** Patient ID'ler UUID, URL'de TC/isim kullanma
4. **Pagination zorunlu:** Toplu veri dondurmede her zaman pagination kullan

### Audit Logging
`AuditLogMiddleware` (`apps/common/middleware.py`) su path'leri otomatik loglar:
- `/api/v1/tracking/`
- `/api/v1/migraine/`
- `/api/v1/epilepsy/`
- `/api/v1/dementia/`
- `/api/v1/doctor/`

Her log kaydinda: user, action, ip_address, path, method, response_status

### Consent (Riza)
`ConsentRecord` modeli ile kullanici rizalari takip edilir:
- consent_type, version, is_active
- given_at, withdrawn_at
- ip_address

### JWT Token Guvenligi
- Access token: 30 dakika
- Refresh token: 7 gun
- Rotate on refresh, blacklist after rotation
- Token'lar httpOnly cookie'lerde saklanir

### Loglama Kurallari
- ASLA hasta adi, TC, telefon loglama
- Sadece UUID (patient ID) kullan
- Error log'larinda stack trace'de PII olmamali

### Report Sharing
`ReportShareRecord` ile rapor paylasimlari audit edilir:
- IP adresi, consent bilgisi, paylasilan kullanici

### Data Retention
- Saglik verileri: aktif hasta icin surekli
- Silinen hesap: anonimize et
- Audit log'lar: 5 yil sakla

### Frontend Guvenligi
- Patient data'yi ASLA localStorage'da saklama
- Sadece httpOnly cookie kullan
- CSP header'lari zorunlu
- XSS korumasi: kullanici girdilerini sanitize et

### Django Security Checklist
```bash
DJANGO_SETTINGS_MODULE=config.settings.production python3 manage.py check --deploy
```
Bu komut HSTS, CSRF, secure cookies, SSL redirect vb. kontrol eder.
