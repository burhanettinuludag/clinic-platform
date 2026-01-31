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
from apps.accounts.models import CustomUser
if not CustomUser.objects.filter(is_superuser=True).exists():
    CustomUser.objects.create_superuser('admin@norosera.com', 'admin123', first_name='Admin', last_name='User')
    print('Admin kullanıcı oluşturuldu: admin@norosera.com / admin123')
    print('UYARI: Şifreyi hemen değiştirin!')
else:
    print('Admin kullanıcı zaten mevcut.')
"

# Container durumları
echo -e "${YELLOW}7. Container durumları:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}=== Deployment Tamamlandı ===${NC}"
echo ""
echo "Site: https://norosera.com"
echo "Admin: https://norosera.com/admin/"
echo ""
