#!/bin/bash
# ===========================================
# NOROSERA - Gunluk PostgreSQL Backup
# ===========================================
# Kullanim: ./scripts/backup-db.sh
# Cron: 0 4 * * * /opt/norosera/scripts/backup-db.sh >> /var/log/clinic/backup.log 2>&1

set -e

BACKUP_DIR="/opt/norosera/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="norosera_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Docker container'dan pg_dump
docker-compose -f /opt/norosera/docker-compose.prod.yml exec -T db \
  pg_dump -U ${DB_USER:-postgres} ${DB_NAME:-norosera_prod} | gzip > "$BACKUP_DIR/$FILENAME"

# Eski backup'ları temizle
find $BACKUP_DIR -name "norosera_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Boyut kontrolü
SIZE=$(du -h "$BACKUP_DIR/$FILENAME" | cut -f1)
echo "$(date): Backup tamamlandi: $FILENAME ($SIZE)"

# Opsiyonel: S3'e yükle (aktifleştirmek için yorum kaldır)
# aws s3 cp "$BACKUP_DIR/$FILENAME" s3://norosera-backups/$FILENAME
