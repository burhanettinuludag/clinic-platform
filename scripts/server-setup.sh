#!/bin/bash
# Norosera Server Setup Script
# Ubuntu 22.04 LTS için

set -e

echo "=== Norosera Server Kurulumu ==="

# Sistem güncellemesi
echo "1. Sistem güncelleniyor..."
apt update && apt upgrade -y

# Gerekli paketler
echo "2. Gerekli paketler yükleniyor..."
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw \
    fail2ban

# Docker kurulumu
echo "3. Docker yükleniyor..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Docker Compose kurulumu
echo "4. Docker Compose yükleniyor..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Kullanıcı oluşturma
echo "5. Deploy kullanıcısı oluşturuluyor..."
useradd -m -s /bin/bash -G docker deploy || true
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
chown -R deploy:deploy /home/deploy/.ssh

# Firewall ayarları
echo "6. Firewall yapılandırılıyor..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Fail2ban başlatma
echo "7. Fail2ban başlatılıyor..."
systemctl enable fail2ban
systemctl start fail2ban

# Proje dizini
echo "8. Proje dizini oluşturuluyor..."
mkdir -p /opt/norosera
chown deploy:deploy /opt/norosera

echo ""
echo "=== Kurulum Tamamlandı ==="
echo ""
echo "Sonraki adımlar:"
echo "1. Domain DNS kayıtlarını VPS IP'sine yönlendirin"
echo "2. Projeyi /opt/norosera dizinine yükleyin"
echo "3. .env dosyasını düzenleyin"
echo "4. SSL sertifikası için certbot kullanın"
echo ""
