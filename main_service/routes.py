from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, TaskTestCase, Submission, AlgorythmTheory, Theme, Comment, TaskComment, TheoryComment
from rabbitmq_producer import publish_submission_task
from flask import current_app
import json
from sqlalchemy import func, case
import requests

main_bp = Blueprint('main', __name__)

# Получение задач
@main_bp.route('/tasks/', methods=['GET'])
def get_tasks_details():
    tasks = Task.query.all()
    if not tasks:
        return jsonify({"msg": "Задачи не найдена"}), 404
    
    tasks_data = []
    
    for task in tasks:
        task_data = {
            "task_id": task.task_id,
            "title": task.title,
            "difficulty_level": task.difficulty_level,
            "theme_id": task.theme_id,
            "theme_title": task.theme.title if task.theme else None
        }
        tasks_data.append(task_data)
    
    return jsonify(tasks_data), 200


# Получение задачи
@main_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_details(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"msg": "Задача не найдена"}), 404

    example_tests = TaskTestCase.query.filter_by(task_id=task_id, is_example=True).all()
    
    task_data = {
        "task_id": task.task_id,
        "title": task.title,
        "description": task.description,
        "difficulty_level": task.difficulty_level,
        "time_limit_ms": task.time_limit_ms,
        "memory_limit_mb": task.memory_limit_mb,
        "example_tests": [{
            "input": t.input_data, 
            "output": t.expected_output
        } for t in example_tests]
    }
    
    return jsonify(task_data), 200


# Отправка кода на выполнение
@main_bp.route('/submit_code', methods=['POST'])
@jwt_required() 
def submit_code():
    data = request.get_json()
    user_id = get_jwt_identity() 
    task_id = data.get('task_id')
    code = data.get('code')
    language = data.get('language', 'python') 
    print("Перед ифами")
    if not task_id:
        return jsonify({"msg": "Отсутствуют задача"}), 400
    
    if not code:
        return jsonify({"msg": "Отсутствуют выполняемый код"}), 400

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"msg": "Задача с таким ID не найдена"}), 404
    print("Перед try")
    try:
        #Сохраненфем попытку в БД
        print(user_id, task_id, code)
        new_submission = Submission(
            user_id=user_id,
            task_id=task_id,
            code=code,
            is_complete=False, 
            status='PENDING',
            language=language
        )
        print("перед add")
        db.session.add(new_submission)
        print("перед flush")
        db.session.flush() 
        print("Сохранено в бд")
        submission_id = new_submission.submission_id

        #Отправка асинхронной задачи в RabbitM
        success = publish_submission_task(
            submission_id=submission_id,
            task_id=task_id,
            user_id=user_id,
            code=code,
            language=language
        )
        
        if success:
            db.session.commit()
            return jsonify({
                "msg": "Код отправлен на проверку. Ожидайте результата.",
                "submission_id": submission_id,
                "user_id": user_id 
            }), 202 
        else:
            db.session.rollback()
            return jsonify({"msg": "Сервис исполнения кода временно недоступен (RabbitMQ ошибка)"}), 503
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Внутренняя ошибка сервера"}), 500


# Получить теорию по теме
@main_bp.route('/theory/<int:theme_id>', methods=['GET'])
def get_theory(theme_id):
    theory = AlgorythmTheory.query.filter_by(theme_id=theme_id).first()
    if not theory:
        return jsonify({'msg': 'Теория не найдена'}), 404
    return jsonify({
        'theory_id': theory.theory_id,
        'theme_id': theory.theme_id,
        'description': theory.description
    }), 200

