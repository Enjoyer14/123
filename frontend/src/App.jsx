import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { WebSocketProvider } from './contexts/WebSocketContext'
import Login from './pages/Login'
import Register from './pages/Register'
import TaskList from './pages/TaskList'
import TaskDetail from './pages/TaskDetail'
import Theory from './pages/Theory'
import Profile from './pages/Profile';
import './App.css'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="loading">Загрузка...</div>
  }
  
  return user ? children : <Navigate to="/login" />
}

function App() {
  return (
    <AuthProvider>
      <WebSocketProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route 
                path="/tasks" 
                element={
                  <ProtectedRoute>
                    <TaskList />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/task/:taskId" 
                element={
                  <ProtectedRoute>
                    <TaskDetail />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/theory/:themeId" 
                element={
                  <ProtectedRoute>
                    <Theory />
                  </ProtectedRoute>
                } 
              />
              <Route path="/" element={<Navigate to="/tasks" />} />
              <Route
                path="/profile"
                element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
                }
              />
              </Routes>
          </div>
        </Router>
      </WebSocketProvider>
    </AuthProvider>
  )
}

export default App