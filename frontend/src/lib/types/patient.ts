export interface DiseaseModule {
  id: string;
  slug: string;
  disease_type: 'migraine' | 'epilepsy' | 'parkinson' | 'dementia';
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  description_tr: string;
  description_en: string;
  icon: string;
  is_active: boolean;
  order: number;
}

export interface PatientModule {
  id: string;
  disease_module: string;
  disease_module_detail: DiseaseModule;
  enrolled_at: string;
  is_active: boolean;
}

export interface TaskTemplate {
  id: string;
  disease_module: string;
  title: string;
  title_tr: string;
  title_en: string;
  description: string;
  description_tr: string;
  description_en: string;
  task_type: 'diary_entry' | 'checklist' | 'education' | 'exercise' | 'medication' | 'survey';
  frequency: 'daily' | 'weekly' | 'on_event' | 'one_time';
  points: number;
  order: number;
  is_active: boolean;
  metadata: Record<string, unknown>;
  is_completed_today?: boolean;
  completions_this_week?: string[];
}

export interface TaskCompletion {
  id: string;
  task_template: string;
  task_template_detail?: TaskTemplate;
  completed_date: string;
  response_data: Record<string, unknown>;
  notes: string;
}

export interface TaskStats {
  total_completions: number;
  completed_today: number;
  completed_this_week: number;
  completed_this_month: number;
  current_streak: number;
}

export interface SymptomDefinition {
  id: string;
  disease_module: string;
  key: string;
  label: string;
  label_tr: string;
  label_en: string;
  input_type: 'slider' | 'boolean' | 'choice' | 'text' | 'number';
  config: Record<string, unknown>;
  order: number;
  is_active: boolean;
}

export interface SymptomEntry {
  id: string;
  symptom_definition: string;
  symptom_key: string;
  symptom_label: string;
  recorded_date: string;
  value: unknown;
  notes: string;
}

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
  notes: string;
}

export interface MedicationLog {
  id: string;
  medication: string;
  medication_name: string;
  taken_at: string;
  was_taken: boolean;
  notes: string;
}

export interface ReminderConfig {
  id: string;
  reminder_type: 'medication' | 'exercise' | 'sleep' | 'diary' | 'general';
  title: string;
  time_of_day: string;
  days_of_week: number[];
  is_enabled: boolean;
  linked_medication: string | null;
}

export interface MigraineTrigger {
  id: string;
  name: string;
  name_tr: string;
  name_en: string;
  category: 'dietary' | 'environmental' | 'hormonal' | 'emotional' | 'physical' | 'sleep' | 'other';
  is_predefined: boolean;
  created_by: number | null;
}

export interface MigraineAttack {
  id: string;
  start_datetime: string;
  end_datetime: string | null;
  duration_minutes: number | null;
  intensity: number;
  pain_location: string;
  has_aura: boolean;
  has_nausea: boolean;
  has_vomiting: boolean;
  has_photophobia: boolean;
  has_phonophobia: boolean;
  medication_taken: string;
  medication_effective: boolean | null;
  triggers_identified: MigraineTrigger[];
  trigger_ids?: string[];
  notes: string;
  created_at: string;
}

export interface MigraineAttackListItem {
  id: string;
  start_datetime: string;
  duration_minutes: number | null;
  intensity: number;
  pain_location: string;
  has_aura: boolean;
  medication_taken: string;
  trigger_count: number;
  created_at: string;
}

export interface MigraineStats {
  total_attacks: number;
  avg_intensity: number;
  avg_duration: number;
  attacks_this_month: number;
  attacks_last_month: number;
  most_common_triggers: { name: string; count: number }[];
  most_common_location: string;
  aura_percentage: number;
}

export interface MigraineChartData {
  month: string;
  count: number;
  avg_intensity: number;
}

export interface MedicationAdherence {
  total_logs: number;
  taken: number;
  missed: number;
  adherence_rate: number;
}

export interface TriggerAnalysis {
  id: string;
  name_tr: string;
  name_en: string;
  category: string;
  attack_count: number;
}

// Epilepsy Types
export interface EpilepsyTrigger {
  id: string;
  name: string;
  name_tr: string;
  name_en: string;
  category: 'sleep' | 'stress' | 'substance' | 'sensory' | 'physical' | 'hormonal' | 'other';
  is_predefined: boolean;
  created_by: number | null;
}

export interface SeizureEvent {
  id: string;
  seizure_datetime: string;
  seizure_type: 'focal_aware' | 'focal_impaired' | 'generalized_tonic_clonic' | 'generalized_absence' | 'generalized_myoclonic' | 'unknown';
  duration_seconds: number | null;
  intensity: number;
  triggers_identified: EpilepsyTrigger[];
  trigger_ids?: string[];
  loss_of_consciousness: boolean;
  medication_taken: boolean;
  post_ictal_notes: string;
  notes: string;
  created_at: string;
}

