import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = (email: string, password: string) =>
  api.post('/auth/login', { email, password });

export const register = (full_name: string, email: string, password: string) =>
  api.post('/auth/register', { full_name, email, password });

export const logout = (refresh_token: string) =>
  api.post('/auth/logout', { refresh_token });

export const forgotPassword = (email: string) =>
  api.post('/auth/forgot-password', { email });

export const resetPassword = (token: string, new_password: string) =>
  api.post('/auth/reset-password', { token, new_password });

// Domains
export const getDomains = (country: string) =>
  api.get(`/domains/?country=${country}`);

export const getQuestions = (domain_id: string) =>
  api.get(`/domains/${domain_id}/questions`);

export const createSession = (data: any) =>
  api.post('/domains/session', data);

// Input
export const processText = (text: string, session_id: string) =>
  api.post('/input/text', { text, session_id });

export const processDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/input/document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Requirements
export const generateRequirements = (session_id: string, document_text: string = '') =>
  api.post('/requirements/generate', { session_id, document_text });

export const getRequirements = (session_id: string) =>
  api.get(`/requirements/${session_id}`);

export const updateRequirement = (requirement_id: string, description: string) =>
  api.put(`/requirements/${requirement_id}`, { description });

// Cross-check
export const crossCheck = (session_id: string) =>
  api.get(`/crosscheck/${session_id}`);

// SRS
export const generateSRS = (session_id: string, project_name: string) =>
  api.post('/srs/generate', { session_id, project_name });

// Use Cases
export const generateUseCases = (session_id: string) =>
  api.post('/usecases/generate', { session_id });

export default api;