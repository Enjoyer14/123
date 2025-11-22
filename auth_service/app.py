from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import db, bcrypt
from routes import auth_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    migrate = Migrate(app, db) # Инициализация миграций для БД
    jwt = JWTManager(app) #инициализация JWT
    
    # CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://frontend.com"]}}, supports_credentials=True) # доступ только с моего фронта
    CORS(app)


    # регистрация блюпринта для роутов
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Обработчик ошибки для недействительных токенов
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({'msg': 'Токен отсутствует или недействителен'}), 401
    
    # Обработчик ошибки для токенов с истекшим сроком годности
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        # Если access_token истек, клиент должен использовать refresh
        return jsonify({'msg': 'Срок действия токена истек', 'expired': True}), 401

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000) # ПОТОМ ПОМЕНЯТЬ НА gunicorn или uWSGI

