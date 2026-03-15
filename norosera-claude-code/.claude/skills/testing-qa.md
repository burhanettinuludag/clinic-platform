# Skill: Test & QA — Norosera

## Trigger
test, test yaz, coverage, QA, kalite, bug, hata, doğrulama, validation

## Rules

### Test Structure
```
backend/
├── apps/
│   ├── patients/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   ├── test_serializers.py
│   │   │   └── test_tasks.py     # Celery task tests
│   │   └── factories.py          # Factory Boy factories
frontend/
├── src/
│   ├── __tests__/
│   │   ├── components/
│   │   └── pages/
│   └── lib/__tests__/
```

### Backend Test Commands
```bash
# All tests
cd backend && python manage.py test

# Specific app
python manage.py test apps.patients

# With coverage
coverage run manage.py test && coverage report -m

# Specific test class
python manage.py test apps.patients.tests.test_views.PatientViewSetTest
```

### Frontend Test Commands
```bash
cd frontend
npm run test                    # All tests
npm run test -- --watch         # Watch mode
npm run test -- --coverage      # With coverage
npx tsc --noEmit                # Type check (always run!)
```

### Factory Pattern (Backend)
```python
# apps/patients/factories.py
import factory
from apps.patients.models import Patient

class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient

    ad = factory.Faker("first_name", locale="tr_TR")
    soyad = factory.Faker("last_name", locale="tr_TR")
    tc_kimlik = factory.LazyFunction(lambda: "".join([str(random.randint(0,9)) for _ in range(11)]))
    telefon = factory.Sequence(lambda n: f"+9053200000{n:02d}")
```

### Required Test Coverage
- Models: field validation, constraints, methods
- Views: CRUD operations, permissions, unauthorized access, pagination
- Serializers: validation, field presence, read-only fields
- Celery tasks: success path, retry on failure, error handling
- Frontend components: render, user interaction, error states

### Pre-commit Test Run
Before any commit, always run:
```bash
cd backend && python manage.py check && python manage.py test --parallel
cd frontend && npx tsc --noEmit && npm run lint
```
