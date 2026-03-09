'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

// Types
export interface CaregiverPatientSummary {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  latest_score: number | null;
  exercises_today: number;
  exercises_this_week: number;
  streak_days: number;
  has_alerts: boolean;
  last_activity: string | null;
}

export interface CaregiverAlert {
  alert_type: 'flagged_note' | 'fall' | 'wandering' | 'medication' | 'score_decline';
  severity: number;
  patient_id: string;
  patient_name: string;
  message: string;
  timestamp: string;
  related_id: string | null;
}

export interface CaregiverPatientDetail {
  patient: CaregiverPatientSummary;
  recent_sessions: Array<{
    id: string;
    exercise_name: string;
    exercise_type: string;
    started_at: string;
    duration_seconds: number | null;
    score: number;
    accuracy_percent: number | null;
  }>;
  recent_assessments: Array<{
    id: string;
    assessment_date: string;
    mood_score: number | null;
    confusion_level: number | null;
    sleep_quality: number | null;
    fall_occurred: boolean;
    wandering_occurred: boolean;
    medication_missed: boolean;
  }>;
  recent_notes: Array<{
    id: string;
    note_type: string;
    note_type_display: string;
    title: string;
    content: string;
    severity: number;
    is_flagged_for_doctor: boolean;
    created_at: string;
  }>;
  cognitive_scores: Array<{
    id: string;
    score_date: string;
    memory_score: number | null;
    attention_score: number | null;
    language_score: number | null;
    problem_solving_score: number | null;
    orientation_score: number | null;
    overall_score: number | null;
  }>;
  latest_screening: {
    total_score: number;
    interpretation: string;
    interpretation_label: string;
    assessment_date: string;
  } | null;
}

// ==================== CAREGIVER PATIENTS ====================

export function useCaregiverPatients() {
  return useQuery<CaregiverPatientSummary[]>({
    queryKey: ['caregiver', 'patients'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/caregiver/patients/');
      return data;
    },
  });
}

export function useCaregiverPatientDetail(patientId: string) {
  return useQuery<CaregiverPatientDetail>({
    queryKey: ['caregiver', 'patients', patientId, 'summary'],
    queryFn: async () => {
      const { data } = await api.get(`/dementia/caregiver/patients/${patientId}/summary/`);
      return data;
    },
    enabled: !!patientId,
  });
}

export function useCaregiverAlerts() {
  return useQuery<CaregiverAlert[]>({
    queryKey: ['caregiver', 'alerts'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/caregiver/alerts/');
      return data;
    },
  });
}
