# Skill: Email Şablonları — Norosera

## Trigger
email, e-posta, mail şablon, bildirim, randevu hatırlatma, hoşgeldin, takip, newsletter

## Email Şablon Kategorileri

### 1. Randevu Bildirimleri

#### Randevu onayı
```
Konu: Randevunuz Onaylandı — Norosera Nöroloji Kliniği

Sayın {hasta_adi},

{tarih} tarihli, saat {saat} randevunuz onaylanmıştır.

📍 Adres: Ankara Caddesi No 243/2, Bornova, İzmir
📞 İletişim: +90 532 382 90 31

Randevunuza gelirken yanınızda bulundurmanız gerekenler:
• Kimlik belgesi
• Varsa önceki tetkik sonuçları (MR, EEG, EMG, kan tahlilleri)
• Kullandığınız ilaç listesi
• Sevk belgesi (SGK hastası iseniz)

Randevunuzu iptal veya ertelemek için en az 24 saat öncesinden
+90 532 382 90 31 numarasını arayınız.

Sağlıklı günler dileriz,
Norosera Nöroloji Kliniği
Prof. Dr. Burhanettin Uludağ
```

#### Randevu hatırlatma (1 gün önce)
```
Konu: Yarınki Randevunuz — Norosera Nöroloji Kliniği

Sayın {hasta_adi},

Yarın {tarih} saat {saat} randevunuz bulunmaktadır.

📍 Ankara Caddesi No 243/2, Bornova, İzmir

{hizmet_turu == "EEG" ? "ÖNEMLİ: EEG çekimi için saçlarınızı 
önceki gece yıkayıp jöle/sprey kullanmayınız." : ""}

{hizmet_turu == "EMG" ? "ÖNEMLİ: EMG tetkiki için rahat kıyafet 
giyiniz. Test süresi yaklaşık 30-45 dakikadır." : ""}

Sağlıklı günler dileriz,
Norosera Nöroloji Kliniği
```

### 2. Takip Mailleri

#### Ziyaret sonrası takip (3 gün sonra)
```
Konu: Ziyaretiniz Hakkında — Norosera Nöroloji Kliniği

Sayın {hasta_adi},

{ziyaret_tarihi} tarihindeki muayeneniz hakkında
durumunuzu sormak istiyoruz.

Tedavinizle ilgili sorularınız varsa veya belirtilerinizde
değişiklik olduysa bizimle iletişime geçebilirsiniz.

📞 +90 532 382 90 31
📧 uludagburhan@yahoo.com

{kontrol_tarihi ? "Bir sonraki kontrol randevunuz: " + kontrol_tarihi : ""}

Sağlıklı günler dileriz,
Prof. Dr. Burhanettin Uludağ
Norosera Nöroloji Kliniği
```

### 3. Django Email Implementation
```python
# apps/notifications/services.py
from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_appointment_confirmation(appointment):
    context = {
        "hasta_adi": appointment.patient.ad,
        "tarih": appointment.date.strftime("%d.%m.%Y"),
        "saat": appointment.time.strftime("%H:%M"),
        "hizmet_turu": appointment.service.name,
    }
    html = render_to_string("emails/appointment_confirmed.html", context)
    send_mail(
        subject="Randevunuz Onaylandı — Norosera Nöroloji Kliniği",
        message="",  # plain text fallback
        from_email="bilgi@norosera.com",
        recipient_list=[appointment.patient.email],
        html_message=html,
    )
```

### 4. Celery Task ile Zamanlama
```python
# apps/notifications/tasks.py
@shared_task
def send_appointment_reminders():
    """Yarınki randevular için hatırlatma gönder"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        date=tomorrow,
        status="confirmed",
        reminder_sent=False,
    )
    for apt in appointments:
        send_appointment_reminder(apt)
        apt.reminder_sent = True
        apt.save(update_fields=["reminder_sent"])
```

### Email Kuralları
- KVKK: Email'de minimum hasta verisi — sadece ad ve randevu bilgisi
- Unsubscribe linki zorunlu (newsletter için)
- HTML + plain text her zaman birlikte
- SPF, DKIM, DMARC yapılandırılmış olmalı
- Test: Spam score kontrol et (mail-tester.com)
