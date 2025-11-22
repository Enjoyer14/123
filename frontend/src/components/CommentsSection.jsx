import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { commentsService, userService } from '../services/api'
import './CommentsSection.css'

const CommentsSection = ({ parentType, parentId }) => {
  const { user } = useAuth()
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [userNames, setUserNames] = useState({})
  const [userNamesLoading, setUserNamesLoading] = useState({})

  useEffect(() => {
    fetchComments()
  }, [parentType, parentId])

  // Функция для загрузки информации о пользователе
  const fetchUserName = useCallback(async (userId) => {
    // Если имя уже загружено или загружается, пропускаем
    if (userNames[userId] || userNamesLoading[userId]) {
      return;
    }

    try {
      // Помечаем пользователя как загружаемого
      setUserNamesLoading(prev => ({ ...prev, [userId]: true }))
      
      const response = await userService.getUserInfo(userId)
      const userName = response.data.name || `Пользователь ${userId}`
      
      // Обновляем состояние с именем пользователя
      setUserNames(prev => ({ ...prev, [userId]: userName }))
    } catch (error) {
      console.error(`Ошибка загрузки пользователя ${userId}:`, error)
      // В случае ошибки используем заглушку
      setUserNames(prev => ({ ...prev, [userId]: `Пользователь ${userId}` }))
    } finally {
      // Убираем из загружаемых
      setUserNamesLoading(prev => {
        const newState = { ...prev }
        delete newState[userId]
        return newState
      })
    }
  }, [userNames, userNamesLoading])

  const fetchComments = async () => {
    setLoading(true)
    try {
      let response
      if (parentType === 'task') {
        response = await commentsService.getTaskComments(parentId)
      } else {
        response = await commentsService.getTheoryComments(parentId)
      }
      
      setComments(response.data)
      
      // Загружаем имена пользователей для всех комментариев
      const userIds = [...new Set(response.data.map(comment => comment.user_id))]
      userIds.forEach(userId => {
        fetchUserName(userId)
      })
    } catch (error) {
      console.error('Ошибка загрузки комментариев:', error)
    } finally {
      setLoading(false)
    }
  }

  const getUserName = (userId) => {
    return userNames[userId] || `Пользователь ${userId}`
  }

  const handleSubmitComment = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return

    setSubmitting(true)
    try {
      if (parentType === 'task') {
        await commentsService.addTaskComment(parentId, {
          description: newComment
        })
      } else {
        await commentsService.addTheoryComment(parentId, {
          description: newComment
        })
      }
      
      setNewComment('')
      fetchComments() // Обновляем комментарии
    } catch (error) {
      console.error('Ошибка добавления комментария:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Удалить комментарий?')) return

    try {
      await commentsService.deleteComment(commentId)
      fetchComments()
    } catch (error) {
      console.error('Ошибка удаления комментария:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU')
  }

  return (
    <div className="comments-section">
      <div className="comments-header">
        <h3>Комментарии</h3>
        <div className="comments-count">{comments.length} комментариев</div>
      </div>

      <div className="comments-scroll-container">
        {user && (
          <form onSubmit={handleSubmitComment} className="comment-form">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Оставьте ваш комментарий..."
              rows="3"
              disabled={submitting}
            />
            <button 
              type="submit" 
              disabled={!newComment.trim() || submitting}
              className="submit-comment-btn"
            >
              {submitting ? 'Отправка...' : 'Отправить'}
            </button>
          </form>
        )}

        <div className="comments-content">
          {loading ? (
            <div className="loading">Загрузка комментариев...</div>
          ) : comments.length === 0 ? (
            <div className="no-comments">
              <div className="no-comments-icon">💬</div>
              <p>Комментариев пока нет</p>
              {user && <p>Будьте первым, кто оставит комментарий!</p>}
            </div>
          ) : (
            comments.map(comment => (
              <div key={comment.comment_id} className="comment-item">
                <div className="comment-header">
                  <span className="comment-author">
                    {getUserName(comment.user_id)}
                    {userNamesLoading[comment.user_id] && (
                      <span className="loading-dots">...</span>
                    )}
                  </span>
                  <span className="comment-date">
                    {formatDate(comment.date)}
                  </span>
                  {user && user.user_id === comment.user_id && (
                    <button
                      onClick={() => handleDeleteComment(comment.comment_id)}
                      className="delete-comment-btn"
                      title="Удалить комментарий"
                    >
                      ×
                    </button>
                  )}
                </div>
                <div className="comment-text">
                  {comment.description}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default CommentsSection