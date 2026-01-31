'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

// Types
export interface CognitiveExercise {
  id: string;
  slug: string;
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  instructions: string;
  exercise_type: string;
  exercise_type_display: string;
  difficulty: string;
  difficulty_display: string;
  estimated_duration_minutes: number;
  icon: string;
  config: Record<string, unknown>;
  order: number;
}

export interface ExerciseSession {
  id: string;
  exercise: string;
  exercise_name: string;
  exercise_type: string;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  score: number;
  max_possible_score: number;
  accuracy_percent: number | null;
  results_data: Record<string, unknown>;
  difficulty_rating: number | null;
  notes: string;
}

export interface DailyAssessment {
  id: string;
  assessment_date: string;
  recorded_by: string;
  recorded_by_name: string;
  mood_score: number | null;
  confusion_level: number | null;
  agitation_level: number | null;
  anxiety_level: number | null;
  sleep_quality: number | null;
  sleep_hours: number | null;
  night_wandering: boolean | null;
  eating_independence: number | null;
  dressing_independence: number | null;
  hygiene_independence: number | null;
  mobility_independence: number | null;
  verbal_communication: number | null;
  recognition_family: boolean | null;
  fall_occurred: boolean;
  wandering_occurred: boolean;
  medication_missed: boolean;
  notes: string;
  concerns: string;
}

export interface CaregiverNote {
  id: string;
  patient: string;
  caregiver: string;
  caregiver_name: string;
  note_type: string;
  note_type_display: string;
  title: string;
  content: string;
  severity: number;
  is_flagged_for_doctor: boolean;
  doctor_reviewed: boolean;
  created_at: string;
}

export interface CognitiveStats {
  total_exercises_completed: number;
  exercises_this_week: number;
  current_streak_days: number;
  avg_score_this_week: number | null;
  avg_score_last_week: number | null;
  score_trend: 'improving' | 'stable' | 'declining';
  favorite_exercise_type: string | null;
  last_assessment_date: string | null;
}

export interface ExercisesByType {
  type: string;
  type_display: string;
  exercises: CognitiveExercise[];
}

// ==================== COGNITIVE EXERCISES ====================

export function useCognitiveExercises(params?: { exercise_type?: string; difficulty?: string }) {
  return useQuery<CognitiveExercise[]>({
    queryKey: ['cognitive-exercises', params],
    queryFn: async () => {
      const { data } = await api.get('/dementia/exercises/', { params });
      return data.results ?? data;
    },
  });
}

export function useCognitiveExercisesByType() {
  return useQuery<ExercisesByType[]>({
    queryKey: ['cognitive-exercises', 'by-type'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/exercises/by_type/');
      return data;
    },
  });
}

