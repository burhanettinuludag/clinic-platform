'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';
import api from '@/lib/api';
import { User, LoginResponse } from '@/lib/types/user';

interface RegisterResult {
  user: User;
  status?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (data: Record<string, string>) => Promise<RegisterResult>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = Cookies.get('access_token');
    if (token) {
      api
        .get('/users/me/')
        .then((res) => setUser(res.data))
        .catch(() => {
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    const { data } = await api.post<LoginResponse>('/auth/login/', {
      email,
      password,
    });
    Cookies.set('access_token', data.tokens.access);
    Cookies.set('refresh_token', data.tokens.refresh);
    Cookies.set('user_role', data.user.role);
    setUser(data.user);
    return data.user;
  };

  const register = async (formData: Record<string, string>): Promise<RegisterResult> => {
    const { data } = await api.post('/auth/register/', formData);

    // Doctor registration: no tokens returned, pending approval
    if (data.status === 'pending_approval') {
      return { user: data.user, status: 'pending_approval' };
    }

    // Normal registration: tokens returned
    Cookies.set('access_token', data.tokens.access);
    Cookies.set('refresh_token', data.tokens.refresh);
    Cookies.set('user_role', data.user.role);
    setUser(data.user);
    return { user: data.user };
  };

  const logout = () => {
    const refreshToken = Cookies.get('refresh_token');
    if (refreshToken) {
      api.post('/auth/logout/', { refresh: refreshToken }).catch(() => {});
    }
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    Cookies.remove('user_role');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
