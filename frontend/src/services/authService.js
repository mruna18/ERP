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
    const response = await api.get('/customer/me/')
    return response.data
  },

  // Update profile (customer id + { first_name, last_name, email, phone, address })
  updateProfile: async (customerId, data) => {
    const response = await api.put(`/customer/${customerId}/update/`, data)
    return response.data
  },

  // Change password (current_password, new_password)
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/customer/me/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  },
}
