'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type {
  DiseaseModule,
  PatientModule,
  TaskTemplate,
  TaskCompletion,
  TaskStats,
  SymptomDefinition,
  SymptomEntry,
  Medication,
  MedicationLog,
  MedicationAdherence,
  ReminderConfig,
  MigraineAttack,
  MigraineAttackListItem,
  MigraineTrigger,
  MigraineStats,
  MigraineChartData,
  TriggerAnalysis,
} from '@/lib/types/patient';

// ==================== MODULES ====================

export function useDiseaseModules() {
  return useQuery<DiseaseModule[]>({
    queryKey: ['disease-modules'],
    queryFn: async () => {
      const { data } = await api.get('/modules/');
      return data.results ?? data;
    },
  });
}

export function usePatientModules() {
  return useQuery<PatientModule[]>({
    queryKey: ['patient-modules'],
    queryFn: async () => {
      const { data } = await api.get('/modules/enrollments/');
      return data.results ?? data;
    },
  });
}

export function useEnrollModule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (diseaseModuleId: string) => {
      const { data } = await api.post('/modules/enrollments/', {
        disease_module: diseaseModuleId,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patient-modules'] });
    },
  });
}

export function useUnenrollModule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (enrollmentId: string) => {
      await api.delete(`/modules/enrollments/${enrollmentId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patient-modules'] });
    },
  });
}

// ==================== TASKS ====================

export function useTodayTasks() {
  return useQuery<TaskTemplate[]>({
    queryKey: ['tasks', 'today'],
    queryFn: async () => {
      const { data } = await api.get('/tasks/templates/today/');
      return data.results ?? data;
    },
  });
}

export function useWeekTasks() {
  return useQuery<TaskTemplate[]>({
    queryKey: ['tasks', 'week'],
    queryFn: async () => {
      const { data } = await api.get('/tasks/templates/week/');
      return data.results ?? data;
    },
  });
}

export function useTaskStats() {
  return useQuery<TaskStats>({
    queryKey: ['tasks', 'stats'],
    queryFn: async () => {
      const { data } = await api.get('/tasks/completions/stats/');
      return data;
    },
  });
}

export function useCompleteTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (completion: {
      task_template: string;
      completed_date: string;
      response_data?: Record<string, unknown>;
      notes?: string;
    }) => {
      const { data } = await api.post('/tasks/completions/', completion);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

// ==================== SYMPTOMS ====================

export function useSymptomDefinitions(moduleId?: string) {
  return useQuery<SymptomDefinition[]>({
    queryKey: ['symptom-definitions', moduleId],
    queryFn: async () => {
      const params = moduleId ? { disease_module: moduleId } : {};
      const { data } = await api.get('/tracking/symptom-definitions/', { params });
      return data.results ?? data;
    },
  });
}

export function useTodaySymptoms() {
  return useQuery<SymptomEntry[]>({
    queryKey: ['symptoms', 'today'],
    queryFn: async () => {
      const { data } = await api.get('/tracking/symptoms/today/');
      return data;
    },
  });
}

export function useSymptomChart(symptomId?: string, days = 30) {
  return useQuery<SymptomEntry[]>({
    queryKey: ['symptoms', 'chart', symptomId, days],
    queryFn: async () => {
      const params: Record<string, string | number> = { days };
      if (symptomId) params.symptom_definition = symptomId;
      const { data } = await api.get('/tracking/symptoms/chart/', { params });
      return data;
    },
  });
}

export function useLogSymptom() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (entry: {
      symptom_definition: string;
      recorded_date: string;
      value: unknown;
      notes?: string;
    }) => {
      const { data } = await api.post('/tracking/symptoms/', entry);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['symptoms'] });
    },
  });
}

// ==================== MEDICATIONS ====================

export function useMedications() {
  return useQuery<Medication[]>({
    queryKey: ['medications'],
    queryFn: async () => {
      const { data } = await api.get('/tracking/medications/');
      return data.results ?? data;
    },
  });
}

export function useActiveMedications() {
  return useQuery<Medication[]>({
    queryKey: ['medications', 'active'],
    queryFn: async () => {
      const { data } = await api.get('/tracking/medications/active/');
      return data.results ?? data;
    },
  });
}

export function useCreateMedication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (med: Partial<Medication>) => {
      const { data } = await api.post('/tracking/medications/', med);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications'] });
    },
  });
}

export function useUpdateMedication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...med }: Partial<Medication> & { id: string }) => {
      const { data } = await api.patch(`/tracking/medications/${id}/`, med);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications'] });
    },
  });
}

export function useTodayMedicationLogs() {
  return useQuery<MedicationLog[]>({
    queryKey: ['medication-logs', 'today'],
    queryFn: async () => {
      const { data } = await api.get('/tracking/medication-logs/today/');
      return data;
    },
  });
}

export function useLogMedication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (log: {
      medication: string;
      taken_at: string;
      was_taken: boolean;
      notes?: string;
    }) => {
      const { data } = await api.post('/tracking/medication-logs/', log);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medication-logs'] });
    },
  });
}

export function useMedicationAdherence() {
  return useQuery<MedicationAdherence>({
    queryKey: ['medication-adherence'],
    queryFn: async () => {
      const { data } = await api.get('/tracking/medication-logs/adherence/');
      return data;
    },
  });
}

// ==================== REMINDERS ====================

export function useReminders() {
  return useQuery<ReminderConfig[]>({
    queryKey: ['reminders'],
    queryFn: async () => {
      const { data } = await api.get('/tracking/reminders/');
      return data.results ?? data;
    },
  });
}

export function useCreateReminder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (reminder: Partial<ReminderConfig>) => {
      const { data } = await api.post('/tracking/reminders/', reminder);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
    },
  });
}

// ==================== MIGRAINE ====================

export function useMigraineAttacks(params?: { start_date?: string; end_date?: string }) {
  return useQuery<MigraineAttackListItem[]>({
    queryKey: ['migraine-attacks', params],
    queryFn: async () => {
      const { data } = await api.get('/migraine/attacks/', { params });
      return data.results ?? data;
    },
  });
}

export function useMigraineAttack(id: string) {
  return useQuery<MigraineAttack>({
    queryKey: ['migraine-attacks', id],
    queryFn: async () => {
      const { data } = await api.get(`/migraine/attacks/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateAttack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (attack: Partial<MigraineAttack>) => {
      const { data } = await api.post('/migraine/attacks/', attack);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migraine-attacks'] });
      queryClient.invalidateQueries({ queryKey: ['migraine-stats'] });
    },
  });
}

