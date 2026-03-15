# /newapp — Yeni Django App Oluştur

Norosera standartlarına uygun, tam donanımlı yeni bir Django app oluştur.

## Kullanım
```
/newapp <app_adı>
```

## Adımlar:

1. App'i oluştur:
```bash
cd backend && python manage.py startapp <app_adı>
mv <app_adı> apps/<app_adı>
```

2. Standart dosya yapısını kur:
```
apps/<app_adı>/
├── __init__.py
├── admin.py          # ModelAdmin with list_display, search_fields
├── apps.py           # AppConfig with verbose_name (Türkçe)
├── models.py         # Base model with created_at, updated_at
├── serializers.py    # DRF serializers
├── views.py          # ViewSet with permission_classes
├── urls.py           # DefaultRouter
├── tasks.py          # Celery task stubs
├── signals.py        # Signal handlers
├── permissions.py    # Custom permissions
├── filters.py        # DRF filters
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_serializers.py
├── factories.py      # Factory Boy
└── migrations/
    └── __init__.py
```

3. `config/settings/base.py` → `INSTALLED_APPS` listesine `apps.<app_adı>` ekle

4. `config/urls.py` → `urlpatterns` listesine `path("api/v1/<app_adı>/", include("apps.<app_adı>.urls"))` ekle

5. İlk migration'ı oluştur:
```bash
cd backend && python manage.py makemigrations <app_adı>
```

6. Özet raporla: oluşturulan dosyalar, kayıt edilen URL pattern, sonraki adımlar.
