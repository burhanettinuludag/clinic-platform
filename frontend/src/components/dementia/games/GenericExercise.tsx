'use client';

import { useState } from 'react';
import { Play, CheckCircle, Trophy, RotateCcw } from 'lucide-react';

interface Props {
  exercise: {
    name: string;
    name_tr?: string;
    description?: string;
    instructions?: string;
    estimated_duration_minutes?: number;
    icon?: string;
  };
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

export default function GenericExercise({ exercise, config, difficulty, onComplete }: Props) {
  const [phase, setPhase] = useState<'ready' | 'playing' | 'complete'>('ready');
  const [startTime, setStartTime] = useState<number>(0);
  const [selfRating, setSelfRating] = useState<number>(3);

  const startExercise = () => {
    setPhase('playing');
    setStartTime(Date.now());
  };

  const completeExercise = () => {
    const duration = Math.floor((Date.now() - startTime) / 1000);
    setPhase('complete');

    // For generic exercises, we use self-rating as score
    onComplete({
      score: selfRating * 20, // Convert 1-5 to 20-100
      maxScore: 100,
      accuracy: selfRating * 20,
      duration,
      data: {
        selfRating,
        difficulty,
        exerciseType: 'guided',
      },
    });
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Ready Phase */}
      {phase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-purple-50 rounded-xl mb-4">
            <h3 className="font-semibold text-gray-900 mb-2">
              {exercise.name_tr || exercise.name}
            </h3>
            {exercise.description && (
              <p className="text-sm text-gray-600 mb-4">{exercise.description}</p>
            )}
            {exercise.instructions && (
              <div className="p-4 bg-white rounded-lg mb-4 text-left">
                <h4 className="font-medium text-gray-800 mb-2">Talimatlar:</h4>
                <p className="text-sm text-gray-600">{exercise.instructions}</p>
              </div>
            )}
            {exercise.estimated_duration_minutes && (
              <p className="text-xs text-gray-500 mb-4">
                Tahmini süre: {exercise.estimated_duration_minutes} dakika
              </p>
            )}
            <button
              onClick={startExercise}
              className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition mx-auto"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Playing Phase */}
      {phase === 'playing' && (
        <div className="text-center">
          <div className="p-6 bg-white rounded-xl border-2 border-purple-200 mb-4">
            <h3 className="font-semibold text-gray-900 mb-4">
              {exercise.name_tr || exercise.name}
            </h3>

            {exercise.instructions && (
              <div className="p-4 bg-purple-50 rounded-lg mb-6 text-left">
                <p className="text-sm text-gray-700">{exercise.instructions}</p>
              </div>
            )}

            <div className="my-8">
              <p className="text-gray-600 mb-4">
                Egzersizi talimatlar doğrultusunda tamamlayın.
                <br />
                Bitirdiğinizde aşağıdan değerlendirmenizi yapın.
              </p>

              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-3">
                  Egzersizi ne kadar iyi yaptığınızı değerlendirin:
                </p>
                <div className="flex justify-center gap-2">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => setSelfRating(rating)}
                      className={`w-12 h-12 rounded-full font-bold transition-all ${
                        selfRating === rating
                          ? 'bg-purple-600 text-white scale-110'
                          : 'bg-white border-2 border-gray-200 text-gray-600 hover:border-purple-400'
                      }`}
                    >
                      {rating}
                    </button>
                  ))}
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-2 px-2">
                  <span>Zor oldu</span>
                  <span>Çok kolaydı</span>
                </div>
              </div>
            </div>

            <button
              onClick={completeExercise}
              className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition mx-auto"
            >
              <CheckCircle className="w-5 h-5" />
              Tamamlandı
            </button>
          </div>
        </div>
      )}

      {/* Complete Phase */}
      {phase === 'complete' && (
        <div className="text-center p-6 bg-green-50 rounded-xl border-2 border-green-200">
          <Trophy className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Tebrikler!</h3>
          <p className="text-gray-600 mb-4">
            Egzersizi başarıyla tamamladınız.
          </p>
          <div className="text-sm text-gray-600 mb-4">
            Değerlendirmeniz: <span className="font-bold">{selfRating}/5</span>
          </div>
          <button
            onClick={() => {
              setPhase('ready');
              setSelfRating(3);
            }}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Yap
          </button>
        </div>
      )}
    </div>
  );
}
