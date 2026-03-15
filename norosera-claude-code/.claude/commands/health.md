# /health — Sistem Sağlık Kontrolü

Norosera'nın tüm bileşenlerinin durumunu kontrol et.

## Adımlar:

### 1. Backend Sağlığı
```bash
cd backend
python manage.py check
python manage.py showmigrations --plan | grep "\[ \]" | wc -l  # pending migrations
python manage.py diffsettings --all | grep -c "DEBUG.*True"  # debug mode
```

### 2. Frontend Sağlığı  
```bash
cd frontend
npx tsc --noEmit 2>&1 | tail -5  # type errors
npm run lint 2>&1 | grep -c "error"  # lint errors
npm outdated --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Outdated: {len(d)}')" 2>/dev/null
```

### 3. Docker & Servisler
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null
docker-compose ps 2>/dev/null
```

### 4. Database
```bash
cd backend
python manage.py dbshell -c "SELECT pg_database_size('norosera_prod');" 2>/dev/null
python manage.py shell -c "
from django.db import connection
with connection.cursor() as c:
    c.execute('SELECT count(*) FROM pg_stat_activity')
    print(f'Active connections: {c.fetchone()[0]}')
"
```

### 5. Disk & Bellek
```bash
df -h / | tail -1
free -h 2>/dev/null || vm_stat 2>/dev/null
```

### 6. Son Yedek
```bash
ls -lht /opt/norosera/backups/*.dump.gz 2>/dev/null | head -3
```

### 7. Sonuç
```
🏥 NOROSERA SİSTEM SAĞLIK RAPORU
═════════════════════════════════

🐍 Backend:    ✅/❌ (Django check, migrations, debug)
⚛️  Frontend:   ✅/❌ (TypeScript, lint, deps)
🐳 Docker:     ✅/❌ (container durumları)
🗄️ Database:   ✅/❌ (bağlantılar, boyut)
💾 Disk:       ✅/❌ (kullanım oranı)
📦 Yedek:      ✅/❌ (son yedek tarihi)
```
