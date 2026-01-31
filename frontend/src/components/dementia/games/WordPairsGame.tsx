'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Eye, Brain } from 'lucide-react';

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

const WORD_PAIRS = [
  { word1: 'Güneş', word2: 'Ay' },
  { word1: 'Kitap', word2: 'Kalem' },
  { word1: 'Deniz', word2: 'Balık' },
  { word1: 'Ağaç', word2: 'Yaprak' },
  { word1: 'Araba', word2: 'Tekerlek' },
  { word1: 'Masa', word2: 'Sandalye' },
  { word1: 'Elma', word2: 'Armut' },
  { word1: 'Kedi', word2: 'Köpek' },
  { word1: 'Anne', word2: 'Baba' },
  { word1: 'Gece', word2: 'Gündüz' },
  { word1: 'Yaz', word2: 'Kış' },
  { word1: 'Doktor', word2: 'Hastane' },
  { word1: 'Öğretmen', word2: 'Okul' },
  { word1: 'Çiçek', word2: 'Arı' },
  { word1: 'Yağmur', word2: 'Şemsiye' },
  { word1: 'Kahve', word2: 'Fincan' },
];

interface WordPair {
  word1: string;
  word2: string;
}

export default function WordPairsGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'memorize' | 'test' | 'complete'>('ready');
  const [pairs, setPairs] = useState<WordPair[]>([]);
  const [currentTestIndex, setCurrentTestIndex] = useState(0);
  const [options, setOptions] = useState<string[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [score, setScore] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);
  const [memorizeCountdown, setMemorizeCountdown] = useState(0);

  const pairCounts = (config.pair_counts as Record<string, number>) || {
    easy: 4,
    medium: 6,
    hard: 8,
  };
  const displayTime = (config.display_time_seconds as number) || 5;
  const pairCount = pairCounts[difficulty] || 4;

  // Shuffle array
  const shuffleArray = <T,>(array: T[]): T[] => {
    return [...array].sort(() => Math.random() - 0.5);
  };

  // Initialize game
  const initGame = useCallback(() => {
    const shuffledPairs = shuffleArray(WORD_PAIRS).slice(0, pairCount);
    setPairs(shuffledPairs);
    setCurrentTestIndex(0);
    setScore(0);
    setSelectedAnswer(null);
    setFeedback(null);
  }, [pairCount]);

  useEffect(() => {
    initGame();
  }, [initGame]);

  // Start game
  const startGame = () => {
    initGame();
    setGamePhase('memorize');
    setMemorizeCountdown(displayTime * pairCount);
    setStartTime(Date.now());
  };

  // Generate options for current test
  const generateOptions = useCallback((index: number, currentPairs: WordPair[]) => {
    if (index >= currentPairs.length) return;

    const correctAnswer = currentPairs[index].word2;
    const wrongAnswers = shuffleArray(
      WORD_PAIRS.filter((p) => p.word2 !== correctAnswer).map((p) => p.word2)
    ).slice(0, 3);

    setOptions(shuffleArray([correctAnswer, ...wrongAnswers]));
  }, []);

  // Memorize countdown
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (gamePhase === 'memorize' && memorizeCountdown > 0) {
      interval = setInterval(() => {
        setMemorizeCountdown((prev) => prev - 1);
      }, 1000);
    } else if (gamePhase === 'memorize' && memorizeCountdown === 0) {
      // Move to test phase
      setGamePhase('test');
      generateOptions(0, pairs);
    }
    return () => clearInterval(interval);
  }, [gamePhase, memorizeCountdown, generateOptions, pairs]);

  // Handle answer
  const handleAnswer = (answer: string) => {
    if (feedback) return;

    setSelectedAnswer(answer);
    const isCorrect = answer === pairs[currentTestIndex].word2;

    if (isCorrect) {
      setScore((prev) => prev + 1);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    // Next question or end game
    const nextIndex = currentTestIndex + 1;
    setTimeout(() => {
      if (nextIndex >= pairs.length) {
        endGame();
      } else {
        setCurrentTestIndex(nextIndex);
        generateOptions(nextIndex, pairs);
        setSelectedAnswer(null);
        setFeedback(null);
      }
    }, 1500);
  };

  // End game
  const endGame = () => {
    setGamePhase('complete');
    const duration = Math.floor((Date.now() - startTime) / 1000);
    const accuracy = Math.round((score / pairs.length) * 100);

    onComplete({
      score: score * 10,
      maxScore: pairs.length * 10,
      accuracy,
      duration,
      data: {
        pairCount: pairs.length,
        correctAnswers: score,
        difficulty,
      },
    });
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Ready Phase */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-purple-50 rounded-xl mb-4">
            <Brain className="w-12 h-12 text-purple-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Kelime Çiftleri</h3>
            <p className="text-sm text-gray-600 mb-4">
              Size {pairCount} kelime çifti gösterilecek.
              <br />
              Bunları ezberleyin, sonra eşlerini hatırlayın.
            </p>
            <div className="p-3 bg-white rounded-lg mb-4">
              <p className="text-sm text-gray-500">Örnek:</p>
              <p className="font-medium">Güneş → Ay</p>
            </div>
            <button
              onClick={startGame}
              className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition mx-auto"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Memorize Phase */}
      {gamePhase === 'memorize' && (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-4 text-purple-600">
            <Eye className="w-5 h-5" />
            <span className="font-medium">Ezberleme Zamanı</span>
          </div>

          <div className="text-3xl font-bold text-purple-600 mb-6">
            {memorizeCountdown}s
          </div>

          <div className="space-y-3">
            {pairs.map((pair, index) => (
              <div
                key={index}
                className="p-4 bg-white rounded-xl border-2 border-purple-100 flex items-center justify-center gap-4"
              >
                <span className="text-lg font-medium text-gray-800">{pair.word1}</span>
                <span className="text-purple-400">→</span>
                <span className="text-lg font-medium text-purple-600">{pair.word2}</span>
              </div>
            ))}
          </div>

          <p className="text-sm text-gray-500 mt-6">
            Çiftleri iyi ezberleyin!
          </p>
        </div>
      )}

      {/* Test Phase */}
      {gamePhase === 'test' && pairs[currentTestIndex] && (
        <div>
          {/* Progress */}
          <div className="flex justify-between items-center mb-4 text-sm">
            <div className="text-gray-600">
              Soru: <span className="font-bold">{currentTestIndex + 1}/{pairs.length}</span>
            </div>
            <div className="text-gray-600">
              Doğru: <span className="font-bold text-green-600">{score}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
            <div
              className="h-full bg-purple-600 transition-all duration-300"
              style={{ width: `${((currentTestIndex + 1) / pairs.length) * 100}%` }}
            />
          </div>

          {/* Question */}
          <div className={`p-6 rounded-xl mb-6 text-center transition-colors ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : 'bg-purple-50'
          }`}>
            <p className="text-sm text-gray-500 mb-2">Bu kelimenin eşi neydi?</p>
            <p className="text-3xl font-bold text-gray-900">
              {pairs[currentTestIndex].word1}
            </p>
          </div>

          {/* Options */}
          <div className="grid grid-cols-2 gap-3">
            {options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                disabled={!!feedback}
                className={`py-4 px-3 rounded-xl font-medium text-lg transition-all ${
                  feedback
                    ? option === pairs[currentTestIndex].word2
                      ? 'bg-green-500 text-white'
                      : selectedAnswer === option
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-400'
                    : 'bg-white border-2 border-gray-200 text-gray-900 hover:border-purple-400 hover:bg-purple-50'
                } ${feedback ? 'cursor-not-allowed' : ''}`}
              >
                {option}
              </button>
            ))}
          </div>

          {/* Feedback */}
          {feedback && (
            <div className={`mt-4 text-center p-3 rounded-lg ${
              feedback === 'correct' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {feedback === 'correct'
                ? '✓ Doğru!'
                : `✗ Yanlış! Doğru cevap: ${pairs[currentTestIndex].word2}`}
            </div>
          )}
        </div>
      )}

      {/* Complete Phase */}
      {gamePhase === 'complete' && (
        <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
          <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Oyun Bitti!</h3>
          <div className="text-gray-600 mb-4 space-y-1">
            <p>Doğru: <span className="font-bold text-green-600">{score}</span>/{pairs.length}</p>
            <p>Doğruluk: <span className="font-bold">%{Math.round((score / pairs.length) * 100)}</span></p>
          </div>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Oyna
          </button>
        </div>
      )}
    </div>
  );
}
