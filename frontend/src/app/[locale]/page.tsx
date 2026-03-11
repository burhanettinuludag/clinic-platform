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
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
      badgeBg: 'bg-purple-100 text-purple-700',
      linkColor: 'text-purple-600 hover:text-purple-700',
      active: true,
      href: '/patient/migraine',
    },
    {
      name: t('home.modules.epilepsy'),
      icon: Zap,
      description: t('home.modules.epilepsyDesc'),
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
      iconBg: 'bg-amber-100',
      iconColor: 'text-amber-600',
      badgeBg: 'bg-amber-100 text-amber-700',
      linkColor: 'text-amber-600 hover:text-amber-700',
      active: true,
      href: '/patient/epilepsy',
    },
    {
      name: t('home.modules.parkinson'),
      icon: Heart,
      description: t('home.modules.parkinsonDesc'),
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
      badgeBg: 'bg-gray-100 text-gray-500',
      linkColor: '',
      active: false,
      href: '#',
    },
    {
      name: t('home.modules.dementia'),
      icon: Shield,
      description: t('home.modules.dementiaDesc'),
      bgColor: 'bg-rose-50',
      borderColor: 'border-rose-200',
      iconBg: 'bg-rose-100',
      iconColor: 'text-rose-600',
      badgeBg: 'bg-rose-100 text-rose-700',
      linkColor: 'text-rose-600 hover:text-rose-700',
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

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute inset-0 bg-gradient-to-br from-teal-50 via-white to-indigo-50" />
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-teal-100/40 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-indigo-100/30 rounded-full blur-3xl translate-y-1/2 -translate-x-1/3" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-20">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-50 border border-teal-200 mb-8">
              <Brain className="w-4 h-4 text-teal-600" />
              <span className="text-sm font-medium text-teal-700">{t('home.badge')}</span>
            </div>

            {/* Title */}
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

            {/* Subtitle */}
            <p className="text-lg sm:text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              {hero
                ? (locale === 'en' ? hero.subtitle_en : hero.subtitle_tr)
                : t('home.hero.subtitle')}
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href={hero?.cta_url || '/auth/register'}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-teal-600 text-white rounded-xl text-lg font-semibold hover:bg-teal-700 transition-all shadow-lg shadow-teal-600/20 hover:shadow-teal-600/30"
              >
                {hero
                  ? (locale === 'en' ? hero.cta_text_en : hero.cta_text_tr) || t('home.hero.cta')
                  : t('home.hero.cta')}
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href={hero?.secondary_cta_url || '/education'}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-gray-700 rounded-xl text-lg font-semibold border border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-all"
              >
                <BookOpen className="w-5 h-5" />
                {hero
                  ? (locale === 'en' ? hero.secondary_cta_text_en : hero.secondary_cta_text_tr) || t('home.hero.secondaryCta')
                  : t('home.hero.secondaryCta')}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
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
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
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

          {/* Features Grid */}
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

      {/* Disease Modules Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
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

          {/* Modules Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {diseaseModules.map((module) => (
              <div
                key={module.name}
                className={`rounded-2xl border-2 p-6 transition-all duration-300 ${
                  module.active
                    ? `${module.bgColor} ${module.borderColor} hover:shadow-lg`
                    : 'bg-gray-50 border-gray-200 opacity-60'
                }`}
              >
                {/* Icon */}
                <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl ${module.iconBg} mb-4`}>
                  <module.icon className={`w-7 h-7 ${module.iconColor}`} />
                </div>

                {/* Title & Status */}
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-bold text-gray-900">{module.name}</h3>
                  {module.active ? (
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${module.badgeBg}`}>
                      <CheckCircle className="w-3 h-3" />
                      {t('home.modules.active')}
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded-full bg-gray-100 text-gray-400 text-xs font-medium">
                      {t('home.modules.comingSoon')}
                    </span>
                  )}
                </div>

                {/* Description */}
                <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                  {module.description}
                </p>

                {/* Action */}
                {module.active && (
                  <Link
                    href={module.href}
                    className={`inline-flex items-center gap-1 text-sm font-semibold ${module.linkColor} transition-colors`}
                  >
                    {t('home.modules.startUsing')}
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl bg-gradient-to-br from-teal-600 to-teal-700 p-10 md:p-16 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              {t('home.cta.title')}
            </h2>
            <p className="text-teal-100 text-lg mb-8 max-w-2xl mx-auto">
              {t('home.cta.desc')}
            </p>
            <Link
              href="/auth/register"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-teal-700 rounded-xl text-lg font-semibold hover:bg-teal-50 transition-all shadow-lg"
            >
              {t('home.cta.button')}
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
