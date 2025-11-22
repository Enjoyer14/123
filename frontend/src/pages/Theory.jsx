import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { taskService } from '../services/api'
import Header from '../components/Header'
import LoadingSpinner from '../components/LoadingSpinner'
import CommentsSection from '../components/CommentsSection' // Добавьте этот импорт
import './Theory.css'

const Theory = () => {
  const { themeId } = useParams()
  const navigate = useNavigate()
  const [theory, setTheory] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTheory()
  }, [themeId])

  const fetchTheory = async () => {
    try {
      const response = await taskService.getTheory(themeId)
      setTheory(response.data)
    } catch (error) {
      console.error('Ошибка загрузки теории:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner message="Загрузка теории..." />
  }

  if (!theory) {
    return (
      <div className="theory-container">
        <Header />
        <div className="theory-content">
          <h2>Теория не найдена</h2>
          <button onClick={() => navigate('/tasks')} className="back-btn">
            Назад к задачам
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="theory-container">
      <Header />
      <div className="theory-content">
        <button onClick={() => navigate('/tasks')} className="back-btn">
          ← Назад к задачам
        </button>
        <h1>{theory.title}</h1>
        <div className="theory-description">
          {theory.description.split('\n').map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>
        
        {/* Добавьте этот блок для комментариев */}
        <CommentsSection parentType="theory" parentId={theory.theory_id} />
      </div>
    </div>
  )
}

export default Theory