# /commit — Akıllı Git Commit

Değişiklikleri analiz et, conventional commit mesajı oluştur ve commit'le.

## Adımlar:

1. Değişiklikleri analiz et:
```bash
git diff --stat
git diff --cached --stat
```

2. Eğer staged dosya yoksa, tüm değişiklikleri stage'le:
```bash
git add -A
```

3. Değişikliklerin içeriğini oku ve conventional commit formatında mesaj oluştur:
   - `feat:` — Yeni özellik
   - `fix:` — Bug düzeltme
   - `refactor:` — Refactoring
   - `docs:` — Dokümantasyon
   - `test:` — Test ekleme/güncelleme
   - `chore:` — Bakım işleri
   - `style:` — Stil/format değişikliği
   - `perf:` — Performans iyileştirmesi
   - `security:` — Güvenlik düzeltmesi

4. Format:
```
<type>(<scope>): <kısa açıklama>

<detaylı açıklama - Türkçe>

Değişen dosyalar:
- dosya1.py
- dosya2.tsx
```

5. Commit mesajını göster ve onay iste. Onaylanınca:
```bash
git commit -m "<mesaj>"
```
