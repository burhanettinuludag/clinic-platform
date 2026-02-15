import axios from 'axios';
import { emitToast } from './toast-events';
import Cookies from 'js-cookie';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const locale = Cookies.get('NEXT_LOCALE') || 'tr';
  config.headers['Accept-Language'] = locale;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = Cookies.get('refresh_token');
        if (refreshToken) {
          const { data } = await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/token/refresh/`,
            { refresh: refreshToken }
          );
          Cookies.set('access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return api(originalRequest);
        } else {
          // No refresh token - redirect to login
          Cookies.remove('access_token');
          if (typeof window !== 'undefined') {
            const locale = Cookies.get('NEXT_LOCALE') || 'tr';
            window.location.href = `/${locale}/auth/login`;
          }
        }
      } catch {
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        if (typeof window !== 'undefined') {
          const locale = Cookies.get('NEXT_LOCALE') || 'tr';
          window.location.href = `/${locale}/auth/login`;
        }
      }
    }
    // Toast error messages
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      if (status === 403) emitToast('error', detail || 'Bu isleme yetkiniz yok.');
      else if (status === 404) emitToast('warning', detail || 'Kayit bulunamadi.');
      else if (status === 429) emitToast('warning', 'Cok fazla istek. Lutfen bekleyin.');
      else if (status >= 500) emitToast('error', 'Sunucu hatasi. Lutfen tekrar deneyin.');
    } else if (error.code === 'ERR_NETWORK') {
      emitToast('error', 'Baglanti hatasi. Internet baglantinizi kontrol edin.');
    }
    return Promise.reject(error);
  }
);

export default api;
