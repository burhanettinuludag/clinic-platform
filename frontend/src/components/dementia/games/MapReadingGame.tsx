'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Map, Navigation } from 'lucide-react';

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

// Mahalle haritası noktaları
const LANDMARKS = [
  { id: 'ev', name: 'Ev', x: 1, y: 1, color: 'bg-blue-100', icon: '🏠', type: 'home' },
  { id: 'market', name: 'Market', x: 3, y: 0, color: 'bg-green-100', icon: '🛒', type: 'shop' },
  { id: 'eczane', name: 'Eczane', x: 0, y: 2, color: 'bg-red-100', icon: '💊', type: 'health' },
  { id: 'park', name: 'Park', x: 2, y: 2, color: 'bg-emerald-100', icon: '🌳', type: 'leisure' },
  { id: 'cami', name: 'Cami', x: 4, y: 1, color: 'bg-amber-100', icon: '🕌', type: 'religious' },
  { id: 'okul', name: 'Okul', x: 1, y: 3, color: 'bg-yellow-100', icon: '🏫', type: 'education' },
  { id: 'hastane', name: 'Hastane', x: 4, y: 3, color: 'bg-rose-100', icon: '🏥', type: 'health' },
  { id: 'postane', name: 'Postane', x: 0, y: 0, color: 'bg-orange-100', icon: '📮', type: 'service' },
  { id: 'banka', name: 'Banka', x: 3, y: 2, color: 'bg-purple-100', icon: '🏦', type: 'service' },
  { id: 'firın', name: 'Fırın', x: 2, y: 0, color: 'bg-orange-50', icon: '🥖', type: 'shop' },
];

// Yollar (hangi noktalar birbirine bağlı)
const ROADS: Record<string, string[]> = {
  'ev': ['market', 'park', 'eczane', 'firın'],
  'market': ['ev', 'cami', 'firın', 'banka'],
  'eczane': ['ev', 'postane', 'okul'],
  'park': ['ev', 'banka', 'okul'],
  'cami': ['market', 'hastane', 'banka'],
  'okul': ['eczane', 'park', 'hastane'],
  'hastane': ['cami', 'okul', 'banka'],
  'postane': ['eczane', 'firın'],
  'banka': ['market', 'park', 'cami', 'hastane'],
  'firın': ['postane', 'ev', 'market'],
};

// Yön hesapla
function getDirection(from: typeof LANDMARKS[0], to: typeof LANDMARKS[0]): string {
  const dx = to.x - from.x;
  const dy = to.y - from.y;

  // 8 yön desteği
  if (dx === 0 && dy < 0) return 'kuzeye';
  if (dx === 0 && dy > 0) return 'güneye';
  if (dx > 0 && dy === 0) return 'doğuya';
  if (dx < 0 && dy === 0) return 'batıya';
  if (dx > 0 && dy < 0) return 'kuzeydoğuya';
  if (dx < 0 && dy < 0) return 'kuzeybatıya';
  if (dx > 0 && dy > 0) return 'güneydoğuya';
  if (dx < 0 && dy > 0) return 'güneybatıya';
  return '';
}

// BFS ile en kısa yol
function findPath(startId: string, endId: string): string[] {
  const visited = new Set<string>();
  const queue: { id: string; path: string[] }[] = [{ id: startId, path: [startId] }];

  while (queue.length > 0) {
    const { id, path } = queue.shift()!;

    if (id === endId) return path;

    if (visited.has(id)) continue;
    visited.add(id);

    for (const neighbor of ROADS[id] || []) {
      if (!visited.has(neighbor)) {
        queue.push({ id: neighbor, path: [...path, neighbor] });
      }
    }
  }

  return [];
}

interface Question {
  type: 'direction' | 'path' | 'landmark';
  fromLandmark: typeof LANDMARKS[0];
  toLandmark: typeof LANDMARKS[0];
  correctAnswer: string;
  options: string[];
  questionText: string;
}

