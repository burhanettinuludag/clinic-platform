'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Compass, ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from 'lucide-react';

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

type Direction = 'up' | 'down' | 'left' | 'right';

interface Position {
  x: number;
  y: number;
}

const DIRECTION_NAMES: Record<Direction, string> = {
  up: 'Yukarı',
  down: 'Aşağı',
  left: 'Sola',
  right: 'Sağa',
};

const DIRECTION_ARROWS: Record<Direction, typeof ArrowUp> = {
  up: ArrowUp,
  down: ArrowDown,
  left: ArrowLeft,
  right: ArrowRight,
};

const DIRECTION_DELTAS: Record<Direction, Position> = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

// Grid üzerindeki özel noktalar
const GRID_ITEMS = [
  { emoji: '🏠', name: 'Ev' },
  { emoji: '🌳', name: 'Ağaç' },
  { emoji: '⭐', name: 'Yıldız' },
  { emoji: '🎯', name: 'Hedef' },
  { emoji: '💎', name: 'Elmas' },
  { emoji: '🌸', name: 'Çiçek' },
  { emoji: '🍎', name: 'Elma' },
  { emoji: '🔔', name: 'Zil' },
];

export default function DirectionFollowingGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'show' | 'follow' | 'complete'>('ready');
  const [directions, setDirections] = useState<Direction[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [playerPosition, setPlayerPosition] = useState<Position>({ x: 0, y: 0 });
  const [targetPosition, setTargetPosition] = useState<Position>({ x: 0, y: 0 });
  const [startPosition, setStartPosition] = useState<Position>({ x: 0, y: 0 });
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [showCountdown, setShowCountdown] = useState(0);
  const [gridItems, setGridItems] = useState<{ pos: Position; item: typeof GRID_ITEMS[0] }[]>([]);

  const gridSize = difficulty === 'easy' ? 4 : difficulty === 'medium' ? 5 : 6;
  const totalRounds = difficulty === 'easy' ? 5 : difficulty === 'medium' ? 7 : 10;
  const sequenceLength = difficulty === 'easy' ? 3 : difficulty === 'medium' ? 4 : 5;
  const showTime = difficulty === 'easy' ? 5 : difficulty === 'medium' ? 4 : 3;

  // Yeni tur oluştur
  const generateRound = useCallback(() => {
    // Başlangıç pozisyonu (ortaya yakın)
    const start: Position = {
      x: Math.floor(gridSize / 2),
      y: Math.floor(gridSize / 2),
    };
    setStartPosition(start);
    setPlayerPosition(start);

    // Rastgele yönler oluştur ve hedef pozisyonunu hesapla
    const newDirections: Direction[] = [];
    let current = { ...start };

    for (let i = 0; i < sequenceLength; i++) {
      const validDirs: Direction[] = [];

      // Geçerli yönleri bul (grid dışına çıkmayan)
      if (current.y > 0) validDirs.push('up');
      if (current.y < gridSize - 1) validDirs.push('down');
      if (current.x > 0) validDirs.push('left');
      if (current.x < gridSize - 1) validDirs.push('right');

      const dir = validDirs[Math.floor(Math.random() * validDirs.length)];
      newDirections.push(dir);

      current = {
        x: current.x + DIRECTION_DELTAS[dir].x,
        y: current.y + DIRECTION_DELTAS[dir].y,
      };
    }

    setDirections(newDirections);
    setTargetPosition(current);

    // Grid üzerine rastgele öğeler yerleştir
    const items: { pos: Position; item: typeof GRID_ITEMS[0] }[] = [];
    const usedPositions = new Set<string>();
    usedPositions.add(`${start.x},${start.y}`);
    usedPositions.add(`${current.x},${current.y}`);

    const itemCount = Math.min(4, gridSize);
    for (let i = 0; i < itemCount; i++) {
      let pos: Position;
      do {
        pos = {
          x: Math.floor(Math.random() * gridSize),
          y: Math.floor(Math.random() * gridSize),
        };
      } while (usedPositions.has(`${pos.x},${pos.y}`));

      usedPositions.add(`${pos.x},${pos.y}`);
      items.push({ pos, item: GRID_ITEMS[i % GRID_ITEMS.length] });
    }
    setGridItems(items);

    return { start, target: current, directions: newDirections };
  }, [gridSize, sequenceLength]);

  // Oyunu başlat
  const startGame = () => {
    setRound(1);
    setScore(0);
    setCurrentStep(0);
    setFeedback(null);
    setStartTime(Date.now());
    generateRound();
    setGamePhase('show');
    setShowCountdown(showTime);
  };

  // Gösterim sayacı
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (gamePhase === 'show' && showCountdown > 0) {
      interval = setInterval(() => {
        setShowCountdown((prev) => prev - 1);
      }, 1000);
    } else if (gamePhase === 'show' && showCountdown === 0) {
      setGamePhase('follow');
      setCurrentStep(0);
    }
    return () => clearInterval(interval);
  }, [gamePhase, showCountdown]);

  // Yön seçimi
  const handleDirectionClick = (dir: Direction) => {
    if (feedback || gamePhase !== 'follow') return;

    const expectedDir = directions[currentStep];
    const isCorrect = dir === expectedDir;

    if (isCorrect) {
      // Pozisyonu güncelle
      const newPos = {
        x: playerPosition.x + DIRECTION_DELTAS[dir].x,
        y: playerPosition.y + DIRECTION_DELTAS[dir].y,
      };
      setPlayerPosition(newPos);

      if (currentStep === directions.length - 1) {
        // Tur tamamlandı
        setScore((prev) => prev + 10);
        setFeedback('correct');

        setTimeout(() => {
          if (round >= totalRounds) {
            endGame();
          } else {
            setRound((prev) => prev + 1);
            setCurrentStep(0);
            setFeedback(null);
            generateRound();
            setGamePhase('show');
            setShowCountdown(showTime);
          }
        }, 1500);
      } else {
        setCurrentStep((prev) => prev + 1);
      }
    } else {
      setFeedback('wrong');

      setTimeout(() => {
        if (round >= totalRounds) {
          endGame();
        } else {
          setRound((prev) => prev + 1);
          setCurrentStep(0);
          setFeedback(null);
          generateRound();
          setGamePhase('show');
          setShowCountdown(showTime);
        }
      }, 1500);
    }
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
        sequenceLength,
        gameType: 'direction-following',
      },
    });
  };

  // Grid render
  const renderGrid = (showPath: boolean = false) => (
    <div
      className="grid gap-1 bg-gray-200 p-2 rounded-xl mx-auto"
      style={{
        gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))`,
        maxWidth: `${gridSize * 60}px`,
      }}
    >
      {Array.from({ length: gridSize * gridSize }).map((_, idx) => {
        const x = idx % gridSize;
        const y = Math.floor(idx / gridSize);
        const isStart = startPosition.x === x && startPosition.y === y;
        const isTarget = targetPosition.x === x && targetPosition.y === y;
        const isPlayer = playerPosition.x === x && playerPosition.y === y;
        const gridItem = gridItems.find(gi => gi.pos.x === x && gi.pos.y === y);

        // Yol üzerinde mi kontrol et (show fazında)
        let isOnPath = false;
        if (showPath && gamePhase === 'show') {
          let pathPos = { ...startPosition };
          for (let i = 0; i < directions.length; i++) {
            if (pathPos.x === x && pathPos.y === y) {
              isOnPath = true;
              break;
            }
            pathPos = {
              x: pathPos.x + DIRECTION_DELTAS[directions[i]].x,
              y: pathPos.y + DIRECTION_DELTAS[directions[i]].y,
            };
          }
          if (pathPos.x === x && pathPos.y === y) isOnPath = true;
        }

        return (
          <div
            key={idx}
            className={`
              aspect-square rounded-lg flex items-center justify-center text-2xl
              transition-all duration-300
              ${isPlayer ? 'bg-blue-500 ring-2 ring-blue-300' : ''}
              ${isStart && !isPlayer ? 'bg-green-100' : ''}
              ${isTarget ? 'bg-red-100 ring-2 ring-red-300' : ''}
              ${!isPlayer && !isStart && !isTarget ? 'bg-white' : ''}
              ${isOnPath && !isPlayer ? 'bg-yellow-100' : ''}
            `}
          >
            {isPlayer && '🚶'}
            {isTarget && !isPlayer && '🎯'}
            {isStart && !isPlayer && !isTarget && '🚩'}
            {gridItem && !isPlayer && !isTarget && !isStart && gridItem.item.emoji}
          </div>
        );
      })}
    </div>
  );

  return (
    <div className="max-w-lg mx-auto">
      {/* Hazırlık */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-indigo-50 rounded-xl mb-4">
            <Compass className="w-12 h-12 text-indigo-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Yön Takip Testi</h3>
            <p className="text-sm text-gray-600 mb-4">
              Size bir yön dizisi gösterilecek.
              <br />
              Yönleri ezberleyin ve sırayla takip edin.
              <br />
              Hedefe ulaşın!
            </p>

            <div className="p-4 bg-white rounded-lg mb-4">
              <div className="flex justify-center gap-2 mb-2">
                <div className="p-2 bg-gray-100 rounded">
                  <ArrowUp className="w-6 h-6 text-gray-600" />
                </div>
                <div className="p-2 bg-gray-100 rounded">
                  <ArrowRight className="w-6 h-6 text-gray-600" />
                </div>
                <div className="p-2 bg-gray-100 rounded">
                  <ArrowDown className="w-6 h-6 text-gray-600" />
                </div>
              </div>
              <p className="text-sm text-gray-500">Yönleri sırayla takip edin</p>
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

      {/* Yön Gösterimi */}
      {gamePhase === 'show' && (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2 text-indigo-600">
            <Compass className="w-5 h-5" />
            <span className="font-medium">Yönleri Ezberleyin</span>
          </div>

          <div className="text-3xl font-bold text-indigo-600 mb-4">
            {showCountdown}s
          </div>

          {/* Yön dizisi */}
          <div className="flex justify-center gap-2 mb-6 flex-wrap">
            {directions.map((dir, idx) => {
              const ArrowIcon = DIRECTION_ARROWS[dir];
              return (
                <div
                  key={idx}
                  className="flex flex-col items-center p-3 bg-white rounded-xl shadow-md border-2 border-indigo-200"
                >
                  <span className="text-xs text-gray-500 mb-1">{idx + 1}</span>
                  <ArrowIcon className="w-8 h-8 text-indigo-600" />
                  <span className="text-xs font-medium text-gray-700 mt-1">
                    {DIRECTION_NAMES[dir]}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Grid gösterimi */}
          {renderGrid(true)}

          <p className="text-sm text-gray-500 mt-4">
            🚩 Başlangıç → 🎯 Hedef
          </p>
        </div>
      )}

      {/* Takip Aşaması */}
      {gamePhase === 'follow' && (
        <>
          {/* İstatistikler */}
          <div className="flex justify-between items-center mb-4 text-sm">
            <div className="text-gray-600">
              Tur: <span className="font-bold">{round}/{totalRounds}</span>
            </div>
            <div className="text-gray-600">
              Adım: <span className="font-bold">{currentStep + 1}/{directions.length}</span>
            </div>
            <div className="text-gray-600">
              Skor: <span className="font-bold">{score}</span>
            </div>
          </div>

          {/* İlerleme çubuğu */}
          <div className="h-2 bg-gray-200 rounded-full mb-4 overflow-hidden">
            <div
              className="h-full bg-indigo-600 transition-all duration-300"
              style={{ width: `${((currentStep) / directions.length) * 100}%` }}
            />
          </div>

          {/* Grid */}
          <div className={`mb-6 transition-all ${
            feedback === 'correct' ? 'ring-4 ring-green-300 rounded-xl' :
            feedback === 'wrong' ? 'ring-4 ring-red-300 rounded-xl' : ''
          }`}>
            {renderGrid()}
          </div>

          {/* Soru */}
          <div className={`p-3 rounded-xl mb-4 text-center ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : 'bg-indigo-100'
          }`}>
            <p className="text-gray-700 font-medium">
              {currentStep + 1}. adımda hangi yöne gitmelisiniz?
            </p>
          </div>

          {/* Yön butonları */}
          <div className="grid grid-cols-3 gap-2 max-w-xs mx-auto">
            <div />
            <button
              onClick={() => handleDirectionClick('up')}
              disabled={!!feedback}
              className={`p-4 rounded-xl transition-all ${
                feedback ? 'bg-gray-200 cursor-not-allowed' : 'bg-white border-2 border-gray-200 hover:border-indigo-400 hover:bg-indigo-50 active:scale-95'
              }`}
            >
              <ArrowUp className="w-8 h-8 mx-auto text-gray-700" />
              <span className="text-xs text-gray-600">Yukarı</span>
            </button>
            <div />

            <button
              onClick={() => handleDirectionClick('left')}
              disabled={!!feedback}
              className={`p-4 rounded-xl transition-all ${
                feedback ? 'bg-gray-200 cursor-not-allowed' : 'bg-white border-2 border-gray-200 hover:border-indigo-400 hover:bg-indigo-50 active:scale-95'
              }`}
            >
              <ArrowLeft className="w-8 h-8 mx-auto text-gray-700" />
              <span className="text-xs text-gray-600">Sola</span>
            </button>
            <div className="flex items-center justify-center">
              <span className="text-2xl">🚶</span>
            </div>
            <button
              onClick={() => handleDirectionClick('right')}
              disabled={!!feedback}
              className={`p-4 rounded-xl transition-all ${
                feedback ? 'bg-gray-200 cursor-not-allowed' : 'bg-white border-2 border-gray-200 hover:border-indigo-400 hover:bg-indigo-50 active:scale-95'
              }`}
            >
              <ArrowRight className="w-8 h-8 mx-auto text-gray-700" />
              <span className="text-xs text-gray-600">Sağa</span>
            </button>

            <div />
            <button
              onClick={() => handleDirectionClick('down')}
              disabled={!!feedback}
              className={`p-4 rounded-xl transition-all ${
                feedback ? 'bg-gray-200 cursor-not-allowed' : 'bg-white border-2 border-gray-200 hover:border-indigo-400 hover:bg-indigo-50 active:scale-95'
              }`}
            >
              <ArrowDown className="w-8 h-8 mx-auto text-gray-700" />
              <span className="text-xs text-gray-600">Aşağı</span>
            </button>
            <div />
          </div>

          {/* Geri bildirim */}
          {feedback && (
            <div className={`mt-4 text-center p-3 rounded-lg ${
              feedback === 'correct' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {feedback === 'correct'
                ? '✓ Tebrikler! Hedefe ulaştınız! +10 puan'
                : `✗ Yanlış yön! Doğrusu: ${DIRECTION_NAMES[directions[currentStep]]}`}
            </div>
          )}
        </>
      )}

      {/* Oyun Bitti */}
      {gamePhase === 'complete' && (
        <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
          <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Test Tamamlandı!</h3>
          <div className="text-gray-600 mb-4 space-y-1">
            <p>Skor: <span className="font-bold">{score}</span>/{totalRounds * 10}</p>
            <p>Doğruluk: <span className="font-bold">%{Math.round((score / (totalRounds * 10)) * 100)}</span></p>
          </div>
          <button
            onClick={() => {
              setGamePhase('ready');
              setRound(0);
              setScore(0);
            }}
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
