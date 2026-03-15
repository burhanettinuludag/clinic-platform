# /review — Kod İnceleme

Mevcut branch'teki değişiklikleri kapsamlı olarak incele.

## Adımlar:

1. Değişen dosyaları tespit et:
```bash
git diff --name-only HEAD~1
```

2. Her değişen dosya için kontrol et:
   - **Güvenlik:** Hardcoded secrets, SQL injection, XSS riski
   - **KVKK:** Hasta verisi açık mı, audit log var mı
   - **Type safety:** TypeScript `any` kullanımı var mı
   - **Permissions:** API view'larda permission_classes tanımlı mı
   - **Tests:** Yeni kod için test yazılmış mı
   - **i18n:** User-facing text Türkçe mi

3. Spawn sub-agents for parallel review:
   - Security review agent
   - Code quality agent
   - Test coverage agent

4. Sonuçları severity ile raporla:
   - 🔴 CRITICAL: Güvenlik açığı, KVKK ihlali
   - 🟡 WARNING: Test eksik, type safety sorunu
   - 🔵 INFO: Stil önerisi, refactoring fırsatı

5. Özet tablo oluştur ve commit mesajı öner.
