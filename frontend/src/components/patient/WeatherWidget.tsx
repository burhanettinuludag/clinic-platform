'use client';

import { useState, useEffect } from 'react';
import { Cloud, Sun, CloudRain, CloudSnow, Wind, Droplets, Thermometer, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface WeatherData {
  city: string;
  temperature: number;
  humidity: number;
  pressure: number;
  weather_condition: string;
  weather_description: string;
}

const WEATHER_ICONS: Record<string, any> = {
  Clear: Sun,
  Clouds: Cloud,
  Rain: CloudRain,
  Drizzle: CloudRain,
  Snow: CloudSnow,
  Thunderstorm: CloudRain,
};

const WEATHER_BG: Record<string, string> = {
  Clear: 'from-yellow-400 to-orange-400',
  Clouds: 'from-gray-400 to-gray-500',
  Rain: 'from-blue-400 to-blue-600',
  Snow: 'from-blue-100 to-blue-300',
  default: 'from-cyan-400 to-blue-500',
};

export default function WeatherWidget({ city = 'Izmir' }: { city?: string }) {
  const [data, setData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/wellness/weather/current/', { params: { city } })
      .then(res => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [city]);

  if (loading) return <div className="rounded-xl bg-gray-100 p-4 animate-pulse h-24" />;
  if (!data) return null;

  const Icon = WEATHER_ICONS[data.weather_condition] || Cloud;
  const bg = WEATHER_BG[data.weather_condition] || WEATHER_BG.default;

  return (
    <div className={'rounded-xl p-4 text-white bg-gradient-to-br ' + bg}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs opacity-80">{data.city}</p>
          <p className="text-3xl font-bold">{Math.round(data.temperature)}°C</p>
          <p className="text-sm opacity-90 capitalize">{data.weather_description}</p>
        </div>
        <Icon className="h-12 w-12 opacity-80" />
      </div>
      <div className="flex gap-4 mt-3 text-xs opacity-80">
        <span className="flex items-center gap-1"><Droplets className="h-3 w-3" />{data.humidity}%</span>
        <span className="flex items-center gap-1"><Wind className="h-3 w-3" />{data.pressure} hPa</span>
      </div>
    </div>
  );
}
