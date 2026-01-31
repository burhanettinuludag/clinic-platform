// Doctor panel types

export interface AlertFlag {
  type: 'inactive' | 'low_task_completion' | 'high_attack_frequency';
  severity: 'warning' | 'critical' | 'info';
  message: string;
}

export interface EnrolledModuleInfo {
  id: string;
  name: string;
  disease_type: string;
}

export interface DoctorPatient {
  id: string;
  email: string;
  full_name: string;
  phone: string;
  date_of_birth: string | null;
  gender: string;
  enrolled_modules: EnrolledModuleInfo[];
  last_active: string | null;
  alert_flags: AlertFlag[];
}

export interface DoctorPatientDetail extends DoctorPatient {
  emergency_contact_name: string;
  emergency_contact_phone: string;
  notes_text: string;
  date_joined: string;
}

export interface TimelineEntry {
  id: string;
  entry_type: 'migraine_attack' | 'task_completion' | 'symptom_entry' | 'medication_log' | 'doctor_note';
  date: string;
  title: string;
  detail: string;
  severity?: string;
  metadata?: Record<string, unknown>;
}

export interface DoctorNote {
  id: string;
  doctor: string;
  patient: string;
  note_type: 'general' | 'follow_up' | 'medication_change' | 'alert_response';
  content: string;
  is_private: boolean;
  doctor_name: string;
  created_at: string;
  updated_at: string;
}

export interface DoctorAlert {
  patient_id: string;
  patient_name: string;
  alert_type: string;
  severity: 'warning' | 'critical';
  message: string;
  created_at: string;
}

export interface DashboardStats {
  total_patients: number;
  active_patients_7d: number;
  critical_alerts: number;
  warning_alerts: number;
  avg_task_completion_rate: number;
  total_attacks_30d: number;
}

export interface ConsentRecord {
  id: string;
  consent_type: string;
  version: string;
  granted: boolean;
  granted_at: string | null;
  revoked_at: string | null;
  created_at: string;
}
