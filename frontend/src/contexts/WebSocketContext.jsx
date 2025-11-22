import React, { createContext, useContext, useState, useEffect } from 'react'
import io from 'socket.io-client'
import { useAuth } from './AuthContext'

const WebSocketContext = createContext()

export const useWebSocket = () => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const { user } = useAuth()

  useEffect(() => {
    if (user) {
      const newSocket = io('http://localhost:5003', {
        transports: ['websocket']
      })
      
      newSocket.on('connect', () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        newSocket.emit('join_submission_room', { user_id: user.user_id })
      })
      
      newSocket.on('disconnect', () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
      })
      
      newSocket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error)
        setIsConnected(false)
      })

      setSocket(newSocket)

      return () => {
        newSocket.disconnect()
      }
    }
  }, [user])

  const value = {
    socket,
    isConnected
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}