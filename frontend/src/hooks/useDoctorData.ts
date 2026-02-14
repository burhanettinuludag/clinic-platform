'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type {
  DoctorPatient,
  DoctorPatientDetail,
  TimelineEntry,
  DoctorNote,
  DoctorAlert,
  DashboardStats,
  ConsentRecord,
} from '@/lib/types/doctor';

// ==================== DOCTOR PATIENTS ====================

export function useDoctorPatients(params?: { search?: string; module?: string; has_alerts?: string }) {
  return useQuery<DoctorPatient[]>({
    queryKey: ['doctor-patients', params],
    queryFn: async () => {
      const { data } = await api.get('/doctor/patients/', { params });
      return data;
    },
  });
}

export function useDoctorPatient(id: string) {
  return useQuery<DoctorPatientDetail>({
    queryKey: ['doctor-patients', id],
    queryFn: async () => {
      const { data } = await api.get(`/doctor/patients/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

// ==================== PATIENT TIMELINE ====================

export function usePatientTimeline(patientId: string, days?: number) {
  return useQuery<TimelineEntry[]>({
    queryKey: ['patient-timeline', patientId, days],
    queryFn: async () => {
      const { data } = await api.get(`/doctor/patients/${patientId}/timeline/`, {
        params: { days },
      });
      return data;
    },
    enabled: !!patientId,
  });
}

// ==================== PATIENT NOTES ====================

export function usePatientNotes(patientId: string) {
  return useQuery<DoctorNote[]>({
    queryKey: ['patient-notes', patientId],
    queryFn: async () => {
      const { data } = await api.get(`/doctor/patients/${patientId}/notes/`);
      return data;
    },
    enabled: !!patientId,
  });
}

export function useCreateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (noteData: {
      patientId: string;
      note_type: string;
      content: string;
      is_private?: boolean;
    }) => {
      const { patientId, ...body } = noteData;
      const { data } = await api.post(`/doctor/patients/${patientId}/notes/`, body);
      return data as DoctorNote;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patient-notes'] });
      queryClient.invalidateQueries({ queryKey: ['patient-timeline'] });
    },
  });
}

// ==================== DOCTOR ALERTS ====================

export function useDoctorAlerts() {
  return useQuery<DoctorAlert[]>({
    queryKey: ['doctor-alerts'],
    queryFn: async () => {
      const { data } = await api.get('/doctor/alerts/');
      return data;
    },
  });
}

// ==================== DASHBOARD STATS ====================

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await api.get('/doctor/dashboard/stats/');
      return data;
    },
  });
}

// ==================== KVKK / CONSENTS ====================

export function useConsents() {
  return useQuery<ConsentRecord[]>({
    queryKey: ['consents'],
    queryFn: async () => {
      const { data } = await api.get('/kvkk/consent/');
      return data;
    },
  });
}

export function useGrantConsent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (consentData: { consent_type: string; version: string; granted: boolean }) => {
      const { data } = await api.post('/kvkk/consent/grant/', consentData);
      return data as ConsentRecord;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consents'] });
    },
  });
}

// ==================== DEMENTIA REPORT ====================

export interface DementiaReport {
  patient: {
    id: string;
    full_name: string;
    email: string;
    date_of_birth: string | null;
  };
  report_period: {
    days: number;
    start_date: string;
    end_date: string;
  };
  exercise_summary: {
    total_sessions: number;
    completed_sessions: number;
    avg_accuracy: number | null;
    total_duration_minutes: number;
    by_type: Array<{
      type: string;
      type_display: string;
      count: number;
      avg_score: number;
    }>;
  };
  assessment_summary: {
    total_assessments: number;
    avg_mood_score: number | null;
    avg_confusion_level: number | null;
    avg_sleep_quality: number | null;
    incidents: {
      falls: number;
      wanderings: number;
      missed_medications: number;
    };
    adl_scores: {
      eating: number | null;
      dressing: number | null;
      hygiene: number | null;
      mobility: number | null;
      communication: number | null;
    };
  };
  caregiver_notes: {
    total_flagged: number;
    unreviewed: number;
    notes: Array<{
      id: string;
      title: string;
      content: string;
      note_type: string;
      severity: number;
      created_at: string;
      doctor_reviewed: boolean;
    }>;
  };
  cognitive_score_trend: Array<{
    date: string;
    memory: number | null;
    attention: number | null;
    language: number | null;
    problem_solving: number | null;
    overall: number | null;
  }>;
  weekly_performance: Array<{
    week: number;
    start_date: string;
    end_date: string;
    sessions_count: number;
    avg_accuracy: number | null;
  }>;
  recent_sessions: Array<{
    id: string;
    exercise_name: string;
    exercise_type: string;
    date: string;
    score: number;
    accuracy: number | null;
    duration_minutes: number | null;
  }>;
  recent_assessments: Array<{
    date: string;
    mood_score: number | null;
    confusion_level: number | null;
    sleep_quality: number | null;
    sleep_hours: number | null;
    fall_occurred: boolean;
    wandering_occurred: boolean;
    medication_missed: boolean;
    notes: string;
    concerns: string;
  }>;
}

export function useDementiaReport(patientId: string, days = 30) {
  return useQuery<DementiaReport>({
    queryKey: ['dementia-report', patientId, days],
    queryFn: async () => {
      const { data } = await api.get(`/doctor/patients/${patientId}/dementia-report/`, {
        params: { days },
      });
      return data;
    },
    enabled: !!patientId,
  });
}
