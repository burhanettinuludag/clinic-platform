'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Volume2 } from 'lucide-react';

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

const COLORS = [
  'bg-red-500',
  'bg-blue-500',
  'bg-green-500',
  'bg-yellow-500',
  'bg-purple-500',
  'bg-pink-500',
  'bg-orange-500',
  'bg-teal-500',
  'bg-indigo-500',
];

export default function SequenceRecallGame({ config, difficulty, onComplete }: Props) {
  const [sequence, setSequence] = useState<number[]>([]);
  const [playerSequence, setPlayerSequence] = useState<number[]>([]);
  const [isShowingSequence, setIsShowingSequence] = useState(false);
  const [activeSquare, setActiveSquare] = useState<number | null>(null);
  const [gamePhase, setGamePhase] = useState<'ready' | 'showing' | 'input' | 'success' | 'fail' | 'complete'>('ready');
  const [level, setLevel] = useState(1);
  const [score, setScore] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [totalAttempts, setTotalAttempts] = useState(0);

  const gridSize = (config.grid_size as number) || 9;
  const startingLength = (config.starting_length as number) || 3;
  const maxLength = (config.max_length as number) || 9;
  const gridCols = Math.ceil(Math.sqrt(gridSize));

  // Generate new sequence
  const generateSequence = useCallback((length: number) => {
    const newSequence: number[] = [];
    for (let i = 0; i < length; i++) {
      newSequence.push(Math.floor(Math.random() * gridSize));
    }
    return newSequence;
  }, [gridSize]);

  // Show sequence to player
  const showSequence = useCallback(async (seq: number[]) => {
    setIsShowingSequence(true);
    setGamePhase('showing');

    for (let i = 0; i < seq.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 300));
      setActiveSquare(seq[i]);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setActiveSquare(null);
    }

    await new Promise((resolve) => setTimeout(resolve, 300));
    setIsShowingSequence(false);
    setGamePhase('input');
  }, []);

  // Start new round
  const startRound = useCallback(() => {
    const length = startingLength + level - 1;
    const newSequence = generateSequence(Math.min(length, maxLength));
    setSequence(newSequence);
    setPlayerSequence([]);
    showSequence(newSequence);
  }, [level, startingLength, maxLength, generateSequence, showSequence]);

  // Start game
  const startGame = () => {
    setLevel(1);
    setScore(0);
    setCorrectAnswers(0);
    setTotalAttempts(0);
    setStartTime(Date.now());
    setGamePhase('ready');
    setTimeout(() => startRound(), 500);
  };

  // Handle square click
  const handleSquareClick = (index: number) => {
    if (gamePhase !== 'input' || isShowingSequence) return;

    // Visual feedback
    setActiveSquare(index);
    setTimeout(() => setActiveSquare(null), 200);

    const newPlayerSequence = [...playerSequence, index];
    setPlayerSequence(newPlayerSequence);

    const currentIndex = newPlayerSequence.length - 1;

    // Check if correct
    if (newPlayerSequence[currentIndex] !== sequence[currentIndex]) {
      // Wrong!
      setTotalAttempts((prev) => prev + 1);
      setGamePhase('fail');

      // Check if game over (3 levels completed or max reached)
      if (level >= 3) {
        endGame();
      }
      return;
    }

    // Check if sequence complete
    if (newPlayerSequence.length === sequence.length) {
      // Correct!
      setCorrectAnswers((prev) => prev + 1);
      setTotalAttempts((prev) => prev + 1);
      setScore((prev) => prev + level * 10);
      setGamePhase('success');

      // Check if game complete
      if (level >= 5 || startingLength + level >= maxLength) {
        setTimeout(() => endGame(), 1000);
      } else {
        // Next level
        setTimeout(() => {
          setLevel((prev) => prev + 1);
          startRound();
        }, 1500);
      }
    }
  };

  // End game
  const endGame = () => {
    setGamePhase('complete');
    const duration = Math.floor((Date.now() - startTime) / 1000);
    const accuracy = totalAttempts > 0 ? Math.round((correctAnswers / totalAttempts) * 100) : 0;

    onComplete({
      score,
      maxScore: 50, // 5 levels * 10 points
      accuracy,
      duration,
      data: {
        levelsCompleted: level,
        maxSequenceLength: startingLength + level - 1,
        difficulty,
      },
    });
  };

  // Retry after fail
  const retryLevel = () => {
    setPlayerSequence([]);
    showSequence(sequence);
  };

  return (
    <div className="max-w-md mx-auto">
      {/* Instructions */}
      {gamePhase === 'ready' && (
        <div className="text-center mb-6">
          <div className="p-6 bg-indigo-50 rounded-xl mb-4">
            <Volume2 className="w-8 h-8 text-indigo-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Sıra Hatırlama</h3>
            <p className="text-sm text-gray-600 mb-4">
              Karelerin yanma sırasını izleyin ve aynı sırayla tıklayın.
              Her seviyede sıra bir kare daha uzun olacak!
            </p>
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

      {/* Game Stats */}
      {gamePhase !== 'ready' && gamePhase !== 'complete' && (
        <div className="flex justify-between items-center mb-4 text-sm">
          <div className="text-gray-600">
            Seviye: <span className="font-bold text-indigo-600">{level}</span>
          </div>
          <div className="text-gray-600">
            Skor: <span className="font-bold">{score}</span>
          </div>
          <div className="text-gray-600">
            Sıra: <span className="font-bold">{sequence.length}</span> kare
          </div>
        </div>
      )}

      {/* Status Message */}
      {gamePhase === 'showing' && (
        <div className="text-center mb-4 p-3 bg-yellow-50 rounded-lg">
          <p className="text-yellow-800 font-medium">İzleyin...</p>
        </div>
      )}
      {gamePhase === 'input' && (
        <div className="text-center mb-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-blue-800 font-medium">
            Sıranız! ({playerSequence.length}/{sequence.length})
          </p>
        </div>
      )}
      {gamePhase === 'success' && (
        <div className="text-center mb-4 p-3 bg-green-50 rounded-lg">
          <p className="text-green-800 font-medium">Doğru! +{level * 10} puan</p>
        </div>
      )}
      {gamePhase === 'fail' && (
        <div className="text-center mb-4 p-3 bg-red-50 rounded-lg">
          <p className="text-red-800 font-medium mb-2">Yanlış sıra!</p>
          <button
            onClick={retryLevel}
            className="text-sm text-red-600 hover:text-red-700 underline"
          >
            Tekrar Dene
          </button>
        </div>
      )}

      {/* Game Grid */}
      {gamePhase !== 'ready' && gamePhase !== 'complete' && (
        <div
          className="grid gap-2 mb-6"
          style={{
            gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))`,
          }}
        >
          {Array.from({ length: gridSize }).map((_, index) => (
            <button
              key={index}
              onClick={() => handleSquareClick(index)}
              disabled={gamePhase !== 'input'}
              className={`aspect-square rounded-xl transition-all duration-200 ${
                activeSquare === index
                  ? `${COLORS[index % COLORS.length]} scale-95`
                  : 'bg-gray-200 hover:bg-gray-300'
              } ${gamePhase !== 'input' ? 'cursor-not-allowed' : ''}`}
            />
          ))}
        </div>
      )}

      {/* Game Complete */}
      {gamePhase === 'complete' && (
        <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
          <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Oyun Bitti!</h3>
          <div className="text-gray-600 mb-4 space-y-1">
            <p>Skor: <span className="font-bold">{score}</span></p>
            <p>Tamamlanan Seviye: <span className="font-bold">{level}</span></p>
            <p>Doğruluk: <span className="font-bold">%{totalAttempts > 0 ? Math.round((correctAnswers / totalAttempts) * 100) : 0}</span></p>
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
