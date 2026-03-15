# /review — Code Review

Review all changes since the last commit for security, quality, and compliance.

## Steps

1. Get changed files:
```bash
git diff --name-only HEAD
git diff --cached --name-only
```

2. For each changed file, check:

### Security
- Hardcoded secrets (API keys, passwords, tokens)
- SQL injection patterns (raw SQL, string formatting in queries)
- XSS vulnerabilities (unescaped user input in templates)
- Missing CSRF protection

### KVKK Compliance
- Patient data exposed in logs or comments
- Missing permission_classes on patient endpoints
- PII in URL paths
- Missing audit logging for health data access

### Code Quality
- `any` type usage in TypeScript
- Missing error handling
- N+1 query patterns (missing select_related/prefetch_related)
- Fat views (business logic should be in services/models)

### Permissions
- All views MUST have `permission_classes`
- Patient data endpoints need role-based access

### i18n
- User-facing strings must be in Turkish
- Both `_tr` and `_en` field variants provided

### Tests
- New endpoints should have corresponding tests

3. Report findings with severity:
   - **CRITICAL** — Must fix before commit (secrets, security holes)
   - **WARNING** — Should fix (missing tests, type issues)
   - **INFO** — Nice to have (code style, optimization)

$ARGUMENTS
