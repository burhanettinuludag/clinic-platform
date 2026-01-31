'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Timer, Calculator } from 'lucide-react';

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
  num1: number;
  num2: number;
  operation: '+' | '-';
  answer: number;
  options: number[];
}

export default function SimpleMathGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);

  const totalRounds = (config.rounds as number) || 15;
  const operations = (config.operations as string[]) || ['add', 'subtract'];
  const maxNumbers = (config.max_number as Record<string, number>) || { easy: 20, medium: 50, hard: 100 };
  const maxNum = maxNumbers[difficulty] || 20;

  // Generate a question
  const generateQuestion = useCallback((): Question => {
    const opType = operations[Math.floor(Math.random() * operations.length)];
    const operation = opType === 'add' ? '+' : '-';

    let num1 = Math.floor(Math.random() * maxNum) + 1;
    let num2 = Math.floor(Math.random() * maxNum) + 1;

    // For subtraction, make sure result is positive
    if (operation === '-' && num2 > num1) {
      [num1, num2] = [num2, num1];
    }

    const answer = operation === '+' ? num1 + num2 : num1 - num2;

    // Generate wrong options
    const wrongOptions = new Set<number>();
    while (wrongOptions.size < 3) {
      const offset = Math.floor(Math.random() * 10) - 5;
      const wrong = answer + offset;
      if (wrong !== answer && wrong >= 0) {
        wrongOptions.add(wrong);
      }
    }

    // Shuffle options
    const options = [answer, ...Array.from(wrongOptions)]
      .sort(() => Math.random() - 0.5);

    return { num1, num2, operation, answer, options };
  }, [maxNum, operations]);

  // Start game
  const startGame = () => {
    setGamePhase('playing');
    setRound(1);
    setScore(0);
    setCorrectAnswers(0);
    setStartTime(Date.now());
    setCurrentQuestion(generateQuestion());
    setFeedback(null);
    setSelectedAnswer(null);
  };

  // Handle answer
  const handleAnswer = (selected: number) => {
    if (feedback || !currentQuestion) return;

    setSelectedAnswer(selected);
    const isCorrect = selected === currentQuestion.answer;

    if (isCorrect) {
      setScore((prev) => prev + 10);
      setCorrectAnswers((prev) => prev + 1);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    // Next question or end game
    setTimeout(() => {
      if (round >= totalRounds) {
        endGame();
      } else {
        setRound((prev) => prev + 1);
        setCurrentQuestion(generateQuestion());
        setFeedback(null);
        setSelectedAnswer(null);
      }
    }, 1000);
  };

  // End game
  const endGame = () => {
    setGamePhase('complete');
    const duration = Math.floor((Date.now() - startTime) / 1000);
    const accuracy = Math.round((correctAnswers / totalRounds) * 100);

    onComplete({
      score,
      maxScore: totalRounds * 10,
      accuracy,
      duration,
      data: {
        totalRounds,
        correctAnswers,
        difficulty,
        maxNumber: maxNum,
      },
    });
  };

  return (
    <div className="max-w-md mx-auto">
      {/* Instructions */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-indigo-50 rounded-xl mb-4">
            <Calculator className="w-12 h-12 text-indigo-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Basit Matematik</h3>
            <p className="text-sm text-gray-600 mb-4">
              Toplama ve çıkarma işlemlerini çözün.
              <br />
              Doğru cevabı seçeneklerden seçin.
            </p>
            <div className="p-3 bg-white rounded-lg mb-4 text-center">
              <p className="text-2xl font-mono">12 + 5 = ?</p>
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
            <div className="text-gray-600">
              Skor: <span className="font-bold">{score}</span>
            </div>
            <div className="text-gray-600">
              Doğru: <span className="font-bold text-green-600">{correctAnswers}</span>
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
            <p className="text-4xl font-mono font-bold text-gray-900">
              {currentQuestion.num1} {currentQuestion.operation} {currentQuestion.num2} = ?
            </p>
          </div>

          {/* Options */}
          <div className="grid grid-cols-2 gap-3">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                disabled={!!feedback}
                className={`py-4 rounded-xl font-bold text-xl transition-all ${
                  feedback
                    ? option === currentQuestion.answer
                      ? 'bg-green-500 text-white'
                      : selectedAnswer === option
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-400'
                    : 'bg-white border-2 border-gray-200 text-gray-900 hover:border-indigo-400 hover:bg-indigo-50'
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
              {feedback === 'correct' ? '✓ Doğru! +10 puan' : `✗ Yanlış! Cevap: ${currentQuestion.answer}`}
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
            <p>Skor: <span className="font-bold">{score}</span>/{totalRounds * 10}</p>
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
