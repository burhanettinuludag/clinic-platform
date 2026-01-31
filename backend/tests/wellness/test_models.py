"""
Unit tests for wellness models.
"""

import pytest
from datetime import date, time
from django.utils import timezone
from apps.wellness.models import (
    BreathingExercise,
    RelaxationExercise,
    ExerciseSession,
    SleepLog,
    MenstrualLog,
    WaterIntakeLog,
    WeatherData,
    UserWeatherAlert,
)


@pytest.mark.django_db
class TestBreathingExercise:
    """Tests for BreathingExercise model."""

    def test_create_breathing_exercise(self, db):
        """Test creating a breathing exercise."""
        exercise = BreathingExercise.objects.create(
            name_tr='4-7-8 Nefes',
            name_en='4-7-8 Breathing',
            description_tr='Rahatlatici nefes teknigi',
            description_en='Relaxing breathing technique',
            inhale_seconds=4,
            hold_seconds=7,
            exhale_seconds=8,
            hold_after_exhale_seconds=0,
            cycles=4,
            difficulty='beginner',
            benefits_tr='Stresi azaltir',
            benefits_en='Reduces stress',
        )
        assert exercise.name_en == '4-7-8 Breathing'
        assert exercise.inhale_seconds == 4
        assert exercise.hold_seconds == 7
        assert exercise.exhale_seconds == 8
        assert exercise.cycles == 4

    def test_breathing_exercise_str(self, db):
        """Test breathing exercise string representation."""
        exercise = BreathingExercise.objects.create(
            name_tr='Kare Nefes',
            name_en='Box Breathing',
            description_tr='4-4-4-4 nefes teknigi',
            description_en='4-4-4-4 breathing technique',
        )
        assert str(exercise) == 'Kare Nefes'

    def test_breathing_exercise_difficulty_choices(self, db):
        """Test difficulty choices."""
        for difficulty in ['beginner', 'intermediate', 'advanced']:
            exercise = BreathingExercise.objects.create(
                name_tr=f'Test {difficulty}',
                name_en=f'Test {difficulty}',
                description_tr='Test',
                description_en='Test',
                difficulty=difficulty,
            )
            assert exercise.difficulty == difficulty

    def test_breathing_exercise_ordering(self, db):
        """Test breathing exercises are ordered by order field."""
        ex1 = BreathingExercise.objects.create(
            name_tr='Second', name_en='Second',
            description_tr='', description_en='', order=2,
        )
        ex2 = BreathingExercise.objects.create(
            name_tr='First', name_en='First',
            description_tr='', description_en='', order=1,
        )
        exercises = list(BreathingExercise.objects.all())
        assert exercises[0] == ex2
        assert exercises[1] == ex1


@pytest.mark.django_db
class TestRelaxationExercise:
    """Tests for RelaxationExercise model."""

    def test_create_relaxation_exercise(self, db):
        """Test creating a relaxation exercise."""
        exercise = RelaxationExercise.objects.create(
            name_tr='Vucut Tarama',
            name_en='Body Scan',
            description_tr='Vucut farkindaliği meditasyonu',
            description_en='Body awareness meditation',
            exercise_type='body_scan',
            duration_minutes=15,
            steps_tr=['Rahat bir pozisyon alin', 'Gozlerinizi kapatin'],
            steps_en=['Get in a comfortable position', 'Close your eyes'],
        )
        assert exercise.exercise_type == 'body_scan'
        assert exercise.duration_minutes == 15
        assert len(exercise.steps_en) == 2

    def test_relaxation_exercise_types(self, db):
        """Test all exercise type choices."""
        types = ['pmr', 'body_scan', 'visualization', 'grounding', 'mindfulness']
        for ex_type in types:
            exercise = RelaxationExercise.objects.create(
                name_tr=f'Test {ex_type}',
                name_en=f'Test {ex_type}',
                description_tr='Test',
                description_en='Test',
                exercise_type=ex_type,
            )
            assert exercise.exercise_type == ex_type

    def test_relaxation_exercise_str(self, db):
        """Test relaxation exercise string representation."""
        exercise = RelaxationExercise.objects.create(
            name_tr='PMR Egzersizi',
            name_en='PMR Exercise',
            description_tr='Progresif kas gevseme',
            description_en='Progressive muscle relaxation',
            exercise_type='pmr',
        )
        assert str(exercise) == 'PMR Egzersizi'


