'use client';

import { useState, useEffect, useCallback } from 'react';
import { Play, RotateCcw, CheckCircle, Search, Clock } from 'lucide-react';

interface VisualSearchGameProps {
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

interface Target {
  id: number;
  x: number;
  y: number;
  type: string;
  color: string;
  rotation: number;
  isTarget: boolean;
  found: boolean;
}

interface Level {
  targets: Target[];
  targetType: string;
  targetColor: string;
  targetCount: number;
}

const SHAPES = ['circle', 'square', 'triangle', 'star', 'diamond'];
const COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899'];

export default function VisualSearchGame({ config, difficulty, onComplete }: VisualSearchGameProps) {
  const [gameState, setGameState] = useState<'intro' | 'playing' | 'completed'>('intro');
  const [currentLevel, setCurrentLevel] = useState(0);
  const [levels, setLevels] = useState<Level[]>([]);
  const [foundTargets, setFoundTargets] = useState<number[]>([]);
  const [score, setScore] = useState(0);
  const [wrongClicks, setWrongClicks] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);
  const [timeLeft, setTimeLeft] = useState(45);
  const [showFeedback, setShowFeedback] = useState<{ type: 'correct' | 'wrong'; x: number; y: number } | null>(null);

  const difficultySettings = {
    easy: { levels: 4, gridSize: 20, targetCount: 3, distractorCount: 15, timePerLevel: 45 },
    medium: { levels: 5, gridSize: 30, targetCount: 4, distractorCount: 25, timePerLevel: 40 },
    hard: { levels: 6, gridSize: 40, targetCount: 5, distractorCount: 35, timePerLevel: 35 },
  };

  const settings = difficultySettings[difficulty as keyof typeof difficultySettings] || difficultySettings.medium;

  const generateLevel = useCallback((levelIndex: number): Level => {
    const targetType = SHAPES[Math.floor(Math.random() * SHAPES.length)];
    const targetColor = COLORS[Math.floor(Math.random() * COLORS.length)];
    const targets: Target[] = [];
    const positions = new Set<string>();

    // Generate target items
    const targetCount = settings.targetCount + Math.floor(levelIndex / 2);
    for (let i = 0; i < targetCount; i++) {
      let x, y, posKey;
      do {
        x = 20 + Math.random() * 360;
        y = 20 + Math.random() * 260;
        posKey = `${Math.round(x / 30)}-${Math.round(y / 30)}`;
      } while (positions.has(posKey));
      positions.add(posKey);

      targets.push({
        id: i,
        x,
        y,
        type: targetType,
        color: targetColor,
        rotation: Math.random() * 360,
        isTarget: true,
        found: false,
      });
    }

    // Generate distractors
    const distractorCount = settings.distractorCount + levelIndex * 3;
    for (let i = 0; i < distractorCount; i++) {
      let x, y, posKey;
      do {
        x = 20 + Math.random() * 360;
        y = 20 + Math.random() * 260;
        posKey = `${Math.round(x / 30)}-${Math.round(y / 30)}`;
      } while (positions.has(posKey));
      positions.add(posKey);

      // Distractors can be same shape different color, or different shape
      const useSameShape = Math.random() > 0.5;
      const distractorType = useSameShape ? targetType : SHAPES.filter((s) => s !== targetType)[Math.floor(Math.random() * (SHAPES.length - 1))];
      const distractorColor = useSameShape
        ? COLORS.filter((c) => c !== targetColor)[Math.floor(Math.random() * (COLORS.length - 1))]
        : COLORS[Math.floor(Math.random() * COLORS.length)];

      targets.push({
        id: targetCount + i,
        x,
        y,
        type: distractorType,
        color: distractorColor,
        rotation: Math.random() * 360,
        isTarget: false,
        found: false,
      });
    }

    return { targets, targetType, targetColor, targetCount };
  }, [settings.targetCount, settings.distractorCount]);

  const startGame = () => {
    const newLevels = Array.from({ length: settings.levels }, (_, i) => generateLevel(i));
    setLevels(newLevels);
    setCurrentLevel(0);
    setFoundTargets([]);
    setScore(0);
    setWrongClicks(0);
    setStartTime(Date.now());
    setTimeLeft(settings.timePerLevel);
    setGameState('playing');
  };

