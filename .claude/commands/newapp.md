# /newapp — Create New Django App

Create a new Django app following Norosera standards.

## Usage
`/newapp <app_name>`

## Steps

1. Create the app:
```bash
cd backend && source .venv/bin/activate
python3 manage.py startapp $ARGUMENTS
mv $ARGUMENTS apps/$ARGUMENTS
```

2. Generate standard file structure:
```
apps/<app_name>/
├── __init__.py
├── admin.py          # ModelAdmin with list_display, search, filters
├── apps.py           # AppConfig with name='apps.<app_name>'
├── models.py         # Extend TimeStampedModel, bilingual fields
├── serializers.py    # DRF serializers with read-only id/timestamps
├── views.py          # ViewSets with permission_classes
├── urls.py           # Router registration
├── permissions.py    # Custom permissions if needed
├── filters.py        # DRF filters
├── signals.py        # Signal handlers
├── tasks.py          # Celery tasks
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_serializers.py
└── migrations/
    └── __init__.py
```

3. Register in `config/settings/base.py`:
```python
LOCAL_APPS = [
    ...
    'apps.<app_name>',
]
```

4. Add URL routing in `config/urls.py`:
```python
path('api/v1/<app_name>/', include('apps.<app_name>.urls')),
```

5. Create initial migration:
```bash
cd backend && source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.development python3 manage.py makemigrations <app_name>
```

All models must extend `TimeStampedModel` from `apps.common.models`.
All user-facing fields must have `_tr` and `_en` variants.
