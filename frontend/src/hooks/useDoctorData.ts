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
