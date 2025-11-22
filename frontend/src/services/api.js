import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001/api/main'
const AUTH_BASE_URL = 'http://localhost:5000/api/auth'

// Создаем экземпляры axios с базовыми URL
export const authAPI = axios.create({
  baseURL: AUTH_BASE_URL
})

export const mainAPI = axios.create({
  baseURL: API_BASE_URL
})

// Интерцептор для автоматической подстановки токена в authAPI
authAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерцептор для автоматической подстановки токена в mainAPI
mainAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Общий интерцептор для обработки ошибок 401
const handleAuthError = async (error) => {
  if (error.response?.status === 401) {
    // Токен истек, пытаемся обновить
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        // Используем authAPI без интерцептора, чтобы избежать рекурсии
        const response = await axios.post(`${AUTH_BASE_URL}/refresh`, {}, {
          headers: {
            Authorization: `Bearer ${refreshToken}`
          }
        })
        const newToken = response.data.access_token
        localStorage.setItem('access_token', newToken)
        // Повторяем исходный запрос с новым токеном
        error.config.headers.Authorization = `Bearer ${newToken}`
        return axios(error.config)
      } catch (refreshError) {
        // Не удалось обновить токен, перенаправляем на страницу входа
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_data')
        window.location.href = '/login'
      }
    } else {
      // Нет refresh токена, перенаправляем на страницу входа
      window.location.href = '/login'
    }
  }
  return Promise.reject(error)
}

// Добавляем интерцептор ответа для authAPI
authAPI.interceptors.response.use(
  (response) => response,
  handleAuthError
)

// Добавляем интерцептор ответа для mainAPI
mainAPI.interceptors.response.use(
  (response) => response,
  handleAuthError
)

// API методы
export const taskService = {
  getTasks: () => mainAPI.get('/tasks/'),
  getTask: (id) => mainAPI.get(`/tasks/${id}`),
  submitCode: (data) => mainAPI.post('/submit_code', data),
  getThemes: () => mainAPI.get('/themes/'),
  getUserSolved: (userId) => mainAPI.get(`/user_solved/${userId}`),
  getTheory: (themeId) => mainAPI.get(`/theory/${themeId}`),
  markSolved: (data) => mainAPI.post('/mark_solved', data),
  getUserTaskSubmissions: (userId, taskId) => mainAPI.get(`/user_submissions/${userId}/${taskId}`)
}

export const authService = {
  login: (credentials) => authAPI.post('/login', credentials),
  register: (userData) => authAPI.post('/register', userData),
  refresh: (refreshToken) => authAPI.post('/refresh', {}, {
    headers: {
      Authorization: `Bearer ${refreshToken}`
    }
  }),
  updateProfile: (data) => authAPI.put('/profile', data)
}

// Добавляем новые методы для работы с комментариями и пользователями
export const commentsService = {
  getTaskComments: (taskId) => mainAPI.get(`/tasks/${taskId}/comments`),
  getTheoryComments: (theoryId) => mainAPI.get(`/theory/${theoryId}/comments`),
  addTaskComment: (taskId, data) => mainAPI.post(`/tasks/${taskId}/comments`, data),
  addTheoryComment: (theoryId, data) => mainAPI.post(`/theory/${theoryId}/comments`, data),
  deleteComment: (commentId) => mainAPI.delete(`/comments/${commentId}`)
}

export const userService = {
  getUserInfo: (userId) => mainAPI.get(`/user_info/${userId}`)
}

export const profileService = {
  getProfile: (userId) => mainAPI.get(`/profile/${userId}`)
}