'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Type, Play, Trophy, RotateCcw } from 'lucide-react';

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

// Zorluga gore Turkce kelime bankasi
const WORD_BANK: Record<string, string[]> = {
  easy: [
    'ARABA', 'ELMA', 'MASA', 'KAPI', 'OKUL', 'KEDI', 'AYAK', 'DERE', 'GECE',
    'KALE', 'YAZI', 'BABA', 'ANNE', 'KUTU', 'SAAT', 'KUPA', 'OYUN', 'DOST',
    'HAVA', 'YOLU', 'ISIK', 'RENK', 'AGAC', 'BALIK', 'BULUT',
  ],
  medium: [
    'BAHCE', 'KITAP', 'DENIZ', 'BULUT', 'CANTA', 'ORMAN', 'MEYVE', 'SABAH',
    'AKSAM', 'KALEM', 'TABAK', 'CADDE', 'SINIF', 'HAYAT', 'DUVAR', 'RESIM',
    'MISIR', 'SEKER', 'TATIL', 'MELEK', 'LIMON', 'KAYAK', 'SEBZE', 'BARDAK',
  ],
  hard: [
    'HASTANE', 'OTOBUS', 'LOKANTA', 'PENCERE', 'GAZETE', 'TELEFON',
    'BILGISAYAR', 'TELEVIZYON', 'CEVIZLIK', 'KUTUPHANE', 'RESTORAN',
    'APARTMAN', 'OTOMOBIL', 'HELIKOPTER', 'DOKUNMAK', 'MUTFAKTA',
    'KAPALICAR', 'TURUNCU', 'ANLATMAK', 'YAPRAKLAR',
  ],
};

const TOTAL_ROUNDS = 12;

