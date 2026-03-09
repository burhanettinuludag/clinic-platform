'use client';

import { useState, useCallback, useMemo } from 'react';
import { Calendar, Play, Trophy, RotateCcw } from 'lucide-react';

interface Props {
  config: Record<string, unknown>;
  difficulty: string;
  onComplete: (result: {
    score: number;
    maxScore: number;
    accuracy: number;
    duration: number;
    data?: Record<string, unknown>;
  }) => void;
}

const TURKISH_DAYS = ['Pazar', 'Pazartesi', 'Sali', 'Carsamba', 'Persembe', 'Cuma', 'Cumartesi'];
const TURKISH_MONTHS = [
  'Ocak', 'Subat', 'Mart', 'Nisan', 'Mayis', 'Haziran',
  'Temmuz', 'Agustos', 'Eylul', 'Ekim', 'Kasim', 'Aralik',
];
const TURKISH_SEASONS = ['Kis', 'Kis', 'Ilkbahar', 'Ilkbahar', 'Ilkbahar', 'Yaz', 'Yaz', 'Yaz', 'Sonbahar', 'Sonbahar', 'Sonbahar', 'Kis'];
const TIME_OF_DAY_RANGES = [
  { label: 'Gece', start: 0, end: 6 },
  { label: 'Sabah', start: 6, end: 12 },
  { label: 'Ogle', start: 12, end: 14 },
  { label: 'Ogleden Sonra', start: 14, end: 18 },
  { label: 'Aksam', start: 18, end: 21 },
  { label: 'Gece', start: 21, end: 24 },
];

interface Question {
  question: string;
  correctAnswer: string;
  options: string[];
  type: string;
}

