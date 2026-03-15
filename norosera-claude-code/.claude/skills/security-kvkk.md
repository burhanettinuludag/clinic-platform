# Skill: KVKK & Güvenlik — Norosera

## Trigger
kvkk, güvenlik, security, hasta verisi, patient data, gizlilik, privacy, şifreleme, encryption, audit, gdpr

## Rules

### KVKK Özel Nitelikli Veri Kategorileri
Aşağıdaki veriler KVKK kapsamında "özel nitelikli kişisel veri"dir:
- Sağlık verileri (tanı, tedavi, ilaç, lab sonuçları)
- TC Kimlik No
- Ad, Soyad + sağlık verisi kombinasyonu
- Biyometrik veri
- Genetik veri

### Model Encryption
Hasta verileri için field-level encryption:
```python
from django_encrypted_fields import EncryptedCharField, EncryptedTextField

class Patient(models.Model):
    tc_kimlik = EncryptedCharField(max_length=11)
    ad = EncryptedCharField(max_length=100)
    soyad = EncryptedCharField(max_length=100)
    telefon = EncryptedCharField(max_length=15)
    saglik_ozeti = EncryptedTextField(blank=True)
    # Non-sensitive fields can be plain
    created_at = models.DateTimeField(auto_now_add=True)
```

### Audit Logging
Every patient data access MUST be logged:
```python
# apps/legal/mixins.py
class KVKKAuditMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        KVKKAuditLog.objects.create(
            user=request.user,
            action="VIEW",
            model_name=instance.__class__.__name__,
            object_id=instance.pk,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return super().retrieve(request, *args, **kwargs)
```

### API Security Checklist
Every patient endpoint MUST have:
- [ ] `IsAuthenticated` permission
- [ ] Role-based permission (IsDoctor, IsAdmin, IsNurse)
- [ ] Rate limiting (`UserRateThrottle`)
- [ ] KVKKAuditMixin applied
- [ ] No patient PII in URL parameters
- [ ] Response pagination (max 50 records)

### Logging Rules
```python
# NEVER do this:
logger.info(f"Patient {patient.ad} {patient.soyad} updated")  # ❌ PII in logs

# DO this:
logger.info(f"Patient ID:{patient.pk} updated by user:{request.user.pk}")  # ✅
```

### Data Retention
- Active patient data: Retained while patient is active
- Inactive patient data: Auto-anonymize after 2 years via Celery periodic task
- Audit logs: Retained for 5 years (legal requirement)
- Session logs: Retained for 1 year

### Frontend Security
- NEVER store patient data in localStorage or sessionStorage
- Use httpOnly cookies for auth tokens
- Sanitize all user inputs with DOMPurify
- CSP headers configured in Next.js middleware