@pytest.mark.django_db
class TestExerciseSession:
    """Tests for ExerciseSession model."""

    @pytest.fixture
    def breathing_exercise(self, db):
        """Create a breathing exercise for testing."""
        return BreathingExercise.objects.create(
            name_tr='Test Nefes',
            name_en='Test Breathing',
            description_tr='Test',
            description_en='Test',
        )

    @pytest.fixture
    def relaxation_exercise(self, db):
        """Create a relaxation exercise for testing."""
        return RelaxationExercise.objects.create(
            name_tr='Test Gevseme',
            name_en='Test Relaxation',
            description_tr='Test',
            description_en='Test',
            exercise_type='pmr',
        )

    def test_create_breathing_session(self, patient_user, breathing_exercise):
        """Test creating a breathing exercise session."""
        session = ExerciseSession.objects.create(
            user=patient_user,
            breathing_exercise=breathing_exercise,
            duration_seconds=300,
            stress_before=7,
            stress_after=4,
            points_earned=10,
        )
        assert session.breathing_exercise == breathing_exercise
        assert session.relaxation_exercise is None
        assert session.duration_seconds == 300
        assert session.stress_before == 7
        assert session.stress_after == 4

    def test_create_relaxation_session(self, patient_user, relaxation_exercise):
        """Test creating a relaxation exercise session."""
        session = ExerciseSession.objects.create(
            user=patient_user,
            relaxation_exercise=relaxation_exercise,
            duration_seconds=900,
            points_earned=15,
        )
        assert session.relaxation_exercise == relaxation_exercise
        assert session.breathing_exercise is None

    def test_session_ordering(self, patient_user, breathing_exercise):
        """Test sessions are ordered by completed_at descending."""
        session1 = ExerciseSession.objects.create(
            user=patient_user,
            breathing_exercise=breathing_exercise,
            duration_seconds=100,
        )
        session2 = ExerciseSession.objects.create(
            user=patient_user,
            breathing_exercise=breathing_exercise,
            duration_seconds=200,
        )
        sessions = list(ExerciseSession.objects.filter(user=patient_user))
        assert sessions[0] == session2
        assert sessions[1] == session1


@pytest.mark.django_db
class TestSleepLog:
    """Tests for SleepLog model."""

    def test_create_sleep_log(self, patient_user):
        """Test creating a sleep log."""
        log = SleepLog.objects.create(
            user=patient_user,
            date=date.today(),
            bedtime=time(23, 0),
            wake_time=time(7, 0),
            sleep_duration_minutes=480,
            sleep_quality=4,
            had_nightmare=False,
            woke_up_during_night=1,
        )
        assert log.sleep_duration_minutes == 480
        assert log.sleep_quality == 4
        assert log.woke_up_during_night == 1

    def test_sleep_quality_choices(self, patient_user):
        """Test all sleep quality choices (1-5)."""
        for quality in range(1, 6):
            log = SleepLog.objects.create(
                user=patient_user,
                date=date.today().replace(day=quality),
                bedtime=time(23, 0),
                wake_time=time(7, 0),
                sleep_duration_minutes=480,
                sleep_quality=quality,
            )
            assert log.sleep_quality == quality

    def test_unique_sleep_log_per_day(self, patient_user):
        """Test only one sleep log per user per day."""
        SleepLog.objects.create(
            user=patient_user,
            date=date.today(),
            bedtime=time(23, 0),
            wake_time=time(7, 0),
            sleep_duration_minutes=480,
            sleep_quality=3,
        )
        with pytest.raises(Exception):
            SleepLog.objects.create(
                user=patient_user,
                date=date.today(),
                bedtime=time(22, 0),
                wake_time=time(6, 0),
                sleep_duration_minutes=480,
                sleep_quality=4,
            )


