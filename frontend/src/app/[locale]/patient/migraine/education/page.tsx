'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import { Link } from '@/i18n/navigation';
import {
  useEducationItems,
  useStartEducation,
  useCompleteEducation,
  useQuizzes,
  useQuiz,
  useSubmitQuiz,
  type EducationItem,
  type EducationQuiz,
} from '@/hooks/usePatientData';
import {
  ArrowLeft,
  BookOpen,
  Clock,
  CheckCircle2,
  Play,
  FileText,
  Image,
  Sparkles,
  ChevronRight,
  ChevronDown,
  X,
  Brain,
  ShieldAlert,
  Heart,
  GraduationCap,
  Zap,
  Trophy,
  Star,
  RotateCcw,
  Award,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

// ─── Module definitions ───
const MODULE_META: Record<string, { icon: typeof BookOpen; color: string; gradient: string; label: string }> = {
  'migraine-basics': {
    icon: Brain,
    color: 'purple',
    gradient: 'from-purple-500 to-purple-700',
    label: 'Migreni Tanıyalım',
  },
  'migraine-triggers': {
    icon: Zap,
    color: 'orange',
    gradient: 'from-orange-500 to-red-500',
    label: 'Tetikleyicileri Keşfet',
  },
  'migraine-attack': {
    icon: ShieldAlert,
    color: 'red',
    gradient: 'from-red-500 to-pink-600',
    label: 'Atak Yönetimi',
  },
  'migraine-lifestyle': {
    icon: Heart,
    color: 'green',
    gradient: 'from-emerald-500 to-teal-600',
    label: 'Yaşam Tarzı',
  },
  'migraine-advanced': {
    icon: GraduationCap,
    color: 'indigo',
    gradient: 'from-indigo-500 to-blue-600',
    label: 'İleri Konular',
  },
};

const MODULE_ORDER = [
  'migraine-basics',
  'migraine-triggers',
  'migraine-attack',
  'migraine-lifestyle',
  'migraine-advanced',
];

interface CategoryGroup {
  slug: string;
  name: string;
  items: EducationItem[];
  quiz: EducationQuiz | null;
}

export default function MigraineEducationPage() {
  const { data: educationItems, isLoading: loadingItems, isError: errorItems } = useEducationItems({ disease_module: 'migraine' });
  const { data: quizzes, isLoading: loadingQuizzes, isError: errorQuizzes } = useQuizzes({ disease_module: 'migraine' });

  const [selectedItem, setSelectedItem] = useState<EducationItem | null>(null);
  const [activeQuizSlug, setActiveQuizSlug] = useState<string | null>(null);
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set(MODULE_ORDER));

  // Group items by category
  const modules = useMemo<CategoryGroup[]>(() => {
    if (!educationItems) return [];

    const grouped = new Map<string, EducationItem[]>();
    for (const item of educationItems) {
      const cat = item.category_slug ?? 'other';
      if (!grouped.has(cat)) grouped.set(cat, []);
      grouped.get(cat)!.push(item);
    }

    return MODULE_ORDER.map((slug) => {
      const items = grouped.get(slug) ?? [];
      items.sort((a, b) => a.order - b.order);
      const quiz = quizzes?.find((q) => q.category_slug === slug) ?? null;
      return {
        slug,
        name: MODULE_META[slug]?.label ?? slug,
        items,
        quiz,
      };
    }).filter((m) => m.items.length > 0);
  }, [educationItems, quizzes]);

  if (loadingItems || loadingQuizzes) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-pulse text-gray-500">Yükleniyor...</div>
      </div>
    );
  }

  if (errorItems || errorQuizzes) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Link href="/patient/migraine" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Migren Egitim Seti</h1>
        </div>
        <div className="text-center py-12 bg-white rounded-xl border border-red-200">
          <ShieldAlert className="w-12 h-12 text-red-300 mx-auto mb-3" />
          <p className="text-red-600 font-medium">Egitim icerikleri yuklenemedi.</p>
          <p className="text-gray-500 text-sm mt-1">LÃ¼tfen internet baÄlantÄ±nÄ±zÄ± kontrol edin ve sayfayÄ± yenileyin.</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm"
          >
            Sayfayi Yenile
          </button>
        </div>
      </div>
    );
  }

  const completedCount = educationItems?.filter((item) => item.progress?.completed_at).length ?? 0;
  const totalCount = educationItems?.length ?? 0;
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
  const passedQuizzes = quizzes?.filter((q) => q.best_attempt?.passed).length ?? 0;
  const totalQuizzes = quizzes?.length ?? 0;

  const toggleModule = (slug: string) => {
    setExpandedModules((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/patient/migraine" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Migren Egitim Seti</h1>
          <p className="text-sm text-gray-500">5 modul, 25 kart, 5 quiz - asamali ogrenme programi</p>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl p-6 text-white mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8" />
            <div>
              <div className="text-sm opacity-90">Genel Ilerleme</div>
              <div className="text-2xl font-bold">{completedCount}/{totalCount} Kart</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">%{progressPercent}</div>
            <div className="text-sm opacity-90 flex items-center gap-1 justify-end">
              <Trophy className="w-4 h-4" />
              {passedQuizzes}/{totalQuizzes} Quiz
            </div>
          </div>
        </div>
        <div className="h-2 bg-white/30 rounded-full overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Module mini-nav */}
      <div className="grid grid-cols-5 gap-2 mb-6">
        {modules.map((mod, idx) => {
          const meta = MODULE_META[mod.slug];
          const Icon = meta?.icon ?? BookOpen;
          const completed = mod.items.filter((i) => i.progress?.completed_at).length;
          const total = mod.items.length;
          const allDone = completed === total;
          const quizPassed = mod.quiz?.best_attempt?.passed;

          return (
            <button
              key={mod.slug}
              onClick={() => {
                setExpandedModules(new Set([mod.slug]));
                document.getElementById(`module-${mod.slug}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }}
              className={`flex flex-col items-center gap-1 p-3 rounded-xl border-2 transition-all text-center ${
                allDone && quizPassed
                  ? 'border-green-300 bg-green-50'
                  : allDone
                  ? 'border-yellow-300 bg-yellow-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                allDone ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
              }`}>
                {allDone ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
              </div>
              <span className="text-[10px] font-medium text-gray-600 leading-tight">{idx + 1}. Modul</span>
              <span className="text-[10px] text-gray-400">{completed}/{total}</span>
            </button>
          );
        })}
      </div>

      {/* Module Sections */}
      <div className="space-y-4">
        {modules.map((mod, moduleIdx) => {
          const meta = MODULE_META[mod.slug];
          const Icon = meta?.icon ?? BookOpen;
          const isExpanded = expandedModules.has(mod.slug);
          const completed = mod.items.filter((i) => i.progress?.completed_at).length;
          const total = mod.items.length;
          const allDone = completed === total;

          return (
            <div key={mod.slug} id={`module-${mod.slug}`} className="scroll-mt-4">
              {/* Module header */}
              <button
                onClick={() => toggleModule(mod.slug)}
                className={`w-full flex items-center gap-3 p-4 rounded-xl bg-gradient-to-r ${meta?.gradient ?? 'from-gray-500 to-gray-700'} text-white transition-all hover:shadow-md`}
              >
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 text-left">
                  <div className="text-xs opacity-80">Modul {moduleIdx + 1}</div>
                  <div className="font-semibold">{mod.name}</div>
                </div>
                <div className="flex items-center gap-2">
                  {allDone && <CheckCircle2 className="w-5 h-5 text-green-300" />}
                  <span className="text-sm opacity-90">{completed}/{total}</span>
                  <ChevronDown className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                </div>
              </button>

              {/* Module content */}
              {isExpanded && (
                <div className="mt-2 space-y-2 pl-2">
                  {mod.items.map((item, index) => (
                    <EducationCard
                      key={item.id}
                      item={item}
                      index={index + 1}
                      onClick={() => setSelectedItem(item)}
                    />
                  ))}

                  {/* Quiz button */}
                  {mod.quiz && (
                    <QuizCard quiz={mod.quiz} onStart={() => setActiveQuizSlug(mod.quiz!.slug)} allItemsDone={allDone} />
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {educationItems && educationItems.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Henuz egitim icerigi eklenmemis.</p>
        </div>
      )}

      {educationItems && educationItems.length > 0 && modules.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Egitim icerikleri yuklendi fakat modullere atanamadi.</p>
          <p className="text-xs text-gray-400 mt-1">LÃ¼tfen yÃ¶neticinize baÅvurun.</p>
        </div>
      )}

      {/* Education Content Modal */}
      {selectedItem && (
        <EducationModal item={selectedItem} onClose={() => setSelectedItem(null)} />
      )}

      {/* Quiz Modal */}
      {activeQuizSlug && (
        <QuizModal slug={activeQuizSlug} onClose={() => setActiveQuizSlug(null)} />
      )}
    </div>
  );
}

// ─── Education Card ───

function EducationCard({ item, index, onClick }: { item: EducationItem; index: number; onClick: () => void }) {
  const isCompleted = !!item.progress?.completed_at;
  const inProgress = item.progress && !item.progress.completed_at;

  const getContentIcon = () => {
    switch (item.content_type) {
      case 'video': return <Play className="w-4 h-4" />;
      case 'infographic': return <Image className="w-4 h-4" />;
      case 'interactive': return <Sparkles className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <button
      onClick={onClick}
      className={`w-full text-left bg-white rounded-xl border-2 p-4 transition-all hover:shadow-md ${
        isCompleted
          ? 'border-green-200 bg-green-50/30'
          : inProgress
          ? 'border-purple-200 bg-purple-50/30'
          : 'border-gray-200 hover:border-purple-300'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm ${
          isCompleted ? 'bg-green-100 text-green-600' : inProgress ? 'bg-purple-100 text-purple-600' : 'bg-gray-100 text-gray-500'
        }`}>
          {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : <span className="font-semibold">{index}</span>}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-medium text-sm ${isCompleted ? 'text-green-700' : 'text-gray-900'}`}>{item.title}</h3>
          <div className="flex items-center gap-2 mt-0.5 text-xs text-gray-500">
            {getContentIcon()}
            <Clock className="w-3 h-3" />
            <span>{item.estimated_duration_minutes} dk</span>
          </div>
        </div>
        <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
      </div>

      {inProgress && item.progress && (
        <div className="mt-2 pt-2 border-t border-purple-200">
          <div className="h-1.5 bg-purple-100 rounded-full overflow-hidden">
            <div className="h-full bg-purple-500 rounded-full" style={{ width: `${item.progress.progress_percent}%` }} />
          </div>
        </div>
      )}
    </button>
  );
}

// ─── Quiz Card ───

function QuizCard({ quiz, onStart, allItemsDone }: { quiz: EducationQuiz; onStart: () => void; allItemsDone: boolean }) {
  const passed = quiz.best_attempt?.passed;
  const attempted = !!quiz.best_attempt;

  return (
    <div className={`rounded-xl border-2 p-4 transition-all ${
      passed ? 'border-green-300 bg-green-50' : attempted ? 'border-yellow-300 bg-yellow-50' : 'border-indigo-200 bg-indigo-50/50'
    }`}>
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
          passed ? 'bg-green-200 text-green-700' : 'bg-indigo-200 text-indigo-700'
        }`}>
          {passed ? <Trophy className="w-5 h-5" /> : <Brain className="w-5 h-5" />}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-sm text-gray-900">{quiz.title}</h3>
          <p className="text-xs text-gray-500 mt-0.5">{quiz.description}</p>
          <div className="flex items-center gap-3 mt-1 text-xs">
            <span className="text-gray-500">{quiz.question_count} soru</span>
            <span className="text-indigo-600 font-medium">+{quiz.points_reward} puan</span>
            {quiz.best_attempt && (
              <span className={`font-medium ${passed ? 'text-green-600' : 'text-yellow-600'}`}>
                {quiz.best_attempt.score}/{quiz.best_attempt.total_questions}
                {passed ? ' Gecti' : ' Gecemedi'}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={onStart}
          disabled={!allItemsDone && !attempted}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-1 ${
            passed
              ? 'bg-green-600 text-white hover:bg-green-700'
              : !allItemsDone && !attempted
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          {passed ? <><RotateCcw className="w-3 h-3" /> Tekrar</> : attempted ? 'Tekrar Dene' : 'Quiz Baslat'}
        </button>
      </div>
      {!allItemsDone && !attempted && (
        <p className="text-[10px] text-gray-400 mt-2 text-center">Quizi acmak icin tum kartlari tamamlayin</p>
      )}
    </div>
  );
}

// ─── Education Modal ───

function EducationModal({ item, onClose }: { item: EducationItem; onClose: () => void }) {
  const startEducation = useStartEducation();
  const completeEducation = useCompleteEducation();
  const [isCompleting, setIsCompleting] = useState(false);

  const isCompleted = !!item.progress?.completed_at;
  const hasStarted = !!item.progress;

  const handleStart = () => {
    if (!hasStarted) startEducation.mutate(item.id);
  };

  const handleComplete = () => {
    if (item.progress?.id) {
      setIsCompleting(true);
      completeEducation.mutate(item.progress.id, {
        onSuccess: () => setTimeout(onClose, 1000),
        onError: () => setIsCompleting(false),
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-purple-50 to-indigo-50">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{item.title}</h2>
            <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>{item.estimated_duration_minutes} dakika</span>
              {isCompleted && (
                <span className="flex items-center gap-1 text-green-600 font-medium">
                  <CheckCircle2 className="w-4 h-4" /> Tamamlandi
                </span>
              )}
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {item.content_type === 'video' && item.video_url && (
            <div className="aspect-video bg-black rounded-lg mb-6 overflow-hidden">
              <iframe src={item.video_url} className="w-full h-full" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
            </div>
          )}
          {item.image && <img src={item.image} alt={item.title} className="w-full rounded-lg mb-6" />}
          <div className="prose-education">
            <ReactMarkdown>{item.body}</ReactMarkdown>
          </div>
        </div>

        <div className="p-4 border-t bg-gray-50">
          {isCompleted ? (
            <div className="flex items-center justify-center gap-2 py-2 text-green-600">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-medium">Bu icerigi tamamladiniz</span>
            </div>
          ) : isCompleting ? (
            <div className="flex items-center justify-center gap-2 py-2 text-green-600">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-medium">Tamamlandi!</span>
            </div>
          ) : !hasStarted ? (
            <button onClick={handleStart} disabled={startEducation.isPending} className="w-full py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition">
              {startEducation.isPending ? 'Baslatiliyor...' : 'Okumaya Basla'}
            </button>
          ) : (
            <button onClick={handleComplete} disabled={completeEducation.isPending} className="w-full py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition">
              {completeEducation.isPending ? 'Tamamlaniyor...' : 'Tamamladim'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Quiz Modal ───

function QuizModal({ slug, onClose }: { slug: string; onClose: () => void }) {
  const { data: quiz, isLoading } = useQuiz(slug);
  const submitQuiz = useSubmitQuiz();
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Map<string, number>>(new Map());
  const [showResult, setShowResult] = useState(false);
  const [result, setResult] = useState<{ score: number; total: number; passed: boolean } | null>(null);
  const startTime = useRef(Date.now());

  if (isLoading || !quiz) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black/50" onClick={onClose} />
        <div className="relative bg-white rounded-2xl p-8 text-center">
          <div className="animate-pulse text-gray-500">Quiz yukleniyor...</div>
        </div>
      </div>
    );
  }

  const questions = quiz.questions ?? [];
  const question = questions[currentQ];
  const totalQuestions = questions.length;
  const selectedOption = question ? answers.get(question.id) : undefined;
  const allAnswered = answers.size === totalQuestions;

  const handleSelect = (optionIndex: number) => {
    if (!question || showResult) return;
    setAnswers((prev) => {
      const next = new Map(prev);
      next.set(question.id, optionIndex);
      return next;
    });
  };

  const handleSubmit = () => {
    const payload = questions.map((q) => ({
      question_id: q.id,
      selected_option_index: answers.get(q.id) ?? 0,
    }));
    const duration = Math.round((Date.now() - startTime.current) / 1000);

    submitQuiz.mutate(
      { quiz: quiz.id, answers: payload, duration_seconds: duration },
      {
        onSuccess: (data) => {
          setResult({ score: data.score, total: data.total_questions, passed: data.passed });
          setShowResult(true);
        },
      },
    );
  };

  if (showResult && result) {
    const percent = Math.round((result.score / result.total) * 100);
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black/50" onClick={onClose} />
        <div className="relative bg-white rounded-2xl max-w-md w-full p-8 text-center">
          <div className={`w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center ${
            result.passed ? 'bg-green-100' : 'bg-yellow-100'
          }`}>
            {result.passed ? <Trophy className="w-10 h-10 text-green-600" /> : <RotateCcw className="w-10 h-10 text-yellow-600" />}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {result.passed ? 'Tebrikler!' : 'Tekrar Deneyin'}
          </h2>
          <p className="text-gray-600 mb-4">
            {result.score}/{result.total} dogru - %{percent}
          </p>
          {result.passed && (
            <div className="flex items-center justify-center gap-2 text-indigo-600 mb-4">
              <Award className="w-5 h-5" />
              <span className="font-medium">+{quiz.points_reward} puan kazandiniz!</span>
            </div>
          )}
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden mb-6">
            <div
              className={`h-full rounded-full transition-all duration-1000 ${result.passed ? 'bg-green-500' : 'bg-yellow-500'}`}
              style={{ width: `${percent}%` }}
            />
          </div>

          {/* Show answers review */}
          <div className="text-left space-y-3 mb-6 max-h-60 overflow-y-auto">
            {questions.map((q, idx) => {
              const selectedIdx = answers.get(q.id);
              const correctIdx = q.options.findIndex((o) => o.is_correct);
              const isCorrect = selectedIdx === correctIdx;
              return (
                <div key={q.id} className={`p-3 rounded-lg border text-sm ${isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
                  <div className="flex items-start gap-2">
                    {isCorrect ? <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" /> : <X className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />}
                    <div>
                      <p className="font-medium text-gray-800">{idx + 1}. {q.question}</p>
                      {!isCorrect && correctIdx >= 0 && (
                        <p className="text-green-700 mt-1 text-xs">Dogru cevap: {q.options[correctIdx].text}</p>
                      )}
                      {q.explanation && <p className="text-gray-500 mt-1 text-xs">{q.explanation}</p>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex gap-3">
            <button onClick={onClose} className="flex-1 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition">
              Kapat
            </button>
            {!result.passed && (
              <button
                onClick={() => {
                  setAnswers(new Map());
                  setCurrentQ(0);
                  setShowResult(false);
                  setResult(null);
                  startTime.current = Date.now();
                }}
                className="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition"
              >
                Tekrar Dene
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Quiz header */}
        <div className="p-4 border-b bg-gradient-to-r from-indigo-50 to-purple-50">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold text-gray-900">{quiz.title}</h2>
            <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg transition">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          {/* Progress dots */}
          <div className="flex items-center gap-1">
            {questions.map((q, idx) => (
              <button
                key={q.id}
                onClick={() => setCurrentQ(idx)}
                className={`h-2 flex-1 rounded-full transition-all ${
                  idx === currentQ
                    ? 'bg-indigo-600'
                    : answers.has(q.id)
                    ? 'bg-indigo-300'
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <div className="text-xs text-gray-500 mt-1">Soru {currentQ + 1}/{totalQuestions}</div>
        </div>

        {/* Question */}
        {question && (
          <div className="flex-1 overflow-y-auto p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">{question.question}</h3>
            <div className="space-y-3">
              {question.options.map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelect(idx)}
                  className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                    selectedOption === idx
                      ? 'border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center flex-shrink-0 text-sm font-medium ${
                      selectedOption === idx
                        ? 'border-indigo-500 bg-indigo-500 text-white'
                        : 'border-gray-300 text-gray-500'
                    }`}>
                      {String.fromCharCode(65 + idx)}
                    </div>
                    <span className={`text-sm ${selectedOption === idx ? 'text-indigo-900 font-medium' : 'text-gray-700'}`}>
                      {option.text}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="p-4 border-t bg-gray-50 flex items-center justify-between">
          <button
            onClick={() => setCurrentQ((p) => Math.max(0, p - 1))}
            disabled={currentQ === 0}
            className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-30 transition"
          >
            Onceki
          </button>

          {currentQ < totalQuestions - 1 ? (
            <button
              onClick={() => setCurrentQ((p) => Math.min(totalQuestions - 1, p + 1))}
              disabled={selectedOption === undefined}
              className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-30 transition"
            >
              Sonraki
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!allAnswered || submitQuiz.isPending}
              className="px-6 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-30 transition font-medium"
            >
              {submitQuiz.isPending ? 'GÃ¶nderiliyor...' : 'Tamamla'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
