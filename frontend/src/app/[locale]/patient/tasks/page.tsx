'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useTodayTasks, useWeekTasks, useCompleteTask, useTaskStats } from '@/hooks/usePatientData';
import { CheckCircle2, Circle, Trophy, Flame, Target } from 'lucide-react';

export default function TasksPage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState<'today' | 'week'>('today');
  const { data: todayTasks, isLoading: todayLoading } = useTodayTasks();
  const { data: weekTasks, isLoading: weekLoading } = useWeekTasks();
  const { data: stats } = useTaskStats();
  const completeMutation = useCompleteTask();

  const handleComplete = (taskTemplateId: string) => {
    const today = new Date().toISOString().split('T')[0];
    completeMutation.mutate({
      task_template: taskTemplateId,
      completed_date: today,
    });
  };

  const tasks = activeTab === 'today' ? todayTasks : weekTasks;
  const isLoading = activeTab === 'today' ? todayLoading : weekLoading;

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('patient.tasks.title')}</h1>

      {/* Stats Bar */}
      {stats && (
        <div className="flex gap-4 mb-6 overflow-x-auto">
          <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-4 py-2.5 text-sm whitespace-nowrap">
            <Target className="w-4 h-4 text-blue-600" />
            <span className="text-gray-500">{t('common.today')}:</span>
            <span className="font-semibold">{stats.completed_today}</span>
          </div>
          <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-4 py-2.5 text-sm whitespace-nowrap">
            <Trophy className="w-4 h-4 text-yellow-500" />
            <span className="text-gray-500">{t('common.thisWeek')}:</span>
            <span className="font-semibold">{stats.completed_this_week}</span>
          </div>
          <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-4 py-2.5 text-sm whitespace-nowrap">
            <Flame className="w-4 h-4 text-orange-500" />
            <span className="text-gray-500">{t('common.streak')}:</span>
            <span className="font-semibold">{stats.current_streak} {t('patient.dashboard.days')}</span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
        <button
          onClick={() => setActiveTab('today')}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition ${
            activeTab === 'today' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
          }`}
        >
          {t('patient.tasks.todaysTasks')}
        </button>
        <button
          onClick={() => setActiveTab('week')}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition ${
            activeTab === 'week' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
          }`}
        >
          {t('patient.tasks.weeklyTasks')}
        </button>
      </div>

      {/* Task List */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">{t('common.loading')}</div>
      ) : tasks && tasks.length > 0 ? (
        <div className="space-y-3">
          {tasks.map((task) => {
            const isCompleted = task.is_completed_today;
            return (
              <div
                key={task.id}
                className={`bg-white rounded-xl border p-4 transition-all ${
                  isCompleted ? 'border-green-200 bg-green-50/30' : 'border-gray-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => !isCompleted && handleComplete(task.id)}
                    disabled={isCompleted || completeMutation.isPending}
                    className="mt-0.5 flex-shrink-0"
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-6 h-6 text-green-500" />
                    ) : (
                      <Circle className="w-6 h-6 text-gray-300 hover:text-blue-400 transition" />
                    )}
                  </button>
                  <div className="flex-1">
                    <h3 className={`text-sm font-medium ${isCompleted ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-xs text-gray-400 mt-1">{task.description}</p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">
                        {t(`patient.tasks.taskTypes.${task.task_type}`)}
                      </span>
                      <span className="text-xs text-gray-400">
                        +{task.points} {t('common.points')}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">
                        {task.frequency === 'daily' ? t('patient.tasks.daily') : t('patient.tasks.weekly')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">{t('patient.dashboard.noTasks')}</div>
      )}
    </div>
  );
}