# Отметить задачу решённой
@main_bp.route('/mark_solved', methods=['POST'])
def mark_solved():
    data = request.get_json()
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    if not user_id or not task_id:
        return jsonify({'msg': 'user_id и task_id обязательны'}), 400

    try:
        s = Submission(user_id=user_id, task_id=task_id,
                       code='/*marked by frontend*/',
                       is_complete=True, status='ACCEPTED')
        db.session.add(s)
        db.session.commit()
        return jsonify({'msg': 'Отмечено как решенное'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Ошибка сервера', 'error': str(e)}), 500

# Получить список решённых задач пользователя
@main_bp.route('/user_solved/<int:user_id>', methods=['GET'])
def user_solved(user_id):
    solved = Submission.query.filter_by(user_id=user_id, is_complete=True).all()
    solved_ids = [s.task_id for s in solved]
    return jsonify({'solved_task_ids': solved_ids}), 200


# Получение всех тем
@main_bp.route('/themes/', methods=['GET'])
def get_themes():
    themes = Theme.query.all()
    themes_data = [{
        'theme_id': theme.theme_id,
        'title': theme.title,
        'parent_theme_id': theme.parent_theme_id
    } for theme in themes]
    return jsonify(themes_data), 200

# Получение задач с фильтрацией
@main_bp.route('/tasks/filter', methods=['GET'])
def get_filtered_tasks():
    theme_id = request.args.get('theme_id', type=int)
    difficulty = request.args.get('difficulty')
    
    query = Task.query
    
    if theme_id:
        query = query.filter_by(theme_id=theme_id)
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    tasks = query.all()
    tasks_data = []
    
    for task in tasks:
        tasks_data.append({
            "task_id": task.task_id,
            "theme_id": task.theme_id,
            "title": task.title,
            "difficulty_level": task.difficulty_level
        })
    
    return jsonify(tasks_data), 200

@main_bp.route('/user_submissions/<int:user_id>/<int:task_id>', methods=['GET'])
@jwt_required()
def get_user_task_submissions(user_id, task_id):
    try:
        submissions = Submission.query.filter_by(
            user_id=user_id, 
            task_id=task_id
        ).order_by(Submission.date.desc()).all()
        
        result = []
        for submission in submissions:
            result.append({
                'submission_id': submission.submission_id,
                'date': submission.date.isoformat(),
                'code': submission.code,
                'language': submission.language,
                'status': submission.status,
                'is_complete': submission.is_complete,
                'run_time': submission.run_time
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'msg': f'Error fetching submissions: {str(e)}'}), 500
    
# Профиль пользователя со статистикой
@main_bp.route('/profile/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    try:
        current_user_id = get_jwt_identity()
        if int(current_user_id) != user_id:
            return jsonify({'msg': 'Доступ запрещен'}), 403

        # Общее количество решенных задач
        total_solved = db.session.query(func.count(Submission.task_id.distinct())).filter(
            Submission.user_id == user_id,
            Submission.is_complete == True
        ).scalar()

        # Статистика по сложности
        difficulty_stats = db.session.query(
            Task.difficulty_level,
            func.count(Submission.task_id.distinct()).label('solved_count')
        ).join(Submission, Submission.task_id == Task.task_id).filter(
            Submission.user_id == user_id,
            Submission.is_complete == True
        ).group_by(Task.difficulty_level).all()

        # Статистика по темам
        theme_stats = db.session.query(
            Theme.theme_id,
            Theme.title,
            func.count(Submission.task_id.distinct()).label('solved_count')
        ).join(Task, Task.theme_id == Theme.theme_id).join(
            Submission, Submission.task_id == Task.task_id
        ).filter(
            Submission.user_id == user_id,
            Submission.is_complete == True
        ).group_by(Theme.theme_id, Theme.title).all()

        # Преобразуем статистику по сложности в удобный формат
        difficulty_dict = {stat.difficulty_level: stat.solved_count for stat in difficulty_stats}

        profile_data = {
            'user_id': user_id,
            'statistics': {
                'total_solved': total_solved or 0,
                'easy_solved': difficulty_dict.get('EASY', 0),
                'medium_solved': difficulty_dict.get('MEDIUM', 0),
                'hard_solved': difficulty_dict.get('HARD', 0),
                'by_theme': [{
                    'theme_id': theme.theme_id,
                    'title': theme.title,
                    'solved_count': theme.solved_count
                } for theme in theme_stats]
            }
        }

        return jsonify(profile_data), 200
    except Exception as e:
        return jsonify({'msg': f'Error fetching profile: {str(e)}'}), 500

# Получение комментариев к теории
@main_bp.route('/theory/<int:theory_id>/comments', methods=['GET'])
def get_theory_comments(theory_id):
    try:
        comments = db.session.query(
            Comment.comment_id,
            Comment.user_id,
            Comment.date,
            Comment.description
        ).join(
            TheoryComment, TheoryComment.comment_id == Comment.comment_id
        ).filter(
            TheoryComment.theory_id == theory_id
        ).order_by(Comment.date.desc()).all()
        
        result = []
        for comment in comments:
            result.append({
                'comment_id': comment.comment_id,
                'user_id': comment.user_id,
                'date': comment.date.isoformat(),
                'description': comment.description
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'msg': f'Error fetching comments: {str(e)}'}), 500

# Получение комментариев к задаче
@main_bp.route('/tasks/<int:task_id>/comments', methods=['GET'])
def get_task_comments(task_id):
    try:
        comments = db.session.query(
            Comment.comment_id,
            Comment.user_id,
            Comment.date,
            Comment.description
        ).join(
            TaskComment, TaskComment.comment_id == Comment.comment_id
        ).filter(
            TaskComment.task_id == task_id
        ).order_by(Comment.date.desc()).all()
        
        result = []
        for comment in comments:
            result.append({
                'comment_id': comment.comment_id,
                'user_id': comment.user_id,
                'date': comment.date.isoformat(),
                'description': comment.description
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'msg': f'Error fetching comments: {str(e)}'}), 500

# Добавление комментария к задаче
@main_bp.route('/tasks/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def add_task_comment(task_id):
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Создаем комментарий
        new_comment = Comment(
            user_id=user_id,
            description=data['description']
        )
        
        db.session.add(new_comment)
        db.session.flush()  # Получаем comment_id
        
        # Создаем связь с задачей
        task_comment = TaskComment(
            task_id=task_id,
            comment_id=new_comment.comment_id
        )
        db.session.add(task_comment)
        db.session.commit()
        
        return jsonify({
            'msg': 'Комментарий добавлен',
            'comment_id': new_comment.comment_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error adding comment: {str(e)}'}), 500

# Добавление комментария к теории
@main_bp.route('/theory/<int:theory_id>/comments', methods=['POST'])
@jwt_required()
def add_theory_comment(theory_id):
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Создаем комментарий
        new_comment = Comment(
            user_id=user_id,
            description=data['description']
        )
        
        db.session.add(new_comment)
        db.session.flush()  # Получаем comment_id
        
        # Создаем связь с теорией
        theory_comment = TheoryComment(
            theory_id=theory_id,
            comment_id=new_comment.comment_id
        )
        db.session.add(theory_comment)
        db.session.commit()
        
        return jsonify({
            'msg': 'Комментарий добавлен',
            'comment_id': new_comment.comment_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error adding comment: {str(e)}'}), 500

# Удаление комментария
@main_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'msg': 'Комментарий не найден'}), 404
            
        if comment.user_id != int(user_id):
            return jsonify({'msg': 'Недостаточно прав'}), 403
        
        # Удаляем связь из taskcomments или theorycomments
        task_comment = TaskComment.query.filter_by(comment_id=comment_id).first()
        theory_comment = TheoryComment.query.filter_by(comment_id=comment_id).first()
        
        if task_comment:
            db.session.delete(task_comment)
        elif theory_comment:
            db.session.delete(theory_comment)
        else:
            return jsonify({'msg': 'Связь комментария не найдена'}), 404
            
        # Удаляем сам комментарий
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'msg': 'Комментарий удален'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error deleting comment: {str(e)}'}), 500

@main_bp.route('/user_info/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    try:
        # Делаем запрос к auth_service для получения информации о пользователе
        auth_service_url = f"http://auth_service:5000/api/auth/user/{user_id}"
        response = requests.get(auth_service_url)
        
        if response.status_code == 200:
            user_data = response.json()
            return jsonify({
                'user_id': user_data.get('user_id'),
                'name': user_data.get('name'),
                'login': user_data.get('login'),
                'email': user_data.get('email')
            }), 200
        else:
            # Если запрос к auth_service не удался, возвращаем заглушку
            return jsonify({
                'user_id': user_id,
                'name': f'Пользователь {user_id}'
            }), 200
            
    except Exception as e:
        print(f"Error fetching user info from auth service: {e}")
        return jsonify({
            'user_id': user_id,
            'name': f'Пользователь {user_id}'
        }), 200