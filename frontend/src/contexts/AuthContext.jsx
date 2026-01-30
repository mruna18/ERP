import { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/authService'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedCompany, setSelectedCompany] = useState(null)

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('accessToken')
    const companyId = localStorage.getItem('selectedCompanyId')

    if (token) {
      // Verify token is still valid by fetching user
      fetchUser()
    } else {
      setLoading(false)
    }

    if (companyId) {
      // Fetch company details
      fetchCompany(companyId)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const userData = await authService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const fetchCompany = async (companyId) => {
    try {
      const response = await api.get(`/company/${companyId}/`)
      setSelectedCompany(response.data)
    } catch (error) {
      console.error('Failed to fetch company:', error)
    }
  }

  const login = async (email, password) => {
    try {
      const data = await authService.login({ email, password })
      localStorage.setItem('accessToken', data.access_token)
      localStorage.setItem('refreshToken', data.refresh_token)
      await fetchUser()
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
      }
    }
  }

  const register = async (userData) => {
    try {
      await authService.register(userData)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || 'Registration failed',
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('selectedCompanyId')
    setUser(null)
    setSelectedCompany(null)
  }

  const selectCompany = (companyId) => {
    if (companyId == null || companyId === '') {
      localStorage.removeItem('selectedCompanyId')
      setSelectedCompany(null)
      return
    }
    localStorage.setItem('selectedCompanyId', companyId)
    fetchCompany(companyId)
  }

  const clearCompany = () => {
    localStorage.removeItem('selectedCompanyId')
    setSelectedCompany(null)
  }

  const refreshUser = async () => {
    try {
      const userData = await authService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Failed to refresh user', error)
    }
  }

  const value = {
    user,
    loading,
    selectedCompany,
    login,
    register,
    logout,
    selectCompany,
    clearCompany,
    refreshUser,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
