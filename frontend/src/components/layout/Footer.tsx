'use client';

import { useTranslations, useLocale } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { Brain, Mail, Phone, MapPin, Twitter, Linkedin, Instagram, Youtube, Github, ArrowUpRight } from 'lucide-react';
import { usePublicSocialLinks, usePublicSiteConfigs } from '@/hooks/useSiteData';
import type { LucideIcon } from 'lucide-react';

const PLATFORM_ICON_MAP: Record<string, LucideIcon> = {
  twitter: Twitter,
  linkedin: Linkedin,
  instagram: Instagram,
  youtube: Youtube,
  github: Github,
};

export default function Footer() {
  const t = useTranslations();
  const locale = useLocale();
  const { data: socialLinks } = usePublicSocialLinks();
  const { data: configs } = usePublicSiteConfigs();

  const getConfig = (key: string) => configs?.find(c => c.key === key)?.value;

  const contactEmail = getConfig('contact_email') || 'info@norosera.com';
  const contactPhone = getConfig('contact_phone');
  const contactAddress = getConfig('contact_address');
  const footerText = locale === 'en'
    ? getConfig('footer_text_en')
    : getConfig('footer_text_tr');

  const quickLinks = [
    { label: t('nav.home'), href: '/' },
    { label: t('nav.education') || 'Egitim', href: '/education' },
    { label: t('nav.store'), href: '/store' },
    { label: 'Blog', href: '/blog' },
    { label: 'Haberler', href: '/news' },
    { label: 'Iletisim', href: '/contact' },
  ];

  const legalLinks = [
    { label: 'Gizlilik Politikasi', href: '/privacy-policy' },
    { label: 'Kullanim Kosullari', href: '/terms' },
    { label: 'KVKK Aydinlatma Metni', href: '/kvkk' },
  ];

  const diseaseModules = [
    { label: 'Migren Takibi', href: '/patient/dashboard', active: true },
    { label: 'Epilepsi Takibi', href: '#', active: false },
    { label: 'Parkinson Takibi', href: '#', active: false },
    { label: 'Demans Takibi', href: '#', active: false },
  ];

  // Use dynamic social links if available, fallback to static
  const activeSocials = socialLinks?.filter(s => s.url) || [];

  return (
    <footer className="bg-slate-950 border-t border-white/5">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-3 group mb-6">
              <div className="relative">
                <Brain className="w-10 h-10 text-cyan-400 group-hover:text-cyan-300 transition-colors" />
                <div className="absolute inset-0 bg-cyan-400/20 blur-xl rounded-full group-hover:bg-cyan-300/30 transition-colors" />
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-bold text-white tracking-tight">
                  {getConfig('site_name') || 'Norosera'}
                </span>
                <span className="text-[10px] text-cyan-400/80 tracking-widest uppercase">
                  Neurology Platform
                </span>
              </div>
            </Link>

            <p className="text-slate-400 text-sm leading-relaxed mb-6 max-w-sm">
              {t('disclaimer.text') || 'Norolojik sagliginizi takip etmenize ve yasam kalitenizi artirmaniza yardimci olan yapay zeka destekli platform.'}
            </p>

            {/* Contact Info — dynamic */}
            <div className="space-y-3">
              <a href={`mailto:${contactEmail}`} className="flex items-center gap-3 text-slate-400 hover:text-cyan-400 transition-colors text-sm">
                <Mail className="w-4 h-4" />
                {contactEmail}
              </a>
              {contactPhone && (
                <a href={`tel:${contactPhone}`} className="flex items-center gap-3 text-slate-400 hover:text-cyan-400 transition-colors text-sm">
                  <Phone className="w-4 h-4" />
                  {contactPhone}
                </a>
              )}
              {contactAddress && (
                <div className="flex items-start gap-3 text-slate-400 text-sm">
                  <MapPin className="w-4 h-4 mt-0.5" />
                  <span>{contactAddress}</span>
                </div>
              )}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Hizli Erisim</h4>
            <nav className="flex flex-col gap-3">
              {quickLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-slate-400 hover:text-cyan-400 transition-colors text-sm flex items-center gap-1 group"
                >
                  {link.label}
                  <ArrowUpRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                </Link>
              ))}
            </nav>
          </div>

          {/* Modules */}
          <div>
            <h4 className="text-white font-semibold mb-4">Moduller</h4>
            <nav className="flex flex-col gap-3">
              {diseaseModules.map((module) => (
                <Link
                  key={module.label}
                  href={module.href}
                  className={`text-sm flex items-center gap-2 transition-colors ${
                    module.active
                      ? 'text-slate-400 hover:text-cyan-400'
                      : 'text-slate-600 cursor-not-allowed'
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    module.active ? 'bg-emerald-500' : 'bg-slate-600'
                  }`} />
                  {module.label}
                  {!module.active && <span className="text-xs text-slate-600">(Yakinda)</span>}
                </Link>
              ))}
            </nav>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-white font-semibold mb-4">Hukuki</h4>
            <nav className="flex flex-col gap-3">
              {legalLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-slate-400 hover:text-cyan-400 transition-colors text-sm"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            {/* Copyright — dynamic */}
            <p className="text-slate-500 text-sm">
              {footerText || `\u00a9 ${new Date().getFullYear()} Norosera. Tum haklari saklidir.`}
            </p>

            {/* Social Links — dynamic */}
            <div className="flex items-center gap-4">
              {activeSocials.length > 0 ? (
                activeSocials.map((social) => {
                  const Icon = PLATFORM_ICON_MAP[social.platform];
                  if (!Icon) return null;
                  return (
                    <a
                      key={social.platform}
                      href={social.url}
                      aria-label={social.platform_display}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center text-slate-400 hover:bg-cyan-500/10 hover:text-cyan-400 transition-all"
                    >
                      <Icon className="w-4 h-4" />
                    </a>
                  );
                })
              ) : (
                // Fallback static icons
                [Twitter, Linkedin, Instagram, Youtube].map((Icon, i) => (
                  <span
                    key={i}
                    className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center text-slate-600"
                  >
                    <Icon className="w-4 h-4" />
                  </span>
                ))
              )}
            </div>

            {/* Medical Disclaimer Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20">
              <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span className="text-xs text-amber-400">
                Tibbi tavsiye yerine gecmez
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
