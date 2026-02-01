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
    data?: Record<string, unknown>;
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
        {exercise.slug === 'memory-cards' && (
          <MemoryCardsGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'sequence-recall' && (
          <SequenceRecallGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'color-word' && (
          <ColorWordGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'simple-math' && (
          <SimpleMathGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'word-pairs' && (
          <WordPairsGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'pattern-recognition' && (
          <PatternRecognitionGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'category-sorting' && (
          <CategorySortingGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'face-recognition' && (
          <FaceRecognitionGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'real-face-recognition' && (
          <RealFaceRecognitionGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'virtual-home-navigation' && (
          <VirtualHomeNavigationGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'map-reading' && (
          <MapReadingGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'direction-following' && (
          <DirectionFollowingGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'spot-difference' && (
          <SpotDifferenceGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {exercise.slug === 'visual-search' && (
          <VisualSearchGame
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
        {!['memory-cards', 'sequence-recall', 'color-word', 'simple-math', 'word-pairs', 'pattern-recognition', 'category-sorting', 'face-recognition', 'real-face-recognition', 'virtual-home-navigation', 'map-reading', 'direction-following', 'spot-difference', 'visual-search'].includes(exercise.slug) && (
          <GenericExercise
            exercise={exercise}
            config={exercise.config}
            difficulty={exercise.difficulty}
            onComplete={handleComplete}
          />
        )}
      </div>
    </div>
  );
}
