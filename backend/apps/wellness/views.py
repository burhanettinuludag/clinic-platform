from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
import requests
from django.conf import settings

from .models import (
    BreathingExercise, RelaxationExercise, ExerciseSession,
    SleepLog, MenstrualLog, WaterIntakeLog, WeatherData, UserWeatherAlert
)
from .serializers import (
    BreathingExerciseSerializer, RelaxationExerciseSerializer,
    ExerciseSessionSerializer, SleepLogSerializer, MenstrualLogSerializer,
    WaterIntakeLogSerializer, WeatherDataSerializer, UserWeatherAlertSerializer
)


class BreathingExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """Nefes egzersizleri - sadece okuma"""
    queryset = BreathingExercise.objects.filter(is_active=True)
    serializer_class = BreathingExerciseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_difficulty(self, request):
        """Zorluk seviyesine göre grupla"""
        exercises = self.get_queryset()
        grouped = {
            'beginner': BreathingExerciseSerializer(
                exercises.filter(difficulty='beginner'), many=True, context={'request': request}
            ).data,
            'intermediate': BreathingExerciseSerializer(
                exercises.filter(difficulty='intermediate'), many=True, context={'request': request}
            ).data,
            'advanced': BreathingExerciseSerializer(
                exercises.filter(difficulty='advanced'), many=True, context={'request': request}
            ).data,
        }
        return Response(grouped)


class RelaxationExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """Gevşeme egzersizleri - sadece okuma"""
    queryset = RelaxationExercise.objects.filter(is_active=True)
    serializer_class = RelaxationExerciseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Egzersiz tipine göre grupla"""
        exercises = self.get_queryset()
        types = dict(RelaxationExercise.TYPE_CHOICES)
        grouped = {}
        for type_key, type_name in types.items():
            grouped[type_key] = RelaxationExerciseSerializer(
                exercises.filter(exercise_type=type_key), many=True, context={'request': request}
            ).data
        return Response(grouped)


class ExerciseSessionViewSet(viewsets.ModelViewSet):
    """Egzersiz seansları"""
    serializer_class = ExerciseSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExerciseSession.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Egzersiz istatistikleri"""
        sessions = self.get_queryset()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent = sessions.filter(completed_at__gte=thirty_days_ago)

        stats = {
            'total_sessions': sessions.count(),
            'sessions_this_month': recent.count(),
            'total_minutes': sum(s.duration_seconds for s in sessions) // 60,
            'avg_stress_reduction': recent.exclude(
                stress_before__isnull=True
            ).exclude(
                stress_after__isnull=True
            ).annotate(
                reduction=models.F('stress_before') - models.F('stress_after')
            ).aggregate(avg=Avg('reduction'))['avg'] or 0,
            'total_points_earned': sum(s.points_earned for s in sessions),
        }
        return Response(stats)


