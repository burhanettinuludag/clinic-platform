export type UserRole = 'patient' | 'doctor' | 'admin';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  phone: string;
  preferred_language: 'tr' | 'en';
  is_email_verified: boolean;
  date_joined: string;
  last_active: string | null;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  phone?: string;
  preferred_language?: 'tr' | 'en';
}
