'use client';

import { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Trophy, Play, Users, Loader2, AlertCircle } from 'lucide-react';
import Image from 'next/image';

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

// Türk isimleri ve meslekler
const TURKISH_FIRST_NAMES_FEMALE = [
  'Ayşe', 'Fatma', 'Zeynep', 'Elif', 'Emine', 'Hatice', 'Merve', 'Esra', 'Özlem', 'Seda',
  'Derya', 'Sibel', 'Aslı', 'Gül', 'Yasemin', 'Canan', 'Sevgi', 'Hülya', 'Pınar', 'Deniz'
];

const TURKISH_FIRST_NAMES_MALE = [
  'Mehmet', 'Ahmet', 'Ali', 'Mustafa', 'Hasan', 'Hüseyin', 'İbrahim', 'Osman', 'Yusuf', 'Murat',
  'Kemal', 'Emre', 'Can', 'Burak', 'Serkan', 'Tolga', 'Baran', 'Cem', 'Kaan', 'Efe'
];

const TURKISH_LAST_NAMES = [
  'Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Yıldız', 'Aydın', 'Özdemir', 'Arslan', 'Doğan',
  'Kılıç', 'Aslan', 'Çetin', 'Kara', 'Koç', 'Kurt', 'Özkan', 'Şimşek', 'Polat', 'Erdoğan'
];

// İlişki bilgisi kaldırıldı - sadece isim hatırlama testi

interface FaceProfile {
  id: number;
  name: string;
  imageUrl: string;
  gender: 'male' | 'female';
}

interface Question {
  face: FaceProfile;
  options: string[];
  correctAnswer: string;
}

// Rastgele isim oluştur
function generateRandomName(gender: 'male' | 'female'): string {
  const firstNames = gender === 'female' ? TURKISH_FIRST_NAMES_FEMALE : TURKISH_FIRST_NAMES_MALE;
  const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const lastName = TURKISH_LAST_NAMES[Math.floor(Math.random() * TURKISH_LAST_NAMES.length)];
  return `${firstName} ${lastName}`;
}

