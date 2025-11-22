export const formatTime = (ms) => {
  return `${ms}ms`
}

export const formatMemory = (kb) => {
  if (kb < 1024) {
    return `${kb} KB`
  } else {
    return `${(kb / 1024).toFixed(2)} MB`
  }
}

export const getDifficultyColor = (level) => {
  switch (level) {
    case 'EASY':
      return '#28a745'
    case 'MEDIUM':
      return '#ffc107'
    case 'HARD':
      return '#dc3545'
    default:
      return '#6c757d'
  }
}