'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Home, ArrowRight, ArrowLeft, ArrowUp, ArrowDown } from 'lucide-react';

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

// Ev planı odaları
const ROOMS = [
  { id: 'giris', name: 'Giriş', x: 2, y: 0, color: 'bg-amber-100', icon: '🚪' },
  { id: 'salon', name: 'Salon', x: 1, y: 1, color: 'bg-blue-100', icon: '🛋️' },
  { id: 'mutfak', name: 'Mutfak', x: 3, y: 1, color: 'bg-orange-100', icon: '🍳' },
  { id: 'yatak1', name: 'Yatak Odası', x: 0, y: 2, color: 'bg-purple-100', icon: '🛏️' },
  { id: 'banyo', name: 'Banyo', x: 2, y: 2, color: 'bg-cyan-100', icon: '🚿' },
  { id: 'cocuk', name: 'Çocuk Odası', x: 4, y: 2, color: 'bg-pink-100', icon: '🧸' },
  { id: 'balkon', name: 'Balkon', x: 1, y: 3, color: 'bg-green-100', icon: '🌿' },
  { id: 'depo', name: 'Depo', x: 3, y: 3, color: 'bg-gray-200', icon: '📦' },
];

// Odalar arası bağlantılar
const CONNECTIONS: Record<string, string[]> = {
  'giris': ['salon', 'mutfak'],
  'salon': ['giris', 'yatak1', 'banyo', 'balkon'],
  'mutfak': ['giris', 'banyo', 'depo', 'cocuk'],
  'yatak1': ['salon', 'balkon'],
  'banyo': ['salon', 'mutfak'],
  'cocuk': ['mutfak', 'depo'],
  'balkon': ['salon', 'yatak1'],
  'depo': ['mutfak', 'cocuk'],
};

// Yön hesapla
function getDirection(from: typeof ROOMS[0], to: typeof ROOMS[0]): string {
  const dx = to.x - from.x;
  const dy = to.y - from.y;

  if (dy < 0) return 'yukarı';
  if (dy > 0) return 'aşağı';
  if (dx < 0) return 'sola';
  if (dx > 0) return 'sağa';
  return '';
}

// İki oda arası en kısa yol (BFS)
function findPath(startId: string, endId: string): string[] {
  const visited = new Set<string>();
  const queue: { id: string; path: string[] }[] = [{ id: startId, path: [startId] }];

  while (queue.length > 0) {
    const { id, path } = queue.shift()!;

    if (id === endId) return path;

    if (visited.has(id)) continue;
    visited.add(id);

    for (const neighbor of CONNECTIONS[id] || []) {
      if (!visited.has(neighbor)) {
        queue.push({ id: neighbor, path: [...path, neighbor] });
      }
    }
  }

  return [];
}

interface Question {
  fromRoom: typeof ROOMS[0];
  toRoom: typeof ROOMS[0];
  correctPath: string[];
  options: { path: string[]; directions: string }[];
}

