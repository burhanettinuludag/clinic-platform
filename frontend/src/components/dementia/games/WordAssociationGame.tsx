'use client';

import { useState, useEffect, useCallback } from 'react';
import { Link2, Play, Trophy, RotateCcw } from 'lucide-react';

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

interface WordPair {
  prompt: string;
  answer: string;
  distractors: string[];
}

const WORD_PAIRS: WordPair[] = [
  { prompt: 'Gunes', answer: 'Isik', distractors: ['Ses', 'Su', 'Toprak'] },
  { prompt: 'Doktor', answer: 'Hastane', distractors: ['Okul', 'Pazar', 'Sinema'] },
  { prompt: 'Kitap', answer: 'Okumak', distractors: ['Yuzme', 'Kosmak', 'Uyumak'] },
  { prompt: 'Yagmur', answer: 'Semsiye', distractors: ['Gozluk', 'Sapka', 'Eldiven'] },
  { prompt: 'Kus', answer: 'Ucmak', distractors: ['Yuzmek', 'Kazmak', 'Surumek'] },
  { prompt: 'Araba', answer: 'Yol', distractors: ['Deniz', 'Bulut', 'Dag'] },
  { prompt: 'Kedi', answer: 'Miyavlamak', distractors: ['Havlamak', 'Meleme', 'Otmek'] },
  { prompt: 'Buz', answer: 'Soguk', distractors: ['Sicak', 'Ilik', 'Serin'] },
  { prompt: 'Ates', answer: 'Sicak', distractors: ['Soguk', 'Islak', 'Kuru'] },
  { prompt: 'Goz', answer: 'Gormek', distractors: ['Duymak', 'Tatmak', 'Koklamak'] },
  { prompt: 'Kulak', answer: 'Duymak', distractors: ['Gormek', 'Tatmak', 'Dokunmak'] },
  { prompt: 'Ayakkabi', answer: 'Ayak', distractors: ['El', 'Bas', 'Kol'] },
  { prompt: 'Saat', answer: 'Zaman', distractors: ['Renk', 'Ses', 'Koku'] },
  { prompt: 'Kalem', answer: 'Yazmak', distractors: ['Kesmek', 'Boyamak', 'Silmek'] },
  { prompt: 'Yildiz', answer: 'Gece', distractors: ['Sabah', 'Ogle', 'Ikindi'] },
  { prompt: 'Deniz', answer: 'Dalga', distractors: ['Yaprak', 'Kar', 'Ruzgar'] },
  { prompt: 'Agac', answer: 'Yaprak', distractors: ['Tuy', 'Pul', 'Kabuk'] },
  { prompt: 'Cocuk', answer: 'Oyun', distractors: ['Is', 'Uyku', 'Yemek'] },
  { prompt: 'Televizyon', answer: 'Izlemek', distractors: ['Dinlemek', 'Okumak', 'Yazmak'] },
  { prompt: 'Mutfak', answer: 'Yemek', distractors: ['Uyumak', 'Calismak', 'Yuzme'] },
  { prompt: 'Cicek', answer: 'Bahce', distractors: ['Mutfak', 'Garaj', 'Bodrum'] },
  { prompt: 'Soguk', answer: 'Kis', distractors: ['Yaz', 'Ilkbahar', 'Sonbahar'] },
  { prompt: 'Ekmek', answer: 'Firin', distractors: ['Eczane', 'Kutuphane', 'Market'] },
  { prompt: 'Balik', answer: 'Deniz', distractors: ['Dag', 'Col', 'Orman'] },
  { prompt: 'Pilot', answer: 'Ucak', distractors: ['Tren', 'Gemi', 'Bisiklet'] },
  { prompt: 'Kalp', answer: 'Sevgi', distractors: ['Korku', 'Ofke', 'Uzuntu'] },
  { prompt: 'Anahtar', answer: 'Kilit', distractors: ['Pencere', 'Duvar', 'Cati'] },
  { prompt: 'Bardak', answer: 'Icmek', distractors: ['Yemek', 'Kesmek', 'Dikmek'] },
  { prompt: 'Sabun', answer: 'Temizlik', distractors: ['Yemek', 'Oyun', 'Uyku'] },
  { prompt: 'Para', answer: 'Banka', distractors: ['Okul', 'Park', 'Cami'] },
  { prompt: 'Bulut', answer: 'Gok', distractors: ['Toprak', 'Deniz', 'Orman'] },
  { prompt: 'Muzik', answer: 'Dinlemek', distractors: ['Gormek', 'Tatmak', 'Koklamak'] },
];

