'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

// Types
export interface RelativePatientInfo {
  id: string;
  first_name: string;
  last_name: string;
  latest_score: number | null;
  exercises_this_week: number;
  has_today_assessment: boolean;
  today_mood: number | null;
  recent_incidents: number;
}

export interface RelativeNote {
  id: string;
  note_type: string;
  note_type_display: string;
  title: string;
  content: string;
  severity: number;
  is_flagged_for_doctor: boolean;
  created_at: string;
}

export interface RelativeAssessment {
  id: string;
  assessment_date: string;
  mood_score: number | null;
  confusion_level: number | null;
  agitation_level: number | null;
  anxiety_level: number | null;
  sleep_quality: number | null;
  sleep_hours: number | null;
  fall_occurred: boolean;
  wandering_occurred: boolean;
  medication_missed: boolean;
}

export interface RelativeAlert {
  alert_type: 'flagged_note' | 'fall' | 'wandering' | 'medication';
  severity: number;
  patient_id: string;
  patient_name: string;
  message: string;
  timestamp: string;
  related_id: string | null;
}

// ==================== RELATIVE HOOKS ====================

export function useRelativePatient() {
  return useQuery<RelativePatientInfo>({
    queryKey: ['relative', 'patient'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/relative/patient/');
      return data;
    },
  });
}

export function useRelativeNotes() {
  return useQuery<RelativeNote[]>({
    queryKey: ['relative', 'notes'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/relative/notes/');
      return data;
    },
  });
}

export function useRelativeAssessments() {
  return useQuery<RelativeAssessment[]>({
    queryKey: ['relative', 'assessments'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/relative/assessments/');
      return data;
    },
  });
}

export function useRelativeAlerts() {
  return useQuery<RelativeAlert[]>({
    queryKey: ['relative', 'alerts'],
    queryFn: async () => {
      const { data } = await api.get('/dementia/relative/alerts/');
      return data;
    },
  });
}
