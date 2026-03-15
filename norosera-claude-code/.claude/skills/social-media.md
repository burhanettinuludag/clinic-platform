# Skill: Sosyal Medya İçerik — Norosera

## Trigger
sosyal medya, instagram, linkedin, post, paylaşım, social media, içerik takvimi

## Rules

### Platform Formats

#### Instagram
- Kare görsel (1080x1080) veya dikey (1080x1350)
- Caption: max 2200 karakter, ilk 125 karakter önemli
- 20-30 hashtag (Türkçe + İngilizce karışık)
- Medikal doğruluk ZORUNLU — uydurma bilgi YASAK
- Emoji kullanımı: ölçülü, profesyonel

#### LinkedIn
- Profesyonel ton, akademik dil
- 1300-1500 karakter ideal
- 3-5 hashtag yeterli
- Kaynak/referans belirtilmeli

### İçerik Kategorileri
1. **Eğitici:** Nörolojik hastalıklar hakkında bilgilendirme
2. **Klinik tanıtım:** Hizmetler, cihazlar, teknikler
3. **Bilimsel:** Yeni araştırmalar, kongre notları
4. **Sağlık ipuçları:** Genel nöroloji tavsiyeleri

### Template
```python
# apps/social/models.py
class SocialPost(models.Model):
    PLATFORM_CHOICES = [
        ("instagram", "Instagram"),
        ("linkedin", "LinkedIn"),
    ]
    STATUS_CHOICES = [
        ("draft", "Taslak"),
        ("approved", "Onaylandı"),
        ("published", "Yayınlandı"),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content = models.TextField()
    hashtags = models.TextField(blank=True)
    image_prompt = models.TextField(blank=True, help_text="AI görsel üretimi için prompt")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    published_at = models.DateTimeField(null=True, blank=True)
```

### Celery Scheduling
```python
# Celery Beat: Her Pazartesi 09:00 ve Perşembe 14:00 otomatik post
CELERY_BEAT_SCHEDULE = {
    "social-monday-post": {
        "task": "apps.social.tasks.generate_and_schedule_post",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
        "args": ("instagram",),
    },
    "social-thursday-post": {
        "task": "apps.social.tasks.generate_and_schedule_post",
        "schedule": crontab(hour=14, minute=0, day_of_week=4),
        "args": ("linkedin",),
    },
}
```

### Disclaimer
Her medikal içerik postunun altında:
```
⚠️ Bu bilgi genel sağlık bilgilendirmesi amaçlıdır.
Tanı ve tedavi için mutlaka nöroloji uzmanına başvurunuz.
```
