import React, { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { useAuth } from '../contexts/AuthContext'
import { useWebSocket } from '../contexts/WebSocketContext'
import { taskService } from '../services/api'
import Header from '../components/Header'
import LoadingSpinner from '../components/LoadingSpinner'
import CommentsSection from '../components/CommentsSection'
import { LANGUAGES, SUBMISSION_STATUS } from '../utils/constants'
import './TaskDetail.css'

const TaskDetail = () => {
  const { taskId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { socket, isConnected } = useWebSocket()
  
  const [showComments, setShowComments] = useState(false)
  const [task, setTask] = useState(null)
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [nextTaskId, setNextTaskId] = useState(null)
  const [showHistory, setShowHistory] = useState(false)
  const [submissions, setSubmissions] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(false)

  // Функция для преобразования \n в настоящие переносы строк
  const formatTextWithNewlines = (text) => {
    if (typeof text !== 'string') return text;
    return text.replace(/\\n/g, '\n');
  };

  // Сбрасываем все состояния при изменении taskId
  useEffect(() => {
    setTask(null)
    setCode('')
    setLanguage('python')
    setResult(null)
    setLoading(false)
    setSubmitting(false)
    setNextTaskId(null)
    setShowHistory(false)
    setSubmissions([])
    
    // Устанавливаем начальный код для новой задачи
    setInitialCode()
    
    // Загружаем новую задачу
    fetchTask()
  }, [taskId])

  // Используем useCallback для стабильной функции
  const handleSubmissionResult = useCallback((data) => {
    console.log('Received submission result:', data)
    setResult(data)
    setSubmitting(false)
    
    // После получения результата обновляем историю
    if (user && taskId) {
      fetchSubmissions();
    }
    
    if (data.status === 'ACCEPTED' && data.next_task_id) {
      setNextTaskId(data.next_task_id)
    }
  }, [user, taskId])

  useEffect(() => {
    fetchTask()
  }, [taskId])

  useEffect(() => {
    setInitialCode()
  }, [language])

  // Настройка WebSocket слушателей
  useEffect(() => {
    if (!socket || !isConnected) return

    console.log('Setting up WebSocket listeners for task:', taskId)
    
    // Убираем старые слушатели перед добавлением новых
    socket.off('submission_result', handleSubmissionResult)
    socket.on('submission_result', handleSubmissionResult)

    // Очистка при размонтировании
    return () => {
      if (socket) {
        console.log('Cleaning up WebSocket listeners')
        socket.off('submission_result', handleSubmissionResult)
      }
    }
  }, [socket, isConnected, taskId, handleSubmissionResult])

  const setInitialCode = () => {
    const templates = {
      python: '# Напишите ваш код здесь\n# Функция должна читать входные данные из input()\n# и возвращать результат через print()\n\ndef main():\n    # Чтение входных данных\n    data = input().strip()\n    # Ваше решение здесь\n    print(data)\n\nif __name__ == "__main__":\n    main()',
      javascript: '// Напишите ваш код здесь\n// Функция должна читать входные данные из process.stdin\n// и возвращать результат через console.log\n\nconst readline = require("readline");\n\nconst rl = readline.createInterface({\n  input: process.stdin,\n  output: process.stdout\n});\n\nrl.on("line", (input) => {\n  // Ваше решение здесь\n  console.log(input);\n  rl.close();\n});',
      cpp: '// Напишите ваш код здесь\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Чтение входных данных\n    string input;\n    getline(cin, input);\n    // Ваше решение здесь\n    cout << input << endl;\n    return 0;\n}'
    }
    setCode(templates[language] || templates.python)
  }

  const fetchTask = async () => {
    try {
      setLoading(true)
      const response = await taskService.getTask(taskId)
      setTask(response.data)
    } catch (error) {
      console.error('Ошибка загрузки задачи:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSubmissions = async () => {
    if (!user || !taskId) return;
    
    try {
      setLoadingHistory(true)
      // Предполагаем, что у нас есть endpoint для получения отправлений пользователя по задаче
      const response = await taskService.getUserTaskSubmissions(user.user_id, taskId)
      setSubmissions(response.data)
    } catch (error) {
      console.error('Ошибка загрузки истории:', error)
    } finally {
      setLoadingHistory(false)
    }
  }

  const handleShowHistory = () => {
    setShowHistory(true)
    fetchSubmissions()
  }

  const handleCloseHistory = () => {
    setShowHistory(false)
  }

  const loadSubmissionCode = (submissionCode, submissionLanguage) => {
    setCode(submissionCode)
    setLanguage(submissionLanguage)
    setShowHistory(false)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('ru-RU')
  }

  const getStatusDisplay = (status) => {
    return SUBMISSION_STATUS[status] || status
  }

  const getStatusClass = (status) => {
    switch (status) {
      case 'ACCEPTED': return 'status-accepted'
      case 'WRONG_ANSWER': return 'status-wrong'
      case 'TIME_LIMIT_EXCEEDED': return 'status-timeout'
      case 'RUNTIME_ERROR': return 'status-error'
      case 'COMPILATION_ERROR': return 'status-error'
      default: return 'status-pending'
    }
  }

  const handleSubmit = async () => {
    if (!code.trim()) {
      alert('Код не может быть пустым')
      return
    }

    if (submitting) {
      console.log('Already submitting, skipping...')
      return
    }

    setSubmitting(true)
    setResult(null)
    setNextTaskId(null)

    console.log('Submitting code for task:', taskId)

    try {
      const response = await taskService.submitCode({
        task_id: parseInt(taskId),
        code: code,
        language: language
      })

      console.log('Код отправлен на проверку:', response.data)
    } catch (error) {
      console.error('Ошибка отправки кода:', error)
      setResult({
        status: 'ERROR',
        error: error.response?.data?.msg || 'Ошибка отправки кода'
      })
      setSubmitting(false)
    }
  }

  const handleNextTask = () => {
    if (nextTaskId) {
      navigate(`/task/${nextTaskId}`)
    }
  }

  const getStatusMessage = (status) => {
    const statusMessages = {
      'ACCEPTED': 'Задача успешно решена!',
      'WRONG_ANSWER': 'Неверный ответ',
      'TIME_LIMIT_EXCEEDED': 'Превышено время выполнения',
      'RUNTIME_ERROR': 'Ошибка выполнения',
      'COMPILATION_ERROR': 'Ошибка компиляции',
      'INTERNAL_ERROR': 'Внутренняя ошибка системы'
    }
    return statusMessages[status] || status
  }

  if (loading) {
    return <LoadingSpinner message="Загрузка задачи..." />
  }

  if (!task) {
    return (
      <div className="task-detail-container">
        <Header />
        <div className="error-message">
          <h2>Задача не найдена</h2>
          <button onClick={() => navigate('/tasks')} className="back-btn">
            Назад к списку задач
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="task-detail-container">
      <Header />
      
      <div className="task-content">
        <div className="task-info">
          <div className="task-header">
            <button onClick={() => navigate('/tasks')} className="back-btn">
              Назад к списку
            </button>
            <h1>{task.title}</h1>
            {!isConnected && (
              <div className="websocket-warning">
                Соединение с сервером потеряно
              </div>
            )}
          </div>

          <div className="task-description">
            <h3>Условие задачи</h3>
            <div className="description-text">
              {task.description.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
          </div>

          <div className="task-limits">
            <p><strong>Ограничение по времени:</strong> {task.time_limit_ms}ms</p>
            <p><strong>Ограничение по памяти:</strong> {task.memory_limit_mb}MB</p>
            <p><strong>Сложность:</strong> 
              <span className={`difficulty ${task.difficulty_level.toLowerCase()}`}>
                {task.difficulty_level}
              </span>
            </p>
          </div>

          {task.example_tests && task.example_tests.length > 0 && (
            <div className="examples">
              <h3>Примеры:</h3>
              {task.example_tests.map((example, index) => (
                <div key={index} className="example">
                  <div className="example-input">
                    <strong>Входные данные:</strong>
                    <pre>{formatTextWithNewlines(example.input)}</pre>
                  </div>
                  <div className="example-output">
                    <strong>Выходные данные:</strong>
                    <pre>{formatTextWithNewlines(example.output)}</pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="code-section">
          <div className="editor-header">
            <div className="editor-controls">
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                className="language-select"
                disabled={submitting || showHistory || showComments}
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.value} value={lang.value}>
                    {lang.label}
                  </option>
                ))}
              </select>
              
              <button 
                onClick={showHistory ? handleCloseHistory : handleShowHistory}
                className={`history-btn ${showHistory ? 'active' : ''}`}
                title={showHistory ? "Закрыть историю" : "История отправлений"}
              >
                {showHistory ? 'Закрыть историю' : 'История отправлений'}
              </button>
            </div>
            
            {!showHistory && (
              <button 
                onClick={handleSubmit} 
                disabled={submitting || !isConnected}
                className="submit-btn"
              >
                {submitting ? 'Отправка...' : isConnected ? 'Отправить решение' : 'Ожидание соединения...'}
              </button>
            )}
          </div>

          {!showHistory ? (
          // Редактор кода и результаты
          <div className={`editor-and-results ${showComments ? 'with-comments' : ''}`}>
            <div className="editor-area">
              <Editor
                height="100%"
                language={language}
                value={code}
                onChange={setCode}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  automaticLayout: true,
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  readOnly: submitting
                }}
              />
            </div>

              {result && (
                <div className="result-area">
                  <div className={`result ${result.status === 'ACCEPTED' ? 'success' : 'error'}`}>
                    <h4>Результат проверки:</h4>
                    <p><strong>Статус:</strong> {getStatusMessage(result.status)}</p>
                    
                    {result.passed_tests !== undefined && (
                      <p><strong>Тесты:</strong> {result.passed_tests}/{result.total_tests} пройдено</p>
                    )}
                    
                    {result.run_time > 0 && (
                      <p><strong>Время выполнения:</strong> {result.run_time}ms</p>
                    )}

                    {result.memory_used_kb > 0 && (
                      <p><strong>Память:</strong> {result.memory_used_kb} kb</p>
                    )}
                    
                    {result.message && (
                      <div className="result-message">
                        <strong>Сообщение:</strong> {result.message}
                      </div>
                    )}
                    
                    {result.failed_test_input && (
                      <div className="test-details">
                        <div className="failed-test">
                          <strong>Неудачный тест:</strong>
                          <pre>Вход: {formatTextWithNewlines(result.failed_test_input)}</pre>
                          <pre>Ожидалось: {formatTextWithNewlines(result.expected_output)}</pre>
                          <pre>Получено: {formatTextWithNewlines(result.actual_output)}</pre>
                        </div>
                      </div>
                    )}
                    
                    {result.error && (
                      <div className="error-output">
                        <strong>Ошибка:</strong>
                        <pre>{formatTextWithNewlines(result.error)}</pre>
                      </div>
                    )}

                    {/* Блок предложения следующей задачи */}
                    {result.status === 'ACCEPTED' && nextTaskId && (
                      <div className="next-task-suggestion">
                        <div className="next-task-content">
                          <p>🎉 Задача успешно решена! Хотите перейти к следующей задаче?</p>
                          <button onClick={handleNextTask} className="next-task-btn">
                            Перейти к следующей задаче
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Кнопка комментариев под редактором */}
              <div className="comments-toggle-section">
                <button 
                  onClick={() => setShowComments(!showComments)}
                  className={`comments-btn ${showComments ? 'active' : ''}`}
                  disabled={showHistory}
                >
                  {showComments ? '✕ Закрыть комментарии' : '💬 Комментарии'}
                </button>
              </div>

              {/* Панель комментариев */}
              {showComments && (
                <div className="comments-panel">
                  <CommentsSection parentType="task" parentId={taskId} />
                </div>
              )}
            </div>
          ) : (
            // Панель истории отправлений с прокруткой
          <div className="history-container">
            <div className="history-content">
              <h3>История отправлений</h3>
              
              <div className="submissions-list">
                {loadingHistory ? (
                  <div className="history-loading">
                    <LoadingSpinner message="Загрузка истории..." />
                  </div>
                ) : submissions.length === 0 ? (
                  <div className="no-submissions">
                    <p>Нет отправлений для этой задачи</p>
                  </div>
                ) : (
                  submissions.map((submission) => (
                    <div key={submission.submission_id} className="submission-item">
                      <div className="submission-header">
                        <span className="submission-date">
                          {formatDate(submission.date)}
                        </span>
                        <span className={`submission-status ${getStatusClass(submission.status)}`}>
                          {getStatusDisplay(submission.status)}
                        </span>
                      </div>
                      <div className="submission-details">
                        <span className="submission-language">
                          {LANGUAGES.find(lang => lang.value === submission.language)?.label || submission.language}
                        </span>
                        {submission.run_time && (
                          <span className="submission-time">
                            {submission.run_time}ms
                          </span>
                        )}
                        {submission.is_complete && (
                          <span className="submission-complete">✓ Решена</span>
                        )}
                      </div>
                      <div className="submission-code-preview">
                        <pre>{submission.code.substring(0, 200)}{submission.code.length > 200 ? '...' : ''}</pre>
                      </div>
                      <div className="submission-actions">
                        <button 
                          onClick={() => loadSubmissionCode(submission.code, submission.language)}
                          className="load-code-btn"
                        >
                          Загрузить в редактор
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
        </div>
      </div>
    </div>
  )
}

export default TaskDetail