export interface SeizureEventListItem {
  id: string;
  seizure_datetime: string;
  seizure_type: string;
  duration_seconds: number | null;
  intensity: number;
  loss_of_consciousness: boolean;
  medication_taken: boolean;
  trigger_count: number;
  created_at: string;
}

export interface SeizureStats {
  total_seizures: number;
  avg_intensity: number;
  avg_duration: number;
  seizures_this_month: number;
  seizures_last_month: number;
  most_common_triggers: { name: string; count: number }[];
  most_common_type: string;
  consciousness_loss_percentage: number;
}

// Wellness Types
export interface BreathingExercise {
  id: string;
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  description_tr: string;
  description_en: string;
  inhale_seconds: number;
  hold_seconds: number;
  exhale_seconds: number;
  hold_after_exhale_seconds: number;
  cycles: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  benefits: string;
  benefits_tr: string;
  benefits_en: string;
  icon: string;
  color: string;
  total_duration: number;
}

export interface RelaxationExercise {
  id: string;
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  description_tr: string;
  description_en: string;
  exercise_type: 'pmr' | 'body_scan' | 'visualization' | 'grounding' | 'mindfulness';
  duration_minutes: number;
  steps: string[];
  steps_tr: string[];
  steps_en: string[];
  audio_url: string | null;
  benefits: string;
  benefits_tr: string;
  benefits_en: string;
  icon: string;
  color: string;
}

export interface ExerciseSession {
  id: string;
  breathing_exercise: string | null;
  breathing_exercise_name: string | null;
  relaxation_exercise: string | null;
  relaxation_exercise_name: string | null;
  duration_seconds: number;
  completed_at: string;
  stress_before: number | null;
  stress_after: number | null;
  stress_reduction: number | null;
  notes: string;
  points_earned: number;
}

export interface SleepLog {
  id: string;
  date: string;
  bedtime: string;
  wake_time: string;
  sleep_duration_minutes: number;
  sleep_hours: number;
  sleep_quality: 1 | 2 | 3 | 4 | 5;
  had_nightmare: boolean;
  woke_up_during_night: number;
  notes: string;
  created_at: string;
}

export interface MenstrualLog {
  id: string;
  date: string;
  is_period_day: boolean;
  flow_intensity: 'spotting' | 'light' | 'medium' | 'heavy' | '';
  has_cramps: boolean;
  cramp_intensity: number | null;
  has_headache: boolean;
  has_mood_changes: boolean;
  has_bloating: boolean;
  has_fatigue: boolean;
  notes: string;
  created_at: string;
}

export interface WaterIntakeLog {
  id: string;
  date: string;
  glasses: number;
  target_glasses: number;
  percentage: number;
  ml_consumed: number;
  created_at: string;
  updated_at: string;
}

export interface WeatherData {
  id: string;
  city: string;
  country_code: string;
  temperature: number;
  humidity: number;
  pressure: number;
  pressure_status: 'low' | 'normal' | 'high';
  weather_condition: string;
  weather_description: string;
  recorded_at: string;
}

// Gamification Types
export interface Badge {
  id: string;
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  description_tr: string;
  description_en: string;
  icon: string;
  color: string;
  category: 'tracking' | 'streak' | 'milestone' | 'wellness' | 'social';
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  points_reward: number;
  requirement_type: string;
  requirement_value: number;
}

export interface UserBadge {
  id: string;
  badge: Badge;
  earned_at: string;
}

export interface UserStreak {
  id: string;
  streak_type: string;
  streak_type_display: string;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string | null;
  streak_started_at: string | null;
  is_active_today: boolean;
}

export interface UserPoints {
  total_points: number;
  level: number;
  points_to_next_level: number;
  level_progress: number;
  points_this_week: number;
  points_this_month: number;
}

export interface Achievement {
  id: string;
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  description_tr: string;
  description_en: string;
  icon: string;
  color: string;
  period: 'daily' | 'weekly' | 'monthly' | 'one_time';
  target_type: string;
  target_value: number;
  points_reward: number;
}

export interface UserAchievement {
  id: string;
  achievement: Achievement;
  current_progress: number;
  is_completed: boolean;
  completed_at: string | null;
  progress_percentage: number;
  period_start: string;
}

export interface GamificationSummary {
  points: UserPoints;
  streaks: UserStreak[];
  recent_badges: UserBadge[];
  active_achievements: UserAchievement[];
  stats: {
    total_badges: number;
    active_streaks: number;
    completed_achievements: number;
  };
}
