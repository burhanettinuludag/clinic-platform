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
  Sparkles,
  Users,
  Award,
  Clock
} from 'lucide-react';
import NeuralAnimation from '@/components/common/NeuralAnimation';
import BrainIcon from '@/components/common/BrainIcon';

export default function HomePage() {
  const t = useTranslations();

  const features = [
    {
      icon: Activity,
      title: t('home.features.tracking'),
      description: t('home.features.trackingDesc'),
      color: 'cyan',
    },
    {
      icon: BookOpen,
      title: t('home.features.education'),
      description: t('home.features.educationDesc'),
      color: 'purple',
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
      name: 'Migren',
      icon: Brain,
      color: 'purple',
      gradient: 'from-purple-500 to-violet-600',
      bgGlow: 'bg-purple-500/20',
      active: true,
      description: 'Migren ataklarinizi takip edin ve tetikleyicileri kesfin'
    },
    {
      name: 'Epilepsi',
      icon: Zap,
      color: 'amber',
      gradient: 'from-amber-500 to-orange-600',
      bgGlow: 'bg-amber-500/20',
      active: false,
      description: 'Nobetlerinizi kaydedin ve paternleri analiz edin'
    },
    {
      name: 'Parkinson',
      icon: Heart,
      color: 'emerald',
      gradient: 'from-emerald-500 to-teal-600',
      bgGlow: 'bg-emerald-500/20',
      active: false,
      description: 'Motor belirtilerinizi gunluk olarak izleyin'
    },
    {
      name: 'Demans',
      icon: Shield,
      color: 'rose',
      gradient: 'from-rose-500 to-pink-600',
      bgGlow: 'bg-rose-500/20',
      active: false,
      description: 'Bilissel sagligi destekleyen araclar'
    },
  ];

  const stats = [
    { value: '10K+', label: 'Aktif Kullanici', icon: Users },
    { value: '50K+', label: 'Takip Edilen Atak', icon: Activity },
    { value: '100+', label: 'Uzman Doktor', icon: Award },
    { value: '7/24', label: 'Destek', icon: Clock },
  ];

  return (
    <div className="bg-slate-950 min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Neural Animation Background */}
        <NeuralAnimation className="absolute inset-0" />

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950/50 via-transparent to-slate-950" />

        {/* Floating Orbs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />

        <div className="relative z-10 max-w-7xl mx-auto px-4 py-32 text-center">
          {/* Brain Icon */}
          <div className="flex justify-center mb-8">
            <BrainIcon size={120} animated={true} className="brain-glow" />
          </div>

          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/20 mb-8">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="text-sm text-cyan-300">Noroloji Platformu</span>
          </div>

          {/* Title */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-white">Beyninizi</span>
            <br />
            <span className="text-gradient">Anlayın, Yönetin</span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-slate-400 mb-12 max-w-3xl mx-auto leading-relaxed">
            {t('home.hero.subtitle') || 'Norolojik sagliginizi yapay zeka destekli araclarla takip edin, uzman doktorlarla baglanti kurun.'}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-2xl text-lg font-semibold hover:from-cyan-400 hover:to-cyan-500 transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:-translate-y-1"
            >
              {t('home.hero.cta') || 'Hemen Baslayin'}
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/education"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/5 text-white rounded-2xl text-lg font-semibold border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
            >
              <BookOpen className="w-5 h-5" />
              Daha Fazla Bilgi
            </Link>
          </div>

          {/* Scroll Indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
            <div className="w-6 h-10 rounded-full border-2 border-white/20 flex justify-center pt-2">
              <div className="w-1 h-2 bg-white/40 rounded-full animate-pulse" />
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-20 border-y border-white/5">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <div key={i} className="text-center group">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/10 to-purple-500/10 border border-white/5 mb-4 group-hover:border-cyan-500/30 transition-colors">
                  <stat.icon className="w-6 h-6 text-cyan-400" />
                </div>
                <div className="text-3xl md:text-4xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-slate-500 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent" />

        <div className="max-w-7xl mx-auto px-4 relative">
          {/* Section Header */}
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-sm font-medium mb-4">
              Ozellikler
            </span>
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              Sagliginiz Icin <span className="text-gradient">Guclu Araclar</span>
            </h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Norolojik sagliginizi yonetmek icin ihtiyaciniz olan tum araclar tek bir platformda
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <div
                key={i}
                className="group relative p-6 rounded-2xl bg-slate-900/50 border border-white/5 hover:border-cyan-500/30 transition-all duration-300 hover:-translate-y-2"
              >
                {/* Glow Effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />

                <div className="relative">
                  {/* Icon */}
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4 ${
                    feature.color === 'cyan' ? 'bg-cyan-500/10 text-cyan-400' :
                    feature.color === 'purple' ? 'bg-purple-500/10 text-purple-400' :
                    feature.color === 'rose' ? 'bg-rose-500/10 text-rose-400' :
                    'bg-amber-500/10 text-amber-400'
                  }`}>
                    <feature.icon className="w-6 h-6" />
                  </div>

                  {/* Content */}
                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-cyan-300 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-slate-400 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disease Modules Section */}
      <section className="py-24 relative overflow-hidden">
        {/* Background Elements */}
        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />
        <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent" />

        <div className="max-w-7xl mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1 rounded-full bg-purple-500/10 text-purple-400 text-sm font-medium mb-4">
              Moduller
            </span>
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              Hastalik <span className="text-gradient">Takip Modulleri</span>
            </h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Her norolojik durum icin ozel olarak tasarlanmis takip ve analiz araclari
            </p>
          </div>

          {/* Modules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {diseaseModules.map((module, i) => (
              <div
                key={module.name}
                className={`group relative rounded-2xl overflow-hidden transition-all duration-500 ${
                  module.active
                    ? 'bg-slate-900/80 border border-white/10 hover:border-cyan-500/50'
                    : 'bg-slate-900/40 border border-white/5 opacity-70'
                }`}
              >
                {/* Glow Background */}
                {module.active && (
                  <div className={`absolute inset-0 ${module.bgGlow} blur-3xl opacity-0 group-hover:opacity-50 transition-opacity`} />
                )}

                <div className="relative p-6">
                  {/* Icon */}
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${module.gradient} mb-4 shadow-lg ${
                    module.active ? `shadow-${module.color}-500/25` : ''
                  }`}>
                    <module.icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Title & Status */}
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold text-white">{module.name}</h3>
                    {module.active ? (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium">
                        Aktif
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full bg-slate-700 text-slate-400 text-xs font-medium">
                        Yakinda
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-slate-400 text-sm mb-4">
                    {module.description}
                  </p>

                  {/* Action */}
                  {module.active && (
                    <Link
                      href="/auth/register"
                      className={`inline-flex items-center gap-2 text-sm font-medium text-${module.color}-400 hover:text-${module.color}-300 transition-colors`}
                    >
                      Kullanmaya Basla
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="max-w-4xl mx-auto px-4">
          <div className="relative rounded-3xl overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-600 to-purple-700" />
            <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10" />

            {/* Content */}
            <div className="relative p-12 md:p-16 text-center">
              <BrainIcon size={80} animated={false} className="mx-auto mb-8 opacity-90" />

              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Norolojik Sagliginizi Kontrol Altina Alin
              </h2>
              <p className="text-white/80 text-lg mb-8 max-w-2xl mx-auto">
                Binlerce kullanici gibi siz de sagliginizi takip etmeye ve yasam kalitenizi artirmaya baslayın.
              </p>

              <Link
                href="/auth/register"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-slate-900 rounded-2xl text-lg font-semibold hover:bg-slate-100 transition-all shadow-xl hover:-translate-y-1"
              >
                Ucretsiz Hesap Olustur
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
