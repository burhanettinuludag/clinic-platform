'use client';

import { useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { useCognitiveExercises, useCreateExerciseSession } from '@/hooks/useDementiaData';
import { ArrowLeft, Clock, Trophy, RotateCcw, Settings2, ChevronRight, Star, Target, Timer } from 'lucide-react';
import { Link } from '@/i18n/navigation';
import MemoryCardsGame from '@/components/dementia/games/MemoryCardsGame';
import SequenceRecallGame from '@/components/dementia/games/SequenceRecallGame';
import ColorWordGame from '@/components/dementia/games/ColorWordGame';
import SimpleMathGame from '@/components/dementia/games/SimpleMathGame';
import WordPairsGame from '@/components/dementia/games/WordPairsGame';
import PatternRecognitionGame from '@/components/dementia/games/PatternRecognitionGame';
import CategorySortingGame from '@/components/dementia/games/CategorySortingGame';
import FaceRecognitionGame from '@/components/dementia/games/FaceRecognitionGame';
import RealFaceRecognitionGame from '@/components/dementia/games/RealFaceRecognitionGame';
import VirtualHomeNavigationGame from '@/components/dementia/games/VirtualHomeNavigationGame';
import MapReadingGame from '@/components/dementia/games/MapReadingGame';
import DirectionFollowingGame from '@/components/dementia/games/DirectionFollowingGame';
import SpotDifferenceGame from '@/components/dementia/games/SpotDifferenceGame';
import VisualSearchGame from '@/components/dementia/games/VisualSearchGame';
import WordCompletionGame from '@/components/dementia/games/WordCompletionGame';
import WordAssociationGame from '@/components/dementia/games/WordAssociationGame';
import PuzzleArrangeGame from '@/components/dementia/games/PuzzleArrangeGame';
import DateTimeQuizGame from '@/components/dementia/games/DateTimeQuizGame';
import LocationQuizGame from '@/components/dementia/games/LocationQuizGame';
import GenericExercise from '@/components/dementia/games/GenericExercise';

type Difficulty = 'easy' | 'medium' | 'hard';
type Phase = 'setup' | 'playing' | 'results';

interface GameResult {
  score: number;
  maxScore: number;
  accuracy: number;
  duration: number;
  data?: Record<string, any>;
}

const difficultyConfig: Record<Difficulty, { label: string; color: string; bg: string; border: string; description: string }> = {
  easy: {
    label: 'Kolay',
    color: 'text-green-700',
    bg: 'bg-green-50',
    border: 'border-green-200',
    description: 'Daha az kart/soru, daha fazla süre',
  },
  medium: {
    label: 'Orta',
    color: 'text-yellow-700',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    description: 'Dengeli zorluk seviyesi',
  },
  hard: {
    label: 'Zor',
    color: 'text-red-700',
    bg: 'bg-red-50',
    border: 'border-red-200',
    description: 'Daha fazla kart/soru, daha kısa süre',
  },
};

// Map slugs (Turkish DB slugs + English fallback) to game components
const gameMap: Record<string, React.ComponentType<any>> = {
  'hafiza-kartlari': MemoryCardsGame,
  'memory-cards': MemoryCardsGame,
  'sira-hatirlama': SequenceRecallGame,
  'sequence-recall': SequenceRecallGame,
  'renk-kelime-testi': ColorWordGame,
  'color-word': ColorWordGame,
  'basit-matematik': SimpleMathGame,
  'simple-math': SimpleMathGame,
  'kelime-ciftleri': WordPairsGame,
  'word-pairs': WordPairsGame,
  'pattern-recognition': PatternRecognitionGame,
  'category-sorting': CategorySortingGame,
  'face-recognition': FaceRecognitionGame,
  'real-face-recognition': RealFaceRecognitionGame,
  'virtual-home-navigation': VirtualHomeNavigationGame,
  'harita-okuma': MapReadingGame,
  'map-reading': MapReadingGame,
  'direction-following': DirectionFollowingGame,
  'fark-bulma': SpotDifferenceGame,
  'spot-difference': SpotDifferenceGame,
  'gorsel-arama': VisualSearchGame,
  'visual-search': VisualSearchGame,
  'word-completion': WordCompletionGame,
  'word-association': WordAssociationGame,
  'puzzle-arrange': PuzzleArrangeGame,
  'date-time-quiz': DateTimeQuizGame,
  'location-quiz': LocationQuizGame,
  'problem-cozme': SimpleMathGame,
  'ileri-hesaplama': SimpleMathGame,
};

export default function ExercisePage() {
  const params = useParams();
  const slug = params.slug as string;

  const { data: exercises, isLoading } = useCognitiveExercises();
  const createSession = useCreateExerciseSession();

  const exercise = exercises?.find((e) => e.slug === slug);

  const [phase, setPhase] = useState<Phase>('setup');
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>((exercise?.difficulty as Difficulty) || 'easy');
  const [gameKey, setGameKey] = useState(0);
  const [lastResult, setLastResult] = useState<GameResult | null>(null);
  const [sessionCount, setSessionCount] = useState(0);

  const handleComplete = useCallback((result: GameResult) => {
    if (!exercise) return;
    setLastResult(result);
    setPhase('results');
    setSessionCount((c) => c + 1);

    createSession.mutate({
      exercise: exercise.id,
      completed_at: new Date().toISOString(),
      duration_seconds: result.duration,
      score: result.score,
      max_possible_score: result.maxScore,
      accuracy_percent: result.accuracy,
      results_data: { ...result.data, difficulty: selectedDifficulty, session_number: sessionCount + 1 },
    });
  }, [exercise, selectedDifficulty, sessionCount, createSession]);

  const handleStart = () => {
    setPhase('playing');
    setGameKey((k) => k + 1);
    setLastResult(null);
  };

  const handlePlayAgain = () => {
    setPhase('playing');
    setGameKey((k) => k + 1);
    setLastResult(null);
  };

  const handleChangeDifficulty = () => {
    setPhase('setup');
    setLastResult(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Yükleniyor...</div>
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <h1 className="text-xl font-bold text-gray-900 mb-2">Egzersiz Bulunamadi</h1>
        <p className="text-gray-500 mb-4">Bu egzersiz mevcut degil veya kaldirilmis olabilir.</p>
        <Link
          href="/patient/dementia"
          className="text-indigo-600 hover:text-indigo-700 flex items-center gap-2 justify-center"
        >
          <ArrowLeft className="w-4 h-4" />
          Egzersizlere Don
        </Link>
      </div>
    );
  }

  const renderGame = () => {
    const GameComponent = gameMap[exercise.slug];
    if (GameComponent) {
      return (
        <GameComponent
          key={gameKey}
          config={exercise.config}
          difficulty={selectedDifficulty}
          onComplete={handleComplete}
        />
      );
    }
    return (
      <GenericExercise
        key={gameKey}
        exercise={exercise}
        config={exercise.config}
        difficulty={selectedDifficulty}
        onComplete={handleComplete}
      />
    );
  };

  const scorePercent = lastResult ? Math.round((lastResult.score / lastResult.maxScore) * 100) : 0;
  const diffInfo = difficultyConfig[selectedDifficulty];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            href="/patient/dementia"
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-gray-900">{exercise.name}</h1>
            <div className="flex items-center gap-3 text-sm text-gray-500 mt-1">
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                ~{exercise.estimated_duration_minutes} dk
              </span>
              <span className={`px-2 py-0.5 rounded-full text-xs ${diffInfo.bg} ${diffInfo.color}`}>
                {diffInfo.label}
              </span>
              {sessionCount > 0 && (
                <span className="flex items-center gap-1 text-purple-600">
                  <Trophy className="w-4 h-4" />
                  {sessionCount} oturum
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Setup Phase - Difficulty Selection */}
      {phase === 'setup' && (
        <div className="bg-white rounded-xl border border-gray-200 p-8">
          <div className="max-w-lg mx-auto">
            <h2 className="text-lg font-semibold text-gray-900 text-center mb-2">{exercise.name}</h2>
            <p className="text-gray-500 text-center text-sm mb-6">
              {exercise.description || exercise.instructions}
            </p>

            {exercise.instructions && exercise.description && (
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-800 font-medium mb-1">Talimatlar:</p>
                <p className="text-sm text-blue-700">{exercise.instructions}</p>
              </div>
            )}

            {/* Difficulty Selection */}
            <div className="mb-6">
              <p className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                <Settings2 className="w-4 h-4" />
                Zorluk Seviyesi
              </p>
              <div className="grid grid-cols-3 gap-3">
                {(Object.entries(difficultyConfig) as [Difficulty, typeof difficultyConfig.easy][]).map(
                  ([key, config]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedDifficulty(key)}
                      className={`p-4 rounded-xl border-2 transition-all text-center ${
                        selectedDifficulty === key
                          ? `${config.border} ${config.bg} ring-2 ring-offset-1 ${config.border.replace('border-', 'ring-')}`
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <span className={`text-sm font-semibold ${selectedDifficulty === key ? config.color : 'text-gray-700'}`}>
                        {config.label}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">{config.description}</p>
                    </button>
                  )
                )}
              </div>
            </div>

            <p className="text-xs text-gray-400 text-center mb-4">
              Tahmini sure: ~{exercise.estimated_duration_minutes} dakika
            </p>

            <button
              onClick={handleStart}
              className="w-full py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition flex items-center justify-center gap-2"
            >
              Basla
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Playing Phase */}
      {phase === 'playing' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          {renderGame()}
        </div>
      )}

      {/* Results Phase */}
      {phase === 'results' && lastResult && (
        <div className="bg-white rounded-xl border border-gray-200 p-8">
          <div className="max-w-lg mx-auto text-center">
            {/* Score Circle */}
            <div className="relative w-32 h-32 mx-auto mb-6">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="52" stroke="#e5e7eb" strokeWidth="8" fill="none" />
                <circle
                  cx="60" cy="60" r="52"
                  stroke={scorePercent >= 70 ? '#10b981' : scorePercent >= 40 ? '#f59e0b' : '#ef4444'}
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${scorePercent * 3.27} 327`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-gray-900">{scorePercent}</span>
                <span className="text-xs text-gray-500">puan</span>
              </div>
            </div>

            <h2 className="text-xl font-bold text-gray-900 mb-1">
              {scorePercent >= 80 ? 'Harika!' : scorePercent >= 50 ? 'Iyi gidiyorsun!' : 'Pratik yapmaya devam!'}
            </h2>
            <p className="text-sm text-gray-500 mb-6">
              {exercise.name} - {diffInfo.label} seviye
            </p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="bg-gray-50 rounded-lg p-3">
                <Target className="w-5 h-5 text-blue-500 mx-auto mb-1" />
                <p className="text-lg font-bold text-gray-900">%{Math.round(lastResult.accuracy)}</p>
                <p className="text-xs text-gray-500">Dogruluk</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <Timer className="w-5 h-5 text-purple-500 mx-auto mb-1" />
                <p className="text-lg font-bold text-gray-900">
                  {lastResult.duration < 60
                    ? `${lastResult.duration}s`
                    : `${Math.floor(lastResult.duration / 60)}dk ${lastResult.duration % 60}s`}
                </p>
                <p className="text-xs text-gray-500">Sure</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <Star className="w-5 h-5 text-yellow-500 mx-auto mb-1" />
                <p className="text-lg font-bold text-gray-900">{lastResult.score}/{lastResult.maxScore}</p>
                <p className="text-xs text-gray-500">Skor</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handlePlayAgain}
                className="flex-1 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Tekrar Oyna
              </button>
              <button
                onClick={handleChangeDifficulty}
                className="flex-1 py-3 bg-white text-gray-700 border-2 border-gray-200 rounded-xl font-semibold hover:bg-gray-50 transition flex items-center justify-center gap-2"
              >
                <Settings2 className="w-4 h-4" />
                Zorluk Degistir
              </button>
            </div>

            <Link
              href="/patient/dementia?tab=progress"
              className="inline-block mt-4 text-sm text-gray-500 hover:text-gray-700 transition"
            >
              Ilerleme sayfasina don
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
