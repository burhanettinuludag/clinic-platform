'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Folder, CheckCircle, XCircle } from 'lucide-react';

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

// Orijinal Türkçe kelime kategorileri
const CATEGORY_DATA: Record<string, string[]> = {
  'Hayvanlar': ['Kedi', 'Köpek', 'Kuş', 'Balık', 'At', 'İnek', 'Tavuk', 'Koyun'],
  'Meyveler': ['Elma', 'Armut', 'Üzüm', 'Portakal', 'Muz', 'Çilek', 'Kiraz', 'Karpuz'],
  'Renkler': ['Kırmızı', 'Mavi', 'Yeşil', 'Sarı', 'Turuncu', 'Mor', 'Pembe', 'Beyaz'],
  'Sebzeler': ['Domates', 'Biber', 'Salatalık', 'Havuç', 'Patlıcan', 'Kabak', 'Soğan', 'Patates'],
  'Meslekler': ['Doktor', 'Öğretmen', 'Mühendis', 'Aşçı', 'Pilot', 'Hemşire', 'Avukat', 'Polis'],
  'Eşyalar': ['Masa', 'Sandalye', 'Dolap', 'Yatak', 'Koltuk', 'Halı', 'Perde', 'Ayna'],
};

interface WordItem {
  word: string;
  category: string;
  sorted: boolean;
}

