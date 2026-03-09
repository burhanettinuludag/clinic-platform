# Norosera - Production Teknik Dokumantasyonu

**Son Guncelleme:** 7 Mart 2026
**Durum:** ✅ Canli (Live)

---

## 1. Sunucu Bilgileri

| Bilgi | Deger |
|-------|-------|
| **Saglayici** | Hetzner Cloud |
| **Plan** | CX23 (2 vCPU, 4 GB RAM, 40 GB SSD) |
| **Lokasyon** | Nuremberg, Almanya |
| **IP Adresi** | 178.104.30.193 |
| **IPv6** | 2a01:4f8:1c19:c415::1 |
| **Isletim Sistemi** | Ubuntu 24.04.4 LTS |
| **Kernel** | 6.8.0-90-generic |
| **Docker** | 29.3.0 |
| **Docker Compose** | v5.1.0 |

### SSH Erisimi
```bash
ssh root@178.104.30.193
```

---

## 2. Domain & DNS

| Bilgi | Deger |
|-------|-------|
| **Domain** | norosera.com |
| **Kayitci** | Natro |
| **Nameserver** | ns1.natrohost.com, ns2.natrohost.com |
| **A Kaydi** | norosera.com → 178.104.30.193 |
| **CNAME** | www → norosera.com |
| **SSL** | Let's Encrypt (otomatik yenileme) |
| **SSL Bitis** | 4 Haziran 2026 |

---

## 3. URL'ler

| Sayfa | URL |
|-------|-----|
| **Ana Sayfa** | https://norosera.com |
| **Admin Panel** | https://norosera.com/yonetim-7x9k/ |
| **API Root** | https://norosera.com/api/v1/ |
| **Hasta Giris** | https://norosera.com/tr/auth/login |
| **Doktor Giris** | https://norosera.com/tr/auth/login |

---

## 4. Admin & Giris Bilgileri

### Django Admin (Superuser)
| Bilgi | Deger |
|-------|-------|
| **URL** | https://norosera.com/yonetim-7x9k/ |
| **Email** | admin@norosera.com |
| **Sifre** | Norosera2026! |

### PostgreSQL Veritabani
| Bilgi | Deger |
|-------|-------|
| **Host** | db (Docker internal) |
| **Port** | 5432 |
| **Veritabani** | norosera_prod |
| **Kullanici** | norosera |
| **Sifre** | DX0s6DqRprjDc9oVePALs3RZGrhnBaLG |

### Redis
| Bilgi | Deger |
|-------|-------|
| **Host** | redis (Docker internal) |
| **Port** | 6379 |
| **Max Memory** | 256mb |

### Django Secret Key
```
(env dosyasindan alinir - .env.production)
```

### API Anahtarlari
| Servis | Anahtar |
|--------|---------|
| **GROQ API** | (env dosyasindan alinir - .env.production) |

---

## 5. Teknik Mimari

### Servisler (Docker Compose)

```
                    ┌─────────────┐
                    │   Internet   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Nginx    │  :80 (HTTP→HTTPS)
                    │  1.27-alpine│  :443 (HTTPS/HTTP2)
                    └──┬──────┬───┘
                       │      │
              ┌────────▼──┐ ┌─▼────────┐
              │  Backend  │ │ Frontend │
              │  Django   │ │ Next.js  │
              │  Gunicorn │ │ Standalone│
              │  :8000    │ │  :3000   │
              └──┬──┬─────┘ └──────────┘
                 │  │
         ┌───────▼┐ ┌▼────────┐
         │PostgreSQL│ │  Redis  │
         │16-alpine │ │ 7-alpine│
         │  :5432   │ │  :6379  │
         └─────────┘ └─┬──┬───┘
                        │  │
              ┌─────────▼┐ ┌▼──────────┐
              │  Celery   │ │Celery Beat│
              │  Worker   │ │ Scheduler │
              └───────────┘ └───────────┘
```

### Teknoloji Yigini

| Katman | Teknoloji | Versiyon |
|--------|-----------|----------|
| **Frontend** | Next.js | 16.1.5 |
| **Frontend** | React | 19 |
| **Frontend** | TypeScript | 5.x |
| **Frontend** | Tailwind CSS | 4.x |
| **Frontend** | next-intl | Coklu dil (TR/EN) |
| **Backend** | Django | 5.1.5 |
| **Backend** | Django REST Framework | 3.x |
| **Backend** | Gunicorn | 3 worker |
| **Backend** | Celery | Async task worker |
| **Veritabani** | PostgreSQL | 16 |
| **Cache** | Redis | 7 |
| **Web Sunucu** | Nginx | 1.27 |
| **SSL** | Let's Encrypt (Certbot) | Otomatik |
| **Monitoring** | Sentry | Frontend + Backend |

---

## 6. Dosya Yapisi (Sunucuda)

```
/opt/norosera/
├── docker-compose.prod.yml    # Ana compose dosyasi
├── deploy.sh                  # Deploy yardimci scripti
├── .env                       # Root ortam degiskenleri
├── backend/
│   ├── .env                   # Backend ortam degiskenleri
│   ├── Dockerfile             # Backend Docker imaji
│   ├── config/settings/
│   │   ├── base.py            # Temel Django ayarlari
│   │   └── production.py      # Production Django ayarlari
│   └── ...
├── frontend/
│   ├── Dockerfile             # Frontend Docker imaji
│   ├── next.config.ts
│   └── ...
└── nginx/
    ├── active.conf            # Aktif nginx konfigurasyonu
    ├── nginx.init.conf        # HTTP-only baslangic konfig
    └── nginx.prod.conf        # SSL/HTTPS production konfig
```

