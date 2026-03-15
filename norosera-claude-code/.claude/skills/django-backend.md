# Skill: Django Backend — Norosera

## Trigger
django, model, view, serializer, migration, api endpoint, DRF, backend, veritabanı, database

## Rules

### Model Creation
Every new Django model MUST include:
```python
class Meta:
    verbose_name = "Türkçe İsim"
    verbose_name_plural = "Türkçe Çoğul İsim"
    ordering = ["-created_at"]

created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

After creating/modifying any model:
1. Run `python manage.py makemigrations`
2. Run `python manage.py migrate --check`
3. Verify migration file was created in `apps/<app>/migrations/`

### API View Pattern
Every DRF view MUST follow this pattern:
```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # ALWAYS specify
    throttle_classes = [UserRateThrottle]
    serializer_class = MySerializer
    queryset = MyModel.objects.all()

    def get_queryset(self):
        # Filter by user/clinic context
        return super().get_queryset().filter(clinic=self.request.user.clinic)
```

### Patient Data Views (KVKK)
Patient-related views require additional:
```python
from apps.legal.mixins import KVKKAuditMixin

class PatientViewSet(KVKKAuditMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDoctor | IsAdmin]
    # KVKKAuditMixin auto-logs all access
```

### Serializer Pattern
```python
class MySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
```

### URL Registration
New apps must register URLs in:
1. `backend/config/urls.py` → `path("api/v1/myapp/", include("apps.myapp.urls"))`
2. Create `apps/myapp/urls.py` with `DefaultRouter`

### Testing Pattern
```python
from rest_framework.test import APITestCase

class MyModelAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(...)
        self.client.force_authenticate(user=self.user)

    def test_list(self):
        response = self.client.get("/api/v1/myapp/")
        self.assertEqual(response.status_code, 200)

    def test_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/myapp/")
        self.assertEqual(response.status_code, 401)
```

### Celery Task Pattern
```python
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def my_async_task(self, param):
    try:
        # task logic
        pass
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc)
```
