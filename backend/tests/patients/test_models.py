"""
Unit tests for patients models.
"""

import pytest
from datetime import date
from apps.patients.models import (
    DiseaseModule,
    PatientModule,
    TaskTemplate,
    TaskCompletion,
)


@pytest.mark.django_db
class TestDiseaseModule:
    """Tests for DiseaseModule model."""

    def test_create_disease_module(self, db):
        """Test creating a disease module."""
        module = DiseaseModule.objects.create(
            slug='epilepsy',
            disease_type='epilepsy',
            name_tr='Epilepsi',
            name_en='Epilepsy',
            description_tr='Epilepsi hastaliği modulu',
            description_en='Epilepsy disease module',
            icon='zap',
            is_active=True,
            order=2,
        )
        assert module.slug == 'epilepsy'
        assert module.disease_type == 'epilepsy'
        assert module.is_active is True

    def test_disease_module_str(self, disease_module):
        """Test disease module string representation."""
        assert str(disease_module) == 'Migraine'

    def test_disease_types(self, db):
        """Test all disease type choices."""
        types = ['migraine', 'epilepsy', 'parkinson', 'dementia']
        for dtype in types:
            module = DiseaseModule.objects.create(
                slug=dtype,
                disease_type=dtype,
                name_tr=f'Test {dtype}',
                name_en=f'Test {dtype}',
            )
            assert module.disease_type == dtype

    def test_unique_slug(self, disease_module):
        """Test slug must be unique."""
        with pytest.raises(Exception):
            DiseaseModule.objects.create(
                slug=disease_module.slug,
                disease_type='epilepsy',
                name_tr='Test',
                name_en='Test',
            )

    def test_ordering(self, db):
        """Test modules are ordered by order field."""
        m1 = DiseaseModule.objects.create(
            slug='second', disease_type='epilepsy',
            name_tr='Second', name_en='Second', order=2,
        )
        m2 = DiseaseModule.objects.create(
            slug='first', disease_type='parkinson',
            name_tr='First', name_en='First', order=1,
        )
        modules = list(DiseaseModule.objects.all())
        assert modules[0] == m2
        assert modules[1] == m1


@pytest.mark.django_db
class TestPatientModule:
    """Tests for PatientModule model."""

    def test_enroll_patient(self, patient_user, disease_module):
        """Test enrolling a patient in a disease module."""
        enrollment = PatientModule.objects.create(
            patient=patient_user,
            disease_module=disease_module,
            is_active=True,
        )
        assert enrollment.patient == patient_user
        assert enrollment.disease_module == disease_module
        assert enrollment.is_active is True
        assert enrollment.enrolled_at is not None

    def test_patient_module_str(self, patient_user, disease_module):
        """Test patient module string representation."""
        enrollment = PatientModule.objects.create(
            patient=patient_user,
            disease_module=disease_module,
        )
        expected = f"{patient_user} - {disease_module}"
        assert str(enrollment) == expected

    def test_unique_enrollment(self, patient_user, disease_module):
        """Test patient can only enroll once per module."""
        PatientModule.objects.create(
            patient=patient_user,
            disease_module=disease_module,
        )
        with pytest.raises(Exception):
            PatientModule.objects.create(
                patient=patient_user,
                disease_module=disease_module,
            )

    def test_multiple_modules(self, patient_user, db):
        """Test patient can enroll in multiple modules."""
        module1 = DiseaseModule.objects.create(
            slug='test1', disease_type='epilepsy',
            name_tr='Test1', name_en='Test1',
        )
        module2 = DiseaseModule.objects.create(
            slug='test2', disease_type='parkinson',
            name_tr='Test2', name_en='Test2',
        )
        PatientModule.objects.create(patient=patient_user, disease_module=module1)
        PatientModule.objects.create(patient=patient_user, disease_module=module2)
        assert patient_user.enrolled_modules.count() == 2


