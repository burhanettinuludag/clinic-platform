'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Clock } from 'lucide-react';

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

const CARD_EMOJIS = [
  '🍎', '🍊', '🍋', '🍇', '🍓', '🍒', '🥝', '🍑',
  '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼',
  '⭐', '🌙', '☀️', '🌈', '❤️', '💎', '🎈', '🎁',
];

interface Card {
  id: number;
  emoji: string;
  isFlipped: boolean;
  isMatched: boolean;
}

export default function MemoryCardsGame({ config, difficulty, onComplete }: Props) {
  const [cards, setCards] = useState<Card[]>([]);
  const [flippedCards, setFlippedCards] = useState<number[]>([]);
  const [moves, setMoves] = useState(0);
  const [matches, setMatches] = useState(0);
  const [gameStarted, setGameStarted] = useState(false);
  const [gameComplete, setGameComplete] = useState(false);
  const [startTime, setStartTime] = useState<number>(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Get grid size based on difficulty
  const getGridSize = () => {
    const gridSizes = (config.grid_sizes as Record<string, number[]>) || {
      easy: [3, 4],
      medium: [4, 4],
      hard: [4, 5],
    };
    return gridSizes[difficulty] || [3, 4];
  };

  const [rows, cols] = getGridSize();
  const totalPairs = (rows * cols) / 2;

  // Initialize game
  const initGame = useCallback(() => {
    const pairCount = (rows * cols) / 2;
    const selectedEmojis = CARD_EMOJIS.slice(0, pairCount);
    const cardPairs = [...selectedEmojis, ...selectedEmojis];

    // Shuffle cards
    const shuffled = cardPairs
      .map((emoji, index) => ({
        id: index,
        emoji,
        isFlipped: false,
        isMatched: false,
      }))
      .sort(() => Math.random() - 0.5);

    setCards(shuffled);
    setFlippedCards([]);
    setMoves(0);
    setMatches(0);
    setGameComplete(false);
    setGameStarted(false);
    setElapsedTime(0);
  }, [rows, cols]);

  useEffect(() => {
    initGame();
  }, [initGame]);

  // Timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (gameStarted && !gameComplete) {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [gameStarted, gameComplete, startTime]);

  // Check for match
  useEffect(() => {
    if (flippedCards.length === 2) {
      const [first, second] = flippedCards;
      const firstCard = cards[first];
      const secondCard = cards[second];

      if (firstCard.emoji === secondCard.emoji) {
        // Match found
        setTimeout(() => {
          setCards((prev) =>
            prev.map((card, idx) =>
              idx === first || idx === second
                ? { ...card, isMatched: true }
                : card
            )
          );
          setMatches((prev) => prev + 1);
          setFlippedCards([]);
        }, 500);
      } else {
        // No match
        setTimeout(() => {
          setCards((prev) =>
            prev.map((card, idx) =>
              idx === first || idx === second
                ? { ...card, isFlipped: false }
                : card
            )
          );
          setFlippedCards([]);
        }, 1000);
      }
    }
  }, [flippedCards, cards]);

  // Check for game complete
  useEffect(() => {
    if (matches === totalPairs && matches > 0) {
      setGameComplete(true);
      const duration = Math.floor((Date.now() - startTime) / 1000);
      const maxMoves = totalPairs * 2; // Perfect game = 2 moves per pair
      const accuracy = Math.min(100, Math.round((maxMoves / moves) * 100));
      const score = Math.round(accuracy * (120 / Math.max(duration, 1)));

      onComplete({
        score: Math.min(score, 100),
        maxScore: 100,
        accuracy,
        duration,
        data: {
          moves,
          pairs: totalPairs,
          difficulty,
        },
      });
    }
  }, [matches, totalPairs, moves, startTime, difficulty, onComplete]);

  const handleCardClick = (index: number) => {
    // Start game on first click
    if (!gameStarted) {
      setGameStarted(true);
      setStartTime(Date.now());
    }

    // Ignore if already flipped, matched, or two cards are already flipped
    if (
      cards[index].isFlipped ||
      cards[index].isMatched ||
      flippedCards.length >= 2
    ) {
      return;
    }

    setCards((prev) =>
      prev.map((card, idx) =>
        idx === index ? { ...card, isFlipped: true } : card
      )
    );
    setFlippedCards((prev) => [...prev, index]);
    setMoves((prev) => prev + 1);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Instructions */}
      {!gameStarted && (
        <div className="text-center mb-6 p-4 bg-indigo-50 rounded-lg">
          <p className="text-indigo-800">
            Kartlara tıklayarak eşleşen çiftleri bulun. Tüm çiftleri bulmaya çalışın!
          </p>
        </div>
      )}

      {/* Stats */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-gray-600">
            <Clock className="w-4 h-4" />
            <span className="font-mono">{formatTime(elapsedTime)}</span>
          </div>
          <div className="text-gray-600">
            <span className="font-semibold">{moves}</span> hamle
          </div>
          <div className="text-gray-600">
            <span className="font-semibold text-green-600">{matches}</span>/{totalPairs} eşleşme
          </div>
        </div>
        <button
          onClick={initGame}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition"
        >
          <RotateCcw className="w-4 h-4" />
          Yeniden Başla
        </button>
      </div>

      {/* Game Board */}
      <div
        className="grid gap-2 mb-6"
        style={{
          gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
        }}
      >
        {cards.map((card, index) => (
          <button
            key={card.id}
            onClick={() => handleCardClick(index)}
            disabled={card.isMatched || gameComplete}
            className={`aspect-square rounded-xl text-3xl md:text-4xl flex items-center justify-center transition-all duration-300 transform ${
              card.isFlipped || card.isMatched
                ? 'bg-white border-2 border-indigo-200 rotate-0'
                : 'bg-indigo-600 hover:bg-indigo-700 rotate-y-180'
            } ${card.isMatched ? 'opacity-60 scale-95' : ''}`}
            style={{
              transformStyle: 'preserve-3d',
            }}
          >
            {(card.isFlipped || card.isMatched) && card.emoji}
          </button>
        ))}
      </div>

      {/* Game Complete */}
      {gameComplete && (
        <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
          <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Tebrikler!</h3>
          <p className="text-gray-600 mb-4">
            {totalPairs} çifti {moves} hamlede ve {formatTime(elapsedTime)} sürede buldunuz!
          </p>
          <button
            onClick={initGame}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Tekrar Oyna
          </button>
        </div>
      )}
    </div>
  );
}
