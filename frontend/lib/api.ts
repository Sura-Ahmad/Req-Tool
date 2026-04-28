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

// Auth — current user
export const getMe = () => api.get('/auth/me');

// Admin
export const getStats = () => api.get('/admin/stats');
export const getUsers = () => api.get('/admin/users');
export const toggleUser = (user_id: string) => api.put(`/admin/users/${user_id}/toggle-active`);
export const getSessions = () => api.get('/admin/sessions');
export const getDomainsAdmin = () => api.get('/admin/domains');
export const createDomain = (data: { name: string; name_ar: string; country: string }) =>
  api.post('/admin/domains', data);
export const updateDomain = (domain_id: string, data: { name?: string; name_ar?: string; country?: string; is_active?: boolean }) =>
  api.put(`/admin/domains/${domain_id}`, data);
export const deleteDomain = (domain_id: string) => api.delete(`/admin/domains/${domain_id}`);
export const getQuestionsAdmin = (domain_id: string) => api.get(`/admin/domains/${domain_id}/questions`);
export const createQuestion = (domain_id: string, data: { question_text: string; question_text_ar: string; question_order: string }) =>
  api.post(`/admin/domains/${domain_id}/questions`, data);
export const updateQuestion = (question_id: string, data: { question_text?: string; question_text_ar?: string; question_order?: string; is_active?: boolean }) =>
  api.put(`/admin/questions/${question_id}`, data);
export const deleteQuestion = (question_id: string) => api.delete(`/admin/questions/${question_id}`);

export default api;