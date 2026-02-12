'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useDiseaseModules, usePatientModules, useEnrollModule, useUnenrollModule } from '@/hooks/usePatientData';
import { Brain, Zap, Activity, BookOpen, Check, ArrowRight } from 'lucide-react';

const moduleIcons: Record<string, typeof Brain> = {
  brain: Brain,
  zap: Zap,
  activity: Activity,
};

const moduleRoutes: Record<string, string> = {
  migraine: '/patient/migraine',
  epilepsy: '/patient/epilepsy',
  dementia: '/patient/dementia',
  parkinson: '/patient/parkinson',
};

export default function ModulesPage() {
  const t = useTranslations();
  const { data: allModules, isLoading } = useDiseaseModules();
  const { data: enrolledModules } = usePatientModules();
  const enrollMutation = useEnrollModule();
  const unenrollMutation = useUnenrollModule();

  const enrolledIds = new Set(enrolledModules?.map((m) => m.disease_module) ?? []);

  const getEnrollmentId = (moduleId: string) => {
    return enrolledModules?.find((m) => m.disease_module === moduleId)?.id;
  };

  if (isLoading) {
    return <div className="text-center py-12 text-gray-500">{t('common.loading')}</div>;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">{t('patient.modules.title')}</h1>
      <p className="text-gray-500 mb-8">{t('patient.modules.subtitle')}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {allModules?.map((mod) => {
          const Icon = moduleIcons[mod.icon] || BookOpen;
          const isEnrolled = enrolledIds.has(mod.id);
          const isActive = mod.is_active;
          const moduleHref = moduleRoutes[mod.disease_type];

          return (
            <div
              key={mod.id}
              className={`bg-white rounded-xl border-2 p-6 transition-all ${
                isEnrolled
                  ? 'border-blue-300 bg-blue-50/30'
                  : isActive
                  ? 'border-gray-200 hover:border-gray-300'
                  : 'border-gray-100 opacity-60'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${isEnrolled ? 'bg-blue-100' : 'bg-gray-100'}`}>
                  <Icon className={`w-6 h-6 ${isEnrolled ? 'text-blue-600' : 'text-gray-500'}`} />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{mod.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{mod.description}</p>
                </div>
              </div>

              <div className="mt-4 space-y-2">
                {isEnrolled ? (
                  <>
                    {moduleHref && (
                      <Link
                        href={moduleHref}
                        className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition"
                      >
                        {t('patient.modules.goToModule')} <ArrowRight className="w-4 h-4" />
                      </Link>
                    )}
                    <div className="flex items-center gap-2">
                      <span className="flex items-center gap-1.5 text-sm text-blue-600 font-medium">
                        <Check className="w-4 h-4" /> {t('patient.modules.enrolled')}
                      </span>
                      <button
                        onClick={() => {
                          const id = getEnrollmentId(mod.id);
                          if (id) unenrollMutation.mutate(id);
                        }}
                        disabled={unenrollMutation.isPending}
                        className="ml-auto text-xs text-red-500 hover:text-red-600"
                      >
                        {t('patient.modules.unenroll')}
                      </button>
                    </div>
                  </>
                ) : isActive ? (
                  <button
                    onClick={() => enrollMutation.mutate(mod.id)}
                    disabled={enrollMutation.isPending}
                    className="w-full py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {t('patient.modules.enroll')}
                  </button>
                ) : (
                  <span className="block text-center text-sm text-gray-400 py-2.5">
                    {t('patient.modules.comingSoon')}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
