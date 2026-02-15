'use client';

import WeatherWidget from '@/components/patient/WeatherWidget';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/context/AuthContext';
import { Link } from '@/i18n/navigation';
import {
  useTodayTasks,
  useTaskStats,
  useMigraineStats,
  useMedicationAdherence,
} from '@/hooks/usePatientData';
import {
  Activity,
  CheckSquare,
  Brain,
  Pill,
  Flame,
  ArrowRight,
  CheckCircle2,
  Circle,
} from 'lucide-react';

export default function PatientDashboard() {
  const t = useTranslations();
  const { user } = useAuth();
  const { data: todayTasks, isLoading: tasksLoading } = useTodayTasks();
  const { data: taskStats } = useTaskStats();
  const { data: migraineStats } = useMigraineStats();
  const { data: adherence } = useMedicationAdherence();

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        {t('patient.dashboard.title')}, {user?.first_name}!
      </h1>

      {/* Stats Grid */}
      <div className="mb-6"><WeatherWidget city="Izmir" /></div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-2">
            <CheckSquare className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-gray-500">{t('patient.dashboard.completedToday')}</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {taskStats?.completed_today ?? 0}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-green-600" />
            <span className="text-xs text-gray-500">{t('patient.dashboard.weeklyProgress')}</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {taskStats?.completed_this_week ?? 0}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-2">
            <Flame className="w-4 h-4 text-orange-600" />
            <span className="text-xs text-gray-500">{t('patient.dashboard.currentStreak')}</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {taskStats?.current_streak ?? 0} {t('patient.dashboard.days')}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-2">
            <Pill className="w-4 h-4 text-purple-600" />
            <span className="text-xs text-gray-500">{t('patient.medications.adherenceRate')}</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            %{adherence?.adherence_rate ?? 0}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Tasks */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">{t('patient.dashboard.todayTasks')}</h2>
            <Link href="/patient/tasks" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
              {t('common.next')} <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {tasksLoading ? (
            <div className="text-sm text-gray-500 text-center py-6">{t('common.loading')}</div>
          ) : todayTasks && todayTasks.length > 0 ? (
            <div className="space-y-2">
              {todayTasks.slice(0, 5).map((task) => (
                <div
                  key={task.id}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  {task.is_completed_today ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                  ) : (
                    <Circle className="w-5 h-5 text-gray-300 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <span className={`text-sm ${task.is_completed_today ? 'line-through text-gray-400' : 'text-gray-700'}`}>
                      {task.title}
                    </span>
                    <span className="block text-xs text-gray-400">
                      +{task.points} {t('common.points')}
                    </span>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-500">
                    {t(`patient.tasks.taskTypes.${task.task_type}`)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500 mb-3">{t('patient.dashboard.noTasks')}</p>
              <Link
                href="/patient/modules"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
              >
                {t('patient.dashboard.selectModule')}
              </Link>
            </div>
          )}
        </div>

        {/* Migraine Stats */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              {t('patient.migraine.title')}
            </h2>
            <Link href="/patient/migraine" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
              {t('common.next')} <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {migraineStats ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-red-50 rounded-lg p-3">
                  <div className="text-xs text-red-600 mb-1">{t('patient.migraine.attacksThisMonth')}</div>
                  <div className="text-xl font-bold text-red-700">{migraineStats.attacks_this_month}</div>
                </div>
                <div className="bg-orange-50 rounded-lg p-3">
                  <div className="text-xs text-orange-600 mb-1">{t('patient.migraine.avgIntensity')}</div>
                  <div className="text-xl font-bold text-orange-700">{migraineStats.avg_intensity}/10</div>
                </div>
              </div>
              {migraineStats.most_common_triggers.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 mb-2">{t('patient.migraine.commonTriggers')}</div>
                  <div className="flex flex-wrap gap-2">
                    {migraineStats.most_common_triggers.slice(0, 3).map((trigger, i) => (
                      <span key={i} className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                        {trigger.name} ({trigger.count})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-sm text-gray-500 text-center py-6">
              {t('patient.migraine.noAttacks')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
