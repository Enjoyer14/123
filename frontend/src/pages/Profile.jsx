import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { profileService } from '../services/api'
import Header from '../components/Header'
import LoadingSpinner from '../components/LoadingSpinner'
import EditProfileModal from '../components/EditProfileModal' // Добавьте этот импорт
import './Profile.css'

const Profile = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [activeTab, setActiveTab] = useState('stats')
  const [loading, setLoading] = useState(true)
  const [themes, setThemes] = useState([])
  const [themeFilter, setThemeFilter] = useState('all')
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

  useEffect(() => {
    if (user) {
      fetchProfile()
    }
  }, [user])

  const fetchProfile = async () => {
    try {
      const response = await profileService.getProfile(user.user_id)
      setProfile(response.data)
    } catch (error) {
      console.error('Ошибка загрузки профиля:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredStats = () => {
    if (!profile) return { by_theme: [] }

    let filteredThemes = profile.statistics.by_theme
    
    if (themeFilter !== 'all') {
      filteredThemes = filteredThemes.filter(theme => 
        theme.theme_id === parseInt(themeFilter)
      )
    }

    return {
      ...profile.statistics,
      by_theme: filteredThemes
    }
  }

  if (loading) {
    return <LoadingSpinner message="Загрузка профиля..." />
  }

  if (!profile) {
    return (
      <div className="profile-container">
        <Header />
        <div className="error-message">
          <h2>Профиль не найден</h2>
        </div>
      </div>
    )
  }

  const stats = filteredStats()

  return (
    <div className="profile-container">
      <Header />
      
      <div className="profile-content">
        <div className="profile-header">
          <div className="profile-info">
            <h1>Профиль пользователя {user.name}</h1>
          </div>
          <div className="profile-actions">
            <button 
              onClick={() => setIsEditModalOpen(true)}
              className="edit-profile-btn"
            >
              Редактировать профиль
            </button>
            <button 
              onClick={() => navigate('/tasks')}
              className="back-btn"
            >
              Назад к задачам
            </button>
          </div>
        </div>

        {activeTab === 'stats' && (
          <div className="stats-tab">
            <div className="stats-filters">
              <div className="filter-group">
                <label>Тема:</label>
                <select 
                  value={themeFilter} 
                  onChange={(e) => setThemeFilter(e.target.value)}
                >
                  <option value="all">Все темы</option>
                  {stats.by_theme.map(theme => (
                    <option key={theme.theme_id} value={theme.theme_id}>
                      {theme.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="stats-overview">
              <div className="stat-card total">
                <h3>Всего решено</h3>
                <p className="stat-number">{stats.total_solved}</p>
              </div>
              
              <div className="stat-card easy">
                <h3>Easy</h3>
                <p className="stat-number">{stats.easy_solved}</p>
              </div>
              
              <div className="stat-card medium">
                <h3>Medium</h3>
                <p className="stat-number">{stats.medium_solved}</p>
              </div>
              
              <div className="stat-card hard">
                <h3>Hard</h3>
                <p className="stat-number">{stats.hard_solved}</p>
              </div>
            </div>

            <div className="theme-stats">
              <h3>Статистика по темам</h3>
              {stats.by_theme.length === 0 ? (
                <p className="no-data">Ни одной задачи еще не решено</p>
              ) : (
                <div className="theme-list">
                  {stats.by_theme.map(theme => (
                    <div key={theme.theme_id} className="theme-item">
                      <span className="theme-title">{theme.title}</span>
                      <span className="theme-count">{theme.solved_count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      <EditProfileModal 
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
      />
    </div>
  )
}

export default Profile