export default function MapReadingGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'learn' | 'playing' | 'complete'>('ready');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [learnCountdown, setLearnCountdown] = useState(0);
  const [highlightedPath, setHighlightedPath] = useState<string[]>([]);

  const totalRounds = difficulty === 'easy' ? 6 : difficulty === 'medium' ? 8 : 12;
  const learnTime = difficulty === 'easy' ? 45 : difficulty === 'medium' ? 30 : 20;

  // Soru oluştur
  const generateQuestion = useCallback((): Question => {
    const questionTypes: ('direction' | 'path' | 'landmark')[] =
      difficulty === 'easy' ? ['direction', 'landmark'] : ['direction', 'path', 'landmark'];
    const type = questionTypes[Math.floor(Math.random() * questionTypes.length)];

    const fromIdx = Math.floor(Math.random() * LANDMARKS.length);
    const fromLandmark = LANDMARKS[fromIdx];

    let toLandmark: typeof LANDMARKS[0];
    do {
      const toIdx = Math.floor(Math.random() * LANDMARKS.length);
      toLandmark = LANDMARKS[toIdx];
    } while (fromLandmark.id === toLandmark.id);

    let correctAnswer: string;
    let options: string[];
    let questionText: string;

    if (type === 'direction') {
      // Yön sorusu
      correctAnswer = getDirection(fromLandmark, toLandmark);
      const allDirections = ['kuzeye', 'güneye', 'doğuya', 'batıya', 'kuzeydoğuya', 'kuzeybatıya', 'güneydoğuya', 'güneybatıya'];
      const wrongOptions = allDirections.filter(d => d !== correctAnswer).sort(() => Math.random() - 0.5).slice(0, 3);
      options = [correctAnswer, ...wrongOptions].sort(() => Math.random() - 0.5);
      questionText = `${fromLandmark.name}'dan ${toLandmark.name}'a gitmek için hangi yöne gitmelisiniz?`;
    } else if (type === 'path') {
      // Yol sorusu
      const path = findPath(fromLandmark.id, toLandmark.id);
      if (path.length > 2) {
        const middleLandmark = LANDMARKS.find(l => l.id === path[1])!;
        correctAnswer = middleLandmark.name;
        const wrongOptions = LANDMARKS
          .filter(l => l.id !== path[1] && l.id !== fromLandmark.id && l.id !== toLandmark.id)
          .map(l => l.name)
          .sort(() => Math.random() - 0.5)
          .slice(0, 3);
        options = [correctAnswer, ...wrongOptions].sort(() => Math.random() - 0.5);
        questionText = `${fromLandmark.name}'dan ${toLandmark.name}'a giderken ilk uğrayacağınız yer neresi?`;
      } else {
        // Direkt bağlantı varsa yön sorusu yap
        correctAnswer = getDirection(fromLandmark, toLandmark);
        const allDirections = ['kuzeye', 'güneye', 'doğuya', 'batıya'];
        const wrongOptions = allDirections.filter(d => d !== correctAnswer).slice(0, 3);
        options = [correctAnswer, ...wrongOptions].sort(() => Math.random() - 0.5);
        questionText = `${fromLandmark.name}'dan ${toLandmark.name}'a hangi yönde?`;
      }
    } else {
      // Landmark sorusu
      const nearbyLandmarks = ROADS[fromLandmark.id] || [];
      if (nearbyLandmarks.length > 0) {
        const nearbyId = nearbyLandmarks[Math.floor(Math.random() * nearbyLandmarks.length)];
        const nearbyLandmark = LANDMARKS.find(l => l.id === nearbyId)!;
        correctAnswer = nearbyLandmark.name;
        const wrongOptions = LANDMARKS
          .filter(l => !nearbyLandmarks.includes(l.id) && l.id !== fromLandmark.id)
          .map(l => l.name)
          .sort(() => Math.random() - 0.5)
          .slice(0, 3);
        options = [correctAnswer, ...wrongOptions].sort(() => Math.random() - 0.5);
        questionText = `${fromLandmark.name}'ın yanında hangi yer var?`;
        return { type, fromLandmark, toLandmark: nearbyLandmark, correctAnswer, options, questionText };
      } else {
        // Fallback to direction
        correctAnswer = getDirection(fromLandmark, toLandmark);
        const allDirections = ['kuzeye', 'güneye', 'doğuya', 'batıya'];
        const wrongOptions = allDirections.filter(d => d !== correctAnswer).slice(0, 3);
        options = [correctAnswer, ...wrongOptions].sort(() => Math.random() - 0.5);
        questionText = `${fromLandmark.name}'dan ${toLandmark.name}'a hangi yönde?`;
      }
    }

    return { type, fromLandmark, toLandmark, correctAnswer, options, questionText };
  }, [difficulty]);

  // Oyunu başlat
  const startGame = () => {
    setGamePhase('learn');
    setLearnCountdown(learnTime);
  };

  // Teste başla
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

  // Cevap kontrolü
  const handleAnswer = (answer: string) => {
    if (feedback || !currentQuestion) return;

    setSelectedOption(answer);
    const isCorrect = answer === currentQuestion.correctAnswer;

    if (isCorrect) {
      setScore((prev) => prev + 10);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    // Doğru yolu göster
    if (currentQuestion.type === 'path') {
      const path = findPath(currentQuestion.fromLandmark.id, currentQuestion.toLandmark.id);
      setHighlightedPath(path);
    } else {
      setHighlightedPath([currentQuestion.fromLandmark.id, currentQuestion.toLandmark.id]);
    }

    setTimeout(() => {
      setHighlightedPath([]);
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
        gameType: 'map-reading',
      },
    });
  };

  // Harita render
  const renderMap = () => (
    <div className="relative bg-gray-100 p-3 rounded-xl border-2 border-gray-300">
      {/* Pusula */}
      <div className="absolute top-2 right-2 bg-white rounded-full p-2 shadow-md text-xs">
        <div className="text-center font-bold text-gray-600">K</div>
        <div className="flex justify-between">
          <span className="text-gray-400">B</span>
          <span className="mx-2">⬆️</span>
          <span className="text-gray-400">D</span>
        </div>
        <div className="text-center text-gray-400">G</div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-5 gap-2" style={{ minHeight: '280px' }}>
        {Array.from({ length: 20 }).map((_, idx) => {
          const x = idx % 5;
          const y = Math.floor(idx / 5);
          const landmark = LANDMARKS.find(l => l.x === x && l.y === y);

          if (!landmark) {
            // Yol göster
            return (
              <div key={idx} className="bg-gray-200 rounded flex items-center justify-center">
                <div className="w-full h-0.5 bg-gray-300" />
              </div>
            );
          }

          const isHighlighted = highlightedPath.includes(landmark.id);
          const isFrom = currentQuestion?.fromLandmark.id === landmark.id;
          const isTo = currentQuestion?.toLandmark.id === landmark.id;

          return (
            <div
              key={idx}
              className={`
                ${landmark.color} rounded-lg p-2 flex flex-col items-center justify-center
                transition-all duration-300 border-2
                ${isHighlighted ? 'ring-2 ring-blue-400 scale-105' : ''}
                ${isFrom ? 'border-green-500 ring-2 ring-green-300' : ''}
                ${isTo ? 'border-red-500 ring-2 ring-red-300' : 'border-transparent'}
              `}
            >
              <span className="text-2xl">{landmark.icon}</span>
              <span className="text-xs font-medium text-gray-700 mt-1 text-center leading-tight">
                {landmark.name}
              </span>
            </div>
          );
        })}
      </div>

      {/* Yol çizgileri - basitleştirilmiş */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Yatay ve dikey yollar burada SVG ile çizilebilir */}
      </div>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto">
      {/* Hazırlık */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-blue-50 rounded-xl mb-4">
            <Map className="w-12 h-12 text-blue-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Harita Okuma Testi</h3>
            <p className="text-sm text-gray-600 mb-4">
              Mahalle haritasını inceleyeceksiniz.
              <br />
              Sonra yön ve konum sorularına cevap vereceksiniz.
            </p>

            {renderMap()}

            <button
              onClick={startGame}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition mx-auto mt-4"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Öğrenme */}
      {gamePhase === 'learn' && (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2 text-blue-600">
            <Map className="w-5 h-5" />
            <span className="font-medium">Haritayı İnceleyin</span>
          </div>

          <div className="text-3xl font-bold text-blue-600 mb-4">
            {learnCountdown}s
          </div>

          {renderMap()}

          <p className="text-sm text-gray-500 mt-4 mb-4">
            Yerlerin konumlarını ve birbirine olan yönlerini ezberleyin!
          </p>

          <button
            onClick={startTest}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
          >
            Hazırım, Teste Başla
          </button>
        </div>
      )}

      {/* Test */}
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
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${(round / totalRounds) * 100}%` }}
            />
          </div>

          {/* Harita */}
          <div className="mb-4">
            {renderMap()}
          </div>

          {/* Soru */}
          <div className={`p-4 rounded-xl mb-4 text-center transition-colors ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : 'bg-blue-100'
          }`}>
            <Navigation className="w-6 h-6 text-blue-600 mx-auto mb-2" />
            <p className="text-gray-800 font-medium">
              {currentQuestion.questionText}
            </p>
          </div>

          {/* Seçenekler */}
          <div className="grid grid-cols-2 gap-2">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                disabled={!!feedback}
                className={`py-3 px-4 rounded-xl font-medium transition-all text-sm ${
                  feedback
                    ? option === currentQuestion.correctAnswer
                      ? 'bg-green-500 text-white'
                      : selectedOption === option
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-400'
                    : 'bg-white border-2 border-gray-200 text-gray-900 hover:border-blue-400 hover:bg-blue-50'
                } ${feedback ? 'cursor-not-allowed' : ''}`}
              >
                {option}
              </button>
            ))}
          </div>

          {/* Geri bildirim */}
          {feedback && (
            <div className={`mt-4 text-center p-3 rounded-lg ${
              feedback === 'correct' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {feedback === 'correct'
                ? '✓ Doğru! +10 puan'
                : `✗ Yanlış! Doğru cevap: ${currentQuestion.correctAnswer}`}
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
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Oyna
          </button>
        </div>
      )}
    </div>
  );
}
