from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt() # для хэширования пароля

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def __init__(self, name, login, email, password):
        self.name = name
        self.login = login
        self.email = email
        self.role = 'user'
        self.password_hash = self._set_password(password)

    def _set_password(self, password):
        # bcrypt для безопасного хеширования
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'login': self.login,
            'email': self.email,
            'role': self.role
        }
