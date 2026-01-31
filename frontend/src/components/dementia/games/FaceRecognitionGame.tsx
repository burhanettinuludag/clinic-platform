'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Users } from 'lucide-react';

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

// Yüz profilleri - Orijinal Türk isimleri ve karakteristik özellikleri
const FACE_PROFILES = [
  { id: 1, name: 'Ayşe Teyze', relation: 'Komşu', trait: 'Gözlüklü, kısa saçlı', emoji: '👵', color: 'bg-pink-100' },
  { id: 2, name: 'Ahmet Amca', relation: 'Aile dostu', trait: 'Bıyıklı, şapkalı', emoji: '👴', color: 'bg-blue-100' },
  { id: 3, name: 'Fatma Hanım', relation: 'Market sahibi', trait: 'Uzun saçlı, güler yüzlü', emoji: '👩', color: 'bg-yellow-100' },
  { id: 4, name: 'Mehmet Bey', relation: 'Eski iş arkadaşı', trait: 'Kel, sakallı', emoji: '👨', color: 'bg-green-100' },
  { id: 5, name: 'Zeynep', relation: 'Torunu', trait: 'Genç, örgülü saçlı', emoji: '👧', color: 'bg-purple-100' },
  { id: 6, name: 'Ali', relation: 'Oğlu', trait: 'Orta yaşlı, gözlüklü', emoji: '👨‍💼', color: 'bg-orange-100' },
  { id: 7, name: 'Emine Teyze', relation: 'Kuzen', trait: 'Başörtülü, neşeli', emoji: '🧕', color: 'bg-teal-100' },
  { id: 8, name: 'Hasan Dede', relation: 'Amca', trait: 'Yaşlı, beyaz saçlı', emoji: '👴🏻', color: 'bg-red-100' },
  { id: 9, name: 'Selin', relation: 'Hemşire', trait: 'Genç, beyaz önlüklü', emoji: '👩‍⚕️', color: 'bg-cyan-100' },
  { id: 10, name: 'Kemal Bey', relation: 'Doktor', trait: 'Orta yaşlı, ciddi', emoji: '👨‍⚕️', color: 'bg-indigo-100' },
];

interface FaceProfile {
  id: number;
  name: string;
  relation: string;
  trait: string;
  emoji: string;
  color: string;
}

interface Question {
  face: FaceProfile;
  questionType: 'name' | 'relation';
  options: string[];
  correctAnswer: string;
}

