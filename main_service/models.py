from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# таблица Theme
class Theme(db.Model):
    __tablename__ = 'theme'
    theme_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    parent_theme_id = db.Column(db.Integer, db.ForeignKey('theme.theme_id'), nullable=True)
    
    # Рекурсивная связь для иерархии
    parent_theme = db.relationship('Theme', remote_side=[theme_id], backref='subthemes')

#----------------------------------------------------------------------------------------------------

# таблица AlgorythmTheories (Теория)
class AlgorythmTheory(db.Model):
    __tablename__ = 'algorythmtheories'
    theory_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.theme_id'), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    theme = db.relationship('Theme', backref=db.backref('theory', uselist=False))

#----------------------------------------------------------------------------------------------------

#таблица Tasks (Задачи)
class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.theme_id'), nullable=False)
    title = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False) # 'EASY', 'MEDIUM', 'HARD'
    time_limit_ms = db.Column(db.Integer, nullable=False)
    memory_limit_mb = db.Column(db.Integer, nullable=False)
    
    theme = db.relationship('Theme', backref='tasks')
    
#----------------------------------------------------------------------------------------------------

#таблица TaskTestCases (Тесты для задач)
class TaskTestCase(db.Model):
    __tablename__ = 'tasktestcases'
    test_case_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_example = db.Column(db.Boolean, nullable=False, default=False)
    
    task = db.relationship('Task', backref='test_cases')
    
    __table_args__ = (
        db.UniqueConstraint('task_id', 'input_data', 'expected_output', name='idx_unique_test_case'),
    )

#----------------------------------------------------------------------------------------------------

# таблица Submissions (Попытки)
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
    
    task = db.relationship('Task', backref='submissions')
    
    __table_args__ = (
        db.Index('idx_user_task_complete', 'user_id', 'is_complete'),
    )
    
#----------------------------------------------------------------------------------------------------

# таблицы Comments (комментариев)
class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.current_timestamp())
    description = db.Column(db.Text, nullable=False)

class TaskComment(db.Model):
    __tablename__ = 'taskcomments'
    task_comment_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    comment_id = db.Column(db.BigInteger, db.ForeignKey('comments.comment_id'), unique=True, nullable=False)
    
    comment = db.relationship('Comment', backref=db.backref('task_link', uselist=False))

class TheoryComment(db.Model):
    __tablename__ = 'theorycomments'
    theory_comment_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    theory_id = db.Column(db.Integer, db.ForeignKey('algorythmtheories.theory_id'), nullable=False)
    comment_id = db.Column(db.BigInteger, db.ForeignKey('comments.comment_id'), unique=True, nullable=False)
    
    comment = db.relationship('Comment', backref=db.backref('theory_link', uselist=False))
