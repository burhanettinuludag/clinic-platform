# /test — Run All Tests

Run backend and frontend tests in parallel. Report results.

## Steps

1. **Backend tests:**
```bash
cd backend && source .venv/bin/activate && DJANGO_SETTINGS_MODULE=config.settings.development pytest --verbosity=2
```

2. **Frontend type check:**
```bash
cd frontend && npx tsc --noEmit
```

3. **Frontend lint:**
```bash
cd frontend && npm run lint
```

4. Summarize results:
   - Total tests passed/failed
   - TypeScript errors (if any)
   - Lint warnings (if any)
   - Overall: READY TO COMMIT or NEEDS FIXES

Run backend and frontend checks in parallel for speed. If any check fails, report the specific errors and suggest fixes.