function shuffleArray<T>(arr: T[]): T[] {
  const shuffled = [...arr];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

function getDistractors(correct: string, pool: string[], count: number): string[] {
  const others = pool.filter((item) => item !== correct);
  const shuffled = shuffleArray(others);
  return shuffled.slice(0, count);
}

export default function DateTimeQuizGame({ config, difficulty, onComplete }: Props) {
  const [phase, setPhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [feedback, setFeedback] = useState<null | { correct: boolean; correctAnswer: string }>(null);
  const [answers, setAnswers] = useState<boolean[]>([]);

  const questionTypes = useMemo(() => {
    const types = config.question_types as string[] | undefined;
    return types || ['day', 'date', 'month', 'year', 'season', 'time_of_day'];
  }, [config]);

  const generateQuestions = useCallback((): Question[] => {
    const now = new Date();
    const currentDay = TURKISH_DAYS[now.getDay()];
    const currentDate = now.getDate();
    const currentMonth = TURKISH_MONTHS[now.getMonth()];
    const currentYear = now.getFullYear();
    const currentSeason = TURKISH_SEASONS[now.getMonth()];
    const currentHour = now.getHours();
    const currentTimeOfDay =
      TIME_OF_DAY_RANGES.find((r) => currentHour >= r.start && currentHour < r.end)?.label || 'Gece';

    const allQuestions: Question[] = [];

    if (questionTypes.includes('day')) {
      const distractors = getDistractors(currentDay, TURKISH_DAYS, 3);
      allQuestions.push({
        question: 'Bugun gunlerden ne?',
        correctAnswer: currentDay,
        options: shuffleArray([currentDay, ...distractors]),
        type: 'day',
      });
    }

    if (questionTypes.includes('date')) {
      const correct = String(currentDate);
      const datePool = Array.from({ length: 31 }, (_, i) => String(i + 1));
      const distractors = getDistractors(correct, datePool, 3);
      allQuestions.push({
        question: 'Bugun ayin kaci?',
        correctAnswer: correct,
        options: shuffleArray([correct, ...distractors]),
        type: 'date',
      });
    }

    if (questionTypes.includes('month')) {
      const distractors = getDistractors(currentMonth, TURKISH_MONTHS, 3);
      allQuestions.push({
        question: 'Su an hangi aydayiz?',
        correctAnswer: currentMonth,
        options: shuffleArray([currentMonth, ...distractors]),
        type: 'month',
      });
    }

    if (questionTypes.includes('year')) {
      const correct = String(currentYear);
      const yearPool = [
        String(currentYear - 2),
        String(currentYear - 1),
        String(currentYear),
        String(currentYear + 1),
      ];
      const distractors = getDistractors(correct, yearPool, 3);
      allQuestions.push({
        question: 'Su an hangi yildayiz?',
        correctAnswer: correct,
        options: shuffleArray([correct, ...distractors]),
        type: 'year',
      });
    }

    if (questionTypes.includes('season')) {
      const allSeasons = ['Ilkbahar', 'Yaz', 'Sonbahar', 'Kis'];
      const distractors = getDistractors(currentSeason, allSeasons, 3);
      allQuestions.push({
        question: 'Su an hangi mevsimdeyiz?',
        correctAnswer: currentSeason,
        options: shuffleArray([currentSeason, ...distractors]),
        type: 'season',
      });
    }

    if (questionTypes.includes('time_of_day')) {
      const allTimes = ['Sabah', 'Ogle', 'Ogleden Sonra', 'Aksam', 'Gece'];
      const distractors = getDistractors(currentTimeOfDay, allTimes, 3);
      allQuestions.push({
        question: 'Gunun hangi vaktindeyiz?',
        correctAnswer: currentTimeOfDay,
        options: shuffleArray([currentTimeOfDay, ...distractors]),
        type: 'time_of_day',
      });
    }

    return shuffleArray(allQuestions);
  }, [questionTypes]);

  const startGame = () => {
    const qs = generateQuestions();
    setQuestions(qs);
    setCurrentIdx(0);
    setScore(0);
    setAnswers([]);
    setFeedback(null);
    setStartTime(Date.now());
    setPhase('playing');
  };

  const handleAnswer = (answer: string) => {
    if (feedback) return;

    const current = questions[currentIdx];
    const isCorrect = answer === current.correctAnswer;

    if (isCorrect) {
      setScore((s) => s + 10);
    }
    setAnswers((a) => [...a, isCorrect]);
    setFeedback({ correct: isCorrect, correctAnswer: current.correctAnswer });

    setTimeout(() => {
      setFeedback(null);
      if (currentIdx + 1 < questions.length) {
        setCurrentIdx((i) => i + 1);
      } else {
        // Oyun bitti
        const totalCorrect = (isCorrect ? 1 : 0) + answers.filter(Boolean).length;
        const totalQuestions = questions.length;
        const finalScore = totalCorrect * 10;
        const accuracy = Math.round((totalCorrect / totalQuestions) * 100);
        const duration = Math.floor((Date.now() - startTime) / 1000);

        setPhase('complete');
        onComplete({
          score: Math.max(10, Math.min(finalScore, 100)),
          maxScore: totalQuestions * 10,
          accuracy,
          duration,
          data: {
            totalCorrect,
            totalQuestions,
            difficulty,
            questionTypes: questions.map((q) => q.type),
          },
        });
      }
    }, 1000);
  };

  // ---- READY ----
  if (phase === 'ready') {
    return (
      <div className="text-center">
        <div className="p-6 bg-amber-50 rounded-xl mb-4">
          <Calendar className="w-12 h-12 text-amber-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Tarih ve Zaman Testi</h3>
          <p className="text-sm text-gray-600 mb-4">
            Bugunun tarihi, gunu, mevsimi ve gunun vakti hakkindaki sorulari cevaplayin.
          </p>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition mx-auto"
          >
            <Play className="w-5 h-5" />
            Basla
          </button>
        </div>
      </div>
    );
  }

  // ---- COMPLETE ----
  if (phase === 'complete') {
    const totalCorrect = answers.filter(Boolean).length;
    return (
      <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
        <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-gray-900 mb-2">Tebrikler!</h3>
        <p className="text-gray-600 mb-4">Tarih ve zaman testini tamamladiniz!</p>
        <div className="grid grid-cols-2 gap-4 my-4">
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-amber-600">
              {totalCorrect}/{questions.length}
            </p>
            <p className="text-xs text-gray-500">Dogru</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-green-600">
              {Math.floor((Date.now() - startTime) / 1000)}s
            </p>
            <p className="text-xs text-gray-500">Sure</p>
          </div>
        </div>
        <button
          onClick={() => setPhase('ready')}
          className="flex items-center gap-2 px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition mx-auto"
        >
          <RotateCcw className="w-4 h-4" />
          Tekrar Oyna
        </button>
      </div>
    );
  }

  // ---- PLAYING ----
  const current = questions[currentIdx];

  return (
    <div>
      {/* Progress */}
      <div className="flex items-center justify-between mb-4 text-sm">
        <span className="text-gray-500">
          Soru {currentIdx + 1}/{questions.length}
        </span>
        <span className="font-medium text-amber-600">Puan: {score}</span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
        <div
          className="bg-amber-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
        />
      </div>

      {/* Question */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-100 text-amber-800 rounded-full text-sm mb-4">
          <Calendar className="w-4 h-4" />
          Oryantasyon
        </div>
        <h3 className="text-xl font-bold text-gray-900">{current.question}</h3>
      </div>

      {/* Options */}
      <div className="grid grid-cols-2 gap-3 max-w-md mx-auto">
        {current.options.map((option, idx) => {
          let btnClass = 'bg-white border-2 border-gray-200 text-gray-800 hover:border-amber-400 hover:bg-amber-50';

          if (feedback) {
            if (option === current.correctAnswer) {
              btnClass = 'bg-green-100 border-2 border-green-500 text-green-800';
            } else if (option !== current.correctAnswer && feedback && !feedback.correct) {
              btnClass = 'bg-white border-2 border-gray-200 text-gray-400';
            }
          }

          return (
            <button
              key={idx}
              onClick={() => handleAnswer(option)}
              disabled={!!feedback}
              className={`p-4 rounded-xl font-medium transition-all duration-200 ${btnClass}`}
            >
              {option}
            </button>
          );
        })}
      </div>

      {/* Feedback */}
      {feedback && (
        <div className={`mt-4 text-center text-sm font-medium ${feedback.correct ? 'text-green-600' : 'text-red-600'}`}>
          {feedback.correct ? 'Dogru!' : `Yanlis! Dogru cevap: ${feedback.correctAnswer}`}
        </div>
      )}
    </div>
  );
}
