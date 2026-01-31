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