@pytest.mark.django_db
class TestMenstrualLog:
    """Tests for MenstrualLog model."""

    def test_create_menstrual_log(self, patient_user):
        """Test creating a menstrual log."""
        log = MenstrualLog.objects.create(
            user=patient_user,
            date=date.today(),
            is_period_day=True,
            flow_intensity='medium',
            has_cramps=True,
            cramp_intensity=6,
            has_headache=True,
            has_mood_changes=True,
        )
        assert log.is_period_day is True
        assert log.flow_intensity == 'medium'
        assert log.cramp_intensity == 6

    def test_flow_intensity_choices(self, patient_user):
        """Test all flow intensity choices."""
        flows = ['spotting', 'light', 'medium', 'heavy']
        for i, flow in enumerate(flows):
            log = MenstrualLog.objects.create(
                user=patient_user,
                date=date.today().replace(day=i + 1),
                is_period_day=True,
                flow_intensity=flow,
            )
            assert log.flow_intensity == flow

    def test_unique_menstrual_log_per_day(self, patient_user):
        """Test only one menstrual log per user per day."""
        MenstrualLog.objects.create(
            user=patient_user,
            date=date.today(),
            is_period_day=True,
        )
        with pytest.raises(Exception):
            MenstrualLog.objects.create(
                user=patient_user,
                date=date.today(),
                is_period_day=False,
            )


@pytest.mark.django_db
class TestWaterIntakeLog:
    """Tests for WaterIntakeLog model."""

    def test_create_water_intake_log(self, patient_user):
        """Test creating a water intake log."""
        log = WaterIntakeLog.objects.create(
            user=patient_user,
            date=date.today(),
            glasses=6,
            target_glasses=8,
        )
        assert log.glasses == 6
        assert log.target_glasses == 8

    def test_default_target_glasses(self, patient_user):
        """Test default target glasses is 8."""
        log = WaterIntakeLog.objects.create(
            user=patient_user,
            date=date.today(),
            glasses=3,
        )
        assert log.target_glasses == 8

    def test_unique_water_log_per_day(self, patient_user):
        """Test only one water log per user per day."""
        WaterIntakeLog.objects.create(
            user=patient_user,
            date=date.today(),
            glasses=4,
        )
        with pytest.raises(Exception):
            WaterIntakeLog.objects.create(
                user=patient_user,
                date=date.today(),
                glasses=5,
            )


@pytest.mark.django_db
class TestWeatherData:
    """Tests for WeatherData model."""

    def test_create_weather_data(self, db):
        """Test creating weather data."""
        weather = WeatherData.objects.create(
            city='Istanbul',
            country_code='TR',
            temperature=22.5,
            humidity=65,
            pressure=1013.25,
            weather_condition='Clouds',
            weather_description='Partially cloudy',
            recorded_at=timezone.now(),
        )
        assert weather.city == 'Istanbul'
        assert weather.temperature == 22.5
        assert weather.pressure == 1013.25

    def test_weather_data_ordering(self, db):
        """Test weather data is ordered by recorded_at descending."""
        now = timezone.now()
        weather1 = WeatherData.objects.create(
            city='Istanbul', temperature=20, humidity=60, pressure=1010,
            weather_condition='Clear', weather_description='Clear sky',
            recorded_at=now,
        )
        weather2 = WeatherData.objects.create(
            city='Istanbul', temperature=22, humidity=65, pressure=1015,
            weather_condition='Clouds', weather_description='Cloudy',
            recorded_at=now.replace(hour=now.hour + 1 if now.hour < 23 else 0),
        )
        weather_list = list(WeatherData.objects.all())
        assert weather_list[0] == weather2


@pytest.mark.django_db
class TestUserWeatherAlert:
    """Tests for UserWeatherAlert model."""

    def test_create_weather_alert(self, patient_user):
        """Test creating user weather alert settings."""
        alert = UserWeatherAlert.objects.create(
            user=patient_user,
            city='Ankara',
            country_code='TR',
            alert_on_pressure_drop=True,
            pressure_threshold=7.0,
            alert_on_humidity_high=True,
            humidity_threshold=85,
            is_active=True,
        )
        assert alert.city == 'Ankara'
        assert alert.pressure_threshold == 7.0
        assert alert.humidity_threshold == 85

    def test_default_weather_alert_settings(self, patient_user):
        """Test default weather alert settings."""
        alert = UserWeatherAlert.objects.create(user=patient_user)
        assert alert.city == 'Istanbul'
        assert alert.country_code == 'TR'
        assert alert.alert_on_pressure_drop is True
        assert alert.pressure_threshold == 5.0
        assert alert.alert_on_humidity_high is True
        assert alert.humidity_threshold == 80

    def test_one_alert_per_user(self, patient_user):
        """Test only one weather alert config per user."""
        UserWeatherAlert.objects.create(user=patient_user)
        with pytest.raises(Exception):
            UserWeatherAlert.objects.create(user=patient_user)
