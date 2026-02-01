'use client';

import { useState, useEffect, useCallback } from 'react';
import { Play, RotateCcw, CheckCircle, XCircle, Eye } from 'lucide-react';

interface SpotDifferenceGameProps {
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

interface Difference {
  id: number;
  x: number;
  y: number;
  found: boolean;
}

interface GameLevel {
  gridSize: number;
  baseShapes: { type: string; x: number; y: number; color: string; size: number }[];
  differences: { id: number; x: number; y: number; type: 'color' | 'shape' | 'size' | 'missing' }[];
}

const COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899'];
const SHAPES = ['circle', 'square', 'triangle', 'diamond', 'star'];

export default function SpotDifferenceGame({ config, difficulty, onComplete }: SpotDifferenceGameProps) {
  const [gameState, setGameState] = useState<'intro' | 'playing' | 'completed'>('intro');
  const [currentLevel, setCurrentLevel] = useState(0);
  const [levels, setLevels] = useState<GameLevel[]>([]);
  const [foundDifferences, setFoundDifferences] = useState<number[]>([]);
  const [score, setScore] = useState(0);
  const [wrongClicks, setWrongClicks] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);
  const [timeLeft, setTimeLeft] = useState(60);
  const [showHint, setShowHint] = useState(false);

  const difficultySettings = {
    easy: { levels: 3, differencesPerLevel: 3, timePerLevel: 60, gridComplexity: 4 },
    medium: { levels: 4, differencesPerLevel: 4, timePerLevel: 50, gridComplexity: 6 },
    hard: { levels: 5, differencesPerLevel: 5, timePerLevel: 40, gridComplexity: 8 },
  };

  const settings = difficultySettings[difficulty as keyof typeof difficultySettings] || difficultySettings.medium;

  const generateLevel = useCallback((levelIndex: number): GameLevel => {
    const complexity = settings.gridComplexity + levelIndex;
    const baseShapes: GameLevel['baseShapes'] = [];
    const differences: GameLevel['differences'] = [];

    // Generate base shapes
    for (let i = 0; i < complexity; i++) {
      baseShapes.push({
        type: SHAPES[Math.floor(Math.random() * SHAPES.length)],
        x: 20 + Math.random() * 260,
        y: 20 + Math.random() * 160,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        size: 20 + Math.random() * 20,
      });
    }

    // Generate differences
    const numDifferences = settings.differencesPerLevel;
    const usedIndices = new Set<number>();

    for (let i = 0; i < numDifferences; i++) {
      let shapeIndex;
      do {
        shapeIndex = Math.floor(Math.random() * baseShapes.length);
      } while (usedIndices.has(shapeIndex));
      usedIndices.add(shapeIndex);

      const diffTypes: ('color' | 'shape' | 'size' | 'missing')[] = ['color', 'shape', 'size', 'missing'];
      differences.push({
        id: i,
        x: baseShapes[shapeIndex].x,
        y: baseShapes[shapeIndex].y,
        type: diffTypes[Math.floor(Math.random() * diffTypes.length)],
      });
    }

    return { gridSize: complexity, baseShapes, differences };
  }, [settings.gridComplexity, settings.differencesPerLevel]);

  const startGame = () => {
    const newLevels = Array.from({ length: settings.levels }, (_, i) => generateLevel(i));
    setLevels(newLevels);
    setCurrentLevel(0);
    setFoundDifferences([]);
    setScore(0);
    setWrongClicks(0);
    setStartTime(Date.now());
    setTimeLeft(settings.timePerLevel);
    setShowHint(false);
    setGameState('playing');
  };

