'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Cookies from 'js-cookie';
import api from '@/lib/api';

function hasAuth() { return !!Cookies.get('access_token'); }
function useAuthQuery<T>(options: Parameters<typeof useQuery<T>>[0]) {
  return useAuthQuery<T>({ ...options, enabled: hasAuth() && (options.enabled !== false), retry: false });
}
import type {
  ParkinsonTrigger,
  ParkinsonSymptomEntry,
  ParkinsonMedication,
  MedicationSchedule,
  ParkinsonMedicationLog,
  HoehnYahrAssessment,
  SchwabEnglandAssessment,
  NMSQuestAssessment,
  NoseraMotorAssessment,
  NoseraDailyLivingAssessment,
  ParkinsonVisit,
  ParkinsonDashboard,
  SymptomChartData,
  SymptomStats,
  LEDSummary,
} from '@/lib/types/parkinson';

const PK = '/parkinson';

// ==================== DASHBOARD ====================

export function useParkinsonDashboard() {
  return useAuthQuery<ParkinsonDashboard>({
    queryKey: ['parkinson-dashboard'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/dashboard/`);
      return data.results?.[0] ?? data;
    },
  });
}

// ==================== TETİKLEYİCİLER ====================

export function useParkinsonTriggers() {
  return useAuthQuery<ParkinsonTrigger[]>({
    queryKey: ['parkinson-triggers'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/triggers/`);
      return data.results ?? data;
    },
  });
}

// ==================== SEMPTOM GÜNLÜKLERİ ====================

export function useParkinsonSymptoms() {
  return useAuthQuery<ParkinsonSymptomEntry[]>({
    queryKey: ['parkinson-symptoms'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/symptoms/`);
      return data.results ?? data;
    },
  });
}

export function useParkinsonSymptomChart(days = 30) {
  return useAuthQuery<SymptomChartData[]>({
    queryKey: ['parkinson-symptom-chart', days],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/symptoms/chart/`, { params: { days } });
      return data;
    },
  });
}

export function useParkinsonSymptomStats() {
  return useAuthQuery<SymptomStats>({
    queryKey: ['parkinson-symptom-stats'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/symptoms/stats/`);
      return data;
    },
  });
}

export function useCreateParkinsonSymptom() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<ParkinsonSymptomEntry> & { trigger_ids?: string[] }) => {
      const { data } = await api.post(`${PK}/symptoms/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-symptoms'] });
      qc.invalidateQueries({ queryKey: ['parkinson-symptom-chart'] });
      qc.invalidateQueries({ queryKey: ['parkinson-symptom-stats'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

export function useDeleteParkinsonSymptom() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`${PK}/symptoms/${id}/`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-symptoms'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

// ==================== İLAÇ YÖNETİMİ ====================

export function useParkinsonMedications() {
  return useAuthQuery<ParkinsonMedication[]>({
    queryKey: ['parkinson-medications'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/medications/`);
      return data.results ?? data;
    },
  });
}

export function useCreateParkinsonMedication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<ParkinsonMedication>) => {
      const { data } = await api.post(`${PK}/medications/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-medications'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

export function useUpdateParkinsonMedication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: Partial<ParkinsonMedication> & { id: string }) => {
      const { data } = await api.patch(`${PK}/medications/${id}/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-medications'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

export function useDeleteParkinsonMedication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`${PK}/medications/${id}/`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-medications'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

export function useLEDSummary() {
  return useAuthQuery<LEDSummary>({
    queryKey: ['parkinson-led-summary'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/medications/led_summary/`);
      return data;
    },
  });
}

// ==================== İLAÇ PROGRAMI ====================

export function useMedicationSchedules(medicationId: string) {
  return useAuthQuery<MedicationSchedule[]>({
    queryKey: ['parkinson-med-schedules', medicationId],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/medications/${medicationId}/schedules/`);
      return data.results ?? data;
    },
    enabled: !!medicationId,
  });
}

export function useCreateMedicationSchedule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ medicationId, ...payload }: Partial<MedicationSchedule> & { medicationId: string }) => {
      const { data } = await api.post(`${PK}/medications/${medicationId}/schedules/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-med-schedules'] });
      qc.invalidateQueries({ queryKey: ['parkinson-medications'] });
    },
  });
}

// ==================== İLAÇ KAYITLARI ====================

export function useParkinsonMedLogs() {
  return useAuthQuery<ParkinsonMedicationLog[]>({
    queryKey: ['parkinson-med-logs'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/medication-logs/`);
      return data.results ?? data;
    },
  });
}

export function useTodayMedLogs() {
  return useAuthQuery<ParkinsonMedicationLog[]>({
    queryKey: ['parkinson-med-logs-today'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/medication-logs/today/`);
      return data;
    },
  });
}

export function useTakeMedication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, motor_state_before }: { id: string; motor_state_before?: string }) => {
      const { data } = await api.post(`${PK}/medication-logs/${id}/take/`, { motor_state_before });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-med-logs'] });
      qc.invalidateQueries({ queryKey: ['parkinson-med-logs-today'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

export function useCreateMedLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<ParkinsonMedicationLog>) => {
      const { data } = await api.post(`${PK}/medication-logs/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-med-logs'] });
      qc.invalidateQueries({ queryKey: ['parkinson-med-logs-today'] });
    },
  });
}

// ==================== KLİNİK DEĞERLENDİRMELER ====================

// Hoehn & Yahr
export function useHoehnYahrAssessments() {
  return useAuthQuery<HoehnYahrAssessment[]>({
    queryKey: ['parkinson-hoehn-yahr'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/assessments/hoehn-yahr/`);
      return data.results ?? data;
    },
  });
}

export function useCreateHoehnYahr() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<HoehnYahrAssessment>) => {
      const { data } = await api.post(`${PK}/assessments/hoehn-yahr/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-hoehn-yahr'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

// Schwab & England
export function useSchwabEnglandAssessments() {
  return useAuthQuery<SchwabEnglandAssessment[]>({
    queryKey: ['parkinson-schwab-england'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/assessments/schwab-england/`);
      return data.results ?? data;
    },
  });
}

