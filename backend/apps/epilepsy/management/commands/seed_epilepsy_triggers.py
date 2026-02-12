from django.core.management.base import BaseCommand
from apps.epilepsy.models import EpilepsyTrigger


class Command(BaseCommand):
    help = 'Seed predefined epilepsy triggers'

    def handle(self, *args, **options):
        triggers_data = [
            # Sleep
            ('Uykusuzluk', 'Sleep deprivation', 'sleep'),
            ('Duzensiz uyku', 'Irregular sleep', 'sleep'),
            # Stress
            ('Stres', 'Stress', 'stress'),
            ('Anksiyete', 'Anxiety', 'stress'),
            # Substance
            ('Alkol', 'Alcohol', 'substance'),
            ('Ilac atlama', 'Missed medication', 'substance'),
            ('Kafein', 'Caffeine', 'substance'),
            # Sensory
            ('Yanip sonen isiklar', 'Flashing lights', 'sensory'),
            ('Parlak isik', 'Bright light', 'sensory'),
            # Physical
            ('Ates', 'Fever', 'physical'),
            ('Hiperventilasyon', 'Hyperventilation', 'physical'),
            ('Agir egzersiz', 'Heavy exercise', 'physical'),
            # Hormonal
            ('Adet donemi', 'Menstrual period', 'hormonal'),
            # Other
            ('Sicaklik degisimi', 'Temperature change', 'other'),
            ('Yogun duygular', 'Intense emotions', 'other'),
        ]

        created_count = 0
        for name_tr, name_en, category in triggers_data:
            _, c = EpilepsyTrigger.objects.get_or_create(
                name_en=name_en,
                is_predefined=True,
                defaults={
                    'name_tr': name_tr,
                    'category': category,
                },
            )
            if c:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} epilepsy triggers (total: {len(triggers_data)})')
        )
