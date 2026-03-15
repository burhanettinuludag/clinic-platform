# Skill: Veritabanı Yedekleme & İzleme — Norosera

## Trigger
yedek, backup, restore, veritabanı, database, log, hata izleme, monitoring, uptime, sağlık kontrolü, health check

## PostgreSQL Yedekleme

### Otomatik yedekleme scripti
```bash
#!/bin/bash
# scripts/backup-db.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/norosera/backups"
DB_NAME="norosera_prod"
S3_BUCKET="norosera-backups"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# pg_dump ile yedek al
pg_dump -Fc -h localhost -U norosera_user $DB_NAME > "$BACKUP_DIR/norosera_$TIMESTAMP.dump"

# Sıkıştır
gzip "$BACKUP_DIR/norosera_$TIMESTAMP.dump"

# S3'e yükle (opsiyonel)
# aws s3 cp "$BACKUP_DIR/norosera_$TIMESTAMP.dump.gz" "s3://$S3_BUCKET/"

# Eski yedekleri temizle
find $BACKUP_DIR -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Yedek alındı: norosera_$TIMESTAMP.dump.gz"
```

### Celery Beat ile otomatik zamanlama
```python
# celery_app/schedule.py
CELERY_BEAT_SCHEDULE = {
    "daily-db-backup": {
        "task": "apps.core.tasks.backup_database",
        "schedule": crontab(hour=3, minute=0),  # Her gece 03:00
    },
    "weekly-full-backup": {
        "task": "apps.core.tasks.full_backup",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),  # Pazar 02:00
    },
}
```

### Restore prosedürü
```bash
# 1. Mevcut bağlantıları kes
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='norosera_prod' AND pid <> pg_backend_pid();"

# 2. Restore
gunzip -k norosera_TIMESTAMP.dump.gz
pg_restore -d norosera_prod -c norosera_TIMESTAMP.dump

# 3. Migration kontrol
cd backend && python manage.py migrate --check
```

## Django Health Check

### Endpoint oluştur
```python
# apps/core/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis

def health_check(request):
    status = {"status": "ok", "checks": {}}

    # Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status["checks"]["database"] = "ok"
    except Exception as e:
        status["checks"]["database"] = f"error: {e}"
        status["status"] = "degraded"

    # Redis
    try:
        cache.set("health_check", "ok", 10)
        assert cache.get("health_check") == "ok"
        status["checks"]["redis"] = "ok"
    except Exception:
        status["checks"]["redis"] = "error"
        status["status"] = "degraded"

    # Celery
    try:
        from celery_app import app
        insp = app.control.inspect()
        if insp.ping():
            status["checks"]["celery"] = "ok"
        else:
            status["checks"]["celery"] = "no workers"
            status["status"] = "degraded"
    except Exception:
        status["checks"]["celery"] = "error"

    # Disk
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_pct = (free / total) * 100
    status["checks"]["disk"] = f"{free_pct:.1f}% free"
    if free_pct < 10:
        status["status"] = "critical"

    code = 200 if status["status"] == "ok" else 503
    return JsonResponse(status, status=code)
```

## Log Analizi

### Yapılandırılmış loglama
```python
# config/settings/base.py
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/norosera/app.log",
            "maxBytes": 10_000_000,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        }
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
    "loggers": {
        "apps.patients": {"level": "WARNING"},  # Hasta verisi = minimum log
        "django.security": {"level": "WARNING", "handlers": ["file"]},
    },
}
```

### Hata izleme scripti
```bash
# Son 1 saatteki hataları raporla
grep -c '"levelname": "ERROR"' /var/log/norosera/app.log
grep '"levelname": "ERROR"' /var/log/norosera/app.log | tail -10 | python3 -m json.tool

# En sık hata pattern'leri
grep '"levelname": "ERROR"' /var/log/norosera/app.log | \
    python3 -c "import sys,json; errors=[json.loads(l)['message'] for l in sys.stdin]; 
    from collections import Counter; 
    [print(f'{c}: {m[:80]}') for m,c in Counter(errors).most_common(10)]"
```

## Dependency Güncelleme

### Otomatik güvenlik taraması
```bash
# Backend
cd backend
pip-audit --format json > /tmp/pip-audit.json
pip list --outdated --format json > /tmp/pip-outdated.json

# Frontend
cd frontend
npm audit --json > /tmp/npm-audit.json
npx npm-check-updates --format json > /tmp/npm-outdated.json
```

### Güncelleme stratejisi
- **Critical security:** Hemen güncelle, test çalıştır, deploy
- **Major version:** Branch aç, kapsamlı test, PR ile merge
- **Minor/patch:** Haftalık toplu güncelleme
- **Django/Next.js major:** Ayrı sprint planla
