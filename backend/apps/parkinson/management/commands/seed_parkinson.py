"""Parkinson modülü için ön tanımlı tetikleyiciler ve ilaç bilgileri."""
from django.core.management.base import BaseCommand
from apps.parkinson.models import ParkinsonTrigger


TRIGGERS = [
    # İlaç ilişkili
    ('İlaç etkisi geçmesi (wearing-off)', 'Medication wearing off', 'medication'),
    ('İlaç dozu kaçırma', 'Missed medication dose', 'medication'),
    ('İlaç değişikliği', 'Medication change', 'medication'),
    # Stres / Duygusal
    ('Stres / Kaygı', 'Stress / Anxiety', 'stress'),
    ('Üzüntü / Depresyon', 'Sadness / Depression', 'stress'),
    ('Heyecan / Aşırı duygusal durum', 'Excitement / Emotional state', 'stress'),
    # Fiziksel
    ('Yorgunluk', 'Fatigue', 'physical'),
    ('Aşırı fiziksel aktivite', 'Excessive physical activity', 'physical'),
    ('Hareketsizlik', 'Inactivity / Sedentary', 'physical'),
    ('Düşme', 'Fall', 'physical'),
    # Çevresel
    ('Soğuk hava', 'Cold weather', 'environmental'),
    ('Sıcak hava', 'Hot weather', 'environmental'),
    ('Kalabalık ortam', 'Crowded environment', 'environmental'),
    ('Gürültü', 'Noise', 'environmental'),
    # Beslenme
    ('Protein ağırlıklı yemek', 'High protein meal', 'dietary'),
    ('Yetersiz sıvı alımı', 'Dehydration', 'dietary'),
    ('Kafein', 'Caffeine', 'dietary'),
    ('Alkol', 'Alcohol', 'dietary'),
    # Uyku
    ('Yetersiz uyku', 'Poor sleep', 'sleep'),
    ('Uykusuzluk', 'Insomnia', 'sleep'),
    ('Gece uyanmaları', 'Nighttime awakenings', 'sleep'),
    # Diğer
    ('Enfeksiyon / Hastalık', 'Infection / Illness', 'other'),
    ('Konstipasyon', 'Constipation', 'other'),
    ('Ağrı', 'Pain', 'other'),
]


class Command(BaseCommand):
    help = 'Parkinson modülü için ön tanımlı tetikleyicileri oluştur'

    def handle(self, *args, **options):
        created = 0
        for name_tr, name_en, category in TRIGGERS:
            _, is_new = ParkinsonTrigger.objects.get_or_create(
                name_en=name_en,
                defaults={
                    'name_tr': name_tr,
                    'category': category,
                    'is_predefined': True,
                },
            )
            if is_new:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'{created} yeni tetikleyici oluşturuldu (toplam: {ParkinsonTrigger.objects.count()})'
        ))
