# Norosera - Clinic Platform

Norosera, noerolojik hastaliklar (migren, epilepsi, demans) icin hasta takip, egitim ve hekim paneli sunan full-stack saglik platformudur.

## Tech Stack

- **Backend:** Django 5.1.5, Django REST Framework 3.16.1, PostgreSQL 16, Redis 7, Celery 5.4
- **Frontend:** Next.js 16.1.5, React 19, TypeScript 5.9, Tailwind CSS 4, React Query 5
- **AI:** Groq Llama 3.3 70B (primary), Google Gemini (fallback)
- **Payments:** iyzico
- **Infra:** Docker Compose, Nginx, Gunicorn, Sentry, Let's Encrypt

## Project Structure

```
clinic-platform/
├── backend/                   # Django REST API
│   ├── config/                # Django settings & config
│   │   ├── settings/
│   │   │   ├── base.py        # Shared settings
│   │   │   ├── development.py # Local dev settings
│   │   │   └── production.py  # VPS/production settings
│   │   ├── urls.py            # Root URL routing
│   │   ├── celery.py          # Celery + Beat schedule
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/          # CustomUser, auth, profiles, permissions
│   │   ├── patients/          # DiseaseModule, PatientModule, tasks
│   │   ├── tracking/          # SymptomEntry, Medication, Reminders
│   │   ├── migraine/          # MigraineAttack, triggers
│   │   ├── epilepsy/          # SeizureEvent, triggers
│   │   ├── dementia/          # CognitiveExercise, DailyAssessment, CaregiverNote, Screening
│   │   ├── content/           # Article, EducationItem, NewsArticle, AI review pipeline
│   │   ├── doctor_panel/      # Doctor-specific views & serializers
│   │   ├── wellness/          # Wellness tracking
│   │   ├── gamification/      # Badge, UserStreak, points
│   │   ├── notifications/     # Notification, NotificationPreference
│   │   ├── chat/              # AI chatbot, doctor-patient messaging
│   │   ├── social/            # SocialAccount, SocialCampaign
│   │   ├── store/             # Product, Order, License
│   │   ├── payments/          # iyzico integration
│   │   └── common/            # TimeStampedModel, AuditLog, SiteConfig, FeatureFlag
│   ├── .venv/                 # Python virtual environment
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # Next.js app
│   ├── src/
│   │   ├── app/[locale]/      # Pages (i18n routing)
│   │   │   ├── patient/       # 27 patient routes
│   │   │   ├── doctor/        # 31 doctor/admin routes
│   │   │   ├── caregiver/     # Caregiver panel
│   │   │   ├── auth/          # Login, register
│   │   │   ├── blog/          # Blog listing + detail
│   │   │   ├── news/          # News listing + detail
│   │   │   ├── education/     # Education hub
│   │   │   ├── doctors/       # Doctor directory
│   │   │   ├── store/         # Product store
│   │   │   └── page.tsx       # Homepage
│   │   ├── components/        # React components
│   │   │   ├── layout/        # Header, Footer
│   │   │   ├── common/        # Toast, Skeleton, LoadingSpinner, Breadcrumb
│   │   │   ├── patient/       # MigraineChart, SeizureChart, WeatherWidget
│   │   │   ├── dementia/      # 15+ cognitive game components
│   │   │   ├── chat/          # ChatBubble, ChatInput, MessageList
│   │   │   └── providers/     # QueryProvider
│   │   ├── hooks/             # 13 React Query hooks
│   │   ├── lib/
│   │   │   ├── api.ts         # Axios instance + interceptors
│   │   │   ├── server-api.ts  # SSR/ISR fetch helpers
│   │   │   └── types/         # TypeScript types (user, patient, doctor, content, chat, store)
│   │   ├── context/           # AuthContext, CartContext
│   │   ├── i18n/              # next-intl config (routing, request, navigation)
│   │   └── middleware.ts      # Auth + role-based route protection
│   ├── messages/
│   │   ├── tr.json            # Turkish translations
│   │   └── en.json            # English translations
│   ├── package.json
│   └── next.config.ts
├── nginx/                     # Nginx configs (init, prod)
├── scripts/                   # Server setup, backup, health check scripts
├── docker-compose.yml         # Local development (db, redis, backend, frontend, celery)
├── docker-compose.prod.yml    # Production deployment
└── deploy.sh                  # Deployment commands: init, update, ssl, restart
```

