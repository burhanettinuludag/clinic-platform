'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { RotateCcw, Trophy, Play, Timer } from 'lucide-react';

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

const COLOR_DATA = [
  { name: 'Kırmızı', nameEn: 'red', class: 'text-red-600', bgClass: 'bg-red-500' },
  { name: 'Mavi', nameEn: 'blue', class: 'text-blue-600', bgClass: 'bg-blue-500' },
  { name: 'Yeşil', nameEn: 'green', class: 'text-green-600', bgClass: 'bg-green-500' },
  { name: 'Sarı', nameEn: 'yellow', class: 'text-yellow-500', bgClass: 'bg-yellow-400' },
  { name: 'Mor', nameEn: 'purple', class: 'text-purple-600', bgClass: 'bg-purple-500' },
  { name: 'Turuncu', nameEn: 'orange', class: 'text-orange-500', bgClass: 'bg-orange-500' },
];

interface Question {
  word: string;
  wordColorIndex: number;
  correctColorIndex: number;
}

export default function ColorWordGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);

  const totalRounds = (config.rounds as number) || 15;
  const timePerRound = (config.time_per_round_seconds as number) || 5;

  // Use refs for values needed in callbacks to avoid stale closures
  const roundRef = useRef(round);
  const scoreRef = useRef(score);
  const correctAnswersRef = useRef(correctAnswers);
  const startTimeRef = useRef(startTime);

  useEffect(() => { roundRef.current = round; }, [round]);
  useEffect(() => { scoreRef.current = score; }, [score]);
  useEffect(() => { correctAnswersRef.current = correctAnswers; }, [correctAnswers]);
  useEffect(() => { startTimeRef.current = startTime; }, [startTime]);

  // Generate a question
  const generateQuestion = useCallback((): Question => {
    const wordIndex = Math.floor(Math.random() * COLOR_DATA.length);
    let colorIndex = Math.floor(Math.random() * COLOR_DATA.length);

    // Make sure word and color are different for Stroop effect
    while (colorIndex === wordIndex) {
      colorIndex = Math.floor(Math.random() * COLOR_DATA.length);
    }

    return {
      word: COLOR_DATA[wordIndex].name,
      wordColorIndex: colorIndex,
      correctColorIndex: colorIndex, // Answer is the COLOR, not the word
    };
  }, []);

  // End game
  const endGame = useCallback(() => {
    setGamePhase('complete');
    const duration = Math.floor((Date.now() - startTimeRef.current) / 1000);
    const accuracy = Math.round((correctAnswersRef.current / totalRounds) * 100);

    onComplete({
      score: scoreRef.current,
      maxScore: totalRounds * timePerRound * 2,
      accuracy,
      duration,
      data: {
        totalRounds,
        correctAnswers: correctAnswersRef.current,
        difficulty,
      },
    });
  }, [totalRounds, timePerRound, difficulty, onComplete]);

  // Start game
  const startGame = () => {
    setGamePhase('playing');
    setRound(1);
    setScore(0);
    setCorrectAnswers(0);
    setStartTime(Date.now());
    setCurrentQuestion(generateQuestion());
    setTimeLeft(timePerRound);
    setFeedback(null);
  };

  // Handle answer
  const handleAnswer = useCallback((selectedColorIndex: number) => {
    if (!currentQuestion) return;

    const isCorrect = selectedColorIndex === currentQuestion.correctColorIndex;

    if (isCorrect) {
      setScore((prev) => prev + Math.ceil(timeLeft * 2)); // Bonus for time left
      setCorrectAnswers((prev) => prev + 1);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    // Next question or end game
    setTimeout(() => {
      if (roundRef.current >= totalRounds) {
        endGame();
      } else {
        setRound((prev) => prev + 1);
        setCurrentQuestion(generateQuestion());
        setTimeLeft(timePerRound);
        setFeedback(null);
      }
    }, 800);
  }, [currentQuestion, timeLeft, totalRounds, generateQuestion, timePerRound, endGame]);

  // Timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (gamePhase === 'playing' && timeLeft > 0 && !feedback) {
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            // Time's up - wrong answer
            setFeedback('wrong');
            setTimeout(() => {
              if (roundRef.current >= totalRounds) {
                endGame();
              } else {
                setRound((p) => p + 1);
                setCurrentQuestion(generateQuestion());
                setTimeLeft(timePerRound);
                setFeedback(null);
              }
            }, 800);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [gamePhase, timeLeft, feedback, totalRounds, generateQuestion, timePerRound, endGame]);

  return (
    <div className="max-w-md mx-auto">
      {/* Instructions */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-indigo-50 rounded-xl mb-4">
            <div className="text-4xl mb-4">🎨</div>
            <h3 className="font-semibold text-gray-900 mb-2">Renk Kelime Oyunu (Stroop)</h3>
            <p className="text-sm text-gray-600 mb-4">
              Bir renk ismi göreceksiniz ama <strong>farklı bir renkle</strong> yazılmış olacak.
              <br /><br />
              <strong>Kelimenin YAZILDIĞI rengi</strong> seçin, kelimeyi değil!
            </p>
            <div className="p-3 bg-white rounded-lg mb-4">
              <p className="text-sm text-gray-500 mb-2">Örnek:</p>
              <p className="text-2xl font-bold text-blue-600">Kırmızı</p>
              <p className="text-xs text-gray-500 mt-1">Cevap: MAVİ (yazıldığı renk)</p>
            </div>
            <button
              onClick={startGame}
              className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition mx-auto"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Game */}
      {gamePhase === 'playing' && currentQuestion && (
        <>
          {/* Stats */}
          <div className="flex justify-between items-center mb-4 text-sm">
            <div className="text-gray-600">
              Soru: <span className="font-bold">{round}/{totalRounds}</span>
            </div>
            <div className="flex items-center gap-1 text-gray-600">
              <Timer className="w-4 h-4" />
              <span className={`font-bold ${timeLeft <= 2 ? 'text-red-600' : ''}`}>
                {timeLeft}s
              </span>
            </div>
            <div className="text-gray-600">
              Skor: <span className="font-bold">{score}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
            <div
              className="h-full bg-indigo-600 transition-all duration-300"
              style={{ width: `${(round / totalRounds) * 100}%` }}
            />
          </div>

          {/* Question */}
          <div className={`p-8 rounded-xl mb-6 text-center transition-colors ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : 'bg-gray-100'
          }`}>
            <p className="text-sm text-gray-500 mb-2">Yazıldığı rengi seçin:</p>
            <p className={`text-4xl font-bold ${COLOR_DATA[currentQuestion.wordColorIndex].class}`}>
              {currentQuestion.word}
            </p>
          </div>

          {/* Color Options */}
          <div className="grid grid-cols-3 gap-3">
            {COLOR_DATA.map((color, index) => (
              <button
                key={color.nameEn}
                onClick={() => !feedback && handleAnswer(index)}
                disabled={!!feedback}
                className={`py-4 rounded-xl font-medium text-white transition-transform active:scale-95 ${color.bgClass} ${
                  feedback ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90'
                } ${
                  feedback && index === currentQuestion.correctColorIndex
                    ? 'ring-4 ring-green-400'
                    : ''
                }`}
              >
                {color.name}
              </button>
            ))}
          </div>

          {/* Feedback */}
          {feedback && (
            <div className={`mt-4 text-center p-3 rounded-lg ${
              feedback === 'correct' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {feedback === 'correct' ? '✓ Doğru!' : '✗ Yanlış!'}
            </div>
          )}
        </>
      )}

      {/* Game Complete */}
      {gamePhase === 'complete' && (
        <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
          <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Oyun Bitti!</h3>
          <div className="text-gray-600 mb-4 space-y-1">
            <p>Skor: <span className="font-bold">{score}</span></p>
            <p>Doğru: <span className="font-bold text-green-600">{correctAnswers}</span>/{totalRounds}</p>
            <p>Doğruluk: <span className="font-bold">%{Math.round((correctAnswers / totalRounds) * 100)}</span></p>
          </div>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Oyna
          </button>
        </div>
      )}
    </div>
  );
}
