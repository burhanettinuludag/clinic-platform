'use client';

import { useSocialLinks, useUpdateSocialLink } from '@/hooks/useSiteAdmin';
import { ArrowLeft } from 'lucide-react';
import { Link } from '@/i18n/navigation';

const PLATFORM_ICONS: Record<string, string> = {
  twitter: 'X', linkedin: 'in', instagram: 'IG', youtube: 'YT',
  facebook: 'FB', tiktok: 'TT', github: 'GH',
};

export default function SocialPage() {
  const { data: links, isLoading } = useSocialLinks();
  const updateLink = useUpdateSocialLink();

  if (isLoading) return <div className="p-6"><div className="animate-pulse space-y-4">{[1,2,3,4].map(i => <div key={i} className="h-20 bg-slate-200 rounded-xl" />)}</div></div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/doctor/site-settings" className="text-slate-400 hover:text-slate-600"><ArrowLeft className="h-5 w-5" /></Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Sosyal Medya</h1>
          <p className="text-slate-500 text-sm">Platform linkleri ve siralama</p>
        </div>
      </div>

      <div className="space-y-3">
        {links?.map(link => (
          <div key={link.id} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 font-bold text-slate-600 text-sm">
                {PLATFORM_ICONS[link.platform] || link.platform[0].toUpperCase()}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-slate-900 text-sm">{link.platform_display}</span>
                  <span className="text-xs text-slate-400">Sira: {link.order}</span>
                </div>
                <input
                  defaultValue={link.url}
                  onBlur={(e) => {
                    if (e.target.value !== link.url) {
                      updateLink.mutate({ id: link.id, url: e.target.value });
                    }
                  }}
                  placeholder={`https://${link.platform}.com/norosera`}
                  className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
              </div>
              <button
                onClick={() => updateLink.mutate({ id: link.id, is_active: !link.is_active })}
                className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${link.is_active ? 'bg-green-500' : 'bg-slate-300'}`}>
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${link.is_active ? 'translate-x-6' : 'translate-x-1'}`} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