export default function WordCompletionGame({ config, difficulty, onComplete }: Props) {
  const [phase, setPhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [currentWord, setCurrentWord] = useState('');
  const [maskedIndices, setMaskedIndices] = useState<number[]>([]);
  const [userInputs, setUserInputs] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [usedWords, setUsedWords] = useState<string[]>([]);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const missingPercentage = (config.missing_percentage as number) || 0.3;

  const pickWord = useCallback(() => {
    const words = WORD_BANK[difficulty] || WORD_BANK.easy;
    const available = words.filter((w) => !usedWords.includes(w));
    const pool = available.length > 0 ? available : words;
    return pool[Math.floor(Math.random() * pool.length)];
  }, [difficulty, usedWords]);

  const setupRound = useCallback(() => {
    const word = pickWord();
    const numMissing = Math.max(1, Math.floor(word.length * missingPercentage));
    const indices: number[] = [];
    while (indices.length < numMissing) {
      const idx = Math.floor(Math.random() * word.length);
      if (!indices.includes(idx)) indices.push(idx);
    }
    indices.sort((a, b) => a - b);

    setCurrentWord(word);
    setMaskedIndices(indices);
    setUserInputs(new Array(indices.length).fill(''));
    setUsedWords((prev) => [...prev, word]);
    setFeedback(null);
  }, [pickWord, missingPercentage]);

  const startGame = () => {
    setPhase('playing');
    setStartTime(Date.now());
    setRound(0);
    setScore(0);
    setCorrectCount(0);
    setUsedWords([]);
  };

  useEffect(() => {
    if (phase === 'playing' && feedback === null && round < TOTAL_ROUNDS) {
      setupRound();
    }
  }, [phase, round, feedback, setupRound]);

  // Ilk bos input'a focus
  useEffect(() => {
    if (phase === 'playing' && feedback === null) {
      setTimeout(() => {
        const firstInput = inputRefs.current[0];
        if (firstInput) firstInput.focus();
      }, 100);
    }
  }, [phase, feedback, currentWord]);

  const handleInputChange = (index: number, value: string) => {
    if (feedback) return;
    const char = value.toUpperCase().slice(-1);
    const newInputs = [...userInputs];
    newInputs[index] = char;
    setUserInputs(newInputs);

    // Otomatik sonraki input'a gecis
    if (char && index < maskedIndices.length - 1) {
      const nextInput = inputRefs.current[index + 1];
      if (nextInput) nextInput.focus();
    }

    // Tum harfler doluysa otomatik kontrol
    const allFilled = newInputs.every((inp) => inp.length > 0);
    if (allFilled) {
      checkAnswer(newInputs);
    }
  };

  const checkAnswer = (inputs: string[]) => {
    const isCorrect = maskedIndices.every(
      (maskIdx, i) => inputs[i].toUpperCase() === currentWord[maskIdx]
    );

    if (isCorrect) {
      setScore((s) => s + 10);
      setCorrectCount((c) => c + 1);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    setTimeout(() => {
      const nextRound = round + 1;
      if (nextRound >= TOTAL_ROUNDS) {
        endGame(isCorrect);
      } else {
        setRound(nextRound);
        setFeedback(null);
      }
    }, 1200);
  };

  const endGame = (lastCorrect: boolean) => {
    const finalCorrect = correctCount + (lastCorrect ? 1 : 0);
    const finalScore = score + (lastCorrect ? 10 : 0);
    const duration = Math.floor((Date.now() - startTime) / 1000);
    const accuracy = Math.round((finalCorrect / TOTAL_ROUNDS) * 100);

    setPhase('complete');
    onComplete({
      score: Math.min(finalScore, 100),
      maxScore: 100,
      accuracy,
      duration,
      data: { totalRounds: TOTAL_ROUNDS, correctAnswers: finalCorrect, difficulty },
    });
  };

  const renderWord = () => {
    return currentWord.split('').map((letter, idx) => {
      const maskPos = maskedIndices.indexOf(idx);
      if (maskPos !== -1) {
        return (
          <input
            key={idx}
            ref={(el) => { inputRefs.current[maskPos] = el; }}
            type="text"
            maxLength={1}
            value={userInputs[maskPos]}
            onChange={(e) => handleInputChange(maskPos, e.target.value)}
            disabled={feedback !== null}
            className={`w-10 h-12 text-center text-xl font-bold border-2 rounded-lg mx-0.5 uppercase
              ${feedback === 'correct' ? 'border-green-500 bg-green-50 text-green-700' :
                feedback === 'wrong' ? 'border-red-500 bg-red-50 text-red-700' :
                'border-indigo-400 bg-white text-gray-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-200'
              }`}
          />
        );
      }
      return (
        <span
          key={idx}
          className="w-10 h-12 flex items-center justify-center text-xl font-bold text-gray-800 mx-0.5"
        >
          {letter}
        </span>
      );
    });
  };

  // ---- READY ----
  if (phase === 'ready') {
    return (
      <div className="text-center">
        <div className="p-6 bg-indigo-50 rounded-xl mb-4">
          <Type className="w-12 h-12 text-indigo-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Kelime Tamamlama</h3>
          <p className="text-sm text-gray-600 mb-4">
            Eksik harfleri tamamlayarak kelimeleri bulun. Her kelimede bazi harfler gizlidir.
          </p>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition mx-auto"
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
    const accuracy = Math.round((correctCount / TOTAL_ROUNDS) * 100);
    return (
      <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
        <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-gray-900 mb-2">Oyun Bitti!</h3>
        <div className="grid grid-cols-3 gap-4 my-4">
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-indigo-600">{score}</p>
            <p className="text-xs text-gray-500">Puan</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-green-600">{correctCount}/{TOTAL_ROUNDS}</p>
            <p className="text-xs text-gray-500">Dogru</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-purple-600">%{accuracy}</p>
            <p className="text-xs text-gray-500">Basari</p>
          </div>
        </div>
        <button
          onClick={() => { setPhase('ready'); setScore(0); setCorrectCount(0); setUsedWords([]); }}
          className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition mx-auto"
        >
          <RotateCcw className="w-4 h-4" />
          Tekrar Oyna
        </button>
      </div>
    );
  }

  // ---- PLAYING ----
  return (
    <div>
      {/* Stats */}
      <div className="flex items-center justify-between mb-4 text-sm">
        <span className="text-gray-500">Soru {round + 1}/{TOTAL_ROUNDS}</span>
        <span className="font-medium text-indigo-600">Skor: {score}</span>
        <span className="text-green-600">Dogru: {correctCount}</span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
        <div
          className="bg-indigo-500 h-2 rounded-full transition-all"
          style={{ width: `${(round / TOTAL_ROUNDS) * 100}%` }}
        />
      </div>

      {/* Word display */}
      <div className="flex items-center justify-center flex-wrap gap-1 mb-6 min-h-[60px]">
        {currentWord && renderWord()}
      </div>

      {/* Feedback */}
      {feedback === 'wrong' && (
        <div className="text-center">
          <p className="text-sm text-red-600">
            Dogru cevap: <span className="font-bold">{currentWord}</span>
          </p>
        </div>
      )}
    </div>
  );
}
