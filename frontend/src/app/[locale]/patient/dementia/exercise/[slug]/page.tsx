'use client';

import { useParams } from 'next/navigation';
import { useRouter } from '@/i18n/navigation';
import { useCognitiveExercises, useCreateExerciseSession } from '@/hooks/useDementiaData';
import { ArrowLeft, Clock, Trophy } from 'lucide-react';
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

export default function ExercisePage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const { data: exercises, isLoading } = useCognitiveExercises();
  const createSession = useCreateExerciseSession();

  const exercise = exercises?.find((e) => e.slug === slug);

  const handleComplete = (result: {
    score: number;
    maxScore: number;
    accuracy: number;
    duration: number;
    data?: Record<string, any>;
  }) => {
    if (!exercise) return;

    createSession.mutate(
      {
        exercise: exercise.id,
        completed_at: new Date().toISOString(),
        duration_seconds: result.duration,
        score: result.score,
        max_possible_score: result.maxScore,
        accuracy_percent: result.accuracy,
        results_data: result.data || {},
      },
      {
        onSuccess: () => {
          router.push('/patient/dementia?tab=progress');
        },
      }
    );
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

  const renderGame = () => {
    if (!exercise) return null;
    const GameComponent = gameMap[exercise.slug];
    if (GameComponent) {
      return (
        <GameComponent
          config={exercise.config}
          difficulty={exercise.difficulty}
          onComplete={handleComplete}
        />
      );
    }
    return (
      <GenericExercise
        exercise={exercise}
        config={exercise.config}
        difficulty={exercise.difficulty}
        onComplete={handleComplete}
      />
    );
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
        <h1 className="text-xl font-bold text-gray-900 mb-2">Egzersiz Bulunamadı</h1>
        <p className="text-gray-500 mb-4">Bu egzersiz mevcut değil veya kaldırılmış olabilir.</p>
        <Link
          href="/patient/dementia"
          className="text-indigo-600 hover:text-indigo-700 flex items-center gap-2 justify-center"
        >
          <ArrowLeft className="w-4 h-4" />
          Egzersizlere Dön
        </Link>
      </div>
    );
  }

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
              <span className={`px-2 py-0.5 rounded-full text-xs ${
                exercise.difficulty === 'easy'
                  ? 'bg-green-100 text-green-700'
                  : exercise.difficulty === 'medium'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-red-100 text-red-700'
              }`}>
                {exercise.difficulty_display}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Game Component */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {renderGame()}
      </div>
    </div>
  );
}
