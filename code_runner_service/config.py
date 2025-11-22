import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Настройки psql (подключаемся к БД)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки RabbitMQ
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
    RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT'))
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Имя очереди для прослушивания кода на исполнение
    RABBITMQ_QUEUE_CODE_RUNNER = 'code_submission_queue'
    
    # Имя очереди для результатов куда публикуем
    RABBITMQ_QUEUE_RESULTS = 'code_results_queue'