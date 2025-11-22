import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Настройка скл алхимии для БД
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30) # Время жизни токена доступа
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7) # Время жизни токена обновления
    
    CORE_SERVICE_URL = os.environ.get('CORE_SERVICE_URL')
    FRONT_SERVICE_URI = os.environ.get('FRONT_SERVICE_URI')