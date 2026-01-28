import api from './api'

export const authService = {
  // Register new user
  register: async (userData) => {
    const response = await api.post('/customer/register/', userData)
    return response.data
  },

  // Login (using custom endpoint that accepts email)
  login: async (credentials) => {
    const response = await api.post('/customer/login/', credentials)
    return response.data
  },

  // Refresh token
  refreshToken: async (refreshToken) => {
    const response = await api.post('/api/token/refresh/', {
      refresh: refreshToken,
    })
    return response.data
  },

  // Get current user info
  getCurrentUser: async () => {
    const response = await api.get('/customer/')
    return response.data
  },
}
