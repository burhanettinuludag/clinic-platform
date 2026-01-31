'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Shapes } from 'lucide-react';

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

// Orijinal şekil ve renk sistemimiz
const SHAPES = ['circle', 'square', 'triangle', 'diamond', 'star'];
const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'];

interface PatternItem {
  shape: string;
  color: string;
}

interface Pattern {
  sequence: PatternItem[];
  answer: PatternItem;
  options: PatternItem[];
}

export default function PatternRecognitionGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [currentPattern, setCurrentPattern] = useState<Pattern | null>(null);
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [startTime, setStartTime] = useState<number>(0);

  const totalRounds = (config.rounds as number) || 10;
  const sequenceLength = difficulty === 'easy' ? 3 : difficulty === 'medium' ? 4 : 5;

  // Şekil çizimi
  const renderShape = (shape: string, color: string, size: number = 40) => {
    const style = { fill: color };

    switch (shape) {
      case 'circle':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <circle cx="20" cy="20" r="18" style={style} />
          </svg>
        );
      case 'square':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <rect x="4" y="4" width="32" height="32" style={style} />
          </svg>
        );
      case 'triangle':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <polygon points="20,4 38,36 2,36" style={style} />
          </svg>
        );
      case 'diamond':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <polygon points="20,2 38,20 20,38 2,20" style={style} />
          </svg>
        );
      case 'star':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <polygon
              points="20,2 24,14 38,14 27,22 31,36 20,28 9,36 13,22 2,14 16,14"
              style={style}
            />
          </svg>
        );
      default:
        return null;
    }
  };

  // Desen oluştur
  const generatePattern = useCallback((): Pattern => {
    // Rastgele desen tipi seç
    const patternType = Math.floor(Math.random() * 3);
    const sequence: PatternItem[] = [];

    if (patternType === 0) {
      // Şekil tekrarı deseni (renk sabit)
      const fixedColor = COLORS[Math.floor(Math.random() * COLORS.length)];
      const shapeOrder = [...SHAPES].sort(() => Math.random() - 0.5).slice(0, 3);

      for (let i = 0; i < sequenceLength; i++) {
        sequence.push({
          shape: shapeOrder[i % shapeOrder.length],
          color: fixedColor,
        });
      }
    } else if (patternType === 1) {
      // Renk tekrarı deseni (şekil sabit)
      const fixedShape = SHAPES[Math.floor(Math.random() * SHAPES.length)];
      const colorOrder = [...COLORS].sort(() => Math.random() - 0.5).slice(0, 3);

      for (let i = 0; i < sequenceLength; i++) {
        sequence.push({
          shape: fixedShape,
          color: colorOrder[i % colorOrder.length],
        });
      }
    } else {
      // Karışık desen
      const shapeOrder = [...SHAPES].sort(() => Math.random() - 0.5).slice(0, 2);
      const colorOrder = [...COLORS].sort(() => Math.random() - 0.5).slice(0, 2);

      for (let i = 0; i < sequenceLength; i++) {
        sequence.push({
          shape: shapeOrder[i % shapeOrder.length],
          color: colorOrder[i % colorOrder.length],
        });
      }
    }

    // Doğru cevap: desendeki bir sonraki eleman
    const answer = {
      shape: sequence[sequenceLength % sequence.length]?.shape || sequence[0].shape,
      color: sequence[sequenceLength % sequence.length]?.color || sequence[0].color,
    };

    // Yanlış seçenekler oluştur
    const wrongOptions: PatternItem[] = [];
    while (wrongOptions.length < 3) {
      const wrongOption = {
        shape: SHAPES[Math.floor(Math.random() * SHAPES.length)],
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
      };
      // Doğru cevapla veya diğer yanlışlarla aynı değilse ekle
      if (
        !(wrongOption.shape === answer.shape && wrongOption.color === answer.color) &&
        !wrongOptions.some(
          (o) => o.shape === wrongOption.shape && o.color === wrongOption.color
        )
      ) {
        wrongOptions.push(wrongOption);
      }
    }

    // Seçenekleri karıştır
    const options = [answer, ...wrongOptions].sort(() => Math.random() - 0.5);

    return { sequence, answer, options };
  }, [sequenceLength]);

  // Oyunu başlat
  const startGame = () => {
    setGamePhase('playing');
    setRound(1);
    setScore(0);
    setStartTime(Date.now());
    setCurrentPattern(generatePattern());
    setFeedback(null);
    setSelectedOption(null);
  };

  // Cevap kontrolü
  const handleAnswer = (optionIndex: number) => {
    if (feedback || !currentPattern) return;

    setSelectedOption(optionIndex);
    const selected = currentPattern.options[optionIndex];
    const isCorrect =
      selected.shape === currentPattern.answer.shape &&
      selected.color === currentPattern.answer.color;

    if (isCorrect) {
      setScore((prev) => prev + 10);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    setTimeout(() => {
      if (round >= totalRounds) {
        endGame();
      } else {
        setRound((prev) => prev + 1);
        setCurrentPattern(generatePattern());
        setFeedback(null);
        setSelectedOption(null);
      }
    }, 1200);
  };

  // Oyunu bitir
  const endGame = () => {
    setGamePhase('complete');
    const duration = Math.floor((Date.now() - startTime) / 1000);
    const correctCount = Math.floor(score / 10);
    const accuracy = Math.round((correctCount / totalRounds) * 100);

    onComplete({
      score,
      maxScore: totalRounds * 10,
      accuracy,
      duration,
      data: {
        totalRounds,
        correctAnswers: correctCount,
        difficulty,
      },
    });
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Hazır */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-amber-50 rounded-xl mb-4">
            <Shapes className="w-12 h-12 text-amber-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Desen Tanıma</h3>
            <p className="text-sm text-gray-600 mb-4">
              Şekil ve renk desenini inceleyin.
              <br />
              Sıradaki şekli tahmin edin.
            </p>
            <div className="p-4 bg-white rounded-lg mb-4 flex justify-center gap-2">
              {renderShape('circle', '#3B82F6', 30)}
              {renderShape('square', '#3B82F6', 30)}
              {renderShape('circle', '#3B82F6', 30)}
              <span className="text-2xl text-gray-400">→ ?</span>
            </div>
            <button
              onClick={startGame}
              className="flex items-center gap-2 px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition mx-auto"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Oyun */}
      {gamePhase === 'playing' && currentPattern && (
        <>
          {/* İstatistikler */}
          <div className="flex justify-between items-center mb-4 text-sm">
            <div className="text-gray-600">
              Soru: <span className="font-bold">{round}/{totalRounds}</span>
            </div>
            <div className="text-gray-600">
              Skor: <span className="font-bold">{score}</span>
            </div>
          </div>

          {/* İlerleme çubuğu */}
          <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
            <div
              className="h-full bg-amber-600 transition-all duration-300"
              style={{ width: `${(round / totalRounds) * 100}%` }}
            />
          </div>

          {/* Desen */}
          <div className={`p-6 rounded-xl mb-6 transition-colors ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : 'bg-gray-100'
          }`}>
            <p className="text-sm text-gray-500 text-center mb-4">Deseni inceleyin:</p>
            <div className="flex justify-center items-center gap-3 flex-wrap">
              {currentPattern.sequence.map((item, index) => (
                <div key={index} className="p-2 bg-white rounded-lg shadow-sm">
                  {renderShape(item.shape, item.color, 50)}
                </div>
              ))}
              <div className="text-3xl text-gray-400 mx-2">→</div>
              <div className="p-2 bg-amber-100 rounded-lg border-2 border-amber-400 border-dashed">
                <div className="w-[50px] h-[50px] flex items-center justify-center text-2xl text-amber-600">
                  ?
                </div>
              </div>
            </div>
          </div>

          {/* Seçenekler */}
          <p className="text-sm text-gray-600 text-center mb-3">Sıradaki şekil hangisi?</p>
          <div className="grid grid-cols-4 gap-3">
            {currentPattern.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(index)}
                disabled={!!feedback}
                className={`p-4 rounded-xl transition-all flex items-center justify-center ${
                  feedback
                    ? option.shape === currentPattern.answer.shape &&
                      option.color === currentPattern.answer.color
                      ? 'bg-green-500 ring-2 ring-green-600'
                      : selectedOption === index
                      ? 'bg-red-500'
                      : 'bg-gray-200'
                    : 'bg-white border-2 border-gray-200 hover:border-amber-400 hover:bg-amber-50'
                } ${feedback ? 'cursor-not-allowed' : ''}`}
              >
                {renderShape(option.shape, option.color, 50)}
              </button>
            ))}
          </div>

          {/* Geri bildirim */}
          {feedback && (
            <div className={`mt-4 text-center p-3 rounded-lg ${
              feedback === 'correct' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {feedback === 'correct' ? '✓ Doğru! +10 puan' : '✗ Yanlış!'}
            </div>
          )}
        </>
      )}

      {/* Oyun Bitti */}
      {gamePhase === 'complete' && (
        <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
          <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Oyun Bitti!</h3>
          <div className="text-gray-600 mb-4 space-y-1">
            <p>Skor: <span className="font-bold">{score}</span>/{totalRounds * 10}</p>
            <p>Doğruluk: <span className="font-bold">%{Math.round((score / (totalRounds * 10)) * 100)}</span></p>
          </div>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Oyna
          </button>
        </div>
      )}
    </div>
  );
}
