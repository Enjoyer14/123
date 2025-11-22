from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, JWTManager

from models import db, User, bcrypt

auth_bp = Blueprint('auth', __name__)

# регистрации нового пользователя
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['name', 'login', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"msg": "Отсутствуют обязательные поля"}), 400

    if User.query.filter_by(login=data['login']).first():
        return jsonify({"msg": "Пользователь с таким логином уже существует"}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Пользователь с таким email уже существует"}), 409
    
    try:
        new_user = User(
            name=data['name'],
            login=data['login'],
            email=data['email'],
            password=data['password'] # пароль будет хеширован в конструкторе (есть функция в классе)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"msg": "Пользователь успешно зарегистрирован", "user_id": new_user.user_id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при регистрации: {e}")
        return jsonify({"msg": "Ошибка регистрации"}), 500

# аутентификации пользователя
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login', None)
    password = data.get('password', None)

    user = User.query.filter_by(login=login).first() #поиск юзера

    # проверка существования пользователя и пароля
    if user and user.check_password(password):
        # Создание JWT токенов
        access_token = create_access_token(identity=str(user.user_id), fresh=True)
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200
    else:
        return jsonify({"msg": "Неверный логин или пароль"}), 401

# Получения нового Access Token с помощью Refresh Token
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # Получаем ID пользователя из Refresh Token
    current_user_id = get_jwt_identity()
    # Создаем новый Access Token
    new_access_token = create_access_token(identity=current_user_id, fresh=False)
    return jsonify({'access_token': new_access_token}), 200

# Обновление профиля пользователя
@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"msg": "Пользователь не найден"}), 404

        # Проверка текущего пароля
        current_password = data.get('current_password')
        if not current_password or not user.check_password(current_password):
            return jsonify({"msg": "Неверный текущий пароль"}), 401

        # Обновление имени, если предоставлено
        if 'new_name' in data:
            new_name = data['new_name'].strip()
            if new_name and new_name != user.name:
                # Проверка уникальности имени (если требуется)
                existing_user = User.query.filter(User.name == new_name, User.user_id != current_user_id).first()
                if existing_user:
                    return jsonify({"msg": "Пользователь с таким именем уже существует"}), 409
                user.name = new_name

        # Обновление пароля, если предоставлено
        if 'new_password' in data:
            new_password = data['new_password'].strip()
            if new_password:
                if len(new_password) < 6:
                    return jsonify({"msg": "Пароль должен содержать минимум 6 символов"}), 400
                user.password_hash = user._set_password(new_password)

        db.session.commit()

        return jsonify({
            "msg": "Профиль успешно обновлен",
            "user": user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при обновлении профиля: {e}")
        return jsonify({"msg": "Ошибка при обновлении профиля"}), 500

# Получение информации о пользователе по ID (для внутреннего использования)
@auth_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "Пользователь не найден"}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return jsonify({"msg": "Ошибка при получении пользователя"}), 500