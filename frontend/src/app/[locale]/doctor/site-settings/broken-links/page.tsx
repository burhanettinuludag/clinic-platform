'use client';

import { useState } from 'react';
import {
  useBrokenLinks,
  useBrokenLinkStats,
  useBrokenLinkScans,
  useTriggerScan,
  useFixBrokenLink,
  useRecheckBrokenLink,
  useBulkBrokenLinkAction,
} from '@/hooks/useSiteAdmin';
import type { BrokenLinkItem } from '@/hooks/useSiteAdmin';
import {
  Link2Off,
  Search,
  Play,
  RefreshCw,
  CheckCircle,
  XCircle,
  ExternalLink,
  AlertTriangle,
  Loader2,
  Eye,
  EyeOff,
  Wrench,
  BarChart3,
  Clock,
  Globe,
  Image,
  Video,
  FileText,
} from 'lucide-react';

const STATUS_COLORS: Record<string, string> = {
  detected: 'bg-red-100 text-red-700',
  auto_fixed: 'bg-green-100 text-green-700',
  ai_suggested: 'bg-blue-100 text-blue-700',
  manually_fixed: 'bg-emerald-100 text-emerald-700',
  ignored: 'bg-gray-100 text-gray-500',
};

const LINK_TYPE_ICONS: Record<string, React.ReactNode> = {
  internal: <Globe className="h-4 w-4" />,
  external: <ExternalLink className="h-4 w-4" />,
  image: <Image className="h-4 w-4" />,
  video: <Video className="h-4 w-4" />,
};

