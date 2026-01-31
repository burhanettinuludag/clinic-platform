'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import {
  Trophy, Star, Flame, Target, Award, Medal,
  TrendingUp, Calendar, Zap, Lock, CheckCircle2
} from 'lucide-react';
import api from '@/lib/api';
import {
  GamificationSummary,
  Badge,
  UserBadge,
  UserStreak,
  UserAchievement
} from '@/lib/types/patient';

type TabType = 'overview' | 'badges' | 'achievements' | 'streaks';

export default function RewardsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [summary, setSummary] = useState<GamificationSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/gamification/summary/')
      .then((res) => setSummary(res.data))
      .finally(() => setLoading(false));
  }, []);

  const tabs = [
    { id: 'overview' as TabType, label: 'Genel', icon: TrendingUp },
    { id: 'badges' as TabType, label: 'Rozetler', icon: Award },
    { id: 'achievements' as TabType, label: 'Hedefler', icon: Target },
    { id: 'streaks' as TabType, label: 'Seriler', icon: Flame },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur">
              <Trophy className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Ödüller & İlerleme</h1>
              <p className="text-white/80">Başarılarınızı takip edin</p>
            </div>
          </div>
          {summary && (
            <div className="text-right">
              <div className="text-3xl font-bold">{summary.points.total_points}</div>
              <div className="text-white/80">Toplam Puan</div>
            </div>
          )}
        </div>

        {/* Level Progress */}
        {summary && (
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span>Seviye {summary.points.level}</span>
              <span>{summary.points.level_progress} / 100</span>
            </div>
            <div className="w-full bg-white/30 rounded-full h-3">
              <div
                className="bg-white h-3 rounded-full transition-all"
                style={{ width: `${summary.points.level_progress}%` }}
              />
            </div>
            <div className="text-sm text-white/80 mt-1">
              Sonraki seviyeye {summary.points.points_to_next_level} puan kaldı
            </div>
          </div>
        )}
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
                  ? 'bg-yellow-500 text-white'
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
      {activeTab === 'overview' && summary && <OverviewTab summary={summary} />}
      {activeTab === 'badges' && <BadgesTab />}
      {activeTab === 'achievements' && <AchievementsTab />}
      {activeTab === 'streaks' && summary && <StreaksTab streaks={summary.streaks} />}
    </div>
  );
}

