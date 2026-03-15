# /security — Security Audit

Comprehensive security scan covering dependencies, code, and KVKK compliance.

## Steps

### 1. Dependency Audit
```bash
cd backend && source .venv/bin/activate
pip-audit 2>/dev/null || echo "pip-audit not installed"

cd frontend
npm audit --production
```

### 2. Code Scan
Search for common vulnerabilities in changed and critical files:

- **Hardcoded secrets:** API keys, passwords, tokens in source code
- **SQL injection:** Raw SQL queries, string formatting in `.filter()` / `.extra()`
- **XSS:** Unescaped `|safe` in templates, `dangerouslySetInnerHTML` without sanitization
- **SSRF:** User-controlled URLs in HTTP requests
- **Debug mode:** `DEBUG=True` in production settings
- **Insecure deserialization:** `pickle.loads()`, `yaml.load()` without SafeLoader

### 3. KVKK Compliance
- Patient model fields encrypted at rest
- `AuditLogMiddleware` covers all health data endpoints
- Permission classes on all patient-facing views
- No PII logged (check log statements for patient names, TC numbers)
- `ConsentRecord` model for user consents
- Data retention policy enforced

### 4. Django Security Check
```bash
cd backend && source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.production python3 manage.py check --deploy --tag security
```

## Report Format

Report by severity:
- **CRITICAL** — Fix immediately (exposed secrets, SQL injection)
- **HIGH** — Fix this sprint (missing permissions, KVKK gaps)
- **MEDIUM** — Plan to fix (dependency updates, code improvements)
- **LOW** — Backlog (style, best practices)

$ARGUMENTS
