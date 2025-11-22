import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom' // Добавьте этот импорт
import './Header.css'

const Header = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate() // Добавьте этот хук

  return (
    <header className="header">
      <h1 onClick={() => navigate('/tasks')}>Algorythm Trainer</h1>
      <div className="user-info">
        <button 
          onClick={() => navigate('/profile')} 
          className="profile-btn"
        >
          Профиль
        </button>
        <button onClick={logout} className="logout-btn">Выйти</button>
      </div>
    </header>
  )
}

export default Header