export function useUpdateAttack() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...attack }: Partial<MigraineAttack> & { id: string }) => {
      const { data } = await api.patch(`/migraine/attacks/${id}/`, attack);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migraine-attacks'] });
      queryClient.invalidateQueries({ queryKey: ['migraine-stats'] });
    },
  });
}

export function useMigraineStats() {
  return useQuery<MigraineStats>({
    queryKey: ['migraine-stats'],
    queryFn: async () => {
      const { data } = await api.get('/migraine/attacks/stats/');
      return data;
    },
  });
}

export function useMigraineChart(months = 6) {
  return useQuery<MigraineChartData[]>({
    queryKey: ['migraine-chart', months],
    queryFn: async () => {
      const { data } = await api.get('/migraine/attacks/chart/', {
        params: { months },
      });
      return data;
    },
  });
}

export function useMigraineTriggers() {
  return useQuery<MigraineTrigger[]>({
    queryKey: ['migraine-triggers'],
    queryFn: async () => {
      const { data } = await api.get('/migraine/triggers/');
      return data.results ?? data;
    },
  });
}

export function useCreateTrigger() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (trigger: { name_tr: string; name_en: string; category: string }) => {
      const { data } = await api.post('/migraine/triggers/', trigger);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migraine-triggers'] });
    },
  });
}

export function useTriggerAnalysis() {
  return useQuery<TriggerAnalysis[]>({
    queryKey: ['trigger-analysis'],
    queryFn: async () => {
      const { data } = await api.get('/migraine/triggers/analysis/');
      return data.results ?? data;
    },
  });
}
