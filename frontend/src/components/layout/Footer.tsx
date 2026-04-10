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
    { label: t('nav.education'), href: '/education' },
    { label: t('nav.blog'), href: '/blog' },
    { label: t('nav.news'), href: '/news' },
    { label: t('nav.sleep'), href: '/sleep' },
    { label: t('nav.ms'), href: '/ms' },
    { label: t('nav.store'), href: '/store' },
    { label: t('nav.contact'), href: '/contact' },
  ];

  const legalLinks = [
    { label: t('legal.privacy'), href: '/privacy-policy' },
    { label: t('legal.terms'), href: '/terms' },
    { label: t('legal.kvkk'), href: '/kvkk' },
  ];

  const diseaseModules = [
    { label: t('footer.migraineTracking'), href: '/patient/migraine', active: true },
    { label: t('footer.epilepsyTracking'), href: '/patient/epilepsy', active: true },
    { label: t('footer.parkinsonTracking'), href: '/patient/parkinson', active: true },
    { label: t('footer.dementiaTracking'), href: '/patient/dementia', active: true },
  ];

  const activeSocials = socialLinks?.filter(s => s.url) || [];

  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2.5 group mb-5">
              <Brain className="w-8 h-8 text-teal-600 group-hover:text-teal-500 transition-colors" />
              <div className="flex flex-col">
                <span className="text-xl font-bold text-gray-900 tracking-tight">
                  {getConfig('site_name') || 'Norosera'}
                </span>
                <span className="text-[9px] text-teal-600/80 tracking-widest uppercase -mt-0.5">
                  {t('header.subtitle')}
                </span>
              </div>
            </Link>

            <p className="text-gray-500 text-sm leading-relaxed mb-5 max-w-sm">
              {t('disclaimer.text')}
            </p>

            {/* Contact Info */}
            <div className="space-y-2.5">
              <a href={`mailto:${contactEmail}`} className="flex items-center gap-2.5 text-gray-500 hover:text-teal-600 transition-colors text-sm">
                <Mail className="w-4 h-4" />
                {contactEmail}
              </a>
              {contactPhone && (
                <a href={`tel:${contactPhone}`} className="flex items-center gap-2.5 text-gray-500 hover:text-teal-600 transition-colors text-sm">
                  <Phone className="w-4 h-4" />
                  {contactPhone}
                </a>
              )}
              {contactAddress && (
                <div className="flex items-start gap-2.5 text-gray-500 text-sm">
                  <MapPin className="w-4 h-4 mt-0.5" />
                  <span>{contactAddress}</span>
                </div>
              )}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-gray-900 font-semibold mb-4 text-sm">{t('footer.quickLinks')}</h4>
            <nav className="flex flex-col gap-2.5">
              {quickLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-gray-500 hover:text-teal-600 transition-colors text-sm flex items-center gap-1 group"
                >
                  {link.label}
                  <ArrowUpRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                </Link>
              ))}
            </nav>
          </div>

          {/* Modules */}
          <div>
            <h4 className="text-gray-900 font-semibold mb-4 text-sm">{t('footer.modules')}</h4>
            <nav className="flex flex-col gap-2.5">
              {diseaseModules.map((module) => (
                <Link
                  key={module.label}
                  href={module.href}
                  className={`text-sm flex items-center gap-2 transition-colors ${
                    module.active
                      ? 'text-gray-500 hover:text-teal-600'
                      : 'text-gray-300 cursor-not-allowed'
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    module.active ? 'bg-teal-500' : 'bg-gray-300'
                  }`} />
                  {module.label}
                  {!module.active && <span className="text-xs text-gray-300">({t('home.modules.comingSoon')})</span>}
                </Link>
              ))}
            </nav>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-gray-900 font-semibold mb-4 text-sm">{t('footer.legal')}</h4>
            <nav className="flex flex-col gap-2.5">
              {legalLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-gray-500 hover:text-teal-600 transition-colors text-sm"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            {/* Copyright */}
            <div className="text-center md:text-left">
              <p className="text-gray-400 text-sm">
                {footerText || `\u00a9 ${new Date().getFullYear()} Norosera. ${t('footer.copyright')}`}
              </p>
              <p className="text-gray-400 text-xs mt-1">
                {locale === 'en'
                  ? 'All rights reserved. Developer: Prof. Dr. Burhanettin Uluda\u011f'
                  : 'T\u00fcm haklar\u0131 sakl\u0131d\u0131r. Geli\u015ftirici: Prof. Dr. Burhanettin Uluda\u011f'}
              </p>
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-3">
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
                      className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-400 hover:border-teal-300 hover:text-teal-600 hover:bg-teal-50 transition-all"
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </a>
                  );
                })
              ) : (
                [Twitter, Linkedin, Instagram, Youtube].map((Icon, i) => (
                  <span
                    key={i}
                    className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-300"
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </span>
                ))
              )}
            </div>

            {/* Medical Disclaimer Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              <span className="text-xs text-amber-700 font-medium">
                {t('footer.medicalDisclaimer')}
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
