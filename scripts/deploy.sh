#!/bin/bash
# ===========================================
# NOROSERA DEPLOYMENT SCRIPT
# ===========================================
# Bu script'i VPS sunucusunda çalıştırın
# Kullanım: ./deploy.sh

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Norosera Deployment ===${NC}"

# Çalışma dizini
DEPLOY_DIR="/opt/norosera"
cd $DEPLOY_DIR

# .env kontrolü
if [ ! -f ".env" ]; then
    echo -e "${RED}HATA: .env dosyası bulunamadı!${NC}"
    echo "Önce .env.production dosyasını .env olarak kopyalayın ve düzenleyin."
    exit 1
fi

# Git pull (eğer git repo ise)
if [ -d ".git" ]; then
    echo -e "${YELLOW}1. Git pull yapılıyor...${NC}"
    git pull origin main
fi

# Docker images build
echo -e "${YELLOW}2. Docker images build ediliyor...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Eski container'ları durdur
echo -e "${YELLOW}3. Eski container'lar durduruluyor...${NC}"
docker-compose -f docker-compose.prod.yml down

# Yeni container'ları başlat
echo -e "${YELLOW}4. Yeni container'lar başlatılıyor...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Migrations
echo -e "${YELLOW}5. Database migrations...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --noinput

# Superuser oluştur (ilk kurulumda)
echo -e "${YELLOW}6. Admin kullanıcı kontrolü...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell -c "
import secrets
from apps.accounts.models import CustomUser
if not CustomUser.objects.filter(is_superuser=True).exists():
    password = secrets.token_urlsafe(20)
    CustomUser.objects.create_superuser(
        'admin@norosera.com',
        password,
        first_name='Admin',
        last_name='User',
    )
    print()
    print('=' * 50)
    print('ADMIN KULLANICI OLUSTURULDU')
    print('=' * 50)
    print(f'Email   : admin@norosera.com')
    print(f'Sifre   : {password}')
    print('=' * 50)
    print('UYARI: Bu sifreyi HEMEN degistirin!')
    print('Admin panel: /admin/ -> Sifre Degistir')
    print('=' * 50)
    print()
else:
    print('Admin kullanici zaten mevcut, yeni olusturulmadi.')
"

# Container durumları
echo -e "${YELLOW}7. Container durumları:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}=== Deployment Tamamlandı ===${NC}"
echo ""
ADMIN_PATH=$(grep -oP 'ADMIN_URL=\K.*' .env 2>/dev/null || echo "admin/")
echo "Site: https://norosera.com"
echo "Admin: https://norosera.com/${ADMIN_PATH}"
echo ""
