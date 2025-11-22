from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Модель для чтения ограничений и метаданных задачи
class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.theme_id'), nullable=False)
    title = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False) # 'EASY', 'MEDIUM', 'HARD'
    time_limit_ms = db.Column(db.Integer, nullable=False)
    memory_limit_mb = db.Column(db.Integer, nullable=False)
    
    # Связь с тестовыми случаями
    test_cases = db.relationship('TaskTestCase', backref='task', lazy=True)

# Модель для чтения входных/ожидаемых данных
class TaskTestCase(db.Model):
    __tablename__ = 'tasktestcases'
    test_case_id = db.Column(db.BigInteger, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_example = db.Column(db.Boolean, nullable=False, default=False)
    
# Модель для обновления статуса попытки
class Submission(db.Model):
    __tablename__ = 'submissions'
    submission_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False) # Здесь мы НЕ ставим ForeignKey, так как таблица Users в другом сервисе (Auth)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.current_timestamp())
    code = db.Column(db.Text, nullable=False)
    is_complete = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(50), nullable=True)
    run_time = db.Column(db.Integer, nullable=True) 
    memory_used = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(50), nullable=True)