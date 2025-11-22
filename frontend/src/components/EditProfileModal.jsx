import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { authService } from '../services/api'
import './EditProfileModal.css'

const EditProfileModal = ({ isOpen, onClose }) => {
  const { user, updateUser } = useAuth()
  const [formData, setFormData] = useState({
    newName: user?.name || '',
    newPassword: '',
    currentPassword: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    // Очищаем сообщения при изменении полей
    if (error) setError('')
    if (success) setSuccess('')
  }

  // В EditProfileModal.jsx в функции handleSubmit
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
  
    try {
      // Проверяем наличие токена
      const token = localStorage.getItem('access_token')
      console.log('🔐 Current token:', token ? 'Present' : 'Missing')
      
      // Подготавливаем данные для отправки
      const updateData = {
        current_password: formData.currentPassword
      }
    
      // Добавляем новые данные только если они изменились
      if (formData.newName !== user.name) {
        updateData.new_name = formData.newName
      }
    
      if (formData.newPassword) {
        updateData.new_password = formData.newPassword
      }
    
      console.log('📤 Sending update request with data:', updateData)
      
      const response = await authService.updateProfile(updateData)
      console.log('✅ Update response:', response.data)
      
      setSuccess('Профиль успешно обновлен')
      
      // Обновляем данные пользователя в контексте
      updateUser(response.data.user)
      
      // Закрываем модальное окно через 2 секунды
      setTimeout(() => {
        onClose()
        setFormData({
          newName: response.data.user.name,
          newPassword: '',
          currentPassword: ''
        })
      }, 2000)
    
    } catch (error) {
      console.error('❌ Update error:', error)
      console.error('❌ Error response:', error.response)
      setError(error.response?.data?.msg || 'Ошибка при обновлении профиля')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setFormData({
      newName: user?.name || '',
      newPassword: '',
      currentPassword: ''
    })
    setError('')
    setSuccess('')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Редактирование профиля</h2>
          <button className="close-btn" onClick={handleClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="edit-profile-form">
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="form-group">
            <label htmlFor="newName">Имя пользователя:</label>
            <input
              type="text"
              id="newName"
              name="newName"
              value={formData.newName}
              onChange={handleChange}
              placeholder="Введите новое имя"
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">Новый пароль:</label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleChange}
              placeholder="Введите новый пароль (минимум 6 символов)"
              minLength="6"
            />
            <small>Оставьте пустым, если не хотите менять пароль</small>
          </div>

          <div className="form-group">
            <label htmlFor="currentPassword">Текущий пароль *:</label>
            <input
              type="password"
              id="currentPassword"
              name="currentPassword"
              value={formData.currentPassword}
              onChange={handleChange}
              placeholder="Введите текущий пароль для подтверждения"
              required
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={handleClose}
              className="btn-secondary"
              disabled={loading}
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading || !formData.currentPassword}
              className="btn-primary"
            >
              {loading ? 'Сохранение...' : 'Сохранить изменения'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EditProfileModal