## Development Setup

### Prerequisites
- Python 3.12+, Node.js 18+, PostgreSQL 16, Redis 7

### Run Locally (without Docker)

```bash
# Backend
cd backend && source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.development python3 manage.py runserver 8000

# Frontend
cd frontend && npm run dev
```

### Run with Docker

```bash
docker compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Admin Access
- Django Admin: http://localhost:8000/yonetim-7x9k/
- Credentials: admin@norosera.com / Admin1234!

## Architecture Patterns

### Backend

#### Base Model
All models extend `TimeStampedModel` from `apps.common.models`:
```python
class TimeStampedModel(models.Model):
    id = UUIDField(primary_key=True, default=uuid4)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### User Model & Roles
`CustomUser` uses email as `USERNAME_FIELD`. Roles: `patient`, `doctor`, `admin`, `caregiver`.
Related profiles: `PatientProfile`, `DoctorProfile`, `CaregiverProfile`, `DoctorAuthor`.

#### Permission Classes
Defined in `apps/accounts/permissions.py`:
- `IsPatient`, `IsDoctor`, `IsAdminUser`, `IsCaregiver`, `IsPatientOrCaregiver`
- All have `is_superuser` bypass

#### Bilingual Fields
All user-facing text uses `_tr`/`_en` suffixed fields:
```python
name_tr = CharField(max_length=100)
name_en = CharField(max_length=100)
```
Resolved via `Accept-Language` header in serializers.

#### URL Pattern
```python
# config/urls.py
path('api/v1/migraine/', include('apps.migraine.urls'))
path('api/v1/epilepsy/', include('apps.epilepsy.urls'))
path('api/v1/dementia/', include('apps.dementia.urls'))
# etc.
```

#### Disease Modules
Each disease has its own Django app with dedicated models:
- **Migraine:** `MigraineAttack` (intensity 1-10, pain_location, aura, symptoms), `MigraineTrigger`
- **Epilepsy:** `SeizureEvent` (seizure_type, duration_seconds, loss_of_consciousness), `EpilepsyTrigger`
- **Dementia:** `CognitiveExercise`, `ExerciseSession`, `DailyAssessment`, `CaregiverNote`, `CognitiveScore`, `CognitiveScreening`

#### Authentication
JWT via `djangorestframework-simplejwt`:
- Access token: 30 minutes
- Refresh token: 7 days
- Rotate on refresh, blacklist after rotation

#### API Throttling
- Anonymous: 10/min burst, 100/hour sustained
- Authenticated: 30/min burst, 500/hour sustained
- Auth endpoint: 5/min
- AI agent: 10/hour

#### Celery Beat Schedule
```
cleanup-old-notifications        daily 03:00
send-medication-reminders        every 15 min
update-weather-cache             every 3 hours
daily-streak-check               daily 00:30
auto-generate-weekly-content     Monday 09:00
cleanup-old-agent-tasks          daily 03:00
send-weekly-content-report       Friday 17:00
publish-scheduled-social-posts   every 5 min
refresh-social-tokens            daily 04:00
```

#### KVKK Compliance
- `AuditLogMiddleware` logs all health data access (tracking, migraine, tasks, doctor endpoints)
- `ConsentRecord` tracks user consents by type and version
- `ReportShareRecord` audits report sharing with IP and consent info

### Frontend

