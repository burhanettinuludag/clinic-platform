'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, FileText, Newspaper, Eye, Star, TrendingUp, Loader2 } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '@/lib/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function useOverview() {
  return useQuery({ queryKey: ['analytics-overview'], queryFn: async () => (await api.get('/doctor/analytics/overview/')).data });
}

function useContentStats(period: string) {
  return useQuery({ queryKey: ['analytics-content-stats', period], queryFn: async () => (await api.get(`/doctor/analytics/content-stats/?period=${period}`)).data });
}

function StatCard({ label, value, icon: Icon, color }: { label: string; value: number | string; icon: any; color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600', green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600', red: 'bg-red-50 text-red-600', purple: 'bg-purple-50 text-purple-600',
  };
  return (
    <div className="rounded-xl border bg-white p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-500">{label}</span>
        <div className={'rounded-lg p-2 ' + (colors[color] || colors.blue)}><Icon className="h-4 w-4" /></div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function fmtMonth(d: string) {
  if (!d) return '';
  const date = new Date(d);
  return date.toLocaleDateString('tr-TR', { month: 'short', year: '2-digit' });
}

function fmtDay(d: string) {
  if (!d) return '';
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' });
}

const STATUS_LABELS: Record<string, string> = {
  draft: 'Taslak', review: 'Inceleme', approved: 'Onaylandi', published: 'Yayinda', archived: 'Arsiv', revision: 'Revizyon',
};

export default function AnalyticsPage() {
  const [period, setPeriod] = useState('6months');
  const { data: overview, isLoading: loadO } = useOverview();
  const { data: stats, isLoading: loadS } = useContentStats(period);

  if (loadO || loadS) {
    return <div className="flex items-center justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>;
  }

  const articleMonthly = (stats?.articles_by_month || []).map((d: any) => ({ ...d, date: fmtMonth(d.date) }));
  const newsMonthly = (stats?.news_by_month || []).map((d: any) => ({ ...d, date: fmtMonth(d.date) }));
  const viewsDaily = (stats?.views_by_day || []).map((d: any) => ({ ...d, date: fmtDay(d.date) }));
  const statusDist = (stats?.status_distribution || []).map((d: any) => ({ name: STATUS_LABELS[d.status] || d.status, value: d.count }));

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <BarChart3 className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">Analytics</h1>
        </div>
        <select value={period} onChange={e => setPeriod(e.target.value)} className="rounded-lg border px-3 py-1.5 text-sm bg-white">
          <option value="3months">Son 3 Ay</option>
          <option value="6months">Son 6 Ay</option>
          <option value="12months">Son 12 Ay</option>
        </select>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <StatCard label="Toplam Makale" value={overview?.articles?.total || 0} icon={FileText} color="blue" />
        <StatCard label="Yayinda" value={overview?.articles?.published || 0} icon={TrendingUp} color="green" />
        <StatCard label="Toplam Haber" value={overview?.news?.total || 0} icon={Newspaper} color="orange" />
        <StatCard label="Toplam Goruntulenme" value={overview?.total_views || 0} icon={Eye} color="purple" />
        <StatCard label="Ort. Puan" value={overview?.avg_rating || 0} icon={Star} color="red" />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Aylik Makale */}
        <div className="rounded-xl border bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Aylik Yayinlanan Makale</h3>
          {articleMonthly.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={articleMonthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Makale" />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-sm text-gray-400 text-center py-8">Veri yok</p>}
        </div>

        {/* Aylik Haber */}
        <div className="rounded-xl border bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Aylik Yayinlanan Haber</h3>
          {newsMonthly.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={newsMonthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} name="Haber" />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-sm text-gray-400 text-center py-8">Veri yok</p>}
        </div>

        {/* Gunluk Goruntulenme */}
        <div className="rounded-xl border bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Gunluk Goruntulenme (30 gun)</h3>
          {viewsDaily.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={viewsDaily}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} name="Goruntulenme" />
              </LineChart>
            </ResponsiveContainer>
          ) : <p className="text-sm text-gray-400 text-center py-8">Veri yok</p>}
        </div>

        {/* Status Dagilimi */}
        <div className="rounded-xl border bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Makale Durum Dagilimi</h3>
          {statusDist.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={statusDist} cx="50%" cy="50%" innerRadius={50} outerRadius={90} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {statusDist.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="text-sm text-gray-400 text-center py-8">Veri yok</p>}
        </div>
      </div>
    </div>
  );
}
