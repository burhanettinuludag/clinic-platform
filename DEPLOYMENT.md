# Norosera Deployment Rehberi

Bu rehber, Norosera projesini Natro VPS üzerinde yayınlamak için gereken tüm adımları içerir.

---

## Gereksinimler

- **Natro VPS:** Minimum 2GB RAM, 2 vCPU, Ubuntu 22.04 LTS
- **Domain:** norosera.com (DNS kayıtları VPS IP'sine yönlendirilmiş)

---

## Adım 1: VPS'e Bağlanma

Natro size VPS bilgilerini email ile gönderecek. Terminal'den bağlanın:

```bash
ssh root@VPS_IP_ADRESI
```

---

## Adım 2: Sunucu Hazırlığı

VPS'e bağlandıktan sonra şu komutları sırayla çalıştırın:

```bash
# Sistem güncelleme
apt update && apt upgrade -y

# Docker kurulumu
curl -fsSL https://get.docker.com | sh

# Docker Compose kurulumu
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Git kurulumu
apt install -y git

# Firewall ayarları
ufw allow ssh
ufw allow http
ufw allow https
ufw enable
```

---

## Adım 3: Projeyi Sunucuya Yükleme

### Seçenek A: Git ile (Önerilen)

```bash
cd /opt
git clone https://github.com/KULLANICI_ADINIZ/norosera.git norosera
cd norosera
```

### Seçenek B: Manuel Upload (SCP/SFTP)

Bilgisayarınızdan:
```bash
scp -r /Users/burhanettinuludag/clinic-platform root@VPS_IP:/opt/norosera
```

---

## Adım 4: Environment Dosyasını Düzenleme

```bash
cd /opt/norosera

# .env dosyası oluştur
cp .env.production .env

# Düzenle
nano .env
```

**Değiştirilmesi GEREKEN değerler:**

```env
# Domain
DOMAIN=norosera.com

# Güvenlik - Rastgele güçlü bir key oluşturun
DJANGO_SECRET_KEY=buraya-50-karakterden-uzun-rastgele-string

# Database şifresi
DB_PASSWORD=guclu-bir-sifre-123

# iyzico (merchant panelinden alın)
IYZICO_API_KEY=your-api-key
IYZICO_SECRET_KEY=your-secret-key

# Email (Natro email ayarları)
EMAIL_HOST=mail.norosera.com
EMAIL_HOST_USER=noreply@norosera.com
EMAIL_HOST_PASSWORD=email-sifreniz
```

---

## Adım 5: Domain DNS Ayarları

Natro panelinde Domain → DNS Yönetimi:

| Tip | Host | Değer | TTL |
|-----|------|-------|-----|
| A | @ | VPS_IP | 3600 |
| A | www | VPS_IP | 3600 |

**Not:** DNS yayılması 5-30 dakika sürebilir.

---

## Adım 6: İlk Deployment

```bash
cd /opt/norosera

# Script'lere çalıştırma izni ver
chmod +x scripts/*.sh

# Deploy et
./scripts/deploy.sh
```

Bu komut:
- Docker images build eder
- Container'ları başlatır
- Database migration yapar
- Admin kullanıcı oluşturur

---

## Adım 7: SSL Sertifikası (HTTPS)

DNS kayıtları aktif olduktan sonra:

```bash
cd /opt/norosera
./scripts/ssl-setup.sh
```

---

## Adım 8: Doğrulama

Tarayıcıda açın:
- **Site:** https://norosera.com
- **Admin Panel:** https://norosera.com/admin/
- **API:** https://norosera.com/api/v1/

---

## Günlük İşlemler

### Logları Görüntüleme

```bash
cd /opt/norosera

# Tüm loglar
docker-compose -f docker-compose.prod.yml logs -f

# Sadece backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Sadece hatalar
docker-compose -f docker-compose.prod.yml logs -f | grep -i error
```

### Yeniden Başlatma

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Güncelleme

```bash
cd /opt/norosera
git pull origin main
./scripts/deploy.sh
```

### Database Backup

```bash
# Backup al
docker-compose -f docker-compose.prod.yml exec db pg_dump -U norosera_user norosera_db > backup_$(date +%Y%m%d).sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T db psql -U norosera_user norosera_db < backup_file.sql
```

---

## Sorun Giderme

### Container durumları
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Container yeniden başlat
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Disk kullanımı
```bash
df -h
docker system prune -a  # Kullanılmayan images temizle
```

### SSL yenileme (manuel)
```bash
certbot renew
./scripts/ssl-setup.sh
```

---

## Güvenlik Kontrol Listesi

- [ ] DJANGO_SECRET_KEY değiştirildi
- [ ] DB_PASSWORD güçlü bir şifre
- [ ] Admin şifresi değiştirildi
- [ ] SSL sertifikası aktif
- [ ] Firewall aktif (ufw status)
- [ ] iyzico production keys (sandbox değil)

---

## Destek

Sorun yaşarsanız:
1. Logları kontrol edin
2. Container durumlarını kontrol edin
3. DNS ayarlarını kontrol edin
