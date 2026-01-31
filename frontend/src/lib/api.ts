import axios from 'axios';
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
        }
      } catch {
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        window.location.href = '/tr/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
