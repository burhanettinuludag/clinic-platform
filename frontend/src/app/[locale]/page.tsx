'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import {
  Activity,
  BookOpen,
  Stethoscope,
  Bell,
  Brain,
  Zap,
  Heart,
  Shield,
  ArrowRight,
  Users,
  Award,
  Clock,
  CheckCircle,
  Lock,
  FileCheck,
  Eye,
  UserCheck,
  Quote,
  Sparkles,
  Star,
  GraduationCap,
  Monitor,
  Gamepad2,
  Newspaper,
  Smartphone,
} from 'lucide-react';
import { useActiveHero } from '@/hooks/useSiteData';
import { useLocale } from 'next-intl';

export default function HomePage() {
  const t = useTranslations();
  const locale = useLocale();
  const { data: hero } = useActiveHero();

  const features = [
    {
      icon: Activity,
      title: t('home.features.tracking'),
      description: t('home.features.trackingDesc'),
      color: 'teal',
    },
    {
      icon: BookOpen,
      title: t('home.features.education'),
      description: t('home.features.educationDesc'),
      color: 'indigo',
    },
    {
      icon: Stethoscope,
      title: t('home.features.doctor'),
      description: t('home.features.doctorDesc'),
      color: 'rose',
    },
    {
      icon: Bell,
      title: t('home.features.reminders'),
      description: t('home.features.remindersDesc'),
      color: 'amber',
    },
  ];

  const diseaseModules = [
    {
      name: t('home.modules.migraine'),
      icon: Brain,
      description: t('home.modules.migraineDesc'),
      cta: t('home.modules.migraineCta'),
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
      badgeBg: 'bg-purple-100 text-purple-700',
      linkColor: 'text-purple-600 hover:text-purple-700',
      ctaBg: 'bg-purple-600 hover:bg-purple-700',
      active: true,
      href: '/patient/migraine',
    },
    {
      name: t('home.modules.epilepsy'),
      icon: Zap,
      description: t('home.modules.epilepsyDesc'),
      cta: t('home.modules.epilepsyCta'),
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
      iconBg: 'bg-amber-100',
      iconColor: 'text-amber-600',
      badgeBg: 'bg-amber-100 text-amber-700',
      linkColor: 'text-amber-600 hover:text-amber-700',
      ctaBg: 'bg-amber-600 hover:bg-amber-700',
      active: true,
      href: '/patient/epilepsy',
    },
    {
      name: t('home.modules.parkinson'),
      icon: Heart,
      description: t('home.modules.parkinsonDesc'),
      cta: t('home.modules.earlyAccess'),
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-200',
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
      badgeBg: 'bg-emerald-100 text-emerald-600',
      linkColor: 'text-emerald-600 hover:text-emerald-700',
      ctaBg: 'bg-emerald-600 hover:bg-emerald-700',
      active: false,
      href: '/auth/register',
    },
    {
      name: t('home.modules.dementia'),
      icon: Shield,
      description: t('home.modules.dementiaDesc'),
      cta: t('home.modules.dementiaCta'),
      bgColor: 'bg-rose-50',
      borderColor: 'border-rose-200',
      iconBg: 'bg-rose-100',
      iconColor: 'text-rose-600',
      badgeBg: 'bg-rose-100 text-rose-700',
      linkColor: 'text-rose-600 hover:text-rose-700',
      ctaBg: 'bg-rose-600 hover:bg-rose-700',
      active: true,
      href: '/patient/dementia',
    },
  ];

  const stats = [
    { value: '10K+', label: t('home.stats.activeUsers'), icon: Users },
    { value: '50K+', label: t('home.stats.trackedAttacks'), icon: Activity },
    { value: '100+', label: t('home.stats.expertDoctors'), icon: Award },
    { value: '7/24', label: t('home.stats.support'), icon: Clock },
  ];

  const trustItems = [
    { icon: Lock, title: t('home.trust.encryption'), desc: t('home.trust.encryptionDesc') },
    { icon: FileCheck, title: t('home.trust.kvkk'), desc: t('home.trust.kvkkDesc') },
    { icon: Eye, title: t('home.trust.audit'), desc: t('home.trust.auditDesc') },
    { icon: UserCheck, title: t('home.trust.doctors'), desc: t('home.trust.doctorsDesc') },
  ];

  const personas = [
    {
      icon: Users,
      title: t('home.whoIsItFor.patients'),
      desc: t('home.whoIsItFor.patientsDesc'),
      items: t('home.whoIsItFor.patientsItems'),
      color: 'teal',
    },
    {
      icon: Heart,
      title: t('home.whoIsItFor.caregivers'),
      desc: t('home.whoIsItFor.caregiversDesc'),
      items: t('home.whoIsItFor.caregiversItems'),
      color: 'indigo',
    },
    {
      icon: Stethoscope,
      title: t('home.whoIsItFor.doctors'),
      desc: t('home.whoIsItFor.doctorsDesc'),
      items: t('home.whoIsItFor.doctorsItems'),
      color: 'rose',
    },
  ];

  const personaColors: Record<string, { bg: string; iconBg: string; iconColor: string; itemColor: string }> = {
    teal: { bg: 'border-teal-200', iconBg: 'bg-teal-100', iconColor: 'text-teal-600', itemColor: 'text-teal-700 bg-teal-50' },
    indigo: { bg: 'border-indigo-200', iconBg: 'bg-indigo-100', iconColor: 'text-indigo-600', itemColor: 'text-indigo-700 bg-indigo-50' },
    rose: { bg: 'border-rose-200', iconBg: 'bg-rose-100', iconColor: 'text-rose-600', itemColor: 'text-rose-700 bg-rose-50' },
  };

  const testimonials = [
    { quote: t('home.testimonials.t1quote'), name: t('home.testimonials.t1name'), role: t('home.testimonials.t1role'), color: 'teal' },
    { quote: t('home.testimonials.t2quote'), name: t('home.testimonials.t2name'), role: t('home.testimonials.t2role'), color: 'indigo' },
    { quote: t('home.testimonials.t3quote'), name: t('home.testimonials.t3name'), role: t('home.testimonials.t3role'), color: 'rose' },
    { quote: t('home.testimonials.t4quote'), name: t('home.testimonials.t4name'), role: t('home.testimonials.t4role'), color: 'amber' },
  ];

  const previewScreens = [
    {
      icon: Monitor,
      title: t('home.preview.screen1title'),
      desc: t('home.preview.screen1desc'),
      features: t('home.preview.screen1features'),
      gradient: 'from-teal-500 to-teal-600',
      mockItems: ['Atak #47 - Siddet: 7/10', 'Tetikleyici: Stres, Uyku', 'Sure: 4 saat'],
    },
    {
      icon: Stethoscope,
      title: t('home.preview.screen2title'),
      desc: t('home.preview.screen2desc'),
      features: t('home.preview.screen2features'),
      gradient: 'from-indigo-500 to-indigo-600',
      mockItems: ['12 Aktif Hasta', '3 Kritik Uyari', 'Son Rapor: Bugun'],
    },
    {
      icon: Gamepad2,
      title: t('home.preview.screen3title'),
      desc: t('home.preview.screen3desc'),
      features: t('home.preview.screen3features'),
      gradient: 'from-purple-500 to-purple-600',
      mockItems: ['Kelime Eslestirme: 85%', 'Hafiza Testi: 92%', 'Seri: 7 Gun'],
    },
  ];

  const blogCategories = [
    { icon: Brain, title: t('home.blog.cat1title'), desc: t('home.blog.cat1desc'), href: '/blog', color: 'purple' },
    { icon: Zap, title: t('home.blog.cat2title'), desc: t('home.blog.cat2desc'), href: '/blog', color: 'amber' },
    { icon: Shield, title: t('home.blog.cat3title'), desc: t('home.blog.cat3desc'), href: '/education', color: 'rose' },
    { icon: Newspaper, title: t('home.blog.cat4title'), desc: t('home.blog.cat4desc'), href: '/news', color: 'teal' },
  ];

  const blogColorMap: Record<string, { iconBg: string; iconColor: string }> = {
    purple: { iconBg: 'bg-purple-50', iconColor: 'text-purple-600' },
    amber: { iconBg: 'bg-amber-50', iconColor: 'text-amber-600' },
    rose: { iconBg: 'bg-rose-50', iconColor: 'text-rose-600' },
    teal: { iconBg: 'bg-teal-50', iconColor: 'text-teal-600' },
  };

  const testimonialColorMap: Record<string, { border: string; bg: string; accent: string }> = {
    teal: { border: 'border-teal-200', bg: 'bg-teal-50', accent: 'text-teal-600' },
    indigo: { border: 'border-indigo-200', bg: 'bg-indigo-50', accent: 'text-indigo-600' },
    rose: { border: 'border-rose-200', bg: 'bg-rose-50', accent: 'text-rose-600' },
    amber: { border: 'border-amber-200', bg: 'bg-amber-50', accent: 'text-amber-600' },
  };

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'MedicalBusiness',
    name: 'Norosera',
    description: locale === 'tr'
      ? 'Migren, epilepsi ve demans hastaları için dijital takip, ev eğitimi ve hekim paneli platformu.'
      : 'Digital tracking, home education and physician panel platform for migraine, epilepsy and dementia patients.',
    url: 'https://norosera.com',
    logo: 'https://norosera.com/icon.svg',
    sameAs: [],
    medicalSpecialty: ['Neurology'],
    availableService: [
      { '@type': 'MedicalTherapy', name: 'Migraine Tracking', description: 'Attack diary, trigger analysis, weather correlation' },
      { '@type': 'MedicalTherapy', name: 'Epilepsy Tracking', description: 'Seizure recording, trigger analysis, medication adherence' },
      { '@type': 'MedicalTherapy', name: 'Dementia Care', description: 'Cognitive exercises, daily assessments, caregiver tools' },
    ],
    aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', reviewCount: '1200', bestRating: '5' },
  };

  const webAppJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Norosera',
    applicationCategory: 'HealthApplication',
    operatingSystem: 'Web',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'TRY' },
    description: locale === 'tr'
      ? 'Nörolojik hastalıklar için dijital sağlık platformu'
      : 'Digital health platform for neurological diseases',
  };

  return (
    <div className="bg-white">
      {/* JSON-LD Structured Data */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webAppJsonLd) }} />

      {/* ═══ Hero Section ═══ */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-teal-50 via-white to-indigo-50" />
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-teal-100/40 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-indigo-100/30 rounded-full blur-3xl translate-y-1/2 -translate-x-1/3" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-20">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-50 border border-teal-200 mb-8">
              <Brain className="w-4 h-4 text-teal-600" />
              <span className="text-sm font-medium text-teal-700">{t('home.badge')}</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              {hero ? (
                <span>{locale === 'en' ? hero.title_en : hero.title_tr}</span>
              ) : (
                <>
                  {t('home.hero.titleFallback1')}{' '}
                  <span className="text-teal-600">{t('home.hero.titleHighlight1')}</span>,{' '}
                  <span className="text-teal-600">{t('home.hero.titleHighlight2')}</span>
                </>
              )}
            </h1>

            <p className="text-lg sm:text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              {hero
                ? (locale === 'en' ? hero.subtitle_en : hero.subtitle_tr)
                : t('home.hero.subtitle')}
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link
                href={hero?.cta_url || '/auth/register'}
                className="inline-flex items-center justify-center gap-2 px-10 py-5 bg-teal-600 text-white rounded-2xl text-lg font-bold hover:bg-teal-700 transition-all shadow-xl shadow-teal-600/25 hover:shadow-teal-600/40 hover:scale-[1.02]"
              >
                {hero
                  ? (locale === 'en' ? hero.cta_text_en : hero.cta_text_tr) || t('home.hero.cta')
                  : t('home.hero.cta')}
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href={hero?.secondary_cta_url || '/doctors'}
                className="inline-flex items-center justify-center gap-2 px-10 py-5 bg-white text-gray-700 rounded-2xl text-lg font-semibold border-2 border-gray-200 hover:border-teal-300 hover:bg-teal-50 hover:text-teal-700 transition-all"
              >
                <Stethoscope className="w-5 h-5" />
                {hero
                  ? (locale === 'en' ? hero.secondary_cta_text_en : hero.secondary_cta_text_tr) || t('home.hero.secondaryCta')
                  : t('home.hero.secondaryCta')}
              </Link>
            </div>

            {/* Trust Badges Row */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              {[
                { icon: Shield, label: t('home.trustBadges.kvkk'), color: 'text-emerald-600 bg-emerald-50 border-emerald-200' },
                { icon: Lock, label: t('home.trustBadges.encrypted'), color: 'text-blue-600 bg-blue-50 border-blue-200' },
                { icon: UserCheck, label: t('home.trustBadges.doctorApproved'), color: 'text-indigo-600 bg-indigo-50 border-indigo-200' },
                { icon: Eye, label: t('home.trustBadges.audit'), color: 'text-teal-600 bg-teal-50 border-teal-200' },
              ].map((badge, i) => (
                <div key={i} className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-semibold ${badge.color}`}>
                  <badge.icon className="w-3.5 h-3.5" />
                  {badge.label}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Stats Section with Context ═══ */}
      <section className="py-16 bg-gray-50 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-teal-50 border border-teal-100 mb-3">
                  <stat.icon className="w-5 h-5 text-teal-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-gray-400 mt-6">{t('home.stats.note')}</p>
        </div>
      </section>

      {/* ═══ Who Is It For? (Personas) ═══ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-sm font-medium mb-4">
              {t('home.whoIsItFor.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.whoIsItFor.sectionTitle')}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t('home.whoIsItFor.sectionDesc')}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {personas.map((persona, i) => {
              const colors = personaColors[persona.color] || personaColors.teal;
              return (
                <div key={i} className={`rounded-2xl border-2 ${colors.bg} bg-white p-8 hover:shadow-lg transition-all duration-300`}>
                  <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl ${colors.iconBg} mb-5`}>
                    <persona.icon className={`w-7 h-7 ${colors.iconColor}`} />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{persona.title}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed mb-4">{persona.desc}</p>
                  <div className="flex flex-wrap gap-2">
                    {persona.items.split(', ').map((item, j) => (
                      <span key={j} className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${colors.itemColor}`}>
                        <CheckCircle className="w-3 h-3 mr-1" />
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ Platform Preview / Mini Tour ═══ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 rounded-full bg-teal-50 text-teal-600 text-sm font-medium mb-4">
              {t('home.preview.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.preview.sectionTitle')}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t('home.preview.sectionDesc')}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {previewScreens.map((screen, i) => (
              <div key={i} className="group">
                {/* Mock Screen */}
                <div className={`rounded-t-2xl bg-gradient-to-br ${screen.gradient} p-6 min-h-[200px] relative overflow-hidden`}>
                  {/* Mock browser bar */}
                  <div className="flex items-center gap-1.5 mb-4">
                    <div className="w-2.5 h-2.5 rounded-full bg-white/30" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/30" />
                    <div className="w-2.5 h-2.5 rounded-full bg-white/30" />
                    <div className="flex-1 h-5 rounded bg-white/10 ml-3" />
                  </div>
                  {/* Mock UI content */}
                  <div className="space-y-2.5">
                    {screen.mockItems.map((item, j) => (
                      <div key={j} className="flex items-center gap-2 bg-white/15 backdrop-blur-sm rounded-lg px-3 py-2">
                        <CheckCircle className="w-3.5 h-3.5 text-white/80 flex-shrink-0" />
                        <span className="text-white/90 text-xs font-medium">{item}</span>
                      </div>
                    ))}
                  </div>
                  {/* Decorative elements */}
                  <div className="absolute -bottom-4 -right-4 w-20 h-20 bg-white/5 rounded-full" />
                </div>

                {/* Info card */}
                <div className="rounded-b-2xl bg-white border border-t-0 border-gray-200 p-6 group-hover:shadow-lg transition-all">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`inline-flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br ${screen.gradient} shadow-sm`}>
                      <screen.icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">{screen.title}</h3>
                  </div>
                  <p className="text-gray-600 text-sm leading-relaxed mb-3">{screen.desc}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {screen.features.split(', ').map((feat, j) => (
                      <span key={j} className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 font-medium">
                        {feat}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ Features Section (Enhanced) ═══ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 rounded-full bg-teal-50 text-teal-600 text-sm font-medium mb-4">
              {t('home.features.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.features.sectionTitle')}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t('home.features.sectionDesc')}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => {
              const colorMap: Record<string, { iconBg: string; iconColor: string }> = {
                teal: { iconBg: 'bg-teal-50', iconColor: 'text-teal-600' },
                indigo: { iconBg: 'bg-indigo-50', iconColor: 'text-indigo-600' },
                rose: { iconBg: 'bg-rose-50', iconColor: 'text-rose-600' },
                amber: { iconBg: 'bg-amber-50', iconColor: 'text-amber-600' },
              };
              const colors = colorMap[feature.color] || colorMap.teal;

              return (
                <div
                  key={i}
                  className="p-6 rounded-2xl bg-white border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300"
                >
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl ${colors.iconBg} mb-4`}>
                    <feature.icon className={`w-6 h-6 ${colors.iconColor}`} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-500 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ Disease Modules Section (Enhanced with CTAs) ═══ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-sm font-medium mb-4">
              {t('home.modules.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.modules.sectionTitle')}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t('home.modules.sectionDesc')}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {diseaseModules.map((module) => (
              <div
                key={module.name}
                className={`rounded-2xl border-2 p-6 transition-all duration-300 ${module.bgColor} ${module.borderColor} hover:shadow-lg`}
              >
                <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl ${module.iconBg} mb-4`}>
                  <module.icon className={`w-7 h-7 ${module.iconColor}`} />
                </div>

                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-bold text-gray-900">{module.name}</h3>
                  {module.active ? (
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${module.badgeBg}`}>
                      <CheckCircle className="w-3 h-3" />
                      {t('home.modules.active')}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-600 text-xs font-medium">
                      <Sparkles className="w-3 h-3" />
                      {t('home.modules.comingSoon')}
                    </span>
                  )}
                </div>

                <p className="text-gray-600 text-sm mb-5 leading-relaxed">
                  {module.description}
                </p>

                <Link
                  href={module.href}
                  className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-white ${module.ctaBg} transition-colors shadow-sm`}
                >
                  {module.cta}
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ Testimonials Section ═══ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 rounded-full bg-amber-50 text-amber-600 text-sm font-medium mb-4">
              {t('home.testimonials.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.testimonials.sectionTitle')}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t('home.testimonials.sectionDesc')}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {testimonials.map((testimonial, i) => {
              const colors = testimonialColorMap[testimonial.color] || testimonialColorMap.teal;
              return (
                <div key={i} className={`rounded-2xl border-2 ${colors.border} bg-white p-6 hover:shadow-lg transition-all duration-300 flex flex-col`}>
                  {/* Stars */}
                  <div className="flex gap-0.5 mb-4">
                    {[...Array(5)].map((_, j) => (
                      <Star key={j} className="w-4 h-4 fill-amber-400 text-amber-400" />
                    ))}
                  </div>

                  {/* Quote */}
                  <p className="text-gray-700 text-sm leading-relaxed flex-1 mb-4 italic">
                    &ldquo;{testimonial.quote}&rdquo;
                  </p>

                  {/* Author */}
                  <div className="flex items-center gap-3 pt-4 border-t border-gray-100">
                    <div className={`w-10 h-10 rounded-full ${colors.bg} flex items-center justify-center`}>
                      <span className={`text-sm font-bold ${colors.accent}`}>
                        {testimonial.name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-gray-900">{testimonial.name}</div>
                      <div className="text-xs text-gray-500">{testimonial.role}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ Trust & Security Section ═══ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 rounded-full bg-emerald-50 text-emerald-600 text-sm font-medium mb-4">
              {t('home.trust.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.trust.sectionTitle')}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t('home.trust.sectionDesc')}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {trustItems.map((item, i) => (
              <div key={i} className="rounded-2xl bg-white border border-gray-200 p-6 text-center hover:shadow-lg transition-all duration-300">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-50 mb-4">
                  <item.icon className="w-6 h-6 text-emerald-600" />
                </div>
                <h3 className="text-base font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ User Story Section ═══ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="inline-block px-3 py-1 rounded-full bg-purple-50 text-purple-600 text-sm font-medium mb-4">
              {t('home.story.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.story.sectionTitle')}
            </h2>
          </div>

          <div className="rounded-3xl bg-gradient-to-br from-purple-50 to-indigo-50 border border-purple-100 p-8 md:p-12">
            {/* Quote */}
            <div className="text-center mb-10">
              <Quote className="w-10 h-10 text-purple-300 mx-auto mb-4" />
              <blockquote className="text-xl md:text-2xl font-medium text-gray-800 italic max-w-2xl mx-auto">
                {t('home.story.quote')}
              </blockquote>
              <div className="mt-4">
                <span className="font-semibold text-gray-900">{t('home.story.name')}</span>
                <span className="text-gray-500 ml-2">- {t('home.story.role')}</span>
              </div>
            </div>

            {/* Steps */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { num: '1', title: t('home.story.step1title'), desc: t('home.story.step1desc'), color: 'bg-purple-600' },
                { num: '2', title: t('home.story.step2title'), desc: t('home.story.step2desc'), color: 'bg-indigo-600' },
                { num: '3', title: t('home.story.step3title'), desc: t('home.story.step3desc'), color: 'bg-teal-600' },
              ].map((step) => (
                <div key={step.num} className="bg-white/70 backdrop-blur rounded-xl p-5 border border-white">
                  <div className={`inline-flex items-center justify-center w-8 h-8 rounded-full ${step.color} text-white text-sm font-bold mb-3`}>
                    {step.num}
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">{step.title}</h4>
                  <p className="text-sm text-gray-600 leading-relaxed">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Blog / Knowledge Base Section ═══ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 rounded-full bg-teal-50 text-teal-600 text-sm font-medium mb-4">
              {t('home.blog.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.blog.sectionTitle')}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t('home.blog.sectionDesc')}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
            {blogCategories.map((cat, i) => {
              const colors = blogColorMap[cat.color] || blogColorMap.teal;
              return (
                <Link
                  key={i}
                  href={cat.href}
                  className="group rounded-2xl bg-white border border-gray-200 p-6 hover:shadow-lg hover:border-gray-300 transition-all duration-300"
                >
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl ${colors.iconBg} mb-4 group-hover:scale-110 transition-transform`}>
                    <cat.icon className={`w-6 h-6 ${colors.iconColor}`} />
                  </div>
                  <h3 className="text-base font-bold text-gray-900 mb-2 group-hover:text-teal-600 transition-colors">
                    {cat.title}
                  </h3>
                  <p className="text-gray-500 text-sm leading-relaxed">{cat.desc}</p>
                </Link>
              );
            })}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/blog"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-teal-600 text-white rounded-xl text-sm font-semibold hover:bg-teal-700 transition-all shadow-sm"
            >
              <BookOpen className="w-4 h-4" />
              {t('home.blog.readArticles')}
            </Link>
            <Link
              href="/news"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white text-gray-700 rounded-xl text-sm font-semibold border border-gray-200 hover:border-teal-300 hover:text-teal-700 transition-all"
            >
              <Newspaper className="w-4 h-4" />
              {t('home.blog.readNews')}
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ 3 Steps to Get Started ═══ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            {t('home.steps.sectionTitle')}
          </h2>
          <p className="text-gray-600 text-lg mb-12">
            {t('home.steps.sectionDesc')}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {[
              { num: '1', title: t('home.steps.step1'), desc: t('home.steps.step1desc'), icon: UserCheck },
              { num: '2', title: t('home.steps.step2'), desc: t('home.steps.step2desc'), icon: Brain },
              { num: '3', title: t('home.steps.step3'), desc: t('home.steps.step3desc'), icon: Activity },
            ].map((step) => (
              <div key={step.num} className="relative">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-teal-100 mb-4">
                  <step.icon className="w-7 h-7 text-teal-600" />
                </div>
                <div className="absolute -top-2 -right-2 md:right-auto md:-left-2 w-8 h-8 rounded-full bg-teal-600 text-white text-sm font-bold flex items-center justify-center">
                  {step.num}
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-500 text-sm">{step.desc}</p>
              </div>
            ))}
          </div>

          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-10 py-5 bg-teal-600 text-white rounded-2xl text-lg font-bold hover:bg-teal-700 transition-all shadow-xl shadow-teal-600/25 hover:shadow-teal-600/40 hover:scale-[1.02]"
          >
            {t('home.cta.button')}
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* ═══ Final CTA with App Store Coming Soon ═══ */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl bg-gradient-to-br from-teal-600 to-teal-700 p-10 md:p-16 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              {t('home.cta.title')}
            </h2>
            <p className="text-teal-100 text-lg mb-8 max-w-2xl mx-auto">
              {t('home.cta.desc')}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link
                href="/auth/register"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-teal-700 rounded-xl text-lg font-semibold hover:bg-teal-50 transition-all shadow-lg"
              >
                {t('home.cta.button')}
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/doctors"
                className="inline-flex items-center gap-2 px-8 py-4 bg-teal-500/30 text-white rounded-xl text-lg font-semibold border border-teal-400/50 hover:bg-teal-500/40 transition-all"
              >
                <Stethoscope className="w-5 h-5" />
                {t('home.hero.secondaryCta')}
              </Link>
            </div>

            {/* App Store Coming Soon */}
            <div className="flex items-center justify-center gap-2 text-teal-200/80">
              <Smartphone className="w-4 h-4" />
              <span className="text-sm">{t('home.appStore.comingSoon')}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