@pytest.mark.django_db
class TestTaskTemplate:
    """Tests for TaskTemplate model."""

    def test_create_task_template(self, disease_module):
        """Test creating a task template."""
        task = TaskTemplate.objects.create(
            disease_module=disease_module,
            title_tr='Gunluk Migren Guncesi',
            title_en='Daily Migraine Diary',
            description_tr='Gunluk migren durumunuzu kaydedin',
            description_en='Log your daily migraine status',
            task_type='diary_entry',
            frequency='daily',
            points=5,
            order=1,
            is_active=True,
        )
        assert task.title_en == 'Daily Migraine Diary'
        assert task.task_type == 'diary_entry'
        assert task.frequency == 'daily'
        assert task.points == 5

    def test_task_template_str(self, disease_module):
        """Test task template string representation."""
        task = TaskTemplate.objects.create(
            disease_module=disease_module,
            title_tr='Test Gorev',
            title_en='Test Task',
            task_type='checklist',
            frequency='weekly',
        )
        assert str(task) == 'Test Task'

    def test_task_types(self, disease_module):
        """Test all task type choices."""
        types = ['diary_entry', 'checklist', 'education', 'exercise', 'medication', 'survey']
        for task_type in types:
            task = TaskTemplate.objects.create(
                disease_module=disease_module,
                title_tr=f'Test {task_type}',
                title_en=f'Test {task_type}',
                task_type=task_type,
                frequency='daily',
            )
            assert task.task_type == task_type

    def test_task_frequencies(self, disease_module):
        """Test all task frequency choices."""
        frequencies = ['daily', 'weekly', 'on_event', 'one_time']
        for freq in frequencies:
            task = TaskTemplate.objects.create(
                disease_module=disease_module,
                title_tr=f'Test {freq}',
                title_en=f'Test {freq}',
                task_type='checklist',
                frequency=freq,
            )
            assert task.frequency == freq

    def test_task_with_metadata(self, disease_module):
        """Test task with JSON metadata."""
        task = TaskTemplate.objects.create(
            disease_module=disease_module,
            title_tr='Test',
            title_en='Test',
            task_type='survey',
            frequency='weekly',
            metadata={'questions': ['Q1', 'Q2'], 'required': True},
        )
        assert task.metadata['questions'] == ['Q1', 'Q2']
        assert task.metadata['required'] is True


@pytest.mark.django_db
class TestTaskCompletion:
    """Tests for TaskCompletion model."""

    @pytest.fixture
    def task_template(self, disease_module):
        """Create a task template for testing."""
        return TaskTemplate.objects.create(
            disease_module=disease_module,
            title_tr='Test Gorev',
            title_en='Test Task',
            task_type='diary_entry',
            frequency='daily',
            points=5,
        )

    def test_complete_task(self, patient_user, task_template):
        """Test completing a task."""
        completion = TaskCompletion.objects.create(
            patient=patient_user,
            task_template=task_template,
            completed_date=date.today(),
            response_data={'intensity': 5, 'notes': 'Mild headache'},
            notes='Completed successfully',
        )
        assert completion.patient == patient_user
        assert completion.task_template == task_template
        assert completion.response_data['intensity'] == 5

    def test_task_completion_str(self, patient_user, task_template):
        """Test task completion string representation."""
        completion = TaskCompletion.objects.create(
            patient=patient_user,
            task_template=task_template,
            completed_date=date.today(),
        )
        expected = f"{patient_user} completed {task_template} on {date.today()}"
        assert str(completion) == expected

    def test_multiple_completions_different_days(self, patient_user, task_template):
        """Test multiple task completions on different days."""
        TaskCompletion.objects.create(
            patient=patient_user,
            task_template=task_template,
            completed_date=date.today(),
        )
        TaskCompletion.objects.create(
            patient=patient_user,
            task_template=task_template,
            completed_date=date.today().replace(day=date.today().day - 1 if date.today().day > 1 else 28),
        )
        assert TaskCompletion.objects.filter(patient=patient_user).count() == 2
