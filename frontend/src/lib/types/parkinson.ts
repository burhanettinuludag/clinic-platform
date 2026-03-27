// Parkinson Module Types

export interface ParkinsonTrigger {
  id: string;
  name: string;
  name_tr: string;
  name_en: string;
  category: 'medication' | 'stress' | 'physical' | 'environmental' | 'dietary' | 'sleep' | 'other';
  is_predefined: boolean;
}

export type MotorState = 'on' | 'off' | 'dyskinesia' | 'wearing_off';
export type AffectedSide = 'left' | 'right' | 'bilateral';

export interface ParkinsonSymptomEntry {
  id: string;
  recorded_at: string;
  motor_state: MotorState | '';
  affected_side: AffectedSide | '';
  tremor_severity: number;
  rigidity_severity: number;
  bradykinesia_severity: number;
  postural_instability: number;
  gait_difficulty: number;
  has_freezing: boolean;
  has_balance_problem: boolean;
  has_speech_difficulty: boolean;
  has_swallowing_difficulty: boolean;
  has_sleep_disturbance: boolean;
  has_constipation: boolean;
  has_mood_change: boolean;
  has_cognitive_issue: boolean;
  has_pain: boolean;
  has_fatigue: boolean;
  overall_severity: number;
  on_time_hours: number | null;
  off_time_hours: number | null;
  triggers_identified: ParkinsonTrigger[];
  notes: string;
  created_at: string;
}

export type DrugClass =
  | 'levodopa'
  | 'dopamine_agonist'
  | 'mao_b_inhibitor'
  | 'comt_inhibitor'
  | 'amantadine'
  | 'anticholinergic'
  | 'other';

export interface MedicationSchedule {
  id: string;
  time_of_day: string;
  label: string;
  is_enabled: boolean;
}

export interface ParkinsonMedication {
  id: string;
  name: string;
  generic_name: string;
  drug_class: DrugClass;
  dosage_mg: number;
  frequency_per_day: number;
  led_conversion_factor: number;
  daily_led: number;
  start_date: string;
  end_date: string | null;
  is_active: boolean;
  notes: string;
  schedules: MedicationSchedule[];
  created_at: string;
}

export interface ParkinsonMedicationLog {
  id: string;
  medication: string;
  medication_name: string;
  schedule: string | null;
  scheduled_time: string;
  taken_at: string | null;
  was_taken: boolean;
  motor_state_before: MotorState | '';
  motor_state_after: MotorState | '';
  notes: string;
  created_at: string;
}

export type HoehnYahrStage = '0' | '1' | '1.5' | '2' | '2.5' | '3' | '4' | '5';

export interface HoehnYahrAssessment {
  id: string;
  assessed_at: string;
  stage: HoehnYahrStage;
  stage_display: string;
  assessed_by: string | null;
  notes: string;
  created_at: string;
}

export interface SchwabEnglandAssessment {
  id: string;
  assessed_at: string;
  score: number;
  assessed_by: string | null;
  notes: string;
  created_at: string;
}

export interface NMSQuestAssessment {
  id: string;
  assessed_at: string;
  q1_drooling: boolean;
  q2_dysphagia: boolean;
  q3_constipation: boolean;
  q4_urinary_urgency: boolean;
  q5_nocturia: boolean;
  q6_dizziness: boolean;
  q7_sweating: boolean;
  q8_sexual_dysfunction: boolean;
  q9_insomnia: boolean;
  q10_daytime_sleepiness: boolean;
  q11_rbd: boolean;
  q12_restless_legs: boolean;
  q13_depression: boolean;
  q14_anxiety: boolean;
  q15_apathy: boolean;
  q16_attention_difficulty: boolean;
  q17_memory_problem: boolean;
  q18_hallucination: boolean;
  q19_pain: boolean;
  q20_numbness: boolean;
  q21_taste_smell: boolean;
  q22_weight_change: boolean;
  q23_fatigue: boolean;
  q24_double_vision: boolean;
  q25_speech: boolean;
  q26_falling: boolean;
  q27_freezing: boolean;
  q28_leg_swelling: boolean;
  q29_excessive_saliva: boolean;
  q30_unexplained_fever: boolean;
  total_score: number;
  notes: string;
  created_at: string;
}

export interface NoseraMotorAssessment {
  id: string;
  assessed_at: string;
  tremor_rest: number;
  tremor_action: number;
  rigidity: number;
  finger_tapping: number;
  hand_movements: number;
  leg_agility: number;
  arising_from_chair: number;
  gait: number;
  postural_stability: number;
  body_bradykinesia: number;
  total_score: number;
  assessed_by: string | null;
  notes: string;
  created_at: string;
}

export interface NoseraDailyLivingAssessment {
  id: string;
  assessed_at: string;
  speech: number;
  salivation: number;
  swallowing: number;
  handwriting: number;
  cutting_food: number;
  dressing: number;
  hygiene: number;
  turning_in_bed: number;
  falling: number;
  freezing: number;
  walking: number;
  tremor_impact: number;
  total_score: number;
  notes: string;
  created_at: string;
}

export type VisitType = 'routine' | 'emergency' | 'medication_adjustment' | 'initial' | 'follow_up';

export interface ParkinsonVisit {
  id: string;
  visit_date: string;
  visit_type: VisitType;
  visit_type_display: string;
  doctor_name: string;
  hospital_name: string;
  hoehn_yahr: string | null;
  hoehn_yahr_detail: HoehnYahrAssessment | null;
  schwab_england: string | null;
  schwab_england_detail: SchwabEnglandAssessment | null;
  total_daily_led: number | null;
  medication_changes: string;
  findings: string;
  plan: string;
  next_visit_date: string | null;
  notes: string;
  created_at: string;
}

export interface ParkinsonDashboard {
  total_symptoms: number;
  total_medications: number;
  active_medications: number;
  total_daily_led: number;
  latest_hoehn_yahr: HoehnYahrAssessment | null;
  latest_schwab_england: SchwabEnglandAssessment | null;
  avg_on_time: number | null;
  avg_off_time: number | null;
  recent_symptoms: ParkinsonSymptomEntry[];
  upcoming_medications: ParkinsonMedicationLog[];
  next_visit: ParkinsonVisit | null;
}

export interface SymptomChartData {
  date: string;
  motor_state: MotorState | '';
  tremor: number;
  rigidity: number;
  bradykinesia: number;
  overall: number;
  on_time: number | null;
  off_time: number | null;
}

export interface LEDSummary {
  total_daily_led: number;
  medications: {
    name: string;
    drug_class: DrugClass;
    dosage_mg: number;
    frequency: number;
    led_factor: number;
    daily_led: number;
  }[];
}

export interface SymptomStats {
  total_entries: number;
  last_30_days: number;
  avg_overall_severity: number | null;
  avg_tremor: number | null;
  avg_rigidity: number | null;
  avg_bradykinesia: number | null;
  avg_on_time: number | null;
  avg_off_time: number | null;
}
