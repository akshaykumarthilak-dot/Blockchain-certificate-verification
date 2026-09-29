import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  getStudents: () => api.get('/auth/students'),
};

// Certificates API
export const certificatesAPI = {
  issue: (certificateData) => api.post('/certificates/issue', certificateData),
  getAll: (skip = 0, limit = 100) => api.get(`/certificates/?skip=${skip}&limit=${limit}`),
  getById: (certificateId) => api.get(`/certificates/${certificateId}`),
  transfer: (transferData) => api.post('/certificates/transfer', transferData),
  revoke: (revokeData) => api.post('/certificates/revoke', revokeData),
  verify: (certificateId) => api.get(`/certificates/verify/${certificateId}`),
  verifyByQR: (qrHash) => api.get(`/certificates/verify-qr/${qrHash}`),
};

// Admin API
export const adminAPI = {
  getAllUsers: (skip = 0, limit = 100) => api.get(`/admin/users?skip=${skip}&limit=${limit}`),
  getUser: (userId) => api.get(`/admin/users/${userId}`),
  deactivateUser: (userId) => api.put(`/admin/users/${userId}/deactivate`),
  activateUser: (userId) => api.put(`/admin/users/${userId}/activate`),
  createCategory: (categoryData) => api.post('/admin/categories', categoryData),
  getAllCategories: (skip = 0, limit = 100) => api.get(`/admin/categories?skip=${skip}&limit=${limit}`),
  deleteCategory: (categoryId) => api.delete(`/admin/categories/${categoryId}`),
  getStats: () => api.get('/admin/stats'),
};

export default api;
