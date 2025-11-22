import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Настройки RabbitMQ
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
    RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT'))
    
    # Очередь, которую мы СЛУШАЕМ (результаты от Runner)
    RABBITMQ_QUEUE_RESULTS = 'code_results_queue'
    
    # Настройки SocketIO:
    # 1. Message Queue URL: SocketIO должен использовать тот же брокер (RabbitMQ) 
    #    для рассылки сообщений между рабочими процессами (workers).
    #    Используем amqp:// для RabbitMQ
    #    Формат: amqp://user:password@host:port/vhost
    #    Пока используем гостевой доступ:
    SOCKETIO_MESSAGE_QUEUE = f'amqp://guest:guest@{RABBITMQ_HOST}:5672//'
    
    # NOTE: SocketIO использует Redis или RabbitMQ как "брокер сообщений" 
    # для своих внутренних нужд, это не то же самое, что очередь задач! 
    # Это позволяет масштабировать Flask-SocketIO.