#### i18n (Internationalization)
- Locales: `tr` (default), `en`
- Route pattern: `/tr/patient/dashboard`, `/en/patient/dashboard`
- Translations: `messages/tr.json`, `messages/en.json`
- Library: `next-intl 4.7`

#### Auth & Middleware
- Tokens stored in cookies (`access_token`, `refresh_token`, `user_role`)
- Auto token refresh on 401 via Axios interceptor
- Middleware protects routes by role:
  - `/patient/*` -> patient, doctor, admin
  - `/doctor/*` -> doctor, admin
  - `/doctor/site-settings` -> admin only
  - `/caregiver/*` -> caregiver, admin

#### State Management
- **Server state:** React Query (`@tanstack/react-query`) with 60s stale time
- **Auth state:** AuthContext (React Context)
- **Cart state:** CartContext (React Context)
- **13 custom hooks:** `usePatientData`, `useDoctorData`, `useAuthorData`, `useCaregiverData`, `useChatData`, `useMarketingData`, `useSocialData`, `useSiteData`, `useSiteAdmin`, `useEditorData`, `useStoreData`, `useNotifications`

#### API Client
```typescript
// src/lib/api.ts - Axios instance
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
});
// Request interceptor: adds Bearer token + Accept-Language
// Response interceptor: auto-refresh on 401, toast errors
```

#### Component Patterns
- Feature-based organization (`components/patient/`, `components/dementia/`, `components/chat/`)
- Reusable UI in `components/common/`
- Layout in `components/layout/` (Header, Footer)
- Dementia module has 15+ interactive cognitive game components

