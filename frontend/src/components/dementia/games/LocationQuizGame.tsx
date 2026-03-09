'use client';

import { useState, useCallback, useMemo } from 'react';
import { MapPin, Play, Trophy, RotateCcw } from 'lucide-react';

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

interface Question {
  question: string;
  correctAnswer: string | null; // null = self-report (her cevap dogru)
  options: string[];
  type: string;
  isSelfReport: boolean;
}

function shuffleArray<T>(arr: T[]): T[] {
  const shuffled = [...arr];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Turkiye illeri (secme)
const TURKISH_CITIES = [
  'Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya',
  'Adana', 'Konya', 'Gaziantep', 'Mersin', 'Diyarbakir',
  'Kayseri', 'Eskisehir', 'Samsun', 'Trabzon', 'Denizli',
  'Malatya', 'Erzurum', 'Van', 'Sakarya', 'Mugla',
];

const COUNTRIES = [
  'Turkiye', 'Almanya', 'Fransa', 'Ingiltere', 'Italya',
  'Ispanya', 'Yunanistan', 'Rusya', 'ABD', 'Japonya',
];

const HOME_TYPES = ['Apartman Dairesi', 'Mustakilev', 'Villa', 'Yurt', 'Huzurevi'];

const ROOMS = [
  'Oturma Odasi', 'Yatak Odasi', 'Mutfak', 'Banyo',
  'Balkon', 'Calismadasi', 'Yemek Odasi', 'Koridor',
];

export default function LocationQuizGame({ config, difficulty, onComplete }: Props) {
  const [phase, setPhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [feedback, setFeedback] = useState<null | { correct: boolean; answer: string }>(null);
  const [answers, setAnswers] = useState<boolean[]>([]);

  const questionTypes = useMemo(() => {
    const types = config.question_types as string[] | undefined;
    return types || ['country', 'city', 'home_type', 'current_room'];
  }, [config]);

  const generateQuestions = useCallback((): Question[] => {
    const allQuestions: Question[] = [];

    if (questionTypes.includes('country')) {
      // Dogrulanabilir: Turkiye
      const correct = 'Turkiye';
      const distractors = shuffleArray(COUNTRIES.filter((c) => c !== correct)).slice(0, 3);
      allQuestions.push({
        question: 'Hangi ulkede yasiyorsunuz?',
        correctAnswer: correct,
        options: shuffleArray([correct, ...distractors]),
        type: 'country',
        isSelfReport: false,
      });
    }

    if (questionTypes.includes('city')) {
      // Self-report: dogru cevap bilinemez, her cevap +10
      const cityOptions = shuffleArray(TURKISH_CITIES).slice(0, 4);
      allQuestions.push({
        question: 'Hangi sehirde yasiyorsunuz?',
        correctAnswer: null,
        options: cityOptions,
        type: 'city',
        isSelfReport: true,
      });
    }

    if (questionTypes.includes('home_type')) {
      // Self-report
      allQuestions.push({
        question: 'Ne tip bir evde yasiyorsunuz?',
        correctAnswer: null,
        options: shuffleArray([...HOME_TYPES]).slice(0, 4),
        type: 'home_type',
        isSelfReport: true,
      });
    }

    if (questionTypes.includes('current_room')) {
      // Self-report
      allQuestions.push({
        question: 'Su an evin hangi odasindasiniz?',
        correctAnswer: null,
        options: shuffleArray([...ROOMS]).slice(0, 4),
        type: 'current_room',
        isSelfReport: true,
      });
    }

    // Ek sorular (zorluga gore)
    if (difficulty !== 'easy') {
      if (questionTypes.includes('country')) {
        allQuestions.push({
          question: 'Turkiye hangi kitada yer alir?',
          correctAnswer: 'Avrupa ve Asya',
          options: shuffleArray(['Avrupa ve Asya', 'Sadece Avrupa', 'Sadece Asya', 'Afrika']),
          type: 'geography',
          isSelfReport: false,
        });
      }

      allQuestions.push({
        question: 'Turkiye\'nin baskenti neresidir?',
        correctAnswer: 'Ankara',
        options: shuffleArray(['Ankara', 'Istanbul', 'Izmir', 'Bursa']),
        type: 'geography',
        isSelfReport: false,
      });
    }

    if (difficulty === 'hard') {
      allQuestions.push({
        question: 'Su an hangi semt veya mahallede yasiyorsunuz? (Tahmini secin)',
        correctAnswer: null,
        options: ['Merkez', 'Kenar mahalle', 'Kirsal alan', 'Site ici'],
        type: 'neighborhood',
        isSelfReport: true,
      });

      allQuestions.push({
        question: 'Eviniz kacinci katta?',
        correctAnswer: null,
        options: shuffleArray(['Zemin / Giris', '1-3. kat', '4-7. kat', '8+ kat']),
        type: 'floor',
        isSelfReport: true,
      });
    }

    return allQuestions;
  }, [questionTypes, difficulty]);

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
    let isCorrect: boolean;

    if (current.isSelfReport) {
      // Self-report: cevaplamak yeterli, +10
      isCorrect = true;
    } else {
      isCorrect = answer === current.correctAnswer;
    }

    if (isCorrect) {
      setScore((s) => s + 10);
    }
    setAnswers((a) => [...a, isCorrect]);
    setFeedback({ correct: isCorrect, answer });

    setTimeout(() => {
      setFeedback(null);
      if (currentIdx + 1 < questions.length) {
        setCurrentIdx((i) => i + 1);
      } else {
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
        <div className="p-6 bg-emerald-50 rounded-xl mb-4">
          <MapPin className="w-12 h-12 text-emerald-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Konum Farkindaligi Testi</h3>
          <p className="text-sm text-gray-600 mb-4">
            Yasadiginiz yer ve cevre hakkindaki sorulari cevaplayin. Bazi sorularin tek dogru cevabi
            yoktur, cevaplamaniz yeterlidir.
          </p>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition mx-auto"
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
        <p className="text-gray-600 mb-4">Konum farkindaligi testini tamamladiniz!</p>
        <div className="grid grid-cols-2 gap-4 my-4">
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-emerald-600">
              {totalCorrect}/{questions.length}
            </p>
            <p className="text-xs text-gray-500">Tamamlanan</p>
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
          className="flex items-center gap-2 px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition mx-auto"
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
        <span className="font-medium text-emerald-600">Puan: {score}</span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
        <div
          className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
        />
      </div>

      {/* Question */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-800 rounded-full text-sm mb-4">
          <MapPin className="w-4 h-4" />
          {current.isSelfReport ? 'Kisisel Bilgi' : 'Oryantasyon'}
        </div>
        <h3 className="text-xl font-bold text-gray-900">{current.question}</h3>
        {current.isSelfReport && (
          <p className="text-xs text-gray-400 mt-2">Bu soruda sizin icin en uygun secenegi secin</p>
        )}
      </div>

      {/* Options */}
      <div className="grid grid-cols-2 gap-3 max-w-md mx-auto">
        {current.options.map((option, idx) => {
          let btnClass =
            'bg-white border-2 border-gray-200 text-gray-800 hover:border-emerald-400 hover:bg-emerald-50';

          if (feedback) {
            if (current.isSelfReport && option === feedback.answer) {
              btnClass = 'bg-emerald-100 border-2 border-emerald-500 text-emerald-800';
            } else if (!current.isSelfReport) {
              if (option === current.correctAnswer) {
                btnClass = 'bg-green-100 border-2 border-green-500 text-green-800';
              } else if (option === feedback.answer && !feedback.correct) {
                btnClass = 'bg-red-100 border-2 border-red-500 text-red-800';
              } else {
                btnClass = 'bg-white border-2 border-gray-200 text-gray-400';
              }
            } else {
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
        <div
          className={`mt-4 text-center text-sm font-medium ${
            feedback.correct ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {current.isSelfReport
            ? 'Cevapladiniz!'
            : feedback.correct
            ? 'Dogru!'
            : `Yanlis! Dogru cevap: ${current.correctAnswer}`}
        </div>
      )}
    </div>
  );
}
