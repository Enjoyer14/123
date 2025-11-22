export const DIFFICULTY_LEVELS = {
  EASY: { 
    label: 'Легкая', 
    color: '#28a745',
    bgColor: '#d4edda',
    textColor: '#155724'
  },
  MEDIUM: { 
    label: 'Средняя', 
    color: '#ffc107',
    bgColor: '#fff3cd',
    textColor: '#856404'
  },
  HARD: { 
    label: 'Сложная', 
    color: '#dc3545',
    bgColor: '#f8d7da',
    textColor: '#721c24'
  }
}

export const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'cpp', label: 'C++' }
]

export const SUBMISSION_STATUS = {
  PENDING: 'В обработке',
  ACCEPTED: 'Принято',
  WRONG_ANSWER: 'Неверный ответ',
  TIME_LIMIT_EXCEEDED: 'Превышено время',
  RUNTIME_ERROR: 'Ошибка выполнения',
  COMPILATION_ERROR: 'Ошибка компиляции',
  INTERNAL_ERROR: 'Внутренняя ошибка'
}