# 🧠 Norosera — Neurology Clinic Platform

> Django + Next.js full-stack digital health platform for neurology clinics.

![CI](https://github.com/burhanettinuludag/clinic-platform/actions/workflows/ci.yml/badge.svg)

## Overview

Norosera is a comprehensive clinic management platform that combines patient tracking, AI-powered content management, doctor panels, and gamification into a single solution for neurology practices.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.1, Django REST Framework, PostgreSQL |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, React Query |
| AI | Multi-agent pipeline (Groq Llama 3.3 + Google Gemini) |
| Auth | JWT (SimpleJWT), role-based (patient/doctor/admin) |
| Async | Celery + Redis |
| Cache | Redis |
| i18n | Turkish + English (next-intl) |
| Docs | Swagger UI + ReDoc (drf-spectacular) |
| CI/CD | GitHub Actions |
| Deploy | Docker Compose + Nginx |

## Features

### Patient Modules
- **Migraine Tracking** — attack logging, trigger analysis, education
- **Epilepsy Tracking** — seizure events, triggers, education
- **Dementia Module** — cognitive exercises (6 games), daily assessment, caregiver notes, screening tests
- **Wellness** — breathing exercises, relaxation, sleep tracking, water intake, menstrual cycle, weather widget
- **Symptom & Medication Tracking** — symptom log, medication adherence, reminders
- **Gamification** — badges, streaks, points, achievements, leaderboard

### Doctor Panel
- Dashboard with patient stats and alerts
- Patient management and dementia reports
- AI content generation (full pipeline)
- Author panel (article/news CRUD, status transitions, SEO pipeline)
- Editor panel (review queue, approve/reject, bulk operations, author management)
- DevOps Agent UI (code generation, code review)
- Analytics dashboard (monthly charts, views, status distribution)

### AI Agent System (12 Agents)
| Agent | Purpose |
|-------|---------|
| Content | Medical article generation |
| SEO | SEO optimization |
| Legal | Legal compliance check |
| Translation | TR↔EN translation |
| QA | Quality assessment (6 dimensions) |
| Editor | Final review and publish decision |
| News | News content generation |
| Quality | General quality scoring |
| UI/UX | Interface recommendations |
| Internal Link | Internal link suggestions |
| Publishing | Publishing workflow |
| DevOps | Code generation, review, refactoring |

### CMS & SEO
- Article + NewsArticle models with dual language (TR/EN)
- 5-level author system (0-4) with verification
- E-E-A-T schema markup (Google JSON-LD)
- SSR blog/news pages with generateMetadata
- Dynamic sitemap.xml + robots.txt
- Rich Text Editor (Tiptap) + Image Upload

### Security
- API rate limiting (anon/auth/AI agent throttles)
- reCAPTCHA v3 (register, login, contact)
- JWT with refresh rotation
- CORS whitelist, CSRF protection
- KVKK consent management

### Notifications
- 13 notification templates (TR/EN)
- In-app bell with polling
- Email notifications (HTML templates)
- User preference management
- Celery async email delivery

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 22+
- PostgreSQL 16+
- Redis 7+

### Development Setup
```bash
# Clone
git clone https://github.com/burhanettinuludag/clinic-platform.git
cd clinic-platform

# Backend
cd backend
cp .env.example .env  # edit with your values
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker Setup
```bash
# Development
cp .env.example .env  # edit values
docker compose up -d

# Production
docker compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `backend/.env.example` and `.env.example` for all available configuration options including:
- Database, Redis, Celery
- AI keys (Groq, Gemini)
- reCAPTCHA, OpenWeatherMap
- Email (SMTP), iyzico payments
- Sentry error tracking

## API Documentation

Start the backend and visit:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema**: http://localhost:8000/api/schema/

## Project Structure
```
clinic-platform/
├── backend/
│   ├── apps/
│   │   ├── accounts/        # Auth, user profiles
│   │   ├── content/         # Articles, news, education
│   │   ├── doctor_panel/    # Doctor views, author/editor panels
│   │   ├── notifications/   # Notifications, email service
│   │   ├── patients/        # Disease modules, tasks
│   │   ├── dementia/        # Cognitive exercises, screening
│   │   ├── migraine/        # Attack tracking, triggers
│   │   ├── epilepsy/        # Seizure tracking
│   │   ├── wellness/        # Breathing, sleep, water, menstrual
│   │   ├── tracking/        # Symptoms, medications, reminders
│   │   ├── gamification/    # Badges, streaks, points
│   │   ├── store/           # Products, orders, licenses
│   │   ├── payments/        # Payment processing
│   │   └── common/          # Shared models, throttles, health
│   ├── services/
│   │   ├── agents/          # 12 AI agents
│   │   ├── prompts/         # Agent prompt templates
│   │   ├── orchestrator.py  # Pipeline orchestration
│   │   └── tasks.py         # Celery pipeline tasks
│   └── config/
│       ├── settings/        # base, development, production, testing
│       ├── celery.py        # Celery app config
│       └── urls.py          # Root URL configuration
├── frontend/
│   ├── src/
│   │   ├── app/[locale]/    # Next.js pages (i18n)
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks (React Query)
│   │   └── lib/             # API client, types, utils
│   └── public/              # Static assets
├── nginx/                   # Nginx configs
├── docker-compose.yml       # Development
├── docker-compose.prod.yml  # Production
└── .github/workflows/       # CI/CD
```

## Stats

- **232** Python files (~21,800 lines)
- **89** TypeScript/React files (~3,000 lines)
- **60+** Django models
- **80+** API endpoints
- **12** AI agents
- **37+** frontend pages

## License

Proprietary — UlgarTech © 2025-2026
