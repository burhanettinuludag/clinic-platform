"""
Seed cognitive exercises for dementia module.
Usage: python manage.py seed_cognitive_exercises
"""
from django.core.management.base import BaseCommand
from apps.dementia.models import CognitiveExercise


class Command(BaseCommand):
    help = 'Seeds cognitive exercises for dementia module'

    def handle(self, *args, **options):
        self.stdout.write('Seeding cognitive exercises...')

        exercises = [
            # Memory Exercises
            {
                'slug': 'memory-cards',
                'name_tr': 'Hafıza Kartları',
                'name_en': 'Memory Cards',
                'description_tr': 'Eşleşen kartları bularak hafızanızı geliştirin.',
                'description_en': 'Improve your memory by finding matching cards.',
                'instructions_tr': 'Kartlara tıklayarak çevirin. Aynı iki kartı bulmaya çalışın. Tüm çiftleri bulana kadar devam edin.',
                'instructions_en': 'Click cards to flip them. Try to find two matching cards. Continue until you find all pairs.',
                'exercise_type': 'memory',
                'difficulty': 'easy',
                'estimated_duration_minutes': 5,
                'icon': 'grid-3x3',
                'order': 1,
                'config': {
                    'grid_sizes': {'easy': [3, 4], 'medium': [4, 4], 'hard': [4, 5]},
                    'time_limit_seconds': 120,
                    'card_themes': ['animals', 'fruits', 'objects'],
                },
            },
            {
                'slug': 'word-pairs',
                'name_tr': 'Kelime Çiftleri',
                'name_en': 'Word Pairs',
                'description_tr': 'İlişkili kelime çiftlerini hatırlayın.',
                'description_en': 'Remember associated word pairs.',
                'instructions_tr': 'Size kelime çiftleri gösterilecek. Ardından bir kelime verilecek ve eşini hatırlamanız istenecek.',
                'instructions_en': 'You will be shown word pairs. Then you will be given one word and asked to remember its pair.',
                'exercise_type': 'memory',
                'difficulty': 'medium',
                'estimated_duration_minutes': 7,
                'icon': 'link',
                'order': 2,
                'config': {
                    'pair_counts': {'easy': 4, 'medium': 6, 'hard': 8},
                    'display_time_seconds': 5,
                },
            },
            {
                'slug': 'sequence-recall',
                'name_tr': 'Sıra Hatırlama',
                'name_en': 'Sequence Recall',
                'description_tr': 'Gösterilen sırayı hatırlayın ve tekrarlayın.',
                'description_en': 'Remember and repeat the shown sequence.',
                'instructions_tr': 'Ekranda sırayla yanacak kareleri izleyin. Sonra aynı sırayla tıklayın.',
                'instructions_en': 'Watch the squares light up in sequence. Then click them in the same order.',
                'exercise_type': 'memory',
                'difficulty': 'medium',
                'estimated_duration_minutes': 5,
                'icon': 'layers',
                'order': 3,
                'config': {
                    'starting_length': 3,
                    'max_length': 9,
                    'grid_size': 9,
                },
            },

            # Attention Exercises
            {
                'slug': 'spot-difference',
                'name_tr': 'Farkı Bul',
                'name_en': 'Spot the Difference',
                'description_tr': 'İki resim arasındaki farkları bulun.',
                'description_en': 'Find the differences between two images.',
                'instructions_tr': 'İki resme bakın ve aralarındaki farkları işaretleyin. Tüm farkları bulana kadar devam edin.',
                'instructions_en': 'Look at two images and mark the differences. Continue until you find all differences.',
                'exercise_type': 'attention',
                'difficulty': 'easy',
                'estimated_duration_minutes': 5,
                'icon': 'search',
                'order': 4,
                'config': {
                    'difference_counts': {'easy': 3, 'medium': 5, 'hard': 7},
                    'time_limit_seconds': 120,
                },
            },
            {
                'slug': 'color-word',
                'name_tr': 'Renk Kelime Oyunu',
                'name_en': 'Color Word Game',
                'description_tr': 'Kelimenin yazıldığı rengi seçin (Stroop testi).',
                'description_en': 'Select the color the word is written in (Stroop test).',
                'instructions_tr': 'Bir renk ismi göreceksiniz ama farklı bir renkle yazılmış olacak. Kelimenin YAZILDIĞI rengi seçin.',
                'instructions_en': 'You will see a color name written in a different color. Select the COLOR the word is WRITTEN in.',
                'exercise_type': 'attention',
                'difficulty': 'hard',
                'estimated_duration_minutes': 5,
                'icon': 'palette',
                'order': 5,
                'config': {
                    'colors': ['red', 'blue', 'green', 'yellow', 'purple', 'orange'],
                    'rounds': 20,
                    'time_per_round_seconds': 5,
                },
            },
            {
                'slug': 'visual-search',
                'name_tr': 'Görsel Arama',
                'name_en': 'Visual Search',
                'description_tr': 'Belirtilen nesneyi resimde bulun.',
                'description_en': 'Find the specified object in the image.',
                'instructions_tr': 'Bir nesne tarif edilecek. Resimde o nesneyi bulup tıklayın.',
                'instructions_en': 'An object will be described. Find and click that object in the image.',
                'exercise_type': 'attention',
                'difficulty': 'medium',
                'estimated_duration_minutes': 5,
                'icon': 'eye',
                'order': 6,
                'config': {
                    'item_counts': {'easy': 10, 'medium': 20, 'hard': 30},
                    'time_limit_seconds': 60,
                },
            },

            # Language Exercises
            {
                'slug': 'word-completion',
                'name_tr': 'Kelime Tamamlama',
                'name_en': 'Word Completion',
                'description_tr': 'Eksik harfleri tamamlayarak kelimeyi bulun.',
                'description_en': 'Complete the word by filling in missing letters.',
                'instructions_tr': 'Bazı harfleri eksik bir kelime göreceksiniz. Doğru harfleri yazarak kelimeyi tamamlayın.',
                'instructions_en': 'You will see a word with some letters missing. Type the correct letters to complete the word.',
                'exercise_type': 'language',
                'difficulty': 'easy',
                'estimated_duration_minutes': 5,
                'icon': 'type',
                'order': 7,
                'config': {
                    'word_lengths': {'easy': [4, 5], 'medium': [5, 7], 'hard': [7, 10]},
                    'missing_percentage': 0.3,
                },
            },
            {
                'slug': 'category-sorting',
                'name_tr': 'Kategori Sınıflandırma',
                'name_en': 'Category Sorting',
                'description_tr': 'Kelimeleri doğru kategorilere yerleştirin.',
                'description_en': 'Sort words into correct categories.',
                'instructions_tr': 'Kelimeler gösterilecek. Her kelimeyi ait olduğu kategoriye sürükleyin.',
                'instructions_en': 'Words will be shown. Drag each word to its correct category.',
                'exercise_type': 'language',
                'difficulty': 'medium',
                'estimated_duration_minutes': 6,
                'icon': 'folder',
                'order': 8,
                'config': {
                    'categories': ['Hayvanlar', 'Meyveler', 'Renkler', 'Sayılar'],
                    'words_per_category': 5,
                },
            },
            {
                'slug': 'word-association',
                'name_tr': 'Kelime İlişkilendirme',
                'name_en': 'Word Association',
                'description_tr': 'Verilen kelimeyle ilişkili kelimeyi bulun.',
                'description_en': 'Find the word associated with the given word.',
                'instructions_tr': 'Bir kelime gösterilecek. Bu kelimeyle en çok ilişkili olan kelimeyi seçeneklerden seçin.',
                'instructions_en': 'A word will be shown. Select the word most related to it from the options.',
                'exercise_type': 'language',
                'difficulty': 'medium',
                'estimated_duration_minutes': 5,
                'icon': 'link-2',
                'order': 9,
                'config': {
                    'rounds': 15,
                    'options_count': 4,
                },
            },

            # Problem Solving Exercises
            {
                'slug': 'simple-math',
                'name_tr': 'Basit Matematik',
                'name_en': 'Simple Math',
                'description_tr': 'Basit toplama, çıkarma, çarpma işlemlerini çözün.',
                'description_en': 'Solve simple addition, subtraction, multiplication problems.',
                'instructions_tr': 'Matematik işlemlerini çözün ve doğru cevabı yazın veya seçin.',
                'instructions_en': 'Solve math problems and type or select the correct answer.',
                'exercise_type': 'calculation',
                'difficulty': 'easy',
                'estimated_duration_minutes': 5,
                'icon': 'calculator',
                'order': 10,
                'config': {
                    'operations': ['add', 'subtract'],
                    'max_number': {'easy': 20, 'medium': 50, 'hard': 100},
                    'rounds': 15,
                },
            },
            {
                'slug': 'pattern-recognition',
                'name_tr': 'Desen Tanıma',
                'name_en': 'Pattern Recognition',
                'description_tr': 'Deseni tamamlayacak şekli bulun.',
                'description_en': 'Find the shape that completes the pattern.',
                'instructions_tr': 'Bir desen göreceksiniz. Sıradaki şekli seçeneklerden seçin.',
                'instructions_en': 'You will see a pattern. Select the next shape from the options.',
                'exercise_type': 'problem_solving',
                'difficulty': 'medium',
                'estimated_duration_minutes': 7,
                'icon': 'shapes',
                'order': 11,
                'config': {
                    'pattern_types': ['shapes', 'colors', 'numbers'],
                    'rounds': 10,
                },
            },
            {
                'slug': 'puzzle-arrange',
                'name_tr': 'Resim Dizme',
                'name_en': 'Picture Arrange',
                'description_tr': 'Parçaları doğru sıraya koyarak resmi tamamlayın.',
                'description_en': 'Arrange the pieces in correct order to complete the picture.',
                'instructions_tr': 'Karışık resim parçalarını sürükleyerek doğru konumlarına yerleştirin.',
                'instructions_en': 'Drag the mixed picture pieces to their correct positions.',
                'exercise_type': 'problem_solving',
                'difficulty': 'medium',
                'estimated_duration_minutes': 8,
                'icon': 'puzzle',
                'order': 12,
                'config': {
                    'grid_sizes': {'easy': [2, 2], 'medium': [3, 3], 'hard': [4, 4]},
                },
            },

            # Orientation Exercises
            {
                'slug': 'date-time-quiz',
                'name_tr': 'Tarih ve Zaman',
                'name_en': 'Date and Time',
                'description_tr': 'Bugünün tarihi, günü ve saati hakkında sorular.',
                'description_en': 'Questions about today\'s date, day and time.',
                'instructions_tr': 'Tarih, gün ve saatle ilgili soruları cevaplayın.',
                'instructions_en': 'Answer questions about date, day and time.',
                'exercise_type': 'orientation',
                'difficulty': 'easy',
                'estimated_duration_minutes': 3,
                'icon': 'calendar',
                'order': 13,
                'config': {
                    'question_types': ['day', 'date', 'month', 'year', 'season', 'time_of_day'],
                },
            },
            {
                'slug': 'location-quiz',
                'name_tr': 'Yer Bilgisi',
                'name_en': 'Location Quiz',
                'description_tr': 'Bulunduğunuz yer hakkında sorular.',
                'description_en': 'Questions about your current location.',
                'instructions_tr': 'Bulunduğunuz şehir, ev, oda gibi sorulara cevap verin.',
                'instructions_en': 'Answer questions about your city, home, room, etc.',
                'exercise_type': 'orientation',
                'difficulty': 'easy',
                'estimated_duration_minutes': 3,
                'icon': 'map-pin',
                'order': 14,
                'config': {
                    'question_types': ['city', 'country', 'home_type', 'current_room'],
                },
            },
            {
                'slug': 'face-recognition',
                'name_tr': 'Yüz Tanıma Testi',
                'name_en': 'Face Recognition Test',
                'description_tr': 'Kişilerin yüzlerini ve isimlerini hatırlayın.',
                'description_en': 'Remember faces and names of people.',
                'instructions_tr': 'Size birkaç kişi tanıtılacak. İsimlerini ve kim olduklarını ezberleyin. Ardından sorulan sorulara cevap verin.',
                'instructions_en': 'You will be introduced to several people. Memorize their names and relationships. Then answer the questions.',
                'exercise_type': 'memory',
                'difficulty': 'medium',
                'estimated_duration_minutes': 8,
                'icon': 'users',
                'order': 15,
                'config': {
                    'face_counts': {'easy': 4, 'medium': 6, 'hard': 8},
                    'learn_time_per_face': 5,
                    'questions_per_face': 2,
                },
            },
        ]

        for ex_data in exercises:
            exercise, created = CognitiveExercise.objects.update_or_create(
                slug=ex_data['slug'],
                defaults={
                    **{k: v for k, v in ex_data.items() if k != 'slug'},
                    'is_active': True,
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {ex_data["name_en"]}')

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(exercises)} cognitive exercises!'))