---

## 7. Sik Kullanilan Komutlar

### Sunucuya Baglanma
```bash
ssh root@178.104.30.193
cd /opt/norosera
```

### Servis Durumunu Goruntuleme
```bash
docker compose -f docker-compose.prod.yml ps
```

### Loglari Goruntuleme
```bash
# Tum loglar
docker compose -f docker-compose.prod.yml logs -f

# Belirli servis
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f nginx
```

### Servisleri Yeniden Baslatma
```bash
# Tek servis
docker compose -f docker-compose.prod.yml restart backend

# Tum servisler
docker compose -f docker-compose.prod.yml restart
```

### Kod Guncelleme (Deploy)
Lokal makineden:
```bash
# 1. Degisiklikleri sunucuya gonder
rsync -avz --exclude='node_modules' --exclude='__pycache__' \
  --exclude='.git' --exclude='.next' --exclude='.venv' \
  /Users/burhanettinuludag/Desktop/UlgarTech/clinic-platform/ \
  root@178.104.30.193:/opt/norosera/

# 2. Sunucuda rebuild ve restart
ssh root@178.104.30.193 "cd /opt/norosera && \
  docker compose -f docker-compose.prod.yml build backend frontend && \
  docker compose -f docker-compose.prod.yml up -d && \
  docker compose -f docker-compose.prod.yml exec backend python manage.py migrate && \
  docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput"
```

### Django Migration
```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Django Collectstatic
```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### Django Shell
```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py shell
```

### Veritabani Yedekleme
```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U norosera norosera_prod > backup_$(date +%Y%m%d).sql
```

### Veritabani Geri Yukleme
```bash
cat backup_YYYYMMDD.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U norosera norosera_prod
```

---

## 8. SSL Sertifika Yonetimi

### Otomatik Yenileme
Cron job her gece 03:00'te calisir:
```
0 3 * * * cd /opt/norosera && docker compose -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Manuel Yenileme
```bash
cd /opt/norosera
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Sertifika Durumu
```bash
docker compose -f docker-compose.prod.yml run --rm certbot certificates
```

---

## 9. Guvenlik

### Firewall (UFW)
```
Port 22  (SSH)   → Acik
Port 80  (HTTP)  → Acik (HTTPS'e yonlendirir)
Port 443 (HTTPS) → Acik
Diger portlar    → Kapali
```

### Nginx Guvenlik Onlemleri
- HTTP → HTTPS 301 yonlendirme
- HSTS (max-age: 63072000)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- XSS Protection
- Content Security Policy
- Rate limiting (10r/s genel, 5r/s API)
- Kotu bot engelleme (AhrefsBot, SemrushBot, vb.)
- Hotlink korumasi (resimler)
- SSL: TLSv1.2 ve TLSv1.3

### Django Guvenlik
- SECURE_SSL_REDIRECT = True
- SECURE_HSTS_SECONDS = 63072000
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True
- Custom admin URL: /yonetim-7x9k/
- CORS beyaz listesi: sadece norosera.com

---

## 10. Monitoring & Debugging

### Backend Loglarini Kontrol
```bash
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Nginx Error Loglari
```bash
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/error.log
```

### Disk Kullanimi
```bash
df -h /
docker system df
```

### Bellek Kullanimi
```bash
free -h
docker stats --no-stream
```

### Container Icine Girme
```bash
docker compose -f docker-compose.prod.yml exec backend bash
docker compose -f docker-compose.prod.yml exec frontend sh
docker compose -f docker-compose.prod.yml exec db psql -U norosera norosera_prod
```

---

## 11. Acil Durum

### Servisleri Tamamen Durdurma
```bash
cd /opt/norosera
docker compose -f docker-compose.prod.yml down
```

### Servisleri Tekrar Baslatma
```bash
cd /opt/norosera
docker compose -f docker-compose.prod.yml up -d
```

### Veritabanini Sifirdan Olusturma (DIKKAT: VERI KAYBI!)
```bash
docker compose -f docker-compose.prod.yml down
docker volume rm norosera_postgres_data
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
# Superuser olustur:
docker compose -f docker-compose.prod.yml exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(email='admin@norosera.com', password='Norosera2026!', first_name='Admin', last_name='Norosera')
"
```

---

## 12. Bilinen Kisitlamalar & Yapilacaklar

| Konu | Durum | Oncelik |
|------|-------|---------|
| Email SMTP ayarlanmali (suan console backend) | ⚠️ Beklemede | Yuksek |
| TypeScript `ignoreBuildErrors: true` kapatilmali | ⚠️ Gecici | Orta |
| Sentry DSN bos, monitoring aktif degil | ⚠️ Beklemede | Orta |
| iyzico API anahtarlari ayarlanmali | ⚠️ Beklemede | Yuksek |
| Otomatik veritabani yedekleme (cron) | ❌ Yok | Yuksek |
| Frontend tasarim iyilestirmesi | ❌ Planlanacak | Yuksek |
| Fail2ban kurulumu (brute-force koruma) | ❌ Yok | Orta |
