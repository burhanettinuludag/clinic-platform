'use client';

import { useState, useCallback } from 'react';
import { Grid3X3, Play, Trophy, RotateCcw } from 'lucide-react';

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

// Optimal hamle tahminleri (solvable puzzle icin)
const OPTIMAL_MOVES: Record<string, number> = {
  easy: 6,      // 2x2 (3 karo)
  medium: 30,   // 3x3 (8 karo)
  hard: 80,     // 4x4 (15 karo)
};

export default function PuzzleArrangeGame({ config, difficulty, onComplete }: Props) {
  const [phase, setPhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [tiles, setTiles] = useState<number[]>([]);
  const [moves, setMoves] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [gridSize, setGridSize] = useState(3);

  const getGridSize = useCallback((): number => {
    const gridSizes = config.grid_sizes as Record<string, number[]> | undefined;
    if (gridSizes && gridSizes[difficulty]) {
      return gridSizes[difficulty][0]; // [rows, cols] -> rows (kare grid)
    }
    return difficulty === 'easy' ? 2 : difficulty === 'hard' ? 4 : 3;
  }, [config, difficulty]);

  const createSolvedState = (size: number): number[] => {
    const total = size * size;
    // 1, 2, 3, ..., N-1, 0 (0 = bos karo)
    const arr = [];
    for (let i = 1; i < total; i++) arr.push(i);
    arr.push(0);
    return arr;
  };

  const shuffle = (solved: number[], size: number): number[] => {
    const arr = [...solved];
    let emptyIdx = arr.indexOf(0);
    const total = size * size;
    // Cozulebilir karistirma: gercek hamle simule et
    const shuffleCount = size === 2 ? 20 : size === 3 ? 100 : 200;

    for (let i = 0; i < shuffleCount; i++) {
      const neighbors = getNeighbors(emptyIdx, size);
      const randomNeighbor = neighbors[Math.floor(Math.random() * neighbors.length)];
      [arr[emptyIdx], arr[randomNeighbor]] = [arr[randomNeighbor], arr[emptyIdx]];
      emptyIdx = randomNeighbor;
    }

    // Cozulmus durumla ayni olmasindan kacin
    if (arr.every((v, i) => v === solved[i])) {
      // Son iki karo haric swap yap
      const idx1 = arr[0] === 0 ? 1 : 0;
      const idx2 = arr[1] === 0 ? 2 : 1;
      [arr[idx1], arr[idx2]] = [arr[idx2], arr[idx1]];
    }

    return arr;
  };

  const getNeighbors = (idx: number, size: number): number[] => {
    const row = Math.floor(idx / size);
    const col = idx % size;
    const neighbors: number[] = [];
    if (row > 0) neighbors.push((row - 1) * size + col);       // ust
    if (row < size - 1) neighbors.push((row + 1) * size + col); // alt
    if (col > 0) neighbors.push(row * size + (col - 1));       // sol
    if (col < size - 1) neighbors.push(row * size + (col + 1)); // sag
    return neighbors;
  };

  const isSolved = (arr: number[], size: number): boolean => {
    const solved = createSolvedState(size);
    return arr.every((v, i) => v === solved[i]);
  };

  const startGame = () => {
    const size = getGridSize();
    const solved = createSolvedState(size);
    const shuffled = shuffle(solved, size);
    setGridSize(size);
    setTiles(shuffled);
    setMoves(0);
    setStartTime(Date.now());
    setPhase('playing');
  };

  const handleTileClick = (idx: number) => {
    if (phase !== 'playing' || tiles[idx] === 0) return;

    const emptyIdx = tiles.indexOf(0);
    const neighbors = getNeighbors(emptyIdx, gridSize);

    if (!neighbors.includes(idx)) return;

    // Swap
    const newTiles = [...tiles];
    [newTiles[emptyIdx], newTiles[idx]] = [newTiles[idx], newTiles[emptyIdx]];
    setTiles(newTiles);
    setMoves((m) => m + 1);

    // Cozulmus mu kontrol
    if (isSolved(newTiles, gridSize)) {
      const totalMoves = moves + 1;
      const duration = Math.floor((Date.now() - startTime) / 1000);
      const optimal = OPTIMAL_MOVES[difficulty] || 30;
      // Skor: optimal'e ne kadar yakin
      const efficiency = Math.max(0, 1 - (totalMoves - optimal) / (optimal * 2));
      const finalScore = Math.round(efficiency * 100);
      const accuracy = Math.round(efficiency * 100);

      setPhase('complete');
      onComplete({
        score: Math.max(10, Math.min(finalScore, 100)),
        maxScore: 100,
        accuracy: Math.max(10, accuracy),
        duration,
        data: { moves: totalMoves, gridSize, optimal, difficulty },
      });
    }
  };

  // ---- READY ----
  if (phase === 'ready') {
    return (
      <div className="text-center">
        <div className="p-6 bg-purple-50 rounded-xl mb-4">
          <Grid3X3 className="w-12 h-12 text-purple-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Karo Bulmacasi</h3>
          <p className="text-sm text-gray-600 mb-4">
            Numarali karolari dogru siraya dizin. Bos alana komsu karolari tiklayarak kaydirin.
          </p>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition mx-auto"
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
    return (
      <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
        <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-gray-900 mb-2">Tebrikler!</h3>
        <p className="text-gray-600 mb-4">Bulmacayi basariyla cozdunuz!</p>
        <div className="grid grid-cols-2 gap-4 my-4">
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-purple-600">{moves}</p>
            <p className="text-xs text-gray-500">Hamle</p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-2xl font-bold text-green-600">
              {Math.floor((Date.now() - startTime) / 1000)}s
            </p>
            <p className="text-xs text-gray-500">Sure</p>
          </div>
        </div>
        <button
          onClick={() => setPhase('ready')}
          className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition mx-auto"
        >
          <RotateCcw className="w-4 h-4" />
          Tekrar Oyna
        </button>
      </div>
    );
  }

  // ---- PLAYING ----
  const emptyIdx = tiles.indexOf(0);
  const neighbors = getNeighbors(emptyIdx, gridSize);
  const tileSize = gridSize === 2 ? 'w-28 h-28 text-3xl' : gridSize === 3 ? 'w-20 h-20 text-2xl' : 'w-16 h-16 text-xl';

  return (
    <div>
      {/* Stats */}
      <div className="flex items-center justify-between mb-4 text-sm">
        <span className="text-gray-500">{gridSize}x{gridSize} Bulmaca</span>
        <span className="font-medium text-purple-600">Hamle: {moves}</span>
      </div>

      {/* Grid */}
      <div className="flex justify-center mb-6">
        <div
          className="grid gap-1.5"
          style={{
            gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
          }}
        >
          {tiles.map((tile, idx) => {
            const isMovable = neighbors.includes(idx) && tile !== 0;
            const isEmpty = tile === 0;

            return (
              <button
                key={idx}
                onClick={() => handleTileClick(idx)}
                disabled={!isMovable}
                className={`${tileSize} rounded-lg font-bold transition-all duration-150
                  ${isEmpty
                    ? 'bg-gray-100 border-2 border-dashed border-gray-300'
                    : isMovable
                    ? 'bg-purple-500 text-white border-2 border-purple-600 hover:bg-purple-600 cursor-pointer shadow-md hover:shadow-lg'
                    : 'bg-purple-200 text-purple-800 border-2 border-purple-300 cursor-default'
                  }`}
              >
                {isEmpty ? '' : tile}
              </button>
            );
          })}
        </div>
      </div>

      <p className="text-center text-xs text-gray-400">
        Bos alana komsu parlak karolari tiklayarak kaydirin
      </p>
    </div>
  );
}
