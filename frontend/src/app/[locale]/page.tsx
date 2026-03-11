'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import {
  ArrowRight,
  Play,
  CheckCircle,
  Plus,
  Zap,
  Brain,
  Hand,
  Sparkles,
  Activity,
  BookOpen,
  Stethoscope,
  Bell,
  Users,
  Award,
  Clock,
  Shield,
} from 'lucide-react';
import { useActiveHero } from '@/hooks/useSiteData';
import { useLocale } from 'next-intl';
import Image from 'next/image';

export default function HomePage() {
  const t = useTranslations();
  const locale = useLocale();
  const { data: hero } = useActiveHero();

  const diseaseModules = [
    {
      name: t('home.modules.migraine'),
      icon: Zap,
      description: t('home.modules.migraineDesc'),
      image: '/images/modules/migraine.svg',
      iconBg: 'bg-orange-100',
      iconColor: 'text-orange-500',
      active: true,
      href: '/patient/migraine',
    },
    {
      name: t('home.modules.epilepsy'),
      icon: Brain,
      description: t('home.modules.epilepsyDesc'),
      image: '/images/modules/epilepsy.svg',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-500',
      active: true,
      href: '/patient/epilepsy',
    },
    {
      name: t('home.modules.parkinson'),
      icon: Hand,
      description: t('home.modules.parkinsonDesc'),
      image: '/images/modules/parkinson.svg',
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-500',
      active: false,
      href: '#',
    },
    {
      name: t('home.modules.dementia'),
      icon: Sparkles,
      description: t('home.modules.dementiaDesc'),
      image: '/images/modules/dementia.svg',
      iconBg: 'bg-pink-100',
      iconColor: 'text-pink-500',
      active: true,
      href: '/patient/dementia',
    },
  ];

  const features = [
    {
      icon: Activity,
      title: t('home.features.tracking'),
      description: t('home.features.trackingDesc'),
      iconBg: 'bg-teal-50',
      iconColor: 'text-teal-600',
    },
    {
      icon: BookOpen,
      title: t('home.features.education'),
      description: t('home.features.educationDesc'),
      iconBg: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
    },
    {
      icon: Stethoscope,
      title: t('home.features.doctor'),
      description: t('home.features.doctorDesc'),
      iconBg: 'bg-rose-50',
      iconColor: 'text-rose-600',
    },
    {
      icon: Bell,
      title: t('home.features.reminders'),
      description: t('home.features.remindersDesc'),
      iconBg: 'bg-amber-50',
      iconColor: 'text-amber-600',
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
      {/* ========== HERO SECTION ========== */}
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-50/80 via-white to-teal-50/60">
        {/* Background shapes */}
        <div className="absolute top-20 right-[20%] w-64 h-64 bg-emerald-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-10 left-[10%] w-48 h-48 bg-teal-200/20 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 lg:pt-32 lg:pb-24">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left - Text */}
            <div>
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 border border-emerald-200 mb-8">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="text-sm font-medium text-emerald-700">{t('home.badge')}</span>
              </div>

              {/* Title */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
                {hero ? (
                  <span>{locale === 'en' ? hero.title_en : hero.title_tr}</span>
                ) : (
                  <>
                    {t('home.hero.titleFallback1')}{' '}
                    <span className="text-emerald-600">{t('home.hero.titleHighlight1')}</span>,{' '}
                    {t('home.hero.titleFallback2')}{' '}
                    <span className="text-emerald-600">{t('home.hero.titleHighlight2')}</span>
                  </>
                )}
              </h1>

              {/* Subtitle */}
              <p className="text-lg text-gray-500 mb-10 max-w-lg leading-relaxed">
                {hero
                  ? (locale === 'en' ? hero.subtitle_en : hero.subtitle_tr)
                  : t('home.hero.subtitle')}
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href={hero?.cta_url || '/auth/register'}
                  className="inline-flex items-center justify-center gap-2 px-7 py-4 bg-emerald-600 text-white rounded-full text-base font-semibold hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20 hover:shadow-emerald-600/30"
                >
                  {hero
                    ? (locale === 'en' ? hero.cta_text_en : hero.cta_text_tr) || t('home.hero.cta')
                    : t('home.hero.cta')}
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  href={hero?.secondary_cta_url || '/education'}
                  className="inline-flex items-center justify-center gap-2 px-7 py-4 bg-white text-gray-700 rounded-full text-base font-semibold border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all"
                >
                  <Play className="w-4 h-4" />
                  {hero
                    ? (locale === 'en' ? hero.secondary_cta_text_en : hero.secondary_cta_text_tr) || t('home.hero.secondaryCta')
                    : t('home.hero.secondaryCta')}
                </Link>
              </div>

              {/* Disclaimer */}
              <p className="text-xs text-gray-400 mt-8">
                {t('home.hero.disclaimer')}
              </p>
            </div>

            {/* Right - Illustration */}
            <div className="relative hidden lg:block">
              {/* Main illustration */}
              <div className="relative w-full h-[500px]">
                <Image
                  src="/images/hero/hero-illustration.svg"
                  alt="Norosera Platform"
                  fill
                  className="object-contain"
                  priority
                />
              </div>

              {/* Floating badge - Satisfaction */}
              <div className="absolute top-8 right-4 bg-white rounded-2xl shadow-lg p-4 flex items-center gap-3 animate-float">
                <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">%98</div>
                  <div className="text-xs text-gray-500">{t('home.hero.satisfaction')}</div>
                </div>
              </div>

              {/* Floating badge - Active Users */}
              <div className="absolute bottom-16 left-4 bg-white rounded-2xl shadow-lg p-4 flex items-center gap-3 animate-float-delayed">
                <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
                  <Plus className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">10K+</div>
                  <div className="text-xs text-gray-500">{t('home.stats.activeUsers')}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========== DISEASE MODULES SECTION ========== */}
      <section className="py-20 bg-gradient-to-b from-gray-50/50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-14">
            <span className="inline-block px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-600 text-sm font-medium mb-4">
              {t('home.modules.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.modules.sectionTitle')}
            </h2>
            <p className="text-gray-500 text-lg max-w-2xl mx-auto">
              {t('home.modules.sectionDesc')}
            </p>
          </div>

          {/* Modules Grid - 2x2 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {diseaseModules.map((module) => (
              <div
                key={module.name}
                className={`group rounded-3xl border bg-white overflow-hidden transition-all duration-300 ${
                  module.active
                    ? 'border-gray-200 hover:shadow-xl hover:border-gray-300'
                    : 'border-gray-100 opacity-70'
                }`}
              >
                {/* Card Image */}
                <div className="relative h-48 bg-gradient-to-br from-emerald-50 to-teal-50 overflow-hidden">
                  <Image
                    src={module.image}
                    alt={module.name}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  {/* Status Badge */}
                  <div className="absolute top-4 right-4">
                    {module.active ? (
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-500 text-white text-xs font-semibold shadow-sm">
                        {t('home.modules.active')}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-3 py-1 rounded-full bg-white/90 text-gray-500 text-xs font-semibold shadow-sm">
                        {t('home.modules.comingSoon')}
                      </span>
                    )}
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-6">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-10 h-10 rounded-xl ${module.iconBg} flex items-center justify-center`}>
                      <module.icon className={`w-5 h-5 ${module.iconColor}`} />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900">{module.name}</h3>
                  </div>
                  <p className="text-gray-500 text-sm leading-relaxed mb-4">
                    {module.description}
                  </p>
                  {module.active && (
                    <Link
                      href={module.href}
                      className="inline-flex items-center justify-center w-full gap-2 py-3 rounded-xl border border-gray-200 text-gray-700 text-sm font-semibold hover:bg-gray-50 hover:border-gray-300 transition-all"
                    >
                      {t('home.modules.startUsing')}
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== FEATURES SECTION ========== */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-14">
            <span className="inline-block px-4 py-1.5 rounded-full bg-teal-50 text-teal-600 text-sm font-medium mb-4">
              {t('home.features.sectionLabel')}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              {t('home.features.sectionTitle')}
            </h2>
            <p className="text-gray-500 text-lg max-w-2xl mx-auto">
              {t('home.features.sectionDesc')}
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <div
                key={i}
                className="p-6 rounded-2xl bg-white border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300"
              >
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl ${feature.iconBg} mb-4`}>
                  <feature.icon className={`w-6 h-6 ${feature.iconColor}`} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-500 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== STATS SECTION ========== */}
      <section className="py-16 bg-gray-50 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 mb-3">
                  <stat.icon className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== CTA SECTION ========== */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl bg-gradient-to-br from-emerald-600 to-teal-700 p-10 md:p-16 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              {t('home.cta.title')}
            </h2>
            <p className="text-emerald-100 text-lg mb-8 max-w-2xl mx-auto">
              {t('home.cta.desc')}
            </p>
            <Link
              href="/auth/register"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-emerald-700 rounded-full text-lg font-semibold hover:bg-emerald-50 transition-all shadow-lg"
            >
              {t('home.cta.button')}
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Floating animation styles */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes float-delayed {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
        :global(.animate-float) {
          animation: float 3s ease-in-out infinite;
        }
        :global(.animate-float-delayed) {
          animation: float-delayed 3s ease-in-out infinite 1.5s;
        }
      `}</style>
    </div>
  );
}
