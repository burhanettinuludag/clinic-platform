# /health — System Health Check

Check all system components and report status.

## Checks

### 1. Backend
```bash
cd backend && source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.development python3 manage.py check
```
- Django system check errors/warnings
- Pending migrations count
- DEBUG mode status

### 2. Frontend
```bash
cd frontend
npx tsc --noEmit 2>&1 | tail -5
npm run lint 2>&1 | tail -5
```
- TypeScript compilation errors
- Lint errors/warnings
- Outdated packages: `npm outdated`

### 3. Docker
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
- Running containers and their status

### 4. Database
```bash
cd backend && source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.development python3 -c "
import django; django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT pg_database_size(current_database())')
size = cursor.fetchone()[0]
print(f'DB Size: {size / 1024 / 1024:.1f} MB')
cursor.execute('SELECT count(*) FROM pg_stat_activity')
conns = cursor.fetchone()[0]
print(f'Active connections: {conns}')
"
```

### 5. Disk & Memory
```bash
df -h / | tail -1
```

## Output Format

```
Component       | Status | Details
----------------|--------|--------
Backend         | OK/ERR | ...
Frontend        | OK/ERR | ...
Docker          | OK/ERR | ...
Database        | OK/ERR | ...
Disk            | OK/ERR | ...
```

$ARGUMENTS
