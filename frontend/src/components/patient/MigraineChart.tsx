'use client';

import { useTranslations } from 'next-intl';
import { useMigraineChart } from '@/hooks/usePatientData';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Line,
  ComposedChart,
} from 'recharts';

interface MigraineChartProps {
  months?: number;
}

export default function MigraineChart({ months = 6 }: MigraineChartProps) {
  const t = useTranslations();
  const { data: chartData, isLoading } = useMigraineChart(months);

  if (isLoading) {
    return <div className="h-64 flex items-center justify-center text-gray-400">{t('common.loading')}</div>;
  }

  if (!chartData || chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        {t('patient.migraine.noAttacks')}
      </div>
    );
  }

  const formattedData = chartData.map((item) => ({
    ...item,
    month: new Date(item.month + '-01').toLocaleDateString('tr-TR', {
      month: 'short',
      year: '2-digit',
    }),
  }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" fontSize={12} tick={{ fill: '#9ca3af' }} />
          <YAxis yAxisId="left" fontSize={12} tick={{ fill: '#9ca3af' }} />
          <YAxis yAxisId="right" orientation="right" fontSize={12} tick={{ fill: '#9ca3af' }} />
          <Tooltip
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              fontSize: '12px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Bar
            yAxisId="left"
            dataKey="count"
            fill="#ef4444"
            radius={[4, 4, 0, 0]}
            name="Atak Sayisi"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="avg_intensity"
            stroke="#f97316"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Ort. Siddet"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