export default function RealFaceRecognitionGame({ config, difficulty, onComplete }: Props) {
  const [gamePhase, setGamePhase] = useState<'ready' | 'loading' | 'learn' | 'test' | 'complete'>('ready');
  const [faces, setFaces] = useState<FaceProfile[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [learnCountdown, setLearnCountdown] = useState(0);
  const [loadingError, setLoadingError] = useState<string | null>(null);
  const [currentLearnIndex, setCurrentLearnIndex] = useState(0);

  const faceCount = difficulty === 'easy' ? 4 : difficulty === 'medium' ? 6 : 8;
  const totalQuestions = faceCount; // Her yüz için 1 isim sorusu
  const learnTimePerFace = 8; // Her yüz için 8 saniye öğrenme süresi

  // Yüzleri API'den yükle - farklı yaş gruplarından
  const loadFaces = async () => {
    setGamePhase('loading');
    setLoadingError(null);

    try {
      // Farklı yaş gruplarından kişiler almak için birden fazla istek yapıyoruz
      // Genç (20-35), Orta yaş (36-55), Yaşlı (56-75)
      const youngCount = Math.ceil(faceCount / 3);
      const middleCount = Math.ceil(faceCount / 3);
      const seniorCount = faceCount - youngCount - middleCount;

      // Paralel istekler - Kafkas/Beyaz ırk tipi ülkeler
      const nationalities = 'de,fr,es,it,nl,ch,gb';

      const [youngResponse, middleResponse, seniorResponse] = await Promise.all([
        // Gençler için daha fazla sonuç alıp filtreleyeceğiz
        fetch(`https://randomuser.me/api/?results=${youngCount * 3}&nat=${nationalities}`),
        fetch(`https://randomuser.me/api/?results=${middleCount * 3}&nat=${nationalities}`),
        fetch(`https://randomuser.me/api/?results=${seniorCount * 3}&nat=${nationalities}`),
      ]);

      if (!youngResponse.ok || !middleResponse.ok || !seniorResponse.ok) {
        throw new Error('Fotoğraflar yüklenemedi');
      }

      const [youngData, middleData, seniorData] = await Promise.all([
        youngResponse.json(),
        middleResponse.json(),
        seniorResponse.json(),
      ]);

      // Yaşa göre filtrele
      const filterByAge = (results: any[], minAge: number, maxAge: number, count: number) => {
        return results
          .filter((user: any) => user.dob.age >= minAge && user.dob.age <= maxAge)
          .slice(0, count);
      };

      const youngPeople = filterByAge(youngData.results, 20, 35, youngCount);
      const middlePeople = filterByAge(middleData.results, 36, 55, middleCount);
      const seniorPeople = filterByAge(seniorData.results, 56, 80, seniorCount);

      // Eğer yeterli kişi bulunamazsa, kalan sonuçlardan tamamla
      let allPeople = [...youngPeople, ...middlePeople, ...seniorPeople];

      // Eksik kalan varsa rastgele ekle
      if (allPeople.length < faceCount) {
        const remaining = [...youngData.results, ...middleData.results, ...seniorData.results]
          .filter((p: any) => !allPeople.includes(p))
          .slice(0, faceCount - allPeople.length);
        allPeople = [...allPeople, ...remaining];
      }

      // Karıştır
      allPeople = allPeople.sort(() => Math.random() - 0.5).slice(0, faceCount);

      const loadedFaces: FaceProfile[] = allPeople.map((user: {
        gender: string;
        picture: { large: string };
        dob: { age: number };
      }, index: number) => {
        const gender = user.gender as 'male' | 'female';

        return {
          id: index + 1,
          name: generateRandomName(gender),
          imageUrl: user.picture.large,
          gender,
        };
      });

      setFaces(loadedFaces);
      setGamePhase('learn');
      setLearnCountdown(faceCount * learnTimePerFace);
      setCurrentLearnIndex(0);
      setStartTime(Date.now());
    } catch {
      setLoadingError('Fotoğraflar yüklenirken bir hata oluştu. Lütfen tekrar deneyin.');
      setGamePhase('ready');
    }
  };

  // Öğrenme sayacı
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (gamePhase === 'learn' && learnCountdown > 0) {
      interval = setInterval(() => {
        setLearnCountdown((prev) => {
          const newValue = prev - 1;
          // Her yüz için belirlenen süre geçtikçe sonraki yüze geç
          const elapsedTime = faceCount * learnTimePerFace - newValue;
          const newIndex = Math.min(Math.floor(elapsedTime / learnTimePerFace), faceCount - 1);
          setCurrentLearnIndex(newIndex);
          return newValue;
        });
      }, 1000);
    } else if (gamePhase === 'learn' && learnCountdown === 0) {
      setGamePhase('test');
      generateQuestion(0);
    }
    return () => clearInterval(interval);
  }, [gamePhase, learnCountdown, faceCount, learnTimePerFace]);

  // Soru oluştur - sadece isim sorusu
  const generateQuestion = useCallback((index: number) => {
    const face = faces[index];

    if (!face) return;

    const correctAnswer = face.name;

    // Diğer yüzlerden isimler + rastgele isimler
    let allOptions = faces.map(f => f.name);

    // Eğer yeterli farklı seçenek yoksa rastgele isim ekle
    while (allOptions.length < 8) {
      const randomName = generateRandomName(Math.random() > 0.5 ? 'male' : 'female');
      if (!allOptions.includes(randomName)) {
        allOptions.push(randomName);
      }
    }

    // Yanlış seçenekler
    const wrongOptions = allOptions
      .filter(opt => opt !== correctAnswer)
      .sort(() => Math.random() - 0.5)
      .slice(0, 3);

    const options = [correctAnswer, ...wrongOptions].sort(() => Math.random() - 0.5);

    setCurrentQuestion({
      face,
      options,
      correctAnswer,
    });
  }, [faces]);

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
        gameType: 'real-face-recognition',
      },
    });
  };

  // Oyunu sıfırla
  const resetGame = () => {
    setFaces([]);
    setCurrentQuestion(null);
    setQuestionIndex(0);
    setScore(0);
    setFeedback(null);
    setSelectedAnswer(null);
    setCurrentLearnIndex(0);
    setLoadingError(null);
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Hazırlık */}
      {gamePhase === 'ready' && (
        <div className="text-center">
          <div className="p-6 bg-indigo-50 rounded-xl mb-4">
            <Users className="w-12 h-12 text-indigo-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Yüz Tanıma Testi</h3>
            <p className="text-sm text-gray-600 mb-4">
              Size {faceCount} kişi tanıtılacak.
              <br />
              Her kişinin yüzünü ve ismini ezberleyin.
              <br />
              Sonra isimlerini hatırlamaya çalışın.
            </p>
            <div className="p-4 bg-white rounded-lg mb-4">
              <div className="flex justify-center gap-3 mb-2">
                <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                  <Users className="w-8 h-8 text-gray-400" />
                </div>
                <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                  <Users className="w-8 h-8 text-gray-400" />
                </div>
                <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                  <Users className="w-8 h-8 text-gray-400" />
                </div>
              </div>
              <p className="text-sm text-gray-500">Gerçek yüz fotoğrafları ile test</p>
            </div>

            {loadingError && (
              <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded-lg mb-4 text-sm">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{loadingError}</span>
              </div>
            )}

            <button
              onClick={loadFaces}
              className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition mx-auto"
            >
              <Play className="w-5 h-5" />
              Başla
            </button>
          </div>
        </div>
      )}

      {/* Yükleniyor */}
      {gamePhase === 'loading' && (
        <div className="text-center py-12">
          <Loader2 className="w-12 h-12 text-indigo-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">Yüzler yükleniyor...</p>
        </div>
      )}

      {/* Öğrenme Aşaması */}
      {gamePhase === 'learn' && faces.length > 0 && (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2 text-indigo-600">
            <Users className="w-5 h-5" />
            <span className="font-medium">Kişileri Tanıyın</span>
          </div>

          <div className="text-3xl font-bold text-indigo-600 mb-2">
            {learnCountdown}s
          </div>

          <p className="text-sm text-gray-500 mb-4">
            Kişi {currentLearnIndex + 1} / {faceCount}
          </p>

          {/* İlerleme çubuğu */}
          <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
            <div
              className="h-full bg-indigo-600 transition-all duration-1000"
              style={{ width: `${((currentLearnIndex + 1) / faceCount) * 100}%` }}
            />
          </div>

          {/* Tek yüz gösterimi (büyük) */}
          <div className="flex justify-center mb-6">
            <div className="p-6 bg-white rounded-2xl shadow-lg border-2 border-indigo-200 max-w-sm w-full">
              <div className="relative w-32 h-32 mx-auto mb-4 rounded-full overflow-hidden ring-4 ring-indigo-100">
                <Image
                  src={faces[currentLearnIndex].imageUrl}
                  alt={faces[currentLearnIndex].name}
                  fill
                  className="object-cover"
                  unoptimized
                />
              </div>
              <h3 className="text-xl font-bold text-gray-900">
                {faces[currentLearnIndex].name}
              </h3>
            </div>
          </div>

          {/* Alt küçük resimler - diğer yüzler */}
          <div className="flex justify-center gap-2 flex-wrap">
            {faces.map((face, idx) => (
              <div
                key={face.id}
                className={`relative w-12 h-12 rounded-full overflow-hidden transition-all ${
                  idx === currentLearnIndex
                    ? 'ring-2 ring-indigo-600 scale-110'
                    : idx < currentLearnIndex
                    ? 'opacity-50'
                    : 'opacity-30'
                }`}
              >
                <Image
                  src={face.imageUrl}
                  alt=""
                  fill
                  className="object-cover"
                  unoptimized
                />
              </div>
            ))}
          </div>

          <p className="text-sm text-gray-500 mt-6">
            Her kişinin yüzünü ve ismini dikkatlice ezberleyin!
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
              className="h-full bg-indigo-600 transition-all duration-300"
              style={{ width: `${((questionIndex + 1) / totalQuestions) * 100}%` }}
            />
          </div>

          {/* Soru */}
          <div className={`p-6 rounded-xl mb-6 text-center transition-colors ${
            feedback === 'correct'
              ? 'bg-green-100'
              : feedback === 'wrong'
              ? 'bg-red-100'
              : 'bg-gray-100'
          }`}>
            <div className="relative w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden ring-4 ring-white shadow-lg">
              <Image
                src={currentQuestion.face.imageUrl}
                alt="Kişi"
                fill
                className="object-cover"
                unoptimized
              />
            </div>
            <p className="text-lg text-gray-700 font-medium">
              Bu kişinin adı nedir?
            </p>
          </div>

          {/* Seçenekler */}
          <div className="grid grid-cols-2 gap-3">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                disabled={!!feedback}
                className={`py-4 px-3 rounded-xl font-medium transition-all text-sm ${
                  feedback
                    ? option === currentQuestion.correctAnswer
                      ? 'bg-green-500 text-white'
                      : selectedAnswer === option
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-400'
                    : 'bg-white border-2 border-gray-200 text-gray-900 hover:border-indigo-400 hover:bg-indigo-50'
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

          {/* Yüz özeti */}
          <div className="bg-white rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-500 mb-3">Tanıştığınız kişiler:</p>
            <div className="flex justify-center gap-2 flex-wrap">
              {faces.map((face) => (
                <div key={face.id} className="flex flex-col items-center">
                  <div className="relative w-10 h-10 rounded-full overflow-hidden">
                    <Image
                      src={face.imageUrl}
                      alt={face.name}
                      fill
                      className="object-cover"
                      unoptimized
                    />
                  </div>
                  <span className="text-xs text-gray-600 mt-1">{face.name.split(' ')[0]}</span>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => {
              resetGame();
              loadFaces();
            }}
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