#### Styling
- Tailwind CSS 4 with custom CSS variables
- Primary: Teal (#0d9488 family) - medical theme
- Secondary: Indigo (#6366f1 family)
- Font: Inter
- Custom classes: `.card-medical`, `.btn-primary`, `.text-gradient`

#### Types
All in `src/lib/types/`:
- `user.ts` - UserRole, User, AuthTokens, LoginResponse, RegisterData
- `patient.ts` - DiseaseModule, TaskTemplate, SymptomEntry, Medication, MigraineAttack, SeizureEvent
- `doctor.ts` - DoctorPatient, DashboardStats, DoctorNote, AlertFlag, TimelineEntry
- `content.ts` - Article, EducationItem, Notification, ContentCategory
- `chat.ts` - ChatSession, ChatMessage, Conversation, DirectMessage
- `store.ts` - Product, Order, License, CartItem

## API Endpoints

```
POST   /api/v1/auth/register/           Registration
POST   /api/v1/auth/login/              Login (returns JWT)
POST   /api/v1/auth/token/refresh/      Token refresh
GET    /api/v1/users/me/                Current user profile
GET    /api/v1/health/                  Health check

GET    /api/v1/modules/                 Disease modules list
POST   /api/v1/modules/enroll/          Enroll in module

GET    /api/v1/tracking/symptoms/       Symptom entries
GET    /api/v1/tracking/medications/    Medications
GET    /api/v1/tracking/reminders/      Reminders

GET    /api/v1/migraine/attacks/        Migraine attacks
GET    /api/v1/migraine/triggers/       Migraine triggers
GET    /api/v1/epilepsy/seizures/       Seizure events
GET    /api/v1/dementia/exercises/      Cognitive exercises
GET    /api/v1/dementia/assessments/    Daily assessments
GET    /api/v1/dementia/screenings/     Cognitive screenings

GET    /api/v1/content/articles/        Blog articles
GET    /api/v1/content/education/       Education items
GET    /api/v1/content/news/            News articles

GET    /api/v1/doctor/patients/         Doctor's patient list
GET    /api/v1/doctor/dashboard/        Dashboard statistics

GET    /api/v1/notifications/           User notifications
GET    /api/v1/gamification/badges/     Badges & streaks
GET    /api/v1/chat/sessions/           AI chat sessions

GET    /api/v1/site/config/             Site configuration
GET    /api/v1/site/features/           Feature flags

GET    /api/schema/                     OpenAPI schema
GET    /api/docs/                       Swagger UI
```

## AI Agent System

- 15 agents for content generation, review, publishing
- Primary LLM: Groq Llama 3.3 70B, Fallback: Google Gemini
- Feature flags via `SiteConfig` (14 flags, all enabled except devops)
- Key pipelines: `full_content_v5`, `publish_article`, `news_pipeline`, `marketing_weekly`
- Auto-content: 12 topics configured in SiteConfig, runs weekly on Monday 09:00
- Agent execution tracked in `AgentTask` model (tokens, cost, duration, errors)

## Deployment

### Production (VPS)
- Hetzner CX23, IP: 178.104.30.193
- Project path: `/opt/norosera`
- Domain: norosera.com with SSL via Let's Encrypt

### Deploy Commands
```bash
# First time
bash deploy.sh init

# Update (rebuild + migrate)
bash deploy.sh update

# SSL setup
bash deploy.sh ssl

# Service management
bash deploy.sh restart
bash deploy.sh logs [service]
bash deploy.sh status
```

### Docker Services (Production)
Backend (Gunicorn), Frontend (Next.js standalone), PostgreSQL, Redis, Celery Worker, Celery Beat, Nginx (reverse proxy + SSL), Certbot

## Common Gotchas

1. **`python` not found:** Use `python3` or activate venv first (`source backend/.venv/bin/activate`)
2. **Bash `!` in passwords:** Causes JSON parse errors in curl. Use Python `urllib` instead
3. **Router conflicts:** DiseaseModuleViewSet empty prefix catches slug-like paths. Use separate routers
4. **SimpleLazyObject:** Don't use `type(user).objects`. Use `get_user_model().objects`
5. **PDF generation:** Use `reportlab` (not fpdf2) for Turkish character support. Avoid Unicode bullets (use "-")
6. **Settings module:** Always set `DJANGO_SETTINGS_MODULE=config.settings.development` for local
7. **New app registration:** Add to `LOCAL_APPS` in `config/settings/base.py`
8. **Store/Payments routes:** Only available in DEBUG mode (not production)
9. **Token refresh loop:** Check both `access_token` and `token` cookie names in middleware
10. **Bilingual fields:** Always provide both `_tr` and `_en` variants; serializers resolve by Accept-Language header
11. **Turkish characters (MANDATORY):** When creating Turkish content (`_tr` fields, seed data, translations, any user-facing Turkish text), ALWAYS use proper Turkish Unicode characters: ğ, ş, ç, ı, ö, ü, İ, Ğ, Ş, Ç, Ö, Ü. NEVER use ASCII equivalents (g instead of ğ, s instead of ş, c instead of ç, i instead of ı, o instead of ö, u instead of ü). This applies to seed/management commands, translation JSON files, and any hardcoded Turkish strings.

## Testing

```bash
# Backend tests
cd backend && source .venv/bin/activate
pytest

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

## Key Config Files

| File | Purpose |
|------|---------|
| `backend/config/settings/base.py` | Django shared settings, INSTALLED_APPS |
| `backend/config/settings/development.py` | Local dev overrides |
| `backend/config/settings/production.py` | Production security, HSTS, Sentry |
| `backend/config/urls.py` | API URL routing |
| `backend/config/celery.py` | Celery + Beat schedule |
| `frontend/next.config.ts` | Next.js config, security headers |
| `frontend/src/middleware.ts` | Auth + role-based route protection |
| `frontend/src/lib/api.ts` | Axios instance + interceptors |
| `frontend/messages/tr.json` | Turkish translations |
| `frontend/messages/en.json` | English translations |
| `docker-compose.yml` | Local dev services |
| `docker-compose.prod.yml` | Production services |
| `deploy.sh` | Deployment automation |
| `.env.example` | Environment variable template |