export function useCreateSchwabEngland() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<SchwabEnglandAssessment>) => {
      const { data } = await api.post(`${PK}/assessments/schwab-england/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-schwab-england'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

// NMSQuest
export function useNMSQuestAssessments() {
  return useAuthQuery<NMSQuestAssessment[]>({
    queryKey: ['parkinson-nmsquest'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/assessments/nmsquest/`);
      return data.results ?? data;
    },
  });
}

export function useCreateNMSQuest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<NMSQuestAssessment>) => {
      const { data } = await api.post(`${PK}/assessments/nmsquest/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-nmsquest'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

// Norosera Motor
export function useNoseraMotorAssessments() {
  return useAuthQuery<NoseraMotorAssessment[]>({
    queryKey: ['parkinson-nosera-motor'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/assessments/motor/`);
      return data.results ?? data;
    },
  });
}

export function useCreateNoseraMotor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<NoseraMotorAssessment>) => {
      const { data } = await api.post(`${PK}/assessments/motor/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-nosera-motor'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

// Norosera Daily Living
export function useNoseraDailyLivingAssessments() {
  return useAuthQuery<NoseraDailyLivingAssessment[]>({
    queryKey: ['parkinson-nosera-daily'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/assessments/daily-living/`);
      return data.results ?? data;
    },
  });
}

export function useCreateNoseraDailyLiving() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<NoseraDailyLivingAssessment>) => {
      const { data } = await api.post(`${PK}/assessments/daily-living/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-nosera-daily'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}

// ==================== VİZİT KAYITLARI ====================

export function useParkinsonVisits() {
  return useAuthQuery<ParkinsonVisit[]>({
    queryKey: ['parkinson-visits'],
    queryFn: async () => {
      const { data } = await api.get(`${PK}/visits/`);
      return data.results ?? data;
    },
  });
}

export function useCreateParkinsonVisit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<ParkinsonVisit>) => {
      const { data } = await api.post(`${PK}/visits/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['parkinson-visits'] });
      qc.invalidateQueries({ queryKey: ['parkinson-dashboard'] });
    },
  });
}
