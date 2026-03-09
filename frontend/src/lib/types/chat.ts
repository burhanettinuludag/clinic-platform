// ─── AI Chat Types ───

export interface ChatSession {
  id: string;
  module: 'general' | 'migraine' | 'epilepsy' | 'dementia';
  title: string;
  message_count: number;
  is_active: boolean;
  created_at: string;
  last_message?: {
    role: 'user' | 'assistant';
    content: string;
    created_at: string;
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: ChatSource[];
  confidence: string;
  tokens_used: number;
  llm_provider: string;
  duration_ms: number;
  created_at: string;
}

export interface ChatSource {
  id: string;
  title: string;
  type: 'article' | 'education';
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface AskQuestionResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
}

// ─── Doctor Messaging Types ───

export interface Conversation {
  id: string;
  patient: string;
  doctor: string;
  doctor_name: string;
  doctor_specialty: string;
  patient_name: string;
  subject: string;
  status: 'active' | 'closed' | 'archived';
  last_message_at: string | null;
  patient_unread_count: number;
  doctor_unread_count: number;
  created_at: string;
  last_message?: {
    sender_name: string;
    content: string;
    created_at: string;
  };
}

export interface ConversationDetail extends Conversation {
  messages: DirectMessage[];
}

export interface DirectMessage {
  id: string;
  sender: string;
  sender_name: string;
  sender_role: 'patient' | 'doctor';
  content: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export interface DoctorForChat {
  id: string;
  full_name: string;
  specialty: string;
  bio: string;
  headline: string;
  institution: string;
  city: string;
  is_accepting_patients: boolean;
  profile_photo: string | null;
  is_verified: boolean;
}

export interface DoctorChatStats {
  active_conversations: number;
  total_unread: number;
  total_conversations: number;
}
