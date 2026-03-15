# /security — Güvenlik Taraması

Norosera projesinin kapsamlı güvenlik denetimini yap.

## Adımlar:

1. Spawn 3 paralel sub-agent:

### Sub-agent 1: Dependency Audit
```bash
cd backend && pip-audit 2>/dev/null || pip install pip-audit && pip-audit
cd frontend && npm audit --production
```

### Sub-agent 2: Code Scan
Tüm Python ve TypeScript dosyalarını tara:
- Hardcoded credentials (API key, password, secret)
- SQL injection riski (raw SQL queries without parameterization)
- XSS riski (dangerouslySetInnerHTML, unsanitized user input)
- SSRF riski (user-controlled URLs in fetch/requests)
- Insecure deserialization (pickle.loads, yaml.load without Loader)
- Debug mode production'da açık mı

### Sub-agent 3: KVKK Compliance
- Hasta verisi encrypt edilmiş mi
- Audit log tüm patient endpoint'lerde var mı
- Permission classes doğru mu
- Data retention policy implement edilmiş mi
- Consent form endpoint'i var mı

2. Django security check:
```bash
cd backend && python manage.py check --deploy --tag security
```

3. Sonuçları birleştir:
```
🔴 CRITICAL (Hemen düzelt):
- ...

🟡 HIGH (Bu sprint içinde düzelt):
- ...

🟢 LOW (Backlog):
- ...

📊 Dependency durumu:
- Backend: X vulnerable, Y outdated
- Frontend: X vulnerable, Y outdated
```

4. Her CRITICAL bulgu için fix önerisi sun.