export default function CategorySortingGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [categories, setCategories] = useState<string[]>([]);
  const [words, setWords] = useState<WordItem[]>([]);
  const [currentWord, setCurrentWord] = useState<WordItem | null>(null);
  const [score, setScore] = useState(0);
  const [wrongAnswers, setWrongAnswers] = useState(0);
  const [feedback, setFeedback] = useState<{ type: 'correct' | 'wrong'; category: string } | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [sortedCount, setSortedCount] = useState(0);

  const wordsPerCategory = difficulty === 'easy' ? 3 : difficulty === 'medium' ? 4 : 5;
  const categoryCount = difficulty === 'easy' ? 2 : difficulty === 'medium' ? 3 : 4;

  // Oyunu hazırla
  const initGame = useCallback(() => {
    // Rastgele kategoriler seç
    const allCategories = Object.keys(CATEGORY_DATA);
    const selectedCategories = [...allCategories]
      .sort(() => Math.random() - 0.5)
      .slice(0, categoryCount);

    setCategories(selectedCategories);

    // Her kategoriden kelimeler seç
    const allWords: WordItem[] = [];
    selectedCategories.forEach((category) => {
      const categoryWords = [...CATEGORY_DATA[category]]
        .sort(() => Math.random() - 0.5)
        .slice(0, wordsPerCategory)
        .map((word) => ({ word, category, sorted: false }));
      allWords.push(...categoryWords);
    });

    // Kelimeleri karıştır
    const shuffledWords = allWords.sort(() => Math.random() - 0.5);
    setWords(shuffledWords);
    setCurrentWord(shuffledWords[0] || null);
    setSortedCount(0);
    setScore(0);
    setWrongAnswers(0);
    setFeedback(null);
  }, [categoryCount, wordsPerCategory]);

  useEffect(() => {
    initGame();
  }, [initGame]);

  // Oyunu başlat
  const startGame = () => {
    initGame();
    setGamePhase('playing');
    setStartTime(Date.now());
  };

  // Kategori seçimi
  const handleCategorySelect = (selectedCategory: string) => {
    if (feedback || !currentWord) return;

    const isCorrect = selectedCategory === currentWord.category;

    if (isCorrect) {
      setScore((prev) => prev + 10);
      setFeedback({ type: 'correct', category: selectedCategory });
    } else {
      setWrongAnswers((prev) => prev + 1);
      setFeedback({ type: 'wrong', category: selectedCategory });
    }

    setTimeout(() => {
      const newSortedCount = sortedCount + 1;
      setSortedCount(newSortedCount);

      // Bir sonraki kelimeye geç
      const remainingWords = words.filter((w, idx) => idx > sortedCount);
      if (remainingWords.length > 0) {
        setCurrentWord(remainingWords[0]);
        setFeedback(null);
      } else {
        endGame();
      }
    }, 1000);
  };

  // Oyunu bitir
  const endGame = () => {
    setGamePhase('complete');
    const duration = Math.floor((Date.now() - startTime) / 1000);
    const totalWords = words.length;
    const correctAnswers = Math.floor(score / 10);
    const accuracy = Math.round((correctAnswers / totalWords) * 100);

    onComplete({
      score,
      maxScore: totalWords * 10,
      accuracy,
      duration,
      data: {
        totalWords,
        correctAnswers,
        wrongAnswers,
        categories: categories.length,
        difficulty,
      },
    });
  };

  const totalWords = words.length;
  const progress = totalWords > 0 ? (sortedCount / totalWords) * 100 : 0;

  return (
    <div className="max-w-lg mx-auto">
      {/* Hazır */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-teal-50 rounded-xl mb-4">
            <Folder className="w-12 h-12 text-teal-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Kategori Sınıflandırma</h3>
            <p className="text-sm text-gray-600 mb-4">
              Kelimeleri doğru kategorilere yerleştirin.
              <br />
              Her doğru cevap 10 puan kazandırır.
            </p>
            <div className="p-4 bg-white rounded-lg mb-4 text-center">
              <p className="text-sm text-gray-500 mb-2">Örnek:</p>
              <p className="font-medium text-lg mb-2">&quot;Elma&quot;</p>
              <p className="text-sm text-gray-600">→ Meyveler kategorisine ait</p>
            </div>
            <button
              onClick={startGame}
              className="flex items-center gap-2 px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition mx-auto"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Oyun */}
      {gamePhase === 'playing' && currentWord && (
        <>
          {/* İstatistikler */}
          <div className="flex justify-between items-center mb-4 text-sm">
            <div className="text-gray-600">
              Kelime: <span className="font-bold">{sortedCount + 1}/{totalWords}</span>
            </div>
            <div className="text-gray-600">
              Skor: <span className="font-bold">{score}</span>
            </div>
            <div className="text-gray-600">
              Doğru: <span className="font-bold text-green-600">{Math.floor(score / 10)}</span>
            </div>
          </div>

          {/* İlerleme çubuğu */}
          <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
            <div
              className="h-full bg-teal-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Mevcut kelime */}
          <div className={`p-8 rounded-xl mb-6 text-center transition-colors ${
            feedback?.type === 'correct'
              ? 'bg-green-100'
              : feedback?.type === 'wrong'
              ? 'bg-red-100'
              : 'bg-teal-50'
          }`}>
            <p className="text-sm text-gray-500 mb-2">Bu kelime hangi kategoriye ait?</p>
            <p className="text-3xl font-bold text-gray-900">{currentWord.word}</p>
          </div>

          {/* Kategoriler */}
          <div className="grid grid-cols-2 gap-3">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => handleCategorySelect(category)}
                disabled={!!feedback}
                className={`py-4 px-3 rounded-xl font-medium text-lg transition-all flex items-center justify-center gap-2 ${
                  feedback
                    ? category === currentWord.category
                      ? 'bg-green-500 text-white'
                      : feedback.category === category
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-400'
                    : 'bg-white border-2 border-gray-200 text-gray-900 hover:border-teal-400 hover:bg-teal-50'
                } ${feedback ? 'cursor-not-allowed' : ''}`}
              >
                {feedback && category === currentWord.category && (
                  <CheckCircle className="w-5 h-5" />
                )}
                {feedback && feedback.category === category && feedback.type === 'wrong' && (
                  <XCircle className="w-5 h-5" />
                )}
                {category}
              </button>
            ))}
          </div>

          {/* Geri bildirim */}
          {feedback && (
            <div className={`mt-4 text-center p-3 rounded-lg ${
              feedback.type === 'correct' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {feedback.type === 'correct'
                ? '✓ Doğru! +10 puan'
                : `✗ Yanlış! Doğru kategori: ${currentWord.category}`}
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
            <p>Skor: <span className="font-bold">{score}</span>/{totalWords * 10}</p>
            <p>Doğru: <span className="font-bold text-green-600">{Math.floor(score / 10)}</span>/{totalWords}</p>
            <p>Doğruluk: <span className="font-bold">%{Math.round((score / (totalWords * 10)) * 100)}</span></p>
          </div>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Oyna
          </button>
        </div>
      )}
    </div>
  );
}
