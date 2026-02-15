import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='apps.wellness.tasks.update_weather_cache')
def update_weather_cache():
    """Varsayilan sehirler icin hava durumu cache guncelle."""
    from apps.wellness.models import WeatherData
    from django.conf import settings
    from django.utils import timezone
    import requests

    cities = ['Istanbul', 'Ankara', 'Izmir']
    api_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', None)
    if not api_key:
        logger.warning("No OpenWeatherMap API key configured")
        return {'updated': 0}

    updated = 0
    for city in cities:
        try:
            resp = requests.get(
                'https://api.openweathermap.org/data/2.5/weather',
                params={'q': f'{city},TR', 'appid': api_key, 'units': 'metric', 'lang': 'tr'},
                timeout=10,
            )
            if resp.status_code == 200:
                d = resp.json()
                WeatherData.objects.update_or_create(
                    city=city,
                    defaults={
                        'temperature': d['main']['temp'],
                        'humidity': d['main']['humidity'],
                        'pressure': d['main']['pressure'],
                        'weather_condition': d['weather'][0]['main'],
                        'weather_description': d['weather'][0]['description'],
                        'recorded_at': timezone.now(),
                    },
                )
                updated += 1
        except Exception as e:
            logger.error(f"Weather update failed for {city}: {e}")

    logger.info(f"Updated weather for {updated} cities")
    return {'updated': updated}
