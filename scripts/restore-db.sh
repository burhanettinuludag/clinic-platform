#!/bin/bash
# ===========================================
# NOROSERA - PostgreSQL Restore
# ===========================================
# Kullanim: ./restore-db.sh backup_dosyasi.sql.gz

set -e

if [ -z "$1" ]; then
    echo "Kullanim: ./restore-db.sh backup_dosyasi.sql.gz"
    echo "Mevcut backup'lar:"
    ls -lh /opt/norosera/backups/norosera_*.sql.gz 2>/dev/null || echo "Backup bulunamadi"
    exit 1
fi

echo "UYARI: Bu islem mevcut database'i silecek!"
read -p "Devam etmek istiyor musunuz? (evet/hayir): " confirm

if [ "$confirm" != "evet" ]; then
    echo "Iptal edildi."
    exit 0
fi

gunzip -c "$1" | docker-compose -f /opt/norosera/docker-compose.prod.yml exec -T db \
  psql -U ${DB_USER:-postgres} ${DB_NAME:-norosera_prod}

echo "Restore tamamlandi."
