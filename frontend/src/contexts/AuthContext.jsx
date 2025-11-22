import React, { createContext, useState, useContext, useEffect } from 'react'
import { authService } from '../services/api'

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
  const [token, setToken] = useState(localStorage.getItem('access_token'))

  useEffect(() => {
    if (token) {
      const userData = localStorage.getItem('user_data')
      if (userData) {
        setUser(JSON.parse(userData))
      }
    }
    setLoading(false)
  }, [token])

  // В функции login в AuthContext.jsx
  const login = async (login, password) => {
    try {
      const response = await authService.login({
        login,
        password
      })
    
      const { access_token, refresh_token, user: userData } = response.data
      
      // Сохраняем токены в localStorage
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user_data', JSON.stringify(userData))
      
      setToken(access_token)
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.msg || 'Ошибка входа' 
      }
    }
  }

  const register = async (name, login, email, password) => {
    try {
      const response = await authService.register({
        name,
        login,
        email,
        password
      })

      return { success: true, message: 'Регистрация успешна' }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.msg || 'Ошибка регистрации' 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
    setUser(null)
    setToken(null)
  }

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      const response = await authService.refresh(refreshToken)

      const newToken = response.data.access_token
      localStorage.setItem('access_token', newToken)
      setToken(newToken)
      
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  const updateUser = (userData) => {
    setUser(userData)
    localStorage.setItem('user_data', JSON.stringify(userData))
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    refreshToken,
    updateUser
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}