export default function BrokenLinksPage() {
  const [filterStatus, setFilterStatus] = useState('detected');
  const [filterType, setFilterType] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [fixingId, setFixingId] = useState<string | null>(null);
  const [fixUrl, setFixUrl] = useState('');

  const { data: stats, isLoading: statsLoading } = useBrokenLinkStats();
  const { data: links, isLoading: linksLoading } = useBrokenLinks({
    status: filterStatus || undefined,
    link_type: filterType || undefined,
    source_type: filterSource || undefined,
    search: searchQuery || undefined,
  });
  const { data: scans } = useBrokenLinkScans();
  const triggerScan = useTriggerScan();
  const fixLink = useFixBrokenLink();
  const recheckLink = useRecheckBrokenLink();
  const bulkAction = useBulkBrokenLinkAction();

  const handleTriggerScan = () => {
    if (confirm('Yeni bir link taramasi baslatmak istiyor musunuz? Bu islem birka dakika surebilir.')) {
      triggerScan.mutate();
    }
  };

  const handleFix = (id: string) => {
    if (!fixUrl.trim()) return;
    fixLink.mutate({ id, new_url: fixUrl }, {
      onSuccess: () => {
        setFixingId(null);
        setFixUrl('');
      },
    });
  };

  const handleBulkAction = (action: 'ignore' | 'recheck') => {
    if (selectedIds.length === 0) return;
    const label = action === 'ignore' ? 'yok say' : 'tekrar kontrol et';
    if (confirm(`${selectedIds.length} link icin "${label}" islemini uygulamak istiyor musunuz?`)) {
      bulkAction.mutate({ ids: selectedIds, action }, {
        onSuccess: () => setSelectedIds([]),
      });
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (!links) return;
    if (selectedIds.length === links.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(links.map((l) => l.id));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Link2Off className="h-7 w-7 text-red-500" />
            Kirik Link Yonetimi
          </h1>
          <p className="text-gray-500 mt-1">
            Sitedeki tum kirik linkleri takip edin, tamir edin veya yok sayin.
          </p>
        </div>
        <button
          onClick={handleTriggerScan}
          disabled={triggerScan.isPending}
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 flex items-center gap-2"
        >
          {triggerScan.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          Tarama Baslat
        </button>
      </div>

      {/* Success/Error messages */}
      {triggerScan.isSuccess && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
          Link taramasi baslatildi. Tamamlaninca sonuclar burada gorunecek.
        </div>
      )}
      {triggerScan.isError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {(triggerScan.error as any)?.response?.data?.error || 'Tarama baslatilamadi.'}
        </div>
      )}

      {/* Stats Cards */}
      {!statsLoading && stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard label="Toplam" value={stats.total} icon={<BarChart3 className="h-5 w-5" />} color="gray" />
          <StatCard label="Tespit Edildi" value={stats.detected} icon={<AlertTriangle className="h-5 w-5" />} color="red" />
          <StatCard label="Otomatik Tamir" value={stats.auto_fixed} icon={<CheckCircle className="h-5 w-5" />} color="green" />
          <StatCard label="Manuel Tamir" value={stats.manually_fixed} icon={<Wrench className="h-5 w-5" />} color="emerald" />
          <StatCard label="AI Onerisi" value={stats.ai_suggested} icon={<FileText className="h-5 w-5" />} color="blue" />
          <StatCard label="Yok Sayildi" value={stats.ignored} icon={<EyeOff className="h-5 w-5" />} color="gray" />
        </div>
      )}

      {/* Last Scan Info */}
      {stats?.last_scan && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Clock className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-700">
                Son Tarama: {new Date(stats.last_scan.created_at).toLocaleString('tr-TR')}
              </p>
              <p className="text-xs text-gray-500">
                {stats.last_scan.total_links_checked} link kontrol edildi,{' '}
                {stats.last_scan.broken_links_found} kirik bulundu,{' '}
                {stats.last_scan.auto_fixed_count} otomatik tamir edildi
                ({stats.last_scan.duration_seconds}s)
              </p>
            </div>
          </div>
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            stats.last_scan.status === 'completed' ? 'bg-green-100 text-green-700' :
            stats.last_scan.status === 'running' ? 'bg-yellow-100 text-yellow-700' :
            'bg-red-100 text-red-700'
          }`}>
            {stats.last_scan.status_display}
          </span>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-xl p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="URL veya icerik ara..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>
          {/* Status */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500"
          >
            <option value="">Tum Durumlar</option>
            <option value="detected">Tespit Edildi</option>
            <option value="auto_fixed">Otomatik Tamir</option>
            <option value="manually_fixed">Manuel Tamir</option>
            <option value="ai_suggested">AI Onerisi</option>
            <option value="ignored">Yok Sayildi</option>
          </select>
          {/* Link Type */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500"
          >
            <option value="">Tum Tipler</option>
            <option value="internal">Dahili</option>
            <option value="external">Harici</option>
            <option value="image">Gorsel</option>
            <option value="video">Video</option>
          </select>
          {/* Source Type */}
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500"
          >
            <option value="">Tum Kaynaklar</option>
            <option value="article">Blog Yazisi</option>
            <option value="news">Haber</option>
            <option value="education">Egitim Icerigi</option>
            <option value="announcement">Duyuru</option>
            <option value="social_link">Sosyal Medya</option>
          </select>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedIds.length > 0 && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-3 flex items-center justify-between">
          <span className="text-sm text-indigo-700 font-medium">
            {selectedIds.length} link secildi
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => handleBulkAction('ignore')}
              disabled={bulkAction.isPending}
              className="px-3 py-1.5 text-xs bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-1"
            >
              <EyeOff className="h-3 w-3" /> Yok Say
            </button>
            <button
              onClick={() => handleBulkAction('recheck')}
              disabled={bulkAction.isPending}
              className="px-3 py-1.5 text-xs bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-1"
            >
              <RefreshCw className="h-3 w-3" /> Tekrar Kontrol
            </button>
          </div>
        </div>
      )}

      {/* Links Table */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        {linksLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-teal-600" />
          </div>
        ) : !links || links.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Link2Off className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>Bu filtrelere uygun kirik link bulunamadi.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === links.length && links.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-gray-300"
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">URL</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Durum</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">HTTP</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tip</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kaynak</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kontrol</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Islemler</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {links.map((link) => (
                  <LinkRow
                    key={link.id}
                    link={link}
                    selected={selectedIds.includes(link.id)}
                    onToggle={() => toggleSelect(link.id)}
                    isFixing={fixingId === link.id}
                    fixUrl={fixingId === link.id ? fixUrl : ''}
                    onFixUrlChange={setFixUrl}
                    onStartFix={() => {
                      setFixingId(link.id);
                      setFixUrl(link.suggested_url || '');
                    }}
                    onCancelFix={() => { setFixingId(null); setFixUrl(''); }}
                    onApplyFix={() => handleFix(link.id)}
                    onRecheck={() => recheckLink.mutate(link.id)}
                    fixPending={fixLink.isPending}
                    recheckPending={recheckLink.isPending}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Scan History */}
      {scans && scans.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tarama Gecmisi</h3>
          <div className="space-y-2">
            {scans.slice(0, 10).map((scan) => (
              <div key={scan.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    scan.status === 'completed' ? 'bg-green-100 text-green-700' :
                    scan.status === 'running' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {scan.status_display}
                  </span>
                  <span className="text-sm text-gray-700">
                    {new Date(scan.created_at).toLocaleString('tr-TR')}
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  {scan.total_links_checked} kontrol / {scan.broken_links_found} kirik / {scan.auto_fixed_count} tamir
                  <span className="text-xs text-gray-400 ml-2">({scan.duration_seconds}s)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ==================== SUB-COMPONENTS ====================

function StatCard({ label, value, icon, color }: { label: string; value: number; icon: React.ReactNode; color: string }) {
  const colorMap: Record<string, string> = {
    red: 'bg-red-50 text-red-600',
    green: 'bg-green-50 text-green-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    blue: 'bg-blue-50 text-blue-600',
    gray: 'bg-gray-50 text-gray-600',
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <div className={`p-1.5 rounded-lg ${colorMap[color] || colorMap.gray}`}>
          {icon}
        </div>
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function LinkRow({
  link,
  selected,
  onToggle,
  isFixing,
  fixUrl,
  onFixUrlChange,
  onStartFix,
  onCancelFix,
  onApplyFix,
  onRecheck,
  fixPending,
  recheckPending,
}: {
  link: BrokenLinkItem;
  selected: boolean;
  onToggle: () => void;
  isFixing: boolean;
  fixUrl: string;
  onFixUrlChange: (v: string) => void;
  onStartFix: () => void;
  onCancelFix: () => void;
  onApplyFix: () => void;
  onRecheck: () => void;
  fixPending: boolean;
  recheckPending: boolean;
}) {
  return (
    <>
      <tr className="hover:bg-gray-50">
        <td className="px-4 py-3">
          <input
            type="checkbox"
            checked={selected}
            onChange={onToggle}
            className="rounded border-gray-300"
          />
        </td>
        <td className="px-4 py-3">
          <div className="max-w-xs">
            <a
              href={link.broken_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-red-600 hover:underline break-all line-clamp-2"
            >
              {link.broken_url.length > 80 ? link.broken_url.slice(0, 80) + '...' : link.broken_url}
            </a>
            {link.error_message && (
              <p className="text-xs text-gray-400 mt-0.5">{link.error_message}</p>
            )}
            {link.suggested_url && link.status === 'detected' && (
              <p className="text-xs text-blue-500 mt-0.5">
                Oneri: {link.suggested_url.length > 60 ? link.suggested_url.slice(0, 60) + '...' : link.suggested_url}
              </p>
            )}
          </div>
        </td>
        <td className="px-4 py-3">
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[link.status] || 'bg-gray-100 text-gray-500'}`}>
            {link.status_display}
          </span>
        </td>
        <td className="px-4 py-3">
          <span className={`text-sm font-mono ${
            link.http_status && link.http_status >= 400 ? 'text-red-600' : 'text-gray-500'
          }`}>
            {link.http_status || '-'}
          </span>
        </td>
        <td className="px-4 py-3">
          <div className="flex items-center gap-1 text-gray-500">
            {LINK_TYPE_ICONS[link.link_type]}
            <span className="text-xs">{link.link_type_display}</span>
          </div>
        </td>
        <td className="px-4 py-3">
          <div>
            <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{link.source_type_display}</span>
            <p className="text-xs text-gray-400 mt-0.5 truncate max-w-[150px]">{link.source_title}</p>
          </div>
        </td>
        <td className="px-4 py-3 text-xs text-gray-400">
          {link.check_count}x
        </td>
        <td className="px-4 py-3">
          <div className="flex items-center gap-1">
            {link.status === 'detected' && (
              <>
                <button
                  onClick={onStartFix}
                  className="p-1.5 text-teal-600 hover:bg-teal-50 rounded-lg"
                  title="Tamir Et"
                >
                  <Wrench className="h-4 w-4" />
                </button>
                <button
                  onClick={onRecheck}
                  disabled={recheckPending}
                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg"
                  title="Tekrar Kontrol"
                >
                  <RefreshCw className={`h-4 w-4 ${recheckPending ? 'animate-spin' : ''}`} />
                </button>
              </>
            )}
          </div>
        </td>
      </tr>
      {/* Inline Fix Row */}
      {isFixing && (
        <tr className="bg-teal-50">
          <td colSpan={8} className="px-4 py-3">
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 whitespace-nowrap">Yeni URL:</span>
              <input
                type="url"
                value={fixUrl}
                onChange={(e) => onFixUrlChange(e.target.value)}
                placeholder="https://..."
                className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500"
              />
              <button
                onClick={onApplyFix}
                disabled={fixPending || !fixUrl.trim()}
                className="px-3 py-1.5 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700 disabled:opacity-50 flex items-center gap-1"
              >
                {fixPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <CheckCircle className="h-3 w-3" />}
                Uygula
              </button>
              <button
                onClick={onCancelFix}
                className="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300"
              >
                Iptal
              </button>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