export function useCognitiveExercise(id: string) {
  return useQuery<CognitiveExercise>({
    queryKey: ['cognitive-exercises', id],
    queryFn: async () => {
      const { data } = await api.get(`/dementia/exercises/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

// ==================== EXERCISE SESSIONS ====================

export function useExerciseSessions() {
  return useQuery<ExerciseSession[]>({
    queryKey: ['exercise-sessions'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/sessions/');
      return data.results ?? data;
    },
  });
}

export function useRecentExerciseSessions() {
  return useQuery<ExerciseSession[]>({
    queryKey: ['exercise-sessions', 'recent'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/sessions/recent/');
      return data.results ?? data;
    },
  });
}

export function useExerciseStats() {
  return useQuery<CognitiveStats>({
    queryKey: ['exercise-stats'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/sessions/stats/');
      return data;
    },
  });
}

export function useExerciseChart(days = 30) {
  return useQuery({
    queryKey: ['exercise-chart', days],
    queryFn: async () => {
      const { data } = await api.get('/dementia/sessions/chart/', { params: { days } });
      return data;
    },
  });
}

export function useCreateExerciseSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (session: {
      exercise: string;
      completed_at?: string;
      duration_seconds?: number;
      score: number;
      max_possible_score?: number;
      accuracy_percent?: number;
      results_data?: Record<string, unknown>;
      difficulty_rating?: number;
      notes?: string;
    }) => {
      const { data } = await api.post('/dementia/sessions/', session);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exercise-sessions'] });
      queryClient.invalidateQueries({ queryKey: ['exercise-stats'] });
    },
  });
}

// ==================== DAILY ASSESSMENTS ====================

export function useDailyAssessments() {
  return useQuery<DailyAssessment[]>({
    queryKey: ['daily-assessments'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/assessments/');
      return data.results ?? data;
    },
  });
}

export function useTodayAssessment() {
  return useQuery<DailyAssessment | null>({
    queryKey: ['daily-assessments', 'today'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/assessments/today/');
      return data;
    },
  });
}

export function useAssessmentChart(days = 30) {
  return useQuery({
    queryKey: ['assessment-chart', days],
    queryFn: async () => {
      const { data } = await api.get('/dementia/assessments/chart/', { params: { days } });
      return data;
    },
  });
}

export function useCreateAssessment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (assessment: Partial<DailyAssessment>) => {
      const { data } = await api.post('/dementia/assessments/', assessment);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['daily-assessments'] });
    },
  });
}

export function useUpdateAssessment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...assessment }: Partial<DailyAssessment> & { id: string }) => {
      const { data } = await api.patch(`/dementia/assessments/${id}/`, assessment);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['daily-assessments'] });
    },
  });
}

// ==================== CAREGIVER NOTES ====================

export function useCaregiverNotes() {
  return useQuery<CaregiverNote[]>({
    queryKey: ['caregiver-notes'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/notes/');
      return data.results ?? data;
    },
  });
}

export function useFlaggedNotes() {
  return useQuery<CaregiverNote[]>({
    queryKey: ['caregiver-notes', 'flagged'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/notes/flagged/');
      return data.results ?? data;
    },
  });
}

export function useCreateCaregiverNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (note: {
      note_type: string;
      title: string;
      content: string;
      severity?: number;
      is_flagged_for_doctor?: boolean;
    }) => {
      const { data } = await api.post('/dementia/notes/', note);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['caregiver-notes'] });
    },
  });
}

// ==================== COGNITIVE SCORES ====================

export interface CognitiveScore {
  id: string;
  score_date: string;
  memory_score: number | null;
  attention_score: number | null;
  language_score: number | null;
  problem_solving_score: number | null;
  orientation_score: number | null;
  overall_score: number | null;
  exercises_completed: number;
  total_exercise_minutes: number;
}

export function useCognitiveScores() {
  return useQuery<CognitiveScore[]>({
    queryKey: ['cognitive-scores'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/scores/');
      return data.results ?? data;
    },
  });
}

export function useLatestCognitiveScore() {
  return useQuery<CognitiveScore | null>({
    queryKey: ['cognitive-scores', 'latest'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/scores/latest/');
      return data;
    },
  });
}

export function useCognitiveScoreChart(months = 6) {
  return useQuery({
    queryKey: ['cognitive-score-chart', months],
    queryFn: async () => {
      const { data } = await api.get('/dementia/scores/chart/', { params: { months } });
      return data;
    },
  });
}

// ==================== EXERCISE TYPE STATS ====================

export function useExerciseTypeStats() {
  return useQuery({
    queryKey: ['exercise-type-stats'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/sessions/');
      const sessions = data.results ?? data;

      // Group by exercise type
      const typeStats: Record<string, { count: number; avgScore: number; totalScore: number }> = {};

      sessions.forEach((session: ExerciseSession) => {
        const type = session.exercise_type;
        if (!typeStats[type]) {
          typeStats[type] = { count: 0, avgScore: 0, totalScore: 0 };
        }
        typeStats[type].count += 1;
        if (session.accuracy_percent) {
          typeStats[type].totalScore += session.accuracy_percent;
        }
      });

      // Calculate averages
      Object.keys(typeStats).forEach((type) => {
        if (typeStats[type].count > 0) {
          typeStats[type].avgScore = typeStats[type].totalScore / typeStats[type].count;
        }
      });

      return typeStats;
    },
  });
}

// ==================== COGNITIVE SCREENING ASSESSMENTS ====================

export interface ScreeningDomainScore {
  score: number;
  max: number;
  label: string;
}

export interface CognitiveScreening {
  id: string;
  assessment_date: string;
  administered_by: string;
  administered_by_name: string;
  // Domain scores (0-100 each)
  orientation_score: number | null;
  memory_score: number | null;
  attention_score: number | null;
  language_score: number | null;
  executive_score: number | null;
  // Overall
  total_score: number;
  // Metadata
  responses: Record<string, unknown>;
  duration_minutes: number | null;
  notes: string;
  interpretation: 'normal' | 'mild' | 'moderate' | 'severe';
  interpretation_label: string;
  domain_scores: Record<string, ScreeningDomainScore>;
  created_at: string;
  updated_at: string;
}

export function useCognitiveScreenings() {
  return useQuery<CognitiveScreening[]>({
    queryKey: ['cognitive-screenings'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/screening/');
      return data.results ?? data;
    },
  });
}

export function useLatestCognitiveScreening() {
  return useQuery<CognitiveScreening | null>({
    queryKey: ['cognitive-screenings', 'latest'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/screening/latest/');
      return data;
    },
  });
}

export function useCognitiveScreeningHistory() {
  return useQuery<Array<{
    assessment_date: string;
    total_score: number;
    orientation_score: number | null;
    memory_score: number | null;
    attention_score: number | null;
    language_score: number | null;
    executive_score: number | null;
  }>>({
    queryKey: ['cognitive-screenings', 'history'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/screening/history/');
      return data;
    },
  });
}

export function useCreateCognitiveScreening() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (assessment: {
      assessment_date: string;
      orientation_score?: number;
      memory_score?: number;
      attention_score?: number;
      language_score?: number;
      executive_score?: number;
      responses?: Record<string, unknown>;
      duration_minutes?: number;
      notes?: string;
    }) => {
      const { data } = await api.post('/dementia/screening/', assessment);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cognitive-screenings'] });
    },
  });
}
