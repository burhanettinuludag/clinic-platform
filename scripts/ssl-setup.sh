#!/bin/bash
# ===========================================
# SSL CERTIFICATE SETUP (Let's Encrypt)
# ===========================================
# Bu script'i VPS'te ilk kurulumda çalıştırın
# Domain DNS kayıtları aktif olduktan sonra çalıştırın!

set -e

DOMAIN="norosera.com"
EMAIL="admin@norosera.com"  # Kendi email adresinizi yazın
DEPLOY_DIR="/opt/norosera"

echo "=== SSL Sertifikası Kurulumu ==="

# Certbot kurulumu
echo "1. Certbot yükleniyor..."
apt update
apt install -y certbot

# Nginx'i geçici olarak durdur
echo "2. Nginx durduruluyor..."
docker-compose -f $DEPLOY_DIR/docker-compose.prod.yml stop nginx 2>/dev/null || true

# SSL sertifikası al
echo "3. SSL sertifikası alınıyor..."
certbot certonly --standalone \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive

# SSL dizini oluştur ve kopyala
echo "4. SSL dosyaları hazırlanıyor..."
mkdir -p $DEPLOY_DIR/ssl
cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem $DEPLOY_DIR/ssl/
cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem $DEPLOY_DIR/ssl/

# docker-compose.prod.yml'e SSL volume ekle
echo "5. Nginx config güncelleniyor..."
cp $DEPLOY_DIR/nginx/nginx.prod.conf $DEPLOY_DIR/nginx/nginx.conf

# Nginx'i yeniden başlat
echo "6. Servisler yeniden başlatılıyor..."
docker-compose -f $DEPLOY_DIR/docker-compose.prod.yml up -d

# Auto-renewal cron job
echo "7. Otomatik yenileme ayarlanıyor..."
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && cp -L /etc/letsencrypt/live/$DOMAIN/*.pem $DEPLOY_DIR/ssl/ && docker-compose -f $DEPLOY_DIR/docker-compose.prod.yml restart nginx") | crontab -

echo ""
echo "=== SSL Kurulumu Tamamlandı ==="
echo ""
echo "Site artık HTTPS üzerinden erişilebilir:"
echo "https://$DOMAIN"
echo ""