export default function FaceRecognitionGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'learn' | 'test' | 'complete'>('ready');
  const [faces, setFaces] = useState<FaceProfile[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [learnCountdown, setLearnCountdown] = useState(0);

  const faceCount = difficulty === 'easy' ? 4 : difficulty === 'medium' ? 6 : 8;
  const questionsPerFace = 2; // Her yüz için isim ve ilişki sorusu
  const totalQuestions = faceCount * questionsPerFace;
  const learnTimePerFace = 5; // Her yüz için 5 saniye öğrenme süresi

  // Oyunu hazırla
  const initGame = useCallback(() => {
    const shuffled = [...FACE_PROFILES].sort(() => Math.random() - 0.5);
    const selected = shuffled.slice(0, faceCount);
    setFaces(selected);
    setQuestionIndex(0);
    setScore(0);
    setFeedback(null);
    setSelectedAnswer(null);
  }, [faceCount]);

  useEffect(() => {
    initGame();
  }, [initGame]);

  // Oyunu başlat
  const startGame = () => {
    initGame();
    setGamePhase('learn');
    setLearnCountdown(faceCount * learnTimePerFace);
    setStartTime(Date.now());
  };

  // Öğrenme sayacı
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (gamePhase === 'learn' && learnCountdown > 0) {
      interval = setInterval(() => {
        setLearnCountdown((prev) => prev - 1);
      }, 1000);
    } else if (gamePhase === 'learn' && learnCountdown === 0) {
      setGamePhase('test');
      generateQuestion(0);
    }
    return () => clearInterval(interval);
  }, [gamePhase, learnCountdown]);

  // Soru oluştur
  const generateQuestion = useCallback((index: number) => {
    const faceIndex = Math.floor(index / questionsPerFace);
    const questionType = index % questionsPerFace === 0 ? 'name' : 'relation';
    const face = faces[faceIndex];

    if (!face) return;

    let correctAnswer: string;
    let allOptions: string[];

    if (questionType === 'name') {
      correctAnswer = face.name;
      allOptions = FACE_PROFILES.map(f => f.name);
    } else {
      correctAnswer = face.relation;
      allOptions = FACE_PROFILES.map(f => f.relation);
    }

    // Yanlış seçenekler
    const wrongOptions = allOptions
      .filter(opt => opt !== correctAnswer)
      .sort(() => Math.random() - 0.5)
      .slice(0, 3);

    const options = [correctAnswer, ...wrongOptions].sort(() => Math.random() - 0.5);

    setCurrentQuestion({
      face,
      questionType,
      options,
      correctAnswer,
    });
  }, [faces, questionsPerFace]);

  // Cevap kontrolü
  const handleAnswer = (answer: string) => {
    if (feedback || !currentQuestion) return;

    setSelectedAnswer(answer);
    const isCorrect = answer === currentQuestion.correctAnswer;

    if (isCorrect) {
      setScore((prev) => prev + 10);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    setTimeout(() => {
      const nextIndex = questionIndex + 1;
      if (nextIndex >= totalQuestions) {
        endGame();
      } else {
        setQuestionIndex(nextIndex);
        generateQuestion(nextIndex);
        setFeedback(null);
        setSelectedAnswer(null);
      }
    }, 1500);
  };

  // Oyunu bitir
  const endGame = () => {
    setGamePhase('complete');
    const duration = Math.floor((Date.now() - startTime) / 1000);
    const correctCount = Math.floor(score / 10);
    const accuracy = Math.round((correctCount / totalQuestions) * 100);

    onComplete({
      score,
      maxScore: totalQuestions * 10,
      accuracy,
      duration,
      data: {
        facesLearned: faceCount,
        totalQuestions,
        correctAnswers: correctCount,
        difficulty,
      },
    });
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Hazırlık */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-rose-50 rounded-xl mb-4">
            <Users className="w-12 h-12 text-rose-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Yüz Tanıma Testi</h3>
            <p className="text-sm text-gray-600 mb-4">
              Size {faceCount} kişi tanıtılacak.
              <br />
              İsimlerini ve kim olduklarını ezberleyin.
              <br />
              Sonra sorulara cevap verin.
            </p>
            <div className="p-4 bg-white rounded-lg mb-4">
              <div className="flex justify-center gap-2 mb-2">
                <span className="text-3xl">👵</span>
                <span className="text-3xl">👴</span>
                <span className="text-3xl">👩</span>
              </div>
              <p className="text-sm text-gray-500">Her kişiyi dikkatlice inceleyin</p>
            </div>
            <button
              onClick={startGame}
              className="flex items-center gap-2 px-6 py-3 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition mx-auto"
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
          <div className="flex items-center justify-center gap-2 mb-4 text-rose-600">
            <Users className="w-5 h-5" />
            <span className="font-medium">Kişileri Tanıyın</span>
          </div>

          <div className="text-3xl font-bold text-rose-600 mb-6">
            {learnCountdown}s
          </div>

          <div className="grid grid-cols-2 gap-3">
            {faces.map((face) => (
              <div
                key={face.id}
                className={`p-4 rounded-xl ${face.color} flex flex-col items-center`}
              >
                <span className="text-4xl mb-2">{face.emoji}</span>
                <p className="font-bold text-gray-900">{face.name}</p>
                <p className="text-sm text-gray-600">{face.relation}</p>
                <p className="text-xs text-gray-500 mt-1">{face.trait}</p>
              </div>
            ))}
          </div>

          <p className="text-sm text-gray-500 mt-6">
            Bu kişilerin isimlerini ve yakınlıklarını ezberleyin!
          </p>
        </div>
      )}

      {/* Test Aşaması */}
      {gamePhase === 'test' && currentQuestion && (
        <>
          {/* İstatistikler */}
          <div className="flex justify-between items-center mb-4 text-sm">
            <div className="text-gray-600">
              Soru: <span className="font-bold">{questionIndex + 1}/{totalQuestions}</span>
            </div>
            <div className="text-gray-600">
              Skor: <span className="font-bold">{score}</span>
            </div>
          </div>

          {/* İlerleme çubuğu */}
          <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
            <div
              className="h-full bg-rose-600 transition-all duration-300"
              style={{ width: `${((questionIndex + 1) / totalQuestions) * 100}%` }}
            />
          </div>

          {/* Soru */}
          <div className={`p-6 rounded-xl mb-6 text-center transition-colors ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : currentQuestion.face.color
          }`}>
            <span className="text-5xl mb-3 block">{currentQuestion.face.emoji}</span>
            <p className="text-sm text-gray-600 mb-2">
              {currentQuestion.questionType === 'name'
                ? 'Bu kişinin adı nedir?'
                : 'Bu kişi sizin neyiniz?'}
            </p>
            <p className="text-xs text-gray-500">{currentQuestion.face.trait}</p>
          </div>

          {/* Seçenekler */}
          <div className="grid grid-cols-2 gap-3">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                disabled={!!feedback}
                className={`py-4 px-3 rounded-xl font-medium transition-all ${
                  feedback
                    ? option === currentQuestion.correctAnswer
                      ? 'bg-green-500 text-white'
                      : selectedAnswer === option
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-400'
                    : 'bg-white border-2 border-gray-200 text-gray-900 hover:border-rose-400 hover:bg-rose-50'
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
            <p>Skor: <span className="font-bold">{score}</span>/{totalQuestions * 10}</p>
            <p>Doğru: <span className="font-bold text-green-600">{Math.floor(score / 10)}</span>/{totalQuestions}</p>
            <p>Doğruluk: <span className="font-bold">%{Math.round((score / (totalQuestions * 10)) * 100)}</span></p>
          </div>
          <button
            onClick={startGame}
            className="flex items-center gap-2 px-6 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            Tekrar Oyna
          </button>
        </div>
      )}
    </div>
  );
}