function OverviewTab({ summary }: { summary: GamificationSummary }) {
  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Award className="w-5 h-5 text-yellow-600" />}
          label="Rozetler"
          value={summary.stats.total_badges}
          color="yellow"
        />
        <StatCard
          icon={<Flame className="w-5 h-5 text-orange-600" />}
          label="Aktif Seriler"
          value={summary.stats.active_streaks}
          color="orange"
        />
        <StatCard
          icon={<Target className="w-5 h-5 text-green-600" />}
          label="Tamamlanan"
          value={summary.stats.completed_achievements}
          color="green"
        />
        <StatCard
          icon={<Star className="w-5 h-5 text-blue-600" />}
          label="Bu Hafta"
          value={summary.points.points_this_week}
          suffix=" puan"
          color="blue"
        />
      </div>

      {/* Recent Badges */}
      {summary.recent_badges.length > 0 && (
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">Son Kazanılan Rozetler</h3>
          <div className="flex flex-wrap gap-3">
            {summary.recent_badges.map((ub) => (
              <BadgeCard key={ub.id} badge={ub.badge} earned />
            ))}
          </div>
        </div>
      )}

      {/* Active Achievements */}
      {summary.active_achievements.length > 0 && (
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">Aktif Hedefler</h3>
          <div className="space-y-3">
            {summary.active_achievements.map((ua) => (
              <AchievementProgress key={ua.id} userAchievement={ua} />
            ))}
          </div>
        </div>
      )}

      {/* Streaks */}
      {summary.streaks.length > 0 && (
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">Serileriniz</h3>
          <div className="grid gap-3">
            {summary.streaks.map((streak) => (
              <StreakCard key={streak.id} streak={streak} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function BadgesTab() {
  const [myBadges, setMyBadges] = useState<UserBadge[]>([]);
  const [availableBadges, setAvailableBadges] = useState<Badge[]>([]);

  useEffect(() => {
    api.get('/gamification/badges/my_badges/').then((res) => setMyBadges(res.data));
    api.get('/gamification/badges/available/').then((res) => setAvailableBadges(res.data));
  }, []);

  const rarityColors: Record<string, string> = {
    common: 'from-gray-400 to-gray-500',
    uncommon: 'from-green-400 to-green-600',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-yellow-400 to-orange-500',
  };

  const rarityLabels: Record<string, string> = {
    common: 'Yaygın',
    uncommon: 'Nadir',
    rare: 'Çok Nadir',
    epic: 'Epik',
    legendary: 'Efsanevi',
  };

  return (
    <div className="space-y-6">
      {/* Earned Badges */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-4">
          Kazanılan Rozetler ({myBadges.length})
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {myBadges.map((ub) => (
            <div
              key={ub.id}
              className="bg-white rounded-xl p-4 shadow-sm text-center"
            >
              <div className={`w-16 h-16 mx-auto mb-3 rounded-full bg-gradient-to-br ${rarityColors[ub.badge.rarity]} flex items-center justify-center`}>
                <Award className="w-8 h-8 text-white" />
              </div>
              <h4 className="font-semibold text-gray-900">{ub.badge.name_tr}</h4>
              <p className="text-sm text-gray-500 mt-1">{ub.badge.description_tr}</p>
              <div className="mt-2 text-xs text-gray-400">
                {new Date(ub.earned_at).toLocaleDateString('tr-TR')}
              </div>
              <div className={`mt-2 inline-block px-2 py-1 rounded text-xs text-white bg-gradient-to-r ${rarityColors[ub.badge.rarity]}`}>
                {rarityLabels[ub.badge.rarity]}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Available Badges */}
      {availableBadges.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-4">
            Kazanılabilir Rozetler ({availableBadges.length})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {availableBadges.map((badge) => (
              <div
                key={badge.id}
                className="bg-gray-50 rounded-xl p-4 text-center opacity-60"
              >
                <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-gray-300 flex items-center justify-center">
                  <Lock className="w-8 h-8 text-gray-500" />
                </div>
                <h4 className="font-semibold text-gray-700">{badge.name_tr}</h4>
                <p className="text-sm text-gray-500 mt-1">{badge.description_tr}</p>
                <div className={`mt-2 inline-block px-2 py-1 rounded text-xs text-white bg-gradient-to-r ${rarityColors[badge.rarity]}`}>
                  {rarityLabels[badge.rarity]}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function AchievementsTab() {
  const [daily, setDaily] = useState<UserAchievement[]>([]);
  const [progress, setProgress] = useState<{ active: UserAchievement[]; completed: UserAchievement[] }>({
    active: [],
    completed: [],
  });

  useEffect(() => {
    api.get('/gamification/achievements/daily/').then((res) => setDaily(res.data));
    api.get('/gamification/achievements/my_progress/').then((res) => setProgress(res.data));
  }, []);

  return (
    <div className="space-y-6">
      {/* Daily */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-600" />
          Günlük Hedefler
        </h3>
        <div className="space-y-3">
          {daily.map((ua) => (
            <AchievementProgress key={ua.id} userAchievement={ua} />
          ))}
        </div>
      </div>

      {/* Active */}
      {progress.active.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-4">Devam Eden Hedefler</h3>
          <div className="space-y-3">
            {progress.active.map((ua) => (
              <AchievementProgress key={ua.id} userAchievement={ua} />
            ))}
          </div>
        </div>
      )}

      {/* Completed */}
      {progress.completed.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            Tamamlanan ({progress.completed.length})
          </h3>
          <div className="space-y-3">
            {progress.completed.slice(0, 10).map((ua) => (
              <AchievementProgress key={ua.id} userAchievement={ua} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StreaksTab({ streaks }: { streaks: UserStreak[] }) {
  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-gray-900">Tüm Serileriniz</h3>
      {streaks.length === 0 ? (
        <div className="bg-white rounded-xl p-8 text-center text-gray-500">
          Henüz aktif seriniz yok. Günlük kayıtlar yaparak seri başlatın!
        </div>
      ) : (
        <div className="grid gap-4">
          {streaks.map((streak) => (
            <StreakCard key={streak.id} streak={streak} detailed />
          ))}
        </div>
      )}
    </div>
  );
}

// Components
function StatCard({
  icon,
  label,
  value,
  suffix = '',
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  suffix?: string;
  color: string;
}) {
  const bgColors: Record<string, string> = {
    yellow: 'bg-yellow-50',
    orange: 'bg-orange-50',
    green: 'bg-green-50',
    blue: 'bg-blue-50',
  };

  return (
    <div className={`${bgColors[color]} rounded-xl p-4`}>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-sm text-gray-600">{label}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900">
        {value}{suffix}
      </div>
    </div>
  );
}

function BadgeCard({ badge, earned }: { badge: Badge; earned?: boolean }) {
  return (
    <div className={`flex items-center gap-3 px-4 py-2 rounded-lg ${earned ? 'bg-yellow-50' : 'bg-gray-50'}`}>
      <Award className={`w-6 h-6 ${earned ? 'text-yellow-600' : 'text-gray-400'}`} />
      <div>
        <div className="font-medium text-sm">{badge.name_tr}</div>
        <div className="text-xs text-gray-500">+{badge.points_reward} puan</div>
      </div>
    </div>
  );
}

function AchievementProgress({ userAchievement }: { userAchievement: UserAchievement }) {
  const { achievement, current_progress, progress_percentage, is_completed } = userAchievement;

  return (
    <div className={`bg-white rounded-xl p-4 shadow-sm ${is_completed ? 'border-2 border-green-500' : ''}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${is_completed ? 'bg-green-100' : 'bg-gray-100'}`}>
            {is_completed ? (
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            ) : (
              <Target className="w-5 h-5 text-gray-600" />
            )}
          </div>
          <div>
            <h4 className="font-medium text-gray-900">{achievement.name_tr}</h4>
            <p className="text-sm text-gray-500">{achievement.description_tr}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium text-gray-900">
            {current_progress} / {achievement.target_value}
          </div>
          <div className="text-xs text-yellow-600">+{achievement.points_reward} puan</div>
        </div>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all ${is_completed ? 'bg-green-500' : 'bg-blue-500'}`}
          style={{ width: `${progress_percentage}%` }}
        />
      </div>
    </div>
  );
}

function StreakCard({ streak, detailed }: { streak: UserStreak; detailed?: boolean }) {
  const isActive = streak.is_active_today;

  return (
    <div className={`bg-white rounded-xl p-4 shadow-sm ${isActive ? 'border-l-4 border-orange-500' : ''}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isActive ? 'bg-orange-100' : 'bg-gray-100'}`}>
            <Flame className={`w-5 h-5 ${isActive ? 'text-orange-600' : 'text-gray-400'}`} />
          </div>
          <div>
            <h4 className="font-medium text-gray-900">{streak.streak_type_display}</h4>
            {detailed && streak.streak_started_at && (
              <p className="text-sm text-gray-500">
                Başlangıç: {new Date(streak.streak_started_at).toLocaleDateString('tr-TR')}
              </p>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-1">
            <Flame className={`w-4 h-4 ${isActive ? 'text-orange-500' : 'text-gray-400'}`} />
            <span className="text-2xl font-bold text-gray-900">{streak.current_streak}</span>
          </div>
          <div className="text-xs text-gray-500">En yüksek: {streak.longest_streak}</div>
        </div>
      </div>
    </div>
  );
}
