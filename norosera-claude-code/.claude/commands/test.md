# /test — Tüm Testleri Çalıştır

Norosera projesinin backend ve frontend testlerini paralel olarak çalıştır.

## Adımlar:

1. Backend testlerini çalıştır:
```bash
cd backend && python manage.py test --parallel --verbosity=2
```

2. Frontend type check:
```bash
cd frontend && npx tsc --noEmit
```

3. Frontend lint:
```bash
cd frontend && npm run lint
```

4. Sonuçları özetle: kaç test geçti, kaç başarısız, varsa hataları listele.

5. Eğer tüm testler geçtiyse: "✅ Tüm testler başarılı — commit'e hazır"
   Eğer hata varsa: hataları listele ve düzeltme öner.
