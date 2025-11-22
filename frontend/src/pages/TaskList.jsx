import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { taskService } from '../services/api'
import Header from '../components/Header'
import LoadingSpinner from '../components/LoadingSpinner'
import { DIFFICULTY_LEVELS } from '../utils/constants'
import './TaskList.css'

const TaskList = () => {
  const [tasks, setTasks] = useState([])
  const [themes, setThemes] = useState([])
  const [solvedTasks, setSolvedTasks] = useState(new Set())
  const [filter, setFilter] = useState('all')
  const [difficulty, setDifficulty] = useState('all')
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    fetchTasks()
    fetchThemes()
    fetchSolvedTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      const response = await taskService.getTasks()
      setTasks(response.data)
    } catch (error) {
      console.error('Ошибка загрузки задач:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchThemes = async () => {
    try {
      const response = await taskService.getThemes()
      setThemes(response.data)
    } catch (error) {
      console.error('Ошибка загрузки тем:', error)
    }
  }

  const fetchSolvedTasks = async () => {
    try {
      const response = await taskService.getUserSolved(user.user_id)
      setSolvedTasks(new Set(response.data.solved_task_ids))
    } catch (error) {
      console.error('Ошибка загрузки решенных задач:', error)
    }
  }

  const getTheoryLink = (themeId) => {
    return `/theory/${themeId}`
  }

  const filteredTasks = tasks.filter(task => {
    const matchesTheme = filter === 'all' || task.theme_id == filter
    const matchesDifficulty = difficulty === 'all' || task.difficulty_level === difficulty
    return matchesTheme && matchesDifficulty
  })

  if (loading) {
    return <LoadingSpinner message="Загрузка задач..." />
  }

  return (
    <div className="task-list-container">
      <Header />

      <div className="filters">
        <div className="filter-group">
          <label>Тема:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">Все темы</option>
            {themes.map(theme => (
              <option key={theme.theme_id} value={theme.theme_id}>
                {theme.title}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Сложность:</label>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="all">Все уровни</option>
            {Object.entries(DIFFICULTY_LEVELS).map(([key, { label }]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="tasks-grid">
        {filteredTasks.map(task => (
          <div key={task.task_id} className="task-card">
            <div className="task-header">
              <h3>{task.title}</h3>
              <span 
                className="difficulty"
                style={{ 
                  backgroundColor: DIFFICULTY_LEVELS[task.difficulty_level]?.color || '#6c757d',
                  color: 'white'
                }}
              >
                {DIFFICULTY_LEVELS[task.difficulty_level]?.label || task.difficulty_level}
              </span>
            </div>
            
            <div className="task-theme">
              Тема: {themes.find(t => t.theme_id === task.theme_id)?.title || 'Неизвестно'}
              <Link to={getTheoryLink(task.theme_id)} className="theory-link">
                Теория
              </Link>
            </div>

            <div className="task-status">
              {solvedTasks.has(task.task_id) ? (
                <span className="solved">✓ Решена</span>
              ) : (
                <span className="unsolved">Не решена</span>
              )}
            </div>

            <Link to={`/task/${task.task_id}`} className="solve-btn">
              Решить
            </Link>
          </div>
        ))}
      </div>

      {filteredTasks.length === 0 && (
        <div className="no-tasks">Задачи не найдены</div>
      )}
    </div>
  )
}

export default TaskList