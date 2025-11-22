import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from config import Config
from rabbitmq_consumer import start_rabbitmq_consumer
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": "*"}}) 
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

    @socketio.on('connect')
    def handle_connect():
        logger.info(f'Client connected: {request.sid}')

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f'Client disconnected: {request.sid}')

    @socketio.on('join_submission_room')
    def on_join(data):
        user_id = data.get('user_id')
        if user_id:
            room = f'user_{user_id}'
            join_room(room)
            logger.info(f'Client {request.sid} joined room {room}')
            
    @socketio.on('leave_submission_room')
    def on_leave(data):
        user_id = data.get('user_id')
        if user_id:
            room = f'user_{user_id}'
            leave_room(room)
            logger.info(f'Client {request.sid} left room {room}')

    # Запускаем потребителя RabbitMQ
    start_rabbitmq_consumer(socketio)

    return app, socketio

if __name__ == '__main__':
    logger.info("Starting Notifier Service on port 5003...")
    
    # Бесконечный цикл для переподключения
    while True:
        try:
            app, socketio = create_app()
            logger.info("Notifier Service started successfully")
            socketio.run(app, host='0.0.0.0', port=5003, debug=False, log_output=True)
        except Exception as e:
            logger.error(f"Notifier Service failed: {e}")
            logger.info("Restarting Notifier Service in 10 seconds...")
            time.sleep(10)