function shuffleArray<T>(arr: T[]): T[] {
  const shuffled = [...arr];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export default function WordAssociationGame({ config, difficulty, onComplete }: Props) {
  const [phase, setPhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [questions, setQuestions] = useState<WordPair[]>([]);
  const [options, setOptions] = useState<string[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);

  const totalRounds = (config.rounds as number) || 15;

  const startGame = () => {
    const shuffled = shuffleArray(WORD_PAIRS).slice(0, totalRounds);
    setQuestions(shuffled);
    setPhase('playing');
    setStartTime(Date.now());
    setRound(0);
    setScore(0);
    setCorrectCount(0);
  };

  const setupOptions = useCallback(() => {
    if (questions.length === 0 || round >= questions.length) return;
    const q = questions[round];
    const allOptions = shuffleArray([q.answer, ...q.distractors]);
    setOptions(allOptions);
    setSelectedAnswer(null);
    setIsCorrect(null);
  }, [questions, round]);

  useEffect(() => {
    if (phase === 'playing') {
      setupOptions();
    }
  }, [phase, round, setupOptions]);

  const handleAnswer = (answer: string) => {
    if (selectedAnswer !== null) return;

    const correct = answer === questions[round].answer;
    setSelectedAnswer(answer);
    setIsCorrect(correct);

    if (correct) {
      setScore((s) => s + 10);
      setCorrectCount((c) => c + 1);
    }

    setTimeout(() => {
      const nextRound = round + 1;
      if (nextRound >= Math.min(totalRounds, questions.length)) {
        const finalCorrect = correctCount + (correct ? 1 : 0);
        const finalScore = score + (correct ? 10 : 0);
        const duration = Math.floor((Date.now() - startTime) / 1000);
        const total = Math.min(totalRounds, questions.length);
        const accuracy = Math.round((finalCorrect / total) * 100);

        setPhase('complete');
        onComplete({
          score: Math.min(finalScore, 100),
          maxScore: 100,
          accuracy,
          duration,
          data: { totalRounds: total, correctAnswers: finalCorrect, difficulty },
        });
      } else {
        setRound(nextRound);
      }
    }, 1000);
  };

  // ---- READY ----
  if (phase === 'ready') {
    return (
      <div className="text-center">
        <div className="p-6 bg-teal-50 rounded-xl mb-4">
          <Link2 className="w-12 h-12 text-teal-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Kelime Iliskisi</h3>
          <p className="text-sm text-gray-600 mb-4">
            Verilen kelimeyle en cok iliskili olan kelimeyi secenekler arasindan bulun.
          </p>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition mx-auto"
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
    const total = Math.min(totalRounds, questions.length);
    const accuracy = Math.round((correctCount / total) * 100);
    return (
      <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
        <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-gray-900 mb-2">Oyun Bitti!</h3>
        <div className="grid grid-cols-3 gap-4 my-4">
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-teal-600">{score}</p>
            <p className="text-xs text-gray-500">Puan</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-green-600">{correctCount}/{total}</p>
            <p className="text-xs text-gray-500">Dogru</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-purple-600">%{accuracy}</p>
            <p className="text-xs text-gray-500">Basari</p>
          </div>
        </div>
        <button
          onClick={() => { setPhase('ready'); }}
          className="flex items-center gap-2 px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition mx-auto"
        >
          <RotateCcw className="w-4 h-4" />
          Tekrar Oyna
        </button>
      </div>
    );
  }

  // ---- PLAYING ----
  const currentQ = questions[round];
  const total = Math.min(totalRounds, questions.length);

  return (
    <div>
      {/* Stats */}
      <div className="flex items-center justify-between mb-4 text-sm">
        <span className="text-gray-500">Soru {round + 1}/{total}</span>
        <span className="font-medium text-teal-600">Skor: {score}</span>
        <span className="text-green-600">Dogru: {correctCount}</span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
        <div
          className="bg-teal-500 h-2 rounded-full transition-all"
          style={{ width: `${(round / total) * 100}%` }}
        />
      </div>

      {/* Prompt word */}
      <div className="text-center mb-6">
        <p className="text-sm text-gray-500 mb-1">Bu kelimeyle en iliskili olan nedir?</p>
        <div className="inline-block px-8 py-4 bg-teal-100 rounded-xl">
          <span className="text-3xl font-bold text-teal-800">{currentQ?.prompt}</span>
        </div>
      </div>

      {/* Options */}
      <div className="grid grid-cols-2 gap-3">
        {options.map((opt) => {
          let btnClass = 'bg-white border-2 border-gray-200 text-gray-800 hover:border-teal-400';
          if (selectedAnswer !== null) {
            if (opt === currentQ.answer) {
              btnClass = 'bg-green-500 border-2 border-green-500 text-white';
            } else if (opt === selectedAnswer && !isCorrect) {
              btnClass = 'bg-red-500 border-2 border-red-500 text-white';
            } else {
              btnClass = 'bg-gray-100 border-2 border-gray-200 text-gray-400';
            }
          }
          return (
            <button
              key={opt}
              onClick={() => handleAnswer(opt)}
              disabled={selectedAnswer !== null}
              className={`p-4 rounded-xl font-medium text-lg transition-all ${btnClass}`}
            >
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}