  // Timer
  useEffect(() => {
    if (gameState !== 'playing') return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          if (currentLevel < levels.length - 1) {
            setCurrentLevel((l) => l + 1);
            setFoundTargets([]);
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

  const handleItemClick = (item: Target, e: React.MouseEvent) => {
    if (gameState !== 'playing' || foundTargets.includes(item.id)) return;

    const rect = (e.currentTarget as SVGElement).ownerSVGElement?.getBoundingClientRect();
    if (!rect) return;

    if (item.isTarget) {
      setFoundTargets([...foundTargets, item.id]);
      setScore((s) => s + 15);
      setShowFeedback({ type: 'correct', x: item.x, y: item.y });

      // Check if all targets found
      const level = levels[currentLevel];
      if (foundTargets.length + 1 >= level.targetCount) {
        // Bonus for time remaining
        const timeBonus = Math.round(timeLeft * 0.5);
        setScore((s) => s + timeBonus);

        if (currentLevel < levels.length - 1) {
          setTimeout(() => {
            setCurrentLevel((l) => l + 1);
            setFoundTargets([]);
            setTimeLeft(settings.timePerLevel);
          }, 500);
        } else {
          setTimeout(() => setGameState('completed'), 500);
        }
      }
    } else {
      setWrongClicks((w) => w + 1);
      setScore((s) => Math.max(0, s - 5));
      setShowFeedback({ type: 'wrong', x: item.x, y: item.y });
    }

    setTimeout(() => setShowFeedback(null), 300);
  };

  const renderShape = (item: Target) => {
    const size = 20;
    const style = {
      fill: item.isTarget && foundTargets.includes(item.id) ? '#22c55e' : item.color,
      opacity: foundTargets.includes(item.id) ? 0.5 : 1,
      cursor: 'pointer',
      transition: 'all 0.2s',
    };

    switch (item.type) {
      case 'circle':
        return (
          <circle
            cx={item.x}
            cy={item.y}
            r={size / 2}
            {...style}
            onClick={(e) => handleItemClick(item, e)}
          />
        );
      case 'square':
        return (
          <rect
            x={item.x - size / 2}
            y={item.y - size / 2}
            width={size}
            height={size}
            transform={`rotate(${item.rotation}, ${item.x}, ${item.y})`}
            {...style}
            onClick={(e) => handleItemClick(item, e)}
          />
        );
      case 'triangle':
        const points = `${item.x},${item.y - size / 2} ${item.x - size / 2},${item.y + size / 2} ${item.x + size / 2},${item.y + size / 2}`;
        return (
          <polygon
            points={points}
            transform={`rotate(${item.rotation}, ${item.x}, ${item.y})`}
            {...style}
            onClick={(e) => handleItemClick(item, e)}
          />
        );
      case 'star':
        const starPoints = [];
        for (let i = 0; i < 5; i++) {
          const angle = (i * 72 - 90) * (Math.PI / 180);
          const outerX = item.x + (size / 2) * Math.cos(angle);
          const outerY = item.y + (size / 2) * Math.sin(angle);
          starPoints.push(`${outerX},${outerY}`);
          const innerAngle = ((i * 72 + 36) - 90) * (Math.PI / 180);
          const innerX = item.x + (size / 4) * Math.cos(innerAngle);
          const innerY = item.y + (size / 4) * Math.sin(innerAngle);
          starPoints.push(`${innerX},${innerY}`);
        }
        return (
          <polygon
            points={starPoints.join(' ')}
            transform={`rotate(${item.rotation}, ${item.x}, ${item.y})`}
            {...style}
            onClick={(e) => handleItemClick(item, e)}
          />
        );
      case 'diamond':
        const diamondPoints = `${item.x},${item.y - size / 2} ${item.x + size / 2},${item.y} ${item.x},${item.y + size / 2} ${item.x - size / 2},${item.y}`;
        return (
          <polygon
            points={diamondPoints}
            transform={`rotate(${item.rotation}, ${item.x}, ${item.y})`}
            {...style}
            onClick={(e) => handleItemClick(item, e)}
          />
        );
      default:
        return (
          <circle
            cx={item.x}
            cy={item.y}
            r={size / 2}
            {...style}
            onClick={(e) => handleItemClick(item, e)}
          />
        );
    }
  };

  const renderTargetPreview = (type: string, color: string) => {
    const size = 30;
    const cx = 20;
    const cy = 20;

    switch (type) {
      case 'circle':
        return <circle cx={cx} cy={cy} r={size / 2} fill={color} />;
      case 'square':
        return <rect x={cx - size / 2} y={cy - size / 2} width={size} height={size} fill={color} />;
      case 'triangle':
        return <polygon points={`${cx},${cy - size / 2} ${cx - size / 2},${cy + size / 2} ${cx + size / 2},${cy + size / 2}`} fill={color} />;
      case 'star':
        const starPoints = [];
        for (let i = 0; i < 5; i++) {
          const angle = (i * 72 - 90) * (Math.PI / 180);
          starPoints.push(`${cx + (size / 2) * Math.cos(angle)},${cy + (size / 2) * Math.sin(angle)}`);
          const innerAngle = ((i * 72 + 36) - 90) * (Math.PI / 180);
          starPoints.push(`${cx + (size / 4) * Math.cos(innerAngle)},${cy + (size / 4) * Math.sin(innerAngle)}`);
        }
        return <polygon points={starPoints.join(' ')} fill={color} />;
      case 'diamond':
        return <polygon points={`${cx},${cy - size / 2} ${cx + size / 2},${cy} ${cx},${cy + size / 2} ${cx - size / 2},${cy}`} fill={color} />;
      default:
        return <circle cx={cx} cy={cy} r={size / 2} fill={color} />;
    }
  };

  const finishGame = () => {
    const duration = Math.round((Date.now() - startTime) / 1000);
    const totalTargets = levels.reduce((sum, l) => sum + l.targetCount, 0);
    const accuracy = totalTargets > 0 ? Math.round((score / (totalTargets * 15)) * 100) : 0;

    onComplete({
      score,
      maxScore: totalTargets * 15,
      accuracy: Math.min(100, accuracy),
      duration,
      data: {
        levelsCompleted: currentLevel + 1,
        totalLevels: levels.length,
        wrongClicks,
        totalTargets,
      },
    });
  };

  if (gameState === 'intro') {
    return (
      <div className="text-center py-8">
        <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Search className="w-10 h-10 text-blue-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Görsel Arama</h2>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Karışık şekiller arasından belirtilen hedefi bulun. Hedefle aynı şekil VE renkte olan tüm öğelere tıklayın.
        </p>
        <div className="bg-blue-50 rounded-lg p-4 mb-6 max-w-sm mx-auto">
          <div className="text-sm text-blue-700">
            <div className="flex justify-between mb-1">
              <span>Seviye sayısı:</span>
              <span className="font-semibold">{settings.levels}</span>
            </div>
            <div className="flex justify-between mb-1">
              <span>Her seviyede hedef:</span>
              <span className="font-semibold">{settings.targetCount}+</span>
            </div>
            <div className="flex justify-between">
              <span>Süre (her seviye):</span>
              <span className="font-semibold">{settings.timePerLevel} saniye</span>
            </div>
          </div>
        </div>
        <button
          onClick={startGame}
          className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition flex items-center gap-2 mx-auto"
        >
          <Play className="w-5 h-5" />
          Başla
        </button>
      </div>
    );
  }

  if (gameState === 'completed') {
    const totalTargets = levels.reduce((sum, l) => sum + l.targetCount, 0);
    const accuracy = Math.min(100, Math.round((score / (totalTargets * 15)) * 100));

    return (
      <div className="text-center py-8">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-10 h-10 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Tamamlandı!</h2>
        <div className="bg-gray-50 rounded-xl p-6 max-w-sm mx-auto mb-6">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600">{score}</div>
              <div className="text-sm text-gray-500">Puan</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600">%{accuracy}</div>
              <div className="text-sm text-gray-500">Doğruluk</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600">{currentLevel + 1}/{levels.length}</div>
              <div className="text-sm text-gray-500">Seviye</div>
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
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
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
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            {score} puan
          </span>
        </div>
        <div className={`flex items-center gap-2 text-lg font-bold ${timeLeft <= 10 ? 'text-red-600' : 'text-gray-700'}`}>
          <Clock className="w-5 h-5" />
          {timeLeft}s
        </div>
      </div>

      {/* Target indicator */}
      <div className="flex items-center gap-3 mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
        <span className="text-amber-700 font-medium">Hedef:</span>
        <svg width="40" height="40" viewBox="0 0 40 40">
          {renderTargetPreview(level.targetType, level.targetColor)}
        </svg>
        <span className="text-amber-700">
          ({foundTargets.length}/{level.targetCount} bulundu)
        </span>
      </div>

      {/* Game area */}
      <div className="relative">
        <svg
          viewBox="0 0 400 300"
          className="w-full h-auto bg-gray-100 rounded-xl border-2 border-gray-200"
          style={{ minHeight: '300px' }}
        >
          {level.targets.map((item) => (
            <g key={item.id}>{renderShape(item)}</g>
          ))}

          {/* Feedback animation */}
          {showFeedback && (
            <circle
              cx={showFeedback.x}
              cy={showFeedback.y}
              r="25"
              fill="none"
              stroke={showFeedback.type === 'correct' ? '#22c55e' : '#ef4444'}
              strokeWidth="3"
              opacity="0.8"
            />
          )}
        </svg>
      </div>

      <p className="text-center text-sm text-gray-500 mt-4">
        Yukarıda gösterilen hedefle aynı şekil ve renkteki tüm öğeleri bulun.
      </p>
    </div>
  );
}
