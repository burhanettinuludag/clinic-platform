# /deploy — Production Deploy Readiness Check

Check if the codebase is ready for deployment to VPS (178.104.30.193).

## Pre-Deploy Checklist

1. **Git status:**
```bash
git status
```
All changes should be committed.

2. **Run all tests:**
```bash
cd backend && source .venv/bin/activate && DJANGO_SETTINGS_MODULE=config.settings.development pytest
cd frontend && npx tsc --noEmit
```

3. **Django deploy check:**
```bash
cd backend && source .venv/bin/activate && DJANGO_SETTINGS_MODULE=config.settings.production python3 manage.py check --deploy
```

4. **Check pending migrations:**
```bash
cd backend && source .venv/bin/activate && DJANGO_SETTINGS_MODULE=config.settings.development python3 manage.py showmigrations --plan | grep '\[ \]'
```

5. **Frontend build test:**
```bash
cd frontend && npm run build
```

6. **Docker build test:**
```bash
docker compose -f docker-compose.prod.yml build --no-cache
```

## Deploy Readiness Report

| Check | Status |
|-------|--------|
| Tests pass | ? |
| TypeScript clean | ? |
| Build succeeds | ? |
| Deploy check clean | ? |
| No pending migrations | ? |
| Git clean | ? |

## Deploy Command (only if all checks pass)
```bash
bash deploy.sh update
```

Do NOT deploy unless ALL checks pass. Report any failures with details.

$ARGUMENTS
