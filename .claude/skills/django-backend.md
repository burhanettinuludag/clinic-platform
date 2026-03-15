# Django Backend Skill

## Triggers
model, view, serializer, migration, API, endpoint, Django, DRF, backend

## Rules

### Model Pattern
All models MUST extend `TimeStampedModel` from `apps.common.models`:
```python
from apps.common.models import TimeStampedModel

class MyModel(TimeStampedModel):
    name_tr = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Model Adi"
        verbose_name_plural = "Model Adlari"
        ordering = ['-created_at']
```
This provides: `id` (UUID), `created_at`, `updated_at` automatically.

### Bilingual Fields
ALL user-facing text fields must have `_tr` and `_en` variants:
```python
title_tr = models.CharField(max_length=200)
title_en = models.CharField(max_length=200)
```
Serializers resolve the correct language via `Accept-Language` header.

### Permission Classes
ALWAYS specify `permission_classes` on views. Available in `apps.accounts.permissions`:
- `IsPatient` — patient role
- `IsDoctor` — doctor role
- `IsAdminUser` — admin role
- `IsCaregiver` — caregiver role
- `IsPatientOrCaregiver` — combined
All have `is_superuser` bypass.

```python
from apps.accounts.permissions import IsDoctor

class MyView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]
    throttle_classes = [UserRateThrottle]
```

### URL Registration
1. Create `urls.py` in app with router
2. Add to `config/urls.py`:
```python
path('api/v1/myapp/', include('apps.myapp.urls'))
```

### Settings
- Settings module: `config.settings.base` (shared), `config.settings.development` (local), `config.settings.production` (VPS)
- New apps go in `LOCAL_APPS` list in `config/settings/base.py`
- Always set `DJANGO_SETTINGS_MODULE=config.settings.development` for local dev

### Django Apps (actual structure)
```
apps/
├── accounts/       # CustomUser, auth, profiles, permissions
├── patients/       # DiseaseModule, PatientModule
├── tracking/       # SymptomEntry, Medication, Reminders
├── migraine/       # MigraineAttack, triggers
├── epilepsy/       # SeizureEvent, triggers
├── dementia/       # CognitiveExercise, DailyAssessment, CaregiverNote
├── content/        # Article, EducationItem, NewsArticle, AI review
├── doctor_panel/   # Doctor views, analytics, editor
├── common/         # TimeStampedModel, AuditLog, SiteConfig, FeatureFlag, AgentTask
├── wellness/       # Wellness tracking
├── gamification/   # Badge, UserStreak, points
├── notifications/  # Notification, NotificationPreference
├── chat/           # AI chatbot, doctor-patient messaging
├── social/         # SocialAccount, SocialCampaign
├── store/          # Product, Order, License
└── payments/       # iyzico integration
```

### Migration Checklist
1. `python3 manage.py makemigrations appname`
2. Review generated migration file
3. `python3 manage.py migrate`
4. `python3 manage.py check`

### Common Gotchas
- Use `python3` not `python` (or activate venv first)
- `SimpleLazyObject`: use `get_user_model().objects` not `type(user).objects`
- Router conflicts: DiseaseModuleViewSet empty prefix catches slug-like paths
- Use `reportlab` for PDF (not fpdf2) for Turkish character support
