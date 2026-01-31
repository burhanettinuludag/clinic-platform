from django.core.management.base import BaseCommand
from apps.patients.models import DiseaseModule, TaskTemplate
from apps.tracking.models import SymptomDefinition
from apps.migraine.models import MigraineTrigger


class Command(BaseCommand):
    help = 'Seed migraine module data: triggers, symptom definitions, task templates'

    def handle(self, *args, **options):
        # 1. Disease Module
        module, created = DiseaseModule.objects.get_or_create(
            slug='migraine',
            defaults={
                'disease_type': 'migraine',
                'name_tr': 'Migren',
                'name_en': 'Migraine',
                'description_tr': 'Migren atakları, tetikleyiciler ve semptomların takibi.',
                'description_en': 'Track migraine attacks, triggers and symptoms.',
                'icon': 'brain',
                'is_active': True,
                'order': 1,
            },
        )
        self.stdout.write(f"{'Created' if created else 'Found'} module: {module}")

        # 2. Predefined Triggers
        triggers_data = [
            # Dietary
            ('Stres', 'Stress', 'emotional'),
            ('Uykusuzluk', 'Sleep deprivation', 'sleep'),
            ('Fazla uyku', 'Oversleeping', 'sleep'),
            ('Düzensiz uyku', 'Irregular sleep', 'sleep'),
            ('Çikolata', 'Chocolate', 'dietary'),
            ('Peynir', 'Cheese', 'dietary'),
            ('Alkol', 'Alcohol', 'dietary'),
            ('Kafein', 'Caffeine', 'dietary'),
            ('Öğün atlama', 'Skipping meals', 'dietary'),
            ('Dehidrasyon', 'Dehydration', 'dietary'),
            ('İşlenmiş gıda', 'Processed food', 'dietary'),
            # Environmental
            ('Parlak ışık', 'Bright light', 'environmental'),
            ('Gürültü', 'Loud noise', 'environmental'),
            ('Keskin koku', 'Strong smell', 'environmental'),
            ('Hava değişimi', 'Weather change', 'environmental'),
            ('Yüksek nem', 'High humidity', 'environmental'),
            # Hormonal
            ('Adet dönemi', 'Menstrual period', 'hormonal'),
            ('Doğum kontrol hapı', 'Birth control pill', 'hormonal'),
            # Emotional
            ('Anksiyete', 'Anxiety', 'emotional'),
            ('Depresyon', 'Depression', 'emotional'),
            ('Aşırı heyecan', 'Excitement', 'emotional'),
            # Physical
            ('Ağır egzersiz', 'Heavy exercise', 'physical'),
            ('Uzun ekran süresi', 'Long screen time', 'physical'),
            ('Boyun gerginliği', 'Neck tension', 'physical'),
            ('Seyahat', 'Travel', 'physical'),
        ]

        created_count = 0
        for name_tr, name_en, category in triggers_data:
            _, c = MigraineTrigger.objects.get_or_create(
                name_en=name_en,
                is_predefined=True,
                defaults={
                    'name_tr': name_tr,
                    'category': category,
                },
            )
            if c:
                created_count += 1
        self.stdout.write(f"Created {created_count} triggers (total: {len(triggers_data)})")

        # 3. Symptom Definitions
        symptoms_data = [
            ('headache_intensity', 'Baş ağrısı şiddeti', 'Headache intensity', 'slider',
             {'min': 0, 'max': 10, 'step': 1}),
            ('nausea', 'Bulantı', 'Nausea', 'boolean', {}),
            ('vomiting', 'Kusma', 'Vomiting', 'boolean', {}),
            ('photophobia', 'Işığa duyarlılık', 'Light sensitivity', 'boolean', {}),
            ('phonophobia', 'Sese duyarlılık', 'Sound sensitivity', 'boolean', {}),
            ('aura', 'Aura', 'Aura', 'boolean', {}),
            ('sleep_quality', 'Uyku kalitesi', 'Sleep quality', 'slider',
             {'min': 0, 'max': 10, 'step': 1}),
            ('stress_level', 'Stres düzeyi', 'Stress level', 'slider',
             {'min': 0, 'max': 10, 'step': 1}),
            ('water_intake', 'Su tüketimi (bardak)', 'Water intake (glasses)', 'number',
             {'min': 0, 'max': 20}),
            ('caffeine_intake', 'Kafein tüketimi', 'Caffeine intake', 'choice',
             {'choices_tr': ['Yok', '1 fincan', '2 fincan', '3+'],
              'choices_en': ['None', '1 cup', '2 cups', '3+']}),
            ('exercise', 'Egzersiz yaptım', 'Did exercise', 'boolean', {}),
            ('mood', 'Ruh hali', 'Mood', 'choice',
             {'choices_tr': ['Çok kötü', 'Kötü', 'Normal', 'İyi', 'Çok iyi'],
              'choices_en': ['Very bad', 'Bad', 'Normal', 'Good', 'Very good']}),
        ]

        created_count = 0
        for i, (key, label_tr, label_en, input_type, config) in enumerate(symptoms_data):
            _, c = SymptomDefinition.objects.get_or_create(
                disease_module=module,
                key=key,
                defaults={
                    'label_tr': label_tr,
                    'label_en': label_en,
                    'input_type': input_type,
                    'config': config,
                    'order': i,
                },
            )
            if c:
                created_count += 1
        self.stdout.write(f"Created {created_count} symptom definitions (total: {len(symptoms_data)})")

        # 4. Task Templates
        tasks_data = [
            ('Günlük migren günlüğü', 'Daily migraine diary',
             'Bugünkü semptomları ve atak durumunu kaydedin.',
             'Record today\'s symptoms and attack status.',
             'diary_entry', 'daily', 5),
            ('Tetikleyici kontrol listesi', 'Trigger checklist',
             'Bugün karşılaştığınız tetikleyicileri işaretleyin.',
             'Check triggers you encountered today.',
             'checklist', 'daily', 3),
            ('İlaç takibi', 'Medication tracking',
             'İlaçlarınızı aldınız mı? Kaydedin.',
             'Did you take your medications? Log them.',
             'medication', 'daily', 3),
            ('Su tüketimi takibi', 'Water intake tracking',
             'Günlük su tüketiminizi kaydedin (en az 8 bardak hedefleyin).',
             'Track your daily water intake (aim for at least 8 glasses).',
             'checklist', 'daily', 2),
            ('Uyku günlüğü', 'Sleep diary',
             'Uyku saatinizi ve kalitenizi kaydedin.',
             'Log your sleep time and quality.',
             'diary_entry', 'daily', 3),
            ('Haftalık tetikleyici analizi', 'Weekly trigger analysis',
             'Bu haftaki tetikleyicileri gözden geçirin ve paternleri inceleyin.',
             'Review this week\'s triggers and identify patterns.',
             'survey', 'weekly', 5),
            ('Stres yönetimi egzersizi', 'Stress management exercise',
             'Nefes egzersizi veya meditasyon yapın (10 dakika).',
             'Do breathing exercises or meditation (10 minutes).',
             'exercise', 'daily', 4),
            ('Migren eğitim modülü', 'Migraine education module',
             'Bu haftanın eğitim içeriğini tamamlayın.',
             'Complete this week\'s education content.',
             'education', 'weekly', 5),
        ]

        created_count = 0
        for i, (title_tr, title_en, desc_tr, desc_en, task_type, freq, pts) in enumerate(tasks_data):
            _, c = TaskTemplate.objects.get_or_create(
                disease_module=module,
                title_en=title_en,
                defaults={
                    'title_tr': title_tr,
                    'description_tr': desc_tr,
                    'description_en': desc_en,
                    'task_type': task_type,
                    'frequency': freq,
                    'points': pts,
                    'order': i,
                    'is_active': True,
                },
            )
            if c:
                created_count += 1
        self.stdout.write(f"Created {created_count} task templates (total: {len(tasks_data)})")

        # Also seed inactive modules for future
        future_modules = [
            ('epilepsy', 'Epilepsi', 'Epilepsy', 'Nöbet takibi ve yönetimi.',
             'Seizure tracking and management.', 'zap', 2),
            ('parkinson', 'Parkinson', 'Parkinson', 'Motor semptom takibi ve egzersizler.',
             'Motor symptom tracking and exercises.', 'activity', 3),
            ('dementia', 'Demans', 'Dementia', 'Bilişsel takip ve bakıcı desteği.',
             'Cognitive tracking and caregiver support.', 'brain', 4),
        ]

        for slug, name_tr, name_en, desc_tr, desc_en, icon, order in future_modules:
            DiseaseModule.objects.get_or_create(
                slug=slug,
                defaults={
                    'disease_type': slug,
                    'name_tr': name_tr,
                    'name_en': name_en,
                    'description_tr': desc_tr,
                    'description_en': desc_en,
                    'icon': icon,
                    'is_active': False,
                    'order': order,
                },
            )

        self.stdout.write(self.style.SUCCESS('Migraine seed data created successfully!'))