export default function VirtualHomeNavigationGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'learn' | 'playing' | 'complete'>('ready');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [learnCountdown, setLearnCountdown] = useState(0);
  const [highlightedRoom, setHighlightedRoom] = useState<string | null>(null);

  const totalRounds = difficulty === 'easy' ? 5 : difficulty === 'medium' ? 8 : 10;
  const learnTime = difficulty === 'easy' ? 30 : difficulty === 'medium' ? 20 : 15;

  // Yol tarifini oluştur
  const generateDirections = (path: string[]): string => {
    const directions: string[] = [];
    for (let i = 0; i < path.length - 1; i++) {
      const from = ROOMS.find(r => r.id === path[i])!;
      const to = ROOMS.find(r => r.id === path[i + 1])!;
      const dir = getDirection(from, to);
      directions.push(`${dir} → ${to.name}`);
    }
    return directions.join(', ');
  };

  // Soru oluştur
  const generateQuestion = useCallback((): Question => {
    const availableRooms = [...ROOMS];
    const fromIdx = Math.floor(Math.random() * availableRooms.length);
    const fromRoom = availableRooms[fromIdx];

    // Farklı bir oda seç (en az 2 adım uzakta)
    let toRoom: typeof ROOMS[0];
    let correctPath: string[];
    do {
      const toIdx = Math.floor(Math.random() * availableRooms.length);
      toRoom = availableRooms[toIdx];
      correctPath = findPath(fromRoom.id, toRoom.id);
    } while (fromRoom.id === toRoom.id || correctPath.length < 3);

    // Yanlış seçenekler oluştur
    const wrongPaths: string[][] = [];

    // Alternatif yanlış yollar
    const otherRooms = ROOMS.filter(r => r.id !== fromRoom.id && r.id !== toRoom.id);
    for (let i = 0; i < 3 && otherRooms.length > 0; i++) {
      const randomRoom = otherRooms[Math.floor(Math.random() * otherRooms.length)];
      const wrongPath = findPath(fromRoom.id, randomRoom.id);
      if (wrongPath.length >= 2) {
        wrongPaths.push(wrongPath);
      }
    }

    // Eğer yeterli yanlış seçenek yoksa, doğru yolu modifiye et
    while (wrongPaths.length < 3) {
      const shuffledPath = [fromRoom.id, ...correctPath.slice(1).sort(() => Math.random() - 0.5)];
      if (JSON.stringify(shuffledPath) !== JSON.stringify(correctPath)) {
        wrongPaths.push(shuffledPath);
      }
    }

    const allOptions = [
      { path: correctPath, directions: generateDirections(correctPath) },
      ...wrongPaths.slice(0, 3).map(p => ({ path: p, directions: generateDirections(p) }))
    ].sort(() => Math.random() - 0.5);

    return {
      fromRoom,
      toRoom,
      correctPath,
      options: allOptions,
    };
  }, []);

  // Oyunu başlat
  const startGame = () => {
    setGamePhase('learn');
    setLearnCountdown(learnTime);
  };

  // Öğrenme bitti, teste geç
  const startTest = () => {
    setGamePhase('playing');
    setRound(1);
    setScore(0);
    setStartTime(Date.now());
    setCurrentQuestion(generateQuestion());
    setFeedback(null);
    setSelectedOption(null);
  };

  // Öğrenme sayacı
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (gamePhase === 'learn' && learnCountdown > 0) {
      interval = setInterval(() => {
        setLearnCountdown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [gamePhase, learnCountdown]);

  // Oda vurgulama animasyonu
  useEffect(() => {
    if (gamePhase === 'learn') {
      const interval = setInterval(() => {
        const randomRoom = ROOMS[Math.floor(Math.random() * ROOMS.length)];
        setHighlightedRoom(randomRoom.id);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [gamePhase]);

  // Cevap kontrolü
  const handleAnswer = (optionIndex: number) => {
    if (feedback || !currentQuestion) return;

    setSelectedOption(optionIndex);
    const selected = currentQuestion.options[optionIndex];
    const isCorrect = JSON.stringify(selected.path) === JSON.stringify(currentQuestion.correctPath);

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
        setCurrentQuestion(generateQuestion());
        setFeedback(null);
        setSelectedOption(null);
      }
    }, 2000);
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
        gameType: 'virtual-home-navigation',
      },
    });
  };

  // Ev planı grid render
  const renderHomeMap = (showLabels: boolean = true, highlightPath: string[] = []) => (
    <div className="relative bg-amber-50 p-4 rounded-xl border-2 border-amber-200">
      <div className="grid grid-cols-5 gap-1" style={{ aspectRatio: '5/4' }}>
        {Array.from({ length: 20 }).map((_, idx) => {
          const x = idx % 5;
          const y = Math.floor(idx / 5);
          const room = ROOMS.find(r => r.x === x && r.y === y);

          if (!room) {
            return <div key={idx} className="bg-amber-50" />;
          }

          const isHighlighted = highlightedRoom === room.id || highlightPath.includes(room.id);
          const isStart = currentQuestion?.fromRoom.id === room.id;
          const isEnd = currentQuestion?.toRoom.id === room.id;

          return (
            <div
              key={idx}
              className={`
                ${room.color} rounded-lg p-2 flex flex-col items-center justify-center
                transition-all duration-300 border-2
                ${isHighlighted ? 'ring-2 ring-amber-400 scale-105' : ''}
                ${isStart ? 'border-green-500 ring-2 ring-green-300' : ''}
                ${isEnd ? 'border-red-500 ring-2 ring-red-300' : 'border-transparent'}
              `}
            >
              <span className="text-2xl">{room.icon}</span>
              {showLabels && (
                <span className="text-xs font-medium text-gray-700 mt-1 text-center">
                  {room.name}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Bağlantı çizgileri gösterimi için legend */}
      {gamePhase === 'learn' && (
        <div className="mt-3 text-xs text-gray-500 text-center">
          Odalar arası geçişleri inceleyin
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto">
      {/* Hazırlık */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-amber-50 rounded-xl mb-4">
            <Home className="w-12 h-12 text-amber-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Ev İçi Navigasyon Testi</h3>
            <p className="text-sm text-gray-600 mb-4">
              Bir evin planını inceleyeceksiniz.
              <br />
              Sonra bir odadan diğerine nasıl gidileceğini soracağız.
              <br />
              Doğru yolu bulun!
            </p>

            {renderHomeMap()}

            <button
              onClick={startGame}
              className="flex items-center gap-2 px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition mx-auto mt-4"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Öğrenme Aşaması */}
      {gamePhase === 'learn' && (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2 text-amber-600">
            <Home className="w-5 h-5" />
            <span className="font-medium">Ev Planını İnceleyin</span>
          </div>

          <div className="text-3xl font-bold text-amber-600 mb-4">
            {learnCountdown}s
          </div>

          {renderHomeMap()}

          <p className="text-sm text-gray-500 mt-4 mb-4">
            Odaların konumlarını ve birbirine bağlantılarını ezberleyin!
          </p>

          <button
            onClick={startTest}
            className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition text-sm"
          >
            Hazırım, Teste Başla
          </button>
        </div>
      )}

      {/* Test Aşaması */}
      {gamePhase === 'playing' && currentQuestion && (
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
          <div className="h-2 bg-gray-200 rounded-full mb-4 overflow-hidden">
            <div
              className="h-full bg-amber-600 transition-all duration-300"
              style={{ width: `${(round / totalRounds) * 100}%` }}
            />
          </div>

          {/* Harita */}
          <div className="mb-4">
            {renderHomeMap(true, feedback ? currentQuestion.correctPath : [])}
          </div>

          {/* Soru */}
          <div className={`p-4 rounded-xl mb-4 text-center transition-colors ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : 'bg-amber-100'
          }`}>
            <p className="text-lg font-medium text-gray-800">
              <span className="text-green-600">{currentQuestion.fromRoom.icon} {currentQuestion.fromRoom.name}</span>
              {' '}→{' '}
              <span className="text-red-600">{currentQuestion.toRoom.icon} {currentQuestion.toRoom.name}</span>
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Bu odalar arası en kısa yol hangisi?
            </p>
          </div>

          {/* Seçenekler */}
          <div className="space-y-2">
            {currentQuestion.options.map((option, index) => {
              const isCorrect = JSON.stringify(option.path) === JSON.stringify(currentQuestion.correctPath);
              return (
                <button
                  key={index}
                  onClick={() => handleAnswer(index)}
                  disabled={!!feedback}
                  className={`w-full py-3 px-4 rounded-xl font-medium transition-all text-left text-sm ${
                    feedback
                      ? isCorrect
                        ? 'bg-green-500 text-white'
                        : selectedOption === index
                        ? 'bg-red-500 text-white'
                        : 'bg-gray-200 text-gray-400'
                      : 'bg-white border-2 border-gray-200 text-gray-900 hover:border-amber-400 hover:bg-amber-50'
                  } ${feedback ? 'cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center gap-2">
                    <span className="bg-amber-100 text-amber-700 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span>{option.directions}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Geri bildirim */}
          {feedback && (
            <div className={`mt-4 text-center p-3 rounded-lg ${
              feedback === 'correct' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {feedback === 'correct'
                ? '✓ Doğru! +10 puan'
                : `✗ Yanlış! Doğru yol: ${generateDirections(currentQuestion.correctPath)}`}
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
