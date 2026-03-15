# /deploy — Deploy Hazırlığı

Production deploy öncesi tüm kontrolleri çalıştır.

## Adımlar:

1. Git durumunu kontrol et:
```bash
git status
git log --oneline -5
```

2. Tüm testleri çalıştır:
```bash
cd backend && python manage.py test --parallel
cd frontend && npx tsc --noEmit && npm run build
```

3. Django deploy kontrolü:
```bash
cd backend && python manage.py check --deploy
```

4. Migration durumunu kontrol et:
```bash
cd backend && python manage.py showmigrations --plan | grep "\[ \]"
```

5. Docker build test:
```bash
docker-compose build --no-cache
```

6. Kontrol listesi çıktısı:
   - [ ] Testler geçti
   - [ ] Type check geçti
   - [ ] Build başarılı
   - [ ] Deploy check passed
   - [ ] No pending migrations
   - [ ] .env.production güncel
   - [ ] Database backup alındı

7. Eğer tümü geçtiyse: "✅ Deploy'a hazır — `git push origin main` ile tetiklenecek"
   Eğer sorun varsa: sorunları listele, deploy'u engelle.