class SleepLogViewSet(viewsets.ModelViewSet):
    """Uyku takibi"""
    serializer_class = SleepLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SleepLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Uyku istatistikleri"""
        logs = self.get_queryset()
        thirty_days = logs.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        )

        stats = {
            'avg_duration_hours': round(
                (thirty_days.aggregate(avg=Avg('sleep_duration_minutes'))['avg'] or 0) / 60, 1
            ),
            'avg_quality': round(
                thirty_days.aggregate(avg=Avg('sleep_quality'))['avg'] or 0, 1
            ),
            'total_logs': logs.count(),
            'logs_this_month': thirty_days.count(),
            'nightmare_count': thirty_days.filter(had_nightmare=True).count(),
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def weekly_chart(self, request):
        """Haftalık uyku grafiği"""
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        logs = self.get_queryset().filter(date__gte=seven_days_ago)

        chart_data = []
        for log in logs:
            chart_data.append({
                'date': log.date.isoformat(),
                'hours': round(log.sleep_duration_minutes / 60, 1),
                'quality': log.sleep_quality,
            })
        return Response(chart_data)


class MenstrualLogViewSet(viewsets.ModelViewSet):
    """Adet döngüsü takibi"""
    serializer_class = MenstrualLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MenstrualLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def cycle_stats(self, request):
        """Döngü istatistikleri"""
        logs = self.get_queryset().filter(is_period_day=True).order_by('date')

        if logs.count() < 2:
            return Response({
                'avg_cycle_length': None,
                'avg_period_length': None,
                'headache_correlation': None,
                'message': 'Yeterli veri yok'
            })

        # Döngü uzunluğunu hesapla
        period_starts = []
        current_period_start = None

        for log in logs:
            if current_period_start is None:
                current_period_start = log.date
            elif (log.date - current_period_start).days > 7:
                period_starts.append(current_period_start)
                current_period_start = log.date

        if current_period_start:
            period_starts.append(current_period_start)

        cycle_lengths = []
        for i in range(1, len(period_starts)):
            cycle_lengths.append((period_starts[i] - period_starts[i-1]).days)

        # Baş ağrısı korelasyonu
        total_period_days = logs.count()
        headache_days = logs.filter(has_headache=True).count()

        stats = {
            'avg_cycle_length': round(sum(cycle_lengths) / len(cycle_lengths)) if cycle_lengths else None,
            'total_cycles_tracked': len(period_starts),
            'headache_correlation': round((headache_days / total_period_days) * 100) if total_period_days > 0 else 0,
            'common_symptoms': {
                'cramps': logs.filter(has_cramps=True).count(),
                'headache': headache_days,
                'mood_changes': logs.filter(has_mood_changes=True).count(),
                'bloating': logs.filter(has_bloating=True).count(),
                'fatigue': logs.filter(has_fatigue=True).count(),
            }
        }
        return Response(stats)


class WaterIntakeLogViewSet(viewsets.ModelViewSet):
    """Su tüketimi takibi"""
    serializer_class = WaterIntakeLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WaterIntakeLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_glass(self, request):
        """Bir bardak su ekle"""
        from datetime import date
        today = date.today()

        log, created = WaterIntakeLog.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'glasses': 1}
        )

        if not created:
            log.glasses += 1
            log.save()

        return Response(WaterIntakeLogSerializer(log).data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Bugünkü su tüketimi"""
        from datetime import date
        today = date.today()

        log, created = WaterIntakeLog.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'glasses': 0}
        )

        return Response(WaterIntakeLogSerializer(log).data)

    @action(detail=False, methods=['get'])
    def weekly_chart(self, request):
        """Haftalık su grafiği"""
        from datetime import date, timedelta
        seven_days_ago = date.today() - timedelta(days=7)

        logs = self.get_queryset().filter(date__gte=seven_days_ago)
        chart_data = []
        for log in logs:
            chart_data.append({
                'date': log.date.isoformat(),
                'glasses': log.glasses,
                'target': log.target_glasses,
                'percentage': min(100, round((log.glasses / log.target_glasses) * 100)) if log.target_glasses > 0 else 0
            })
        return Response(chart_data)


class WeatherViewSet(viewsets.ViewSet):
    """Hava durumu servisi"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Mevcut hava durumu"""
        city = request.query_params.get('city', 'Istanbul')

        # Cache kontrol (son 30 dakika)
        thirty_mins_ago = timezone.now() - timedelta(minutes=30)
        cached = WeatherData.objects.filter(
            city__iexact=city,
            recorded_at__gte=thirty_mins_ago
        ).first()

        if cached:
            return Response(WeatherDataSerializer(cached).data)

        # OpenWeatherMap API çağrısı
        api_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', None)
        if not api_key:
            return Response(
                {'error': 'Weather API not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            url = f'https://api.openweathermap.org/data/2.5/weather'
            params = {
                'q': f'{city},TR',
                'appid': api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            weather = WeatherData.objects.create(
                city=city,
                temperature=data['main']['temp'],
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                weather_condition=data['weather'][0]['main'],
                weather_description=data['weather'][0]['description'],
                recorded_at=timezone.now()
            )

            return Response(WeatherDataSerializer(weather).data)

        except requests.RequestException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @action(detail=False, methods=['get'])
    def pressure_history(self, request):
        """Son 24 saatlik basınç değişimi"""
        city = request.query_params.get('city', 'Istanbul')
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

        history = WeatherData.objects.filter(
            city__iexact=city,
            recorded_at__gte=twenty_four_hours_ago
        ).order_by('recorded_at')

        data = []
        for record in history:
            data.append({
                'time': record.recorded_at.isoformat(),
                'pressure': record.pressure,
                'temperature': record.temperature,
                'humidity': record.humidity
            })

        # Basınç değişimi hesapla
        pressure_change = 0
        if len(data) >= 2:
            pressure_change = data[-1]['pressure'] - data[0]['pressure']

        return Response({
            'history': data,
            'pressure_change_24h': round(pressure_change, 1),
            'risk_level': 'high' if abs(pressure_change) > 5 else 'normal'
        })


class UserWeatherAlertViewSet(viewsets.ModelViewSet):
    """Kullanıcı hava uyarı ayarları"""
    serializer_class = UserWeatherAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserWeatherAlert.objects.filter(user=self.request.user)

    def get_object(self):
        obj, _ = UserWeatherAlert.objects.get_or_create(user=self.request.user)
        return obj
