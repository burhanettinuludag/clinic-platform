# Norosera — Clinic Platform | Claude Guidelines

## 1. Critical Rules (MUST follow)

- NEVER modify `.env`, `.env.local`, `.env.production` files without explicit approval
- NEVER run `git push --force`, `rm -rf`, or `DROP TABLE` commands
- NEVER expose patient data, API keys, or KVKK-sensitive information in logs or comments
- ALL Django model changes MUST include a migration file
- ALL API endpoints MUST have corresponding tests
- ALL Next.js pages MUST use SSR or SSG — no client-only data fetching for public pages
- Turkish language MUST be used for user-facing strings; English for code/comments
- ALWAYS run `python manage.py check` after Django changes
- ALWAYS run `npx tsc --noEmit` after TypeScript changes
- ALL blog posts and articles MUST be minimum 3000 karakter (boşluklar dahil). Daha kısa içerik üretme — eksikse detaylandır, örnek ekle, alt başlık aç.

## 2. Project Overview

### Tech Stack
- **Backend:** Django 5.1 + Django REST Framework + Python 3.12
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Database:** PostgreSQL
- **Async:** Celery + Redis
- **CI/CD:** GitHub Actions + Docker
- **Repo:** github.com/burhanettinuludag/clinic-platform (monorepo)

### Directory Structure
```
clinic-platform/
├── backend/                 # Django project root
│   ├── config/              # Django settings, urls, wsgi, asgi
│   ├── apps/                # 15 Django apps
│   │   ├── accounts/        # User auth, profiles
│   │   ├── patients/        # Patient records (KVKK-sensitive)
│   │   ├── appointments/    # Appointment scheduling
│   │   ├── blog/            # Medical blog content
│   │   ├── seo/             # SEO management
│   │   ├── legal/           # KVKK, legal pages
│   │   ├── social/          # Social media automation
│   │   ├── ai_agents/       # 12 AI agent definitions
│   │   ├── analytics/       # Site analytics
│   │   ├── media_manager/   # Image/video management
│   │   ├── notifications/   # Email/SMS notifications
│   │   ├── translations/    # i18n management
│   │   ├── sitemap/         # Dynamic sitemap
│   │   ├── contact/         # Contact forms
│   │   └── services/        # Medical services
│   ├── templates/           # Django templates (admin, emails)
│   ├── static/              # Static files
│   ├── celery_app/          # Celery configuration
│   ├── requirements/        # pip requirements (base, dev, prod)
│   └── manage.py
├── frontend/                # Next.js project root
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities, API client
│   │   ├── hooks/           # Custom React hooks
│   │   ├── types/           # TypeScript type definitions
│   │   └── styles/          # Global styles
│   ├── public/              # Static assets
│   ├── next.config.js
│   └── tailwind.config.ts
├── docker/                  # Docker configs
├── .github/workflows/       # CI/CD pipelines
├── nginx/                   # Nginx config
└── docs/                    # Project documentation
```

### AI Agents (12 total)
Content Agent, SEO Agent, Legal Agent, Translation Agent, UI/UX Agent,
Q&A RAG Agent, Social Media Agent, Analytics Agent, Patient Intake Agent,
Appointment Agent, Notification Agent, Report Agent

### Data Flow
- Public pages: Next.js SSR → Django REST API → PostgreSQL
- Admin/Dashboard: Next.js CSR → Django REST API → PostgreSQL
- Async tasks: Django → Celery → Redis → Worker → PostgreSQL
- Social media: Celery Beat → Social Agent → Instagram/LinkedIn APIs

## 3. How to Work Here

### Backend
```bash
cd backend
python manage.py runserver          # Dev server
python manage.py test               # Run all tests
python manage.py test apps.patients # Test specific app
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py check              # System check
celery -A celery_app worker -l info # Start Celery worker
```

### Frontend
```bash
cd frontend
npm run dev          # Dev server (localhost:3000)
npm run build        # Production build
npm run lint         # ESLint
npx tsc --noEmit     # Type check
npm run test         # Jest tests
```

### Docker
```bash
docker-compose up -d              # Start all services
docker-compose logs -f backend    # Follow backend logs
docker-compose exec backend bash  # Shell into backend
```

### Deployment
```bash
# Backend: pushed via GitHub Actions → Docker → VPS
# Frontend: pushed via GitHub Actions → Vercel
# NEVER deploy directly; always through CI/CD
```

## 4. What Claude Gets Wrong

- Forgets to create migration files after model changes
- Uses `fetch()` in Next.js components instead of server actions or API routes
- Writes English user-facing text instead of Turkish
- Creates API views without permission classes (must always specify)
- Puts secrets in code instead of environment variables
- Ignores KVKK compliance when handling patient data fields
- Uses `any` type in TypeScript instead of proper interfaces
- Forgets to add new URLs to both Django urlpatterns AND Next.js routing
- Runs `pip install` without `--break-system-packages` flag on this system

## 5. KVKK & Security Rules

- Patient data (ad, soyad, TC, telefon, sağlık verileri) = KVKK Özel Nitelikli Veri
- ALL patient endpoints require `IsAuthenticated` + role-based permission
- Patient data MUST be encrypted at rest (Django model field encryption)
- Audit logging required for all patient data access
- Data retention policies must be enforced via Celery periodic tasks
- NEVER log patient identifiable information
