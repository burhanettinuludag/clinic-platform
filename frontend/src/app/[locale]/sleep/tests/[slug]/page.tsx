'use client';

import { useState, useMemo } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ChevronLeft, ChevronRight, ClipboardList, RotateCcw,
  CheckCircle2, AlertTriangle, ShieldCheck, Info,
} from 'lucide-react';
import { useSleepScreeningTest } from '@/hooks/useSleepData';
import type { SleepScreeningResultRange } from '@/lib/types/sleep';

const RESULT_COLORS: Record<string, { bg: string; border: string; text: string; icon: string; bar: string }> = {
  green: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-800',
    icon: 'text-emerald-500',
    bar: 'bg-emerald-500',
  },
  yellow: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-800',
    icon: 'text-amber-500',
    bar: 'bg-amber-500',
  },
  orange: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    text: 'text-orange-800',
    icon: 'text-orange-500',
    bar: 'bg-orange-500',
  },
  red: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-800',
    icon: 'text-red-500',
    bar: 'bg-red-500',
  },
};

export default function SleepTestDetailPage() {
  const t = useTranslations('sleep');
  const params = useParams();
  const locale = (params?.locale as string) || 'tr';
  const slug = params?.slug as string;

  const { data: test, isLoading } = useSleepScreeningTest(slug);

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [showResult, setShowResult] = useState(false);

  const questions = test?.questions || [];
  const totalQuestions = questions.length;
  const progress = totalQuestions > 0 ? ((currentQuestion + 1) / totalQuestions) * 100 : 0;

  const totalScore = useMemo(() => {
    return Object.values(answers).reduce((sum, score) => sum + score, 0);
  }, [answers]);

  const maxPossibleScore = useMemo(() => {
    return questions.reduce((sum, q) => {
      const maxOption = q.options.reduce((max, opt) => Math.max(max, opt.score), 0);
      return sum + maxOption;
    }, 0);
  }, [questions]);

  const resultRange: SleepScreeningResultRange | null = useMemo(() => {
    if (!test?.result_ranges) return null;
    return test.result_ranges.find(
      r => totalScore >= r.min_score && totalScore <= r.max_score
    ) || null;
  }, [test, totalScore]);

  const handleSelectOption = (questionId: string, score: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: score }));
  };

  const handleNext = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      setShowResult(true);
    }
  };

  const handlePrev = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleReset = () => {
    setAnswers({});
    setCurrentQuestion(0);
    setShowResult(false);
  };

  const currentQ = questions[currentQuestion];
  const isCurrentAnswered = currentQ ? answers[currentQ.id] !== undefined : false;
  const allAnswered = questions.every(q => answers[q.id] !== undefined);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-indigo-50/50 via-white to-white flex items-center justify-center">
        <div className="animate-pulse text-center">
          <div className="w-16 h-16 bg-indigo-200 rounded-2xl mx-auto mb-4" />
          <div className="h-6 bg-gray-200 rounded w-48 mx-auto mb-2" />
          <div className="h-4 bg-gray-100 rounded w-32 mx-auto" />
        </div>
      </div>
    );
  }

  if (!test) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-indigo-50/50 via-white to-white flex items-center justify-center">
        <div className="text-center">
          <ClipboardList className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">{t('tests.notFound')}</p>
          <Link href={`/${locale}/sleep/tests`} className="mt-4 inline-block text-indigo-600 hover:underline">
            {t('tests.backToTests')}
          </Link>
        </div>
      </div>
    );
  }

  // ── Sonuç Ekranı ──────────────────────────────────────────────────

  if (showResult && resultRange) {
    const colors = RESULT_COLORS[resultRange.color] || RESULT_COLORS.green;
    const scorePercent = maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 100 : 0;

    return (
      <div className="min-h-screen bg-gradient-to-b from-indigo-50/50 via-white to-white">
        <div className="max-w-2xl mx-auto px-4 py-12">
          {/* Header */}
          <Link
            href={`/${locale}/sleep/tests`}
            className="inline-flex items-center gap-2 text-gray-500 hover:text-indigo-600 transition-colors mb-8"
          >
            <ChevronLeft className="w-4 h-4" />
            {t('tests.backToTests')}
          </Link>

          {/* Result Card */}
          <div className={`${colors.bg} ${colors.border} border-2 rounded-3xl p-8 mb-8`}>
            <div className="text-center mb-6">
              <div className={`w-20 h-20 rounded-full ${colors.bg} border-4 ${colors.border} flex items-center justify-center mx-auto mb-4`}>
                <span className={`text-3xl font-bold ${colors.text}`}>{totalScore}</span>
              </div>
              <p className="text-sm text-gray-500 mb-2">
                {t('tests.result.score')}: {totalScore} / {maxPossibleScore}
              </p>
              <h2 className={`text-2xl font-bold ${colors.text} mb-2`}>{resultRange.title}</h2>
            </div>

            {/* Score Bar */}
            <div className="mb-6">
              <div className="w-full h-3 bg-white/60 rounded-full overflow-hidden">
                <div
                  className={`h-full ${colors.bar} rounded-full transition-all duration-1000 ease-out`}
                  style={{ width: `${scorePercent}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>{t('tests.result.low')}</span>
                <span>{t('tests.result.high')}</span>
              </div>
            </div>

            {/* Description */}
            <p className={`${colors.text} text-center mb-6 leading-relaxed`}>
              {resultRange.description}
            </p>

            {/* Recommendation */}
            {resultRange.recommendation && (
              <div className="bg-white/60 rounded-xl p-5 border border-white/80">
                <h3 className={`font-semibold ${colors.text} mb-2 flex items-center gap-2`}>
                  <CheckCircle2 className="w-5 h-5" />
                  {t('tests.result.recommendation')}
                </h3>
                <p className="text-gray-700 text-sm leading-relaxed">
                  {resultRange.recommendation}
                </p>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 mb-8">
            <button
              onClick={handleReset}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-white border border-gray-200 rounded-xl text-gray-700 hover:border-indigo-300 hover:bg-indigo-50 transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              {t('tests.result.retake')}
            </button>
            <Link
              href={`/${locale}/sleep/tests`}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors"
            >
              <ClipboardList className="w-4 h-4" />
              {t('tests.result.otherTests')}
            </Link>
          </div>

          {/* Disclaimer */}
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 flex gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-amber-800 font-semibold mb-1">{t('tests.disclaimer.title')}</p>
              <p className="text-xs text-amber-700 leading-relaxed">{t('tests.disclaimer.text')}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Soru Ekranı ───────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50/50 via-white to-white">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Link
            href={`/${locale}/sleep/tests`}
            className="inline-flex items-center gap-2 text-gray-500 hover:text-indigo-600 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            {t('tests.backToTests')}
          </Link>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <ShieldCheck className="w-4 h-4" />
            {t('tests.hero.anonymous')}
          </div>
        </div>

        {/* Test Title */}
        <h1 className="text-xl font-bold text-gray-900 mb-2">{test.title}</h1>

        {/* Instructions */}
        {test.instructions && currentQuestion === 0 && (
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 mb-6 flex gap-3">
            <Info className="w-5 h-5 text-indigo-500 shrink-0 mt-0.5" />
            <p className="text-sm text-indigo-700">{test.instructions}</p>
          </div>
        )}

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
            <span>{t('tests.question')} {currentQuestion + 1} / {totalQuestions}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question */}
        {currentQ && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {currentQ.question}
            </h2>
            {currentQ.help_text && (
              <p className="text-sm text-gray-500 mb-4 flex items-start gap-2">
                <Info className="w-4 h-4 shrink-0 mt-0.5" />
                {currentQ.help_text}
              </p>
            )}

            {/* Options */}
            <div className="space-y-3 mt-4">
              {currentQ.options.map(option => {
                const isSelected = answers[currentQ.id] === option.score;
                return (
                  <button
                    key={option.id}
                    onClick={() => handleSelectOption(currentQ.id, option.score)}
                    className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 ${
                      isSelected
                        ? 'border-indigo-500 bg-indigo-50 shadow-sm'
                        : 'border-gray-100 bg-gray-50/50 hover:border-indigo-200 hover:bg-indigo-50/50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-all ${
                        isSelected ? 'border-indigo-500 bg-indigo-500' : 'border-gray-300'
                      }`}>
                        {isSelected && (
                          <div className="w-2 h-2 rounded-full bg-white" />
                        )}
                      </div>
                      <span className={`text-sm ${isSelected ? 'text-indigo-900 font-medium' : 'text-gray-700'}`}>
                        {option.text}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrev}
            disabled={currentQuestion === 0}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
              currentQuestion === 0
                ? 'text-gray-300 cursor-not-allowed'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <ChevronLeft className="w-4 h-4" />
            {t('tests.prev')}
          </button>

          {/* Question dots */}
          <div className="hidden sm:flex items-center gap-1.5">
            {questions.map((q, idx) => (
              <button
                key={q.id}
                onClick={() => setCurrentQuestion(idx)}
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  idx === currentQuestion
                    ? 'bg-indigo-500 scale-125'
                    : answers[q.id] !== undefined
                    ? 'bg-indigo-300'
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>

          <button
            onClick={handleNext}
            disabled={!isCurrentAnswered}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
              !isCurrentAnswered
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : currentQuestion === totalQuestions - 1
                ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm'
                : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm'
            }`}
          >
            {currentQuestion === totalQuestions - 1 ? (
              <>
                {t('tests.showResult')}
                <CheckCircle2 className="w-4 h-4" />
              </>
            ) : (
              <>
                {t('tests.next')}
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
