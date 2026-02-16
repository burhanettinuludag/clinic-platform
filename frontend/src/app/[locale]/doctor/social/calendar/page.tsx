'use client';

import { useState, useMemo } from 'react';
import { useSocialCalendar } from '@/hooks/useSocialData';
import { Link } from '@/i18n/navigation';
import { ArrowLeft, ChevronLeft, ChevronRight, Instagram, Linkedin, Share2 } from 'lucide-react';

const PLATFORM_ICONS: Record<string, typeof Instagram> = {
  instagram: Instagram,
  linkedin: Linkedin,
};

const STATUS_DOTS: Record<string, string> = {
  scheduled: 'bg-purple-500',
  published: 'bg-green-500',
  failed: 'bg-red-500',
  approved: 'bg-blue-500',
  review: 'bg-yellow-500',
};

const DAYS = ['Pzt', 'Sal', 'Car', 'Per', 'Cum', 'Cmt', 'Paz'];
const MONTHS = ['Ocak', 'Subat', 'Mart', 'Nisan', 'Mayis', 'Haziran', 'Temmuz', 'Agustos', 'Eylul', 'Ekim', 'Kasim', 'Aralik'];

export default function SocialCalendarPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [platform, setPlatform] = useState('');

  const monthStr = `${year}-${String(month).padStart(2, '0')}`;
  const { data: calendarData, isLoading } = useSocialCalendar(monthStr, platform || undefined);

  const prevMonth = () => {
    if (month === 1) { setYear(y => y - 1); setMonth(12); }
    else setMonth(m => m - 1);
  };

  const nextMonth = () => {
    if (month === 12) { setYear(y => y + 1); setMonth(1); }
    else setMonth(m => m + 1);
  };

  // Build calendar grid
  const calendarGrid = useMemo(() => {
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);
    const startDow = (firstDay.getDay() + 6) % 7; // Monday = 0

    const days: { day: number; isCurrentMonth: boolean }[] = [];

    // Previous month days
    const prevLastDay = new Date(year, month - 1, 0).getDate();
    for (let i = startDow - 1; i >= 0; i--) {
      days.push({ day: prevLastDay - i, isCurrentMonth: false });
    }

    // Current month
    for (let d = 1; d <= lastDay.getDate(); d++) {
      days.push({ day: d, isCurrentMonth: true });
    }

    // Next month fill
    while (days.length % 7 !== 0) {
      days.push({ day: days.length - lastDay.getDate() - startDow + 1, isCurrentMonth: false });
    }

    return days;
  }, [year, month]);

  // Group posts by day
  const postsByDay = useMemo(() => {
    const map: Record<number, typeof calendarData extends { posts: infer P } ? P : never> = {};
    if (calendarData?.posts) {
      for (const post of calendarData.posts) {
        if (post.scheduled_at) {
          const d = new Date(post.scheduled_at).getDate();
          if (!map[d]) map[d] = [];
          map[d].push(post);
        }
      }
    }
    return map;
  }, [calendarData]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/doctor/social" className="text-gray-400 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Yayin Takvimi</h1>
        </div>
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}
          className="px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">Tum platformlar</option>
          <option value="instagram">Instagram</option>
          <option value="linkedin">LinkedIn</option>
        </select>
      </div>

      {/* Month Navigation */}
      <div className="flex items-center justify-between bg-white rounded-xl border p-4">
        <button onClick={prevMonth} className="p-2 hover:bg-gray-100 rounded-lg">
          <ChevronLeft className="h-5 w-5 text-gray-600" />
        </button>
        <h2 className="text-lg font-semibold text-gray-900">{MONTHS[month - 1]} {year}</h2>
        <button onClick={nextMonth} className="p-2 hover:bg-gray-100 rounded-lg">
          <ChevronRight className="h-5 w-5 text-gray-600" />
        </button>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-xl border overflow-hidden">
        {/* Day headers */}
        <div className="grid grid-cols-7 border-b">
          {DAYS.map(d => (
            <div key={d} className="p-3 text-center text-sm font-medium text-gray-500 bg-gray-50">{d}</div>
          ))}
        </div>

        {/* Calendar cells */}
        <div className="grid grid-cols-7">
          {calendarGrid.map((cell, idx) => {
            const dayPosts = cell.isCurrentMonth ? (postsByDay[cell.day] || []) : [];
            const isToday = cell.isCurrentMonth && cell.day === now.getDate() && month === now.getMonth() + 1 && year === now.getFullYear();

            return (
              <div key={idx} className={`min-h-[100px] border-b border-r p-2 ${!cell.isCurrentMonth ? 'bg-gray-50' : ''}`}>
                <div className={`text-sm font-medium mb-1 ${isToday ? 'bg-cyan-600 text-white w-7 h-7 rounded-full flex items-center justify-center' : cell.isCurrentMonth ? 'text-gray-900' : 'text-gray-300'}`}>
                  {cell.day}
                </div>
                {dayPosts.slice(0, 3).map((post) => {
                  const Icon = PLATFORM_ICONS[post.platform] || Share2;
                  const dotColor = STATUS_DOTS[post.status] || 'bg-gray-400';
                  return (
                    <div key={post.id} className="flex items-center gap-1 mb-0.5 text-xs group">
                      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColor}`} />
                      <Icon className="h-3 w-3 text-gray-400 shrink-0" />
                      <span className="text-gray-600 truncate">{post.caption_tr?.substring(0, 20)}</span>
                    </div>
                  );
                })}
                {dayPosts.length > 3 && (
                  <p className="text-xs text-gray-400 mt-0.5">+{dayPosts.length - 3} daha</p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        {Object.entries(STATUS_DOTS).map(([status, color]) => (
          <div key={status} className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${color}`} />
            <span className="capitalize">{status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
