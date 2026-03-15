# Skill: Deployment & CI/CD — Norosera

## Trigger
deploy, deployment, CI/CD, github actions, docker, vercel, yayınla, production, staging

## Rules

### Architecture
```
GitHub Push → GitHub Actions → Build & Test → Deploy
                                    ├── Backend: Docker → VPS (Django + Gunicorn + Nginx)
                                    └── Frontend: Vercel (Next.js)
```

### GitHub Actions Workflow Structure
```yaml
# .github/workflows/backend-ci.yml
name: Backend CI/CD
on:
  push:
    branches: [main, develop]
    paths: ["backend/**"]
  pull_request:
    branches: [main]
    paths: ["backend/**"]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: norosera_test
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements/dev.txt
      - run: cd backend && python manage.py test --parallel
      - run: cd backend && python manage.py check --deploy

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build & Push Docker
        run: |
          docker build -t norosera-backend ./backend
          # Push to registry
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/norosera
            docker-compose pull backend
            docker-compose up -d backend
            docker-compose exec -T backend python manage.py migrate
```

### Docker Compose
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    env_file: .env
    ports: ["8000:8000"]
    depends_on: [db, redis]
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

  db:
    image: postgres:15
    volumes: [postgres_data:/var/lib/postgresql/data]
    env_file: .env

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  celery:
    build: ./backend
    command: celery -A celery_app worker -l info -c 2
    depends_on: [db, redis]

  celery-beat:
    build: ./backend
    command: celery -A celery_app beat -l info
    depends_on: [db, redis]
```

### Deployment Checklist
Before deploying to production:
1. All tests passing (backend + frontend)
2. `python manage.py check --deploy` passes
3. No pending migrations
4. Environment variables set on target
5. Database backup taken
6. NEVER deploy directly — always through GitHub Actions

### Rollback
```bash
# On VPS, if deployment fails:
docker-compose exec backend python manage.py migrate <app_name> <previous_migration>
docker-compose up -d --no-deps backend  # restart with previous image
```

### Vercel Frontend
- Connected to `main` branch, auto-deploys on push
- Environment variables set in Vercel dashboard
- Preview deployments on pull requests
- Build command: `npm run build`
- Output directory: `.next`
