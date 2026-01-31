'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import {
  Wind, Sparkles, Droplet, Moon, Calendar,
  Play, Pause, RotateCcw, CheckCircle2, Timer,
  Plus, Minus, Target, TrendingUp
} from 'lucide-react';
import api from '@/lib/api';
import {
  BreathingExercise,
  RelaxationExercise,
  WaterIntakeLog,
  SleepLog
} from '@/lib/types/patient';

type TabType = 'breathing' | 'relaxation' | 'water' | 'sleep';

export default function WellnessPage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState<TabType>('breathing');

  const tabs = [
    { id: 'breathing' as TabType, label: 'Nefes', icon: Wind },
    { id: 'relaxation' as TabType, label: 'Gevşeme', icon: Sparkles },
    { id: 'water' as TabType, label: 'Su', icon: Droplet },
    { id: 'sleep' as TabType, label: 'Uyku', icon: Moon },
  ];

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-3 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Wellness</h1>
          <p className="text-gray-500 text-sm">Sağlığınız için egzersizler ve takip</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'breathing' && <BreathingTab />}
      {activeTab === 'relaxation' && <RelaxationTab />}
      {activeTab === 'water' && <WaterTab />}
      {activeTab === 'sleep' && <SleepTab />}
    </div>
  );
}

function BreathingTab() {
  const [exercises, setExercises] = useState<BreathingExercise[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<BreathingExercise | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [phase, setPhase] = useState<'inhale' | 'hold' | 'exhale' | 'hold2'>('inhale');
  const [timeLeft, setTimeLeft] = useState(0);
  const [currentCycle, setCurrentCycle] = useState(1);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    api.get('/wellness/breathing/').then((res) => setExercises(res.data.results || res.data));
  }, []);

  const startExercise = (exercise: BreathingExercise) => {
    setSelectedExercise(exercise);
    setIsRunning(true);
    setPhase('inhale');
    setTimeLeft(exercise.inhale_seconds);
    setCurrentCycle(1);
    setCompleted(false);
  };

  const resetExercise = () => {
    setIsRunning(false);
    setPhase('inhale');
    setTimeLeft(0);
    setCurrentCycle(1);
    setCompleted(false);
  };

  useEffect(() => {
    if (!isRunning || !selectedExercise || completed) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Sonraki faza geç
          if (phase === 'inhale') {
            if (selectedExercise.hold_seconds > 0) {
              setPhase('hold');
              return selectedExercise.hold_seconds;
            } else {
              setPhase('exhale');
              return selectedExercise.exhale_seconds;
            }
          } else if (phase === 'hold') {
            setPhase('exhale');
            return selectedExercise.exhale_seconds;
          } else if (phase === 'exhale') {
            if (selectedExercise.hold_after_exhale_seconds > 0) {
              setPhase('hold2');
              return selectedExercise.hold_after_exhale_seconds;
            } else {
              // Döngüyü tamamla
              if (currentCycle >= selectedExercise.cycles) {
                setCompleted(true);
                setIsRunning(false);
                // Seansı kaydet
                api.post('/wellness/sessions/', {
                  breathing_exercise: selectedExercise.id,
                  duration_seconds: selectedExercise.total_duration,
                });
                return 0;
              }
              setCurrentCycle((c) => c + 1);
              setPhase('inhale');
              return selectedExercise.inhale_seconds;
            }
          } else if (phase === 'hold2') {
            if (currentCycle >= selectedExercise.cycles) {
              setCompleted(true);
              setIsRunning(false);
              api.post('/wellness/sessions/', {
                breathing_exercise: selectedExercise.id,
                duration_seconds: selectedExercise.total_duration,
              });
              return 0;
            }
            setCurrentCycle((c) => c + 1);
            setPhase('inhale');
            return selectedExercise.inhale_seconds;
          }
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isRunning, phase, currentCycle, selectedExercise, completed]);

  const phaseLabels = {
    inhale: 'Nefes Al',
    hold: 'Tut',
    exhale: 'Nefes Ver',
    hold2: 'Bekle',
  };

  const phaseColors = {
    inhale: 'from-blue-400 to-blue-600',
    hold: 'from-purple-400 to-purple-600',
    exhale: 'from-green-400 to-green-600',
    hold2: 'from-gray-400 to-gray-600',
  };

  if (selectedExercise) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <div className="text-center space-y-6">
          <h2 className="text-xl font-semibold">{selectedExercise.name_tr}</h2>

          {completed ? (
            <div className="space-y-4">
              <div className="w-32 h-32 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle2 className="w-16 h-16 text-green-600" />
              </div>
              <p className="text-lg text-green-600 font-medium">Tebrikler! Egzersizi tamamladınız.</p>
              <button
                onClick={resetExercise}
                className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Geri Dön
              </button>
            </div>
          ) : (
            <>
              <div className={`w-48 h-48 mx-auto bg-gradient-to-br ${phaseColors[phase]} rounded-full flex items-center justify-center animate-pulse`}>
                <div className="text-center text-white">
                  <div className="text-5xl font-bold">{timeLeft}</div>
                  <div className="text-lg">{phaseLabels[phase]}</div>
                </div>
              </div>

              <div className="text-gray-500">
                Döngü {currentCycle} / {selectedExercise.cycles}
              </div>

              <div className="flex justify-center gap-4">
                <button
                  onClick={() => setIsRunning(!isRunning)}
                  className="p-4 bg-blue-600 text-white rounded-full hover:bg-blue-700"
                >
                  {isRunning ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                </button>
                <button
                  onClick={resetExercise}
                  className="p-4 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300"
                >
                  <RotateCcw className="w-6 h-6" />
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {exercises.map((exercise) => (
        <div key={exercise.id} className="bg-white rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-3 bg-${exercise.color}-100 rounded-lg`}>
                <Wind className={`w-5 h-5 text-${exercise.color}-600`} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{exercise.name_tr}</h3>
                <p className="text-sm text-gray-500">{exercise.description_tr}</p>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                  <span>{exercise.cycles} döngü</span>
                  <span>{Math.round(exercise.total_duration / 60)} dk</span>
                  <span className="capitalize">{exercise.difficulty === 'beginner' ? 'Başlangıç' : exercise.difficulty === 'intermediate' ? 'Orta' : 'İleri'}</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => startExercise(exercise)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Başla
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function RelaxationTab() {
  const [exercises, setExercises] = useState<RelaxationExercise[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<RelaxationExercise | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    api.get('/wellness/relaxation/').then((res) => setExercises(res.data.results || res.data));
  }, []);

  const startExercise = (exercise: RelaxationExercise) => {
    setSelectedExercise(exercise);
    setCurrentStep(0);
    setIsRunning(true);
  };

  const nextStep = () => {
    if (!selectedExercise) return;
    if (currentStep < selectedExercise.steps_tr.length - 1) {
      setCurrentStep((s) => s + 1);
    } else {
      // Tamamlandı
      api.post('/wellness/sessions/', {
        relaxation_exercise: selectedExercise.id,
        duration_seconds: selectedExercise.duration_minutes * 60,
      });
      setSelectedExercise(null);
      setCurrentStep(0);
      setIsRunning(false);
    }
  };

  const typeLabels: Record<string, string> = {
    pmr: 'Progresif Kas Gevşetme',
    body_scan: 'Vücut Tarama',
    visualization: 'Görselleştirme',
    grounding: 'Topraklama',
    mindfulness: 'Farkındalık',
  };

  if (selectedExercise) {
    const steps = selectedExercise.steps_tr;
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-xl font-semibold">{selectedExercise.name_tr}</h2>
            <p className="text-gray-500 text-sm mt-1">
              Adım {currentStep + 1} / {steps.length}
            </p>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>

          <div className="bg-purple-50 rounded-xl p-6 min-h-[150px] flex items-center justify-center">
            <p className="text-lg text-center text-purple-900">{steps[currentStep]}</p>
          </div>

          <div className="flex justify-center gap-4">
            <button
              onClick={() => {
                setSelectedExercise(null);
                setCurrentStep(0);
              }}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              İptal
            </button>
            <button
              onClick={nextStep}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              {currentStep < steps.length - 1 ? 'Sonraki' : 'Tamamla'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {exercises.map((exercise) => (
        <div key={exercise.id} className="bg-white rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Sparkles className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{exercise.name_tr}</h3>
                <p className="text-sm text-gray-500">{exercise.description_tr}</p>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                  <span>{typeLabels[exercise.exercise_type]}</span>
                  <span>{exercise.duration_minutes} dk</span>
                  <span>{exercise.steps_tr.length} adım</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => startExercise(exercise)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Başla
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function WaterTab() {
  const [todayLog, setTodayLog] = useState<WaterIntakeLog | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchToday = useCallback(async () => {
    try {
      const res = await api.get('/wellness/water/today/');
      setTodayLog(res.data);
    } catch {
      // İlk kez
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchToday();
  }, [fetchToday]);

  const addGlass = async () => {
    try {
      const res = await api.post('/wellness/water/add_glass/');
      setTodayLog(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Yükleniyor...</div>;
  }

  const glasses = todayLog?.glasses || 0;
  const target = todayLog?.target_glasses || 8;
  const percentage = Math.min(100, Math.round((glasses / target) * 100));

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="text-center space-y-6">
        <h2 className="text-xl font-semibold">Günlük Su Tüketimi</h2>

        {/* Circular Progress */}
        <div className="relative w-48 h-48 mx-auto">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="96"
              cy="96"
              r="88"
              fill="none"
              stroke="#E5E7EB"
              strokeWidth="12"
            />
            <circle
              cx="96"
              cy="96"
              r="88"
              fill="none"
              stroke="#3B82F6"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${(percentage / 100) * 553} 553`}
              className="transition-all duration-500"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <Droplet className="w-8 h-8 text-blue-500 mb-1" />
            <span className="text-3xl font-bold text-gray-900">{glasses}</span>
            <span className="text-gray-500">/ {target} bardak</span>
          </div>
        </div>

        <div className="text-gray-600">
          {glasses * 250} ml / {target * 250} ml
        </div>

        <button
          onClick={addGlass}
          className="px-8 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 flex items-center gap-2 mx-auto text-lg"
        >
          <Plus className="w-5 h-5" />
          Bardak Ekle
        </button>

        {percentage >= 100 && (
          <div className="flex items-center justify-center gap-2 text-green-600">
            <CheckCircle2 className="w-5 h-5" />
            <span className="font-medium">Günlük hedefinizi tamamladınız!</span>
          </div>
        )}
      </div>
    </div>
  );
}

function SleepTab() {
  const [logs, setLogs] = useState<SleepLog[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    bedtime: '23:00',
    wake_time: '07:00',
    sleep_quality: 3,
    had_nightmare: false,
    woke_up_during_night: 0,
    notes: '',
  });

  useEffect(() => {
    api.get('/wellness/sleep/').then((res) => setLogs(res.data.results || res.data));
  }, []);

  const calculateDuration = (bedtime: string, wakeTime: string) => {
    const [bedH, bedM] = bedtime.split(':').map(Number);
    const [wakeH, wakeM] = wakeTime.split(':').map(Number);

    let bedMinutes = bedH * 60 + bedM;
    let wakeMinutes = wakeH * 60 + wakeM;

    if (wakeMinutes < bedMinutes) {
      wakeMinutes += 24 * 60; // Ertesi gün
    }

    return wakeMinutes - bedMinutes;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const duration = calculateDuration(formData.bedtime, formData.wake_time);
      await api.post('/wellness/sleep/', {
        ...formData,
        sleep_duration_minutes: duration,
      });
      setShowForm(false);
      const res = await api.get('/wellness/sleep/');
      setLogs(res.data.results || res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const qualityLabels = ['', 'Çok Kötü', 'Kötü', 'Orta', 'İyi', 'Çok İyi'];
  const qualityColors = ['', 'bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-400', 'bg-green-600'];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Uyku Kayıtları</h2>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Kayıt Ekle
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Tarih</label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Uyku Kalitesi</label>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((q) => (
                    <button
                      key={q}
                      type="button"
                      onClick={() => setFormData({ ...formData, sleep_quality: q })}
                      className={`flex-1 py-2 rounded ${formData.sleep_quality === q ? qualityColors[q] + ' text-white' : 'bg-gray-100'}`}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Yatış Saati</label>
                <input
                  type="time"
                  value={formData.bedtime}
                  onChange={(e) => setFormData({ ...formData, bedtime: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Kalkış Saati</label>
                <input
                  type="time"
                  value={formData.wake_time}
                  onChange={(e) => setFormData({ ...formData, wake_time: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
            </div>

            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.had_nightmare}
                  onChange={(e) => setFormData({ ...formData, had_nightmare: e.target.checked })}
                />
                <span className="text-sm">Kabus gördüm</span>
              </label>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Gece uyanma:</span>
                <input
                  type="number"
                  min="0"
                  value={formData.woke_up_during_night}
                  onChange={(e) => setFormData({ ...formData, woke_up_during_night: parseInt(e.target.value) || 0 })}
                  className="w-16 px-2 py-1 border rounded"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-lg"
              >
                İptal
              </button>
              <button
                type="submit"
                className="flex-1 py-2 bg-indigo-600 text-white rounded-lg"
              >
                Kaydet
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-2">
        {logs.map((log) => (
          <div key={log.id} className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Moon className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <div className="font-medium">
                    {new Date(log.date).toLocaleDateString('tr-TR', {
                      day: 'numeric',
                      month: 'long',
                    })}
                  </div>
                  <div className="text-sm text-gray-500">
                    {log.bedtime} - {log.wake_time} • {log.sleep_hours} saat
                  </div>
                </div>
              </div>
              <div className={`px-3 py-1 rounded-full text-white text-sm ${qualityColors[log.sleep_quality]}`}>
                {qualityLabels[log.sleep_quality]}
              </div>
            </div>
          </div>
        ))}

        {logs.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Henüz uyku kaydı bulunmuyor
          </div>
        )}
      </div>
    </div>
  );
}
