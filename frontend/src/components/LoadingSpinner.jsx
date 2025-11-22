import React from 'react'
import './LoadingSpinner.css'

const LoadingSpinner = ({ message = 'Загрузка...' }) => {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  )
}

export default LoadingSpinner