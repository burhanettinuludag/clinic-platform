# /doc — Auto-Generate Documentation

Generate API and model documentation from the codebase.

## Steps

### 1. API Endpoints
Scan `config/urls.py` and all app `urls.py` files to extract:
- HTTP method + URL pattern
- View class/function name
- Permission classes
- Throttle classes
- Brief description

### 2. Model Structure
For each Django app in `apps/`, extract:
- Model name and fields
- Field types and constraints
- Relationships (FK, M2M)
- Meta options

### 3. Generate Documentation
Output a structured summary covering:

**API Reference:**
```
METHOD  URL                          Permission        Description
GET     /api/v1/auth/login/          AllowAny          User login
GET     /api/v1/doctor/patients/     IsDoctor          Doctor's patients
...
```

**Model Reference:**
```
App: migraine
  MigraineAttack
    - intensity (IntegerField, 1-10)
    - pain_location (CharField)
    - aura (BooleanField)
    ...
```

Do NOT create markdown files unless explicitly asked. Output the documentation directly in the response.

$ARGUMENTS