  // Timer
  useEffect(() => {
    if (gameState !== 'playing') return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Time's up for this level, move to next or end
          if (currentLevel < levels.length - 1) {
            setCurrentLevel((l) => l + 1);
            setFoundDifferences([]);
            setShowHint(false);
            return settings.timePerLevel;
          } else {
            setGameState('completed');
            return 0;
          }
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [gameState, currentLevel, levels.length, settings.timePerLevel]);

  const handleImageClick = (side: 'left' | 'right', x: number, y: number) => {
    if (gameState !== 'playing') return;

    const level = levels[currentLevel];
    if (!level) return;

    // Check if click is near a difference
    const clickRadius = 30;
    const foundDiff = level.differences.find((diff) => {
      if (foundDifferences.includes(diff.id)) return false;
      const distance = Math.sqrt(Math.pow(diff.x - x, 2) + Math.pow(diff.y - y, 2));
      return distance < clickRadius;
    });

    if (foundDiff) {
      setFoundDifferences([...foundDifferences, foundDiff.id]);
      setScore((s) => s + 10);

      // Check if all differences found
      if (foundDifferences.length + 1 >= level.differences.length) {
        // Level complete
        if (currentLevel < levels.length - 1) {
          setTimeout(() => {
            setCurrentLevel((l) => l + 1);
            setFoundDifferences([]);
            setTimeLeft(settings.timePerLevel);
            setShowHint(false);
          }, 500);
        } else {
          setGameState('completed');
        }
      }
    } else {
      setWrongClicks((w) => w + 1);
      setScore((s) => Math.max(0, s - 2));
    }
  };

  const renderShape = (shape: { type: string; x: number; y: number; color: string; size: number }, modified?: { type: 'color' | 'shape' | 'size' | 'missing' }) => {
    if (modified?.type === 'missing') return null;

    let actualColor = shape.color;
    let actualSize = shape.size;
    let actualType = shape.type;

    if (modified) {
      if (modified.type === 'color') {
        const otherColors = COLORS.filter((c) => c !== shape.color);
        actualColor = otherColors[Math.floor(Math.random() * otherColors.length)];
      }
      if (modified.type === 'size') {
        actualSize = shape.size * (Math.random() > 0.5 ? 1.5 : 0.7);
      }
      if (modified.type === 'shape') {
        const otherShapes = SHAPES.filter((s) => s !== shape.type);
        actualType = otherShapes[Math.floor(Math.random() * otherShapes.length)];
      }
    }

    const commonProps = {
      fill: actualColor,
      opacity: 0.8,
    };

    switch (actualType) {
      case 'circle':
        return <circle cx={shape.x} cy={shape.y} r={actualSize / 2} {...commonProps} />;
      case 'square':
        return <rect x={shape.x - actualSize / 2} y={shape.y - actualSize / 2} width={actualSize} height={actualSize} {...commonProps} />;
      case 'triangle':
        const points = `${shape.x},${shape.y - actualSize / 2} ${shape.x - actualSize / 2},${shape.y + actualSize / 2} ${shape.x + actualSize / 2},${shape.y + actualSize / 2}`;
        return <polygon points={points} {...commonProps} />;
      case 'diamond':
        const diamondPoints = `${shape.x},${shape.y - actualSize / 2} ${shape.x + actualSize / 2},${shape.y} ${shape.x},${shape.y + actualSize / 2} ${shape.x - actualSize / 2},${shape.y}`;
        return <polygon points={diamondPoints} {...commonProps} />;
      case 'star':
        return <circle cx={shape.x} cy={shape.y} r={actualSize / 2} {...commonProps} stroke={actualColor} strokeWidth="2" fill="none" />;
      default:
        return <circle cx={shape.x} cy={shape.y} r={actualSize / 2} {...commonProps} />;
    }
  };

  const finishGame = () => {
    const duration = Math.round((Date.now() - startTime) / 1000);
    const totalDifferences = levels.reduce((sum, l) => sum + l.differences.length, 0);
    const totalFound = score / 10;
    const accuracy = totalDifferences > 0 ? Math.round((totalFound / totalDifferences) * 100) : 0;

    onComplete({
      score,
      maxScore: totalDifferences * 10,
      accuracy,
      duration,
      data: {
        levelsCompleted: currentLevel + 1,
        totalLevels: levels.length,
        wrongClicks,
        differencesFound: totalFound,
        totalDifferences,
      },
    });
  };

  if (gameState === 'intro') {
    return (
      <div className="text-center py-8">
        <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Eye className="w-10 h-10 text-purple-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Farkı Bul</h2>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          İki resim arasındaki farkları bulun. Farklı olan yerlere tıklayın.
          Yanlış tıklamalar puan kaybettirir.
        </p>
        <div className="bg-purple-50 rounded-lg p-4 mb-6 max-w-sm mx-auto">
          <div className="text-sm text-purple-700">
            <div className="flex justify-between mb-1">
              <span>Seviye sayısı:</span>
              <span className="font-semibold">{settings.levels}</span>
            </div>
            <div className="flex justify-between mb-1">
              <span>Her seviyede fark:</span>
              <span className="font-semibold">{settings.differencesPerLevel}</span>
            </div>
            <div className="flex justify-between">
              <span>Süre (her seviye):</span>
              <span className="font-semibold">{settings.timePerLevel} saniye</span>
            </div>
          </div>
        </div>
        <button
          onClick={startGame}
          className="px-8 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition flex items-center gap-2 mx-auto"
        >
          <Play className="w-5 h-5" />
          Başla
        </button>
      </div>
    );
  }

  if (gameState === 'completed') {
    const totalDifferences = levels.reduce((sum, l) => sum + l.differences.length, 0);
    const accuracy = totalDifferences > 0 ? Math.round(((score / 10) / totalDifferences) * 100) : 0;

    return (
      <div className="text-center py-8">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-10 h-10 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Tamamlandı!</h2>
        <div className="bg-gray-50 rounded-xl p-6 max-w-sm mx-auto mb-6">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-3xl font-bold text-purple-600">{score}</div>
              <div className="text-sm text-gray-500">Puan</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600">%{accuracy}</div>
              <div className="text-sm text-gray-500">Doğruluk</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">{Math.round(score / 10)}/{totalDifferences}</div>
              <div className="text-sm text-gray-500">Bulunan Fark</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-red-600">{wrongClicks}</div>
              <div className="text-sm text-gray-500">Yanlış Tıklama</div>
            </div>
          </div>
        </div>
        <div className="flex gap-3 justify-center">
          <button
            onClick={startGame}
            className="px-6 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Oyna
          </button>
          <button
            onClick={finishGame}
            className="px-6 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition"
          >
            Sonuçları Kaydet
          </button>
        </div>
      </div>
    );
  }

  const level = levels[currentLevel];
  if (!level) return null;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            Seviye {currentLevel + 1}/{levels.length}
          </span>
          <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
            {score} puan
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className={`text-lg font-bold ${timeLeft <= 10 ? 'text-red-600' : 'text-gray-700'}`}>
            {timeLeft}s
          </span>
          <button
            onClick={() => setShowHint(!showHint)}
            className="px-3 py-1 bg-amber-100 text-amber-700 rounded-lg text-sm hover:bg-amber-200 transition"
          >
            İpucu
          </button>
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm text-gray-500">Bulunan:</span>
        {level.differences.map((diff) => (
          <div
            key={diff.id}
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
              foundDifferences.includes(diff.id)
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-500'
            }`}
          >
            {foundDifferences.includes(diff.id) ? '✓' : diff.id + 1}
          </div>
        ))}
      </div>

      {/* Images */}
      <div className="grid grid-cols-2 gap-4">
        {/* Left Image (Original) */}
        <div className="relative">
          <div className="text-center text-sm text-gray-500 mb-2">Orijinal</div>
          <svg
            viewBox="0 0 300 200"
            className="w-full h-auto bg-gray-100 rounded-lg cursor-crosshair border-2 border-gray-200"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const x = ((e.clientX - rect.left) / rect.width) * 300;
              const y = ((e.clientY - rect.top) / rect.height) * 200;
              handleImageClick('left', x, y);
            }}
          >
            {level.baseShapes.map((shape, idx) => (
              <g key={idx}>{renderShape(shape)}</g>
            ))}
            {/* Show found markers */}
            {foundDifferences.map((diffId) => {
              const diff = level.differences.find((d) => d.id === diffId);
              if (!diff) return null;
              return (
                <circle
                  key={`found-left-${diffId}`}
                  cx={diff.x}
                  cy={diff.y}
                  r="25"
                  fill="none"
                  stroke="#22c55e"
                  strokeWidth="3"
                  strokeDasharray="5,5"
                />
              );
            })}
            {/* Show hints */}
            {showHint && level.differences.filter((d) => !foundDifferences.includes(d.id)).slice(0, 1).map((diff) => (
              <circle
                key={`hint-left-${diff.id}`}
                cx={diff.x}
                cy={diff.y}
                r="35"
                fill="none"
                stroke="#f59e0b"
                strokeWidth="2"
                opacity="0.5"
              />
            ))}
          </svg>
        </div>

        {/* Right Image (Modified) */}
        <div className="relative">
          <div className="text-center text-sm text-gray-500 mb-2">Değiştirilmiş</div>
          <svg
            viewBox="0 0 300 200"
            className="w-full h-auto bg-gray-100 rounded-lg cursor-crosshair border-2 border-gray-200"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const x = ((e.clientX - rect.left) / rect.width) * 300;
              const y = ((e.clientY - rect.top) / rect.height) * 200;
              handleImageClick('right', x, y);
            }}
          >
            {level.baseShapes.map((shape, idx) => {
              const diff = level.differences.find((d) => {
                const distance = Math.sqrt(Math.pow(d.x - shape.x, 2) + Math.pow(d.y - shape.y, 2));
                return distance < 5;
              });
              return <g key={idx}>{renderShape(shape, diff)}</g>;
            })}
            {/* Show found markers */}
            {foundDifferences.map((diffId) => {
              const diff = level.differences.find((d) => d.id === diffId);
              if (!diff) return null;
              return (
                <circle
                  key={`found-right-${diffId}`}
                  cx={diff.x}
                  cy={diff.y}
                  r="25"
                  fill="none"
                  stroke="#22c55e"
                  strokeWidth="3"
                  strokeDasharray="5,5"
                />
              );
            })}
            {/* Show hints */}
            {showHint && level.differences.filter((d) => !foundDifferences.includes(d.id)).slice(0, 1).map((diff) => (
              <circle
                key={`hint-right-${diff.id}`}
                cx={diff.x}
                cy={diff.y}
                r="35"
                fill="none"
                stroke="#f59e0b"
                strokeWidth="2"
                opacity="0.5"
              />
            ))}
          </svg>
        </div>
      </div>

      <p className="text-center text-sm text-gray-500 mt-4">
        Farklı olan yerlere tıklayın. Her iki resimde de tıklayabilirsiniz.
      </p>
    </div>
  );
}
