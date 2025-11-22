import pika
import json
import time
import logging
from flask import Flask
from config import Config
from models import db, Task, TaskTestCase, Submission
from code_sandbox import execute_code_in_sandbox_docker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

processing_submissions = {}

def get_next_unsolved_task(current_task_id, user_id):
    """Получить следующую нерешенную задачу"""
    with app.app_context():
        try:
            next_tasks = Task.query.filter(
                Task.task_id > current_task_id
            ).order_by(
                Task.task_id.asc()
            ).all()
            
            for task in next_tasks:
                solved_submission = Submission.query.filter_by(
                    user_id=user_id,
                    task_id=task.task_id,
                    is_complete=True
                ).first()
                
                if not solved_submission:
                    return task.task_id
            
            return None
        except Exception as e:
            logger.error(f"Error finding next task: {e}")
            return None

def process_test_cases(code, language, task, user_id, submission_id):
    """Обработать все тестовые случаи задачи"""
    with app.app_context():
        try:
            test_cases = TaskTestCase.query.filter_by(task_id=task.task_id).all()
            
            if not test_cases:
                logger.error(f"No test cases found for task {task.task_id}")
                return {
                    'status': 'INTERNAL_ERROR',
                    'message': 'No test cases found',
                    'passed_tests': 0,
                    'total_tests': 0,
                    'total_execution_time': 0,
                    'max_memory_used_kb': 0
                }

            passed_tests = 0
            failed_test = None
            total_execution_time = 0
            max_memory_used_kb = 0
            
            for i, test_case in enumerate(test_cases):
                logger.info(f"Running test case {i+1}/{len(test_cases)} for submission {submission_id}")
                
                result = execute_code_in_sandbox_docker(
                    code=code,
                    input_data=test_case.input_data,
                    time_limit_ms=task.time_limit_ms,
                    memory_limit_mb=task.memory_limit_mb,
                    language=language
                )
                
                # Суммируем время выполнения всех тестов
                total_execution_time += result.get('execution_time_ms', 0)
                
                # Обновляем максимальное использование памяти
                current_memory = result.get('memory_used_kb', 0)
                if current_memory > max_memory_used_kb:
                    max_memory_used_kb = current_memory
                
                logger.info(f"Test case {i+1} result: {result['status']}, Memory: {current_memory}KB")
                
                # Проверяем статусы, связанные с памятью
                if result['status'] == 'MEMORY_LIMIT_EXCEEDED':
                    return {
                        'status': result['status'],
                        'message': f'Memory limit exceeded on test case {i+1}: {current_memory/1024:.2f}MB > {task.memory_limit_mb}MB',
                        'passed_tests': passed_tests,
                        'total_tests': len(test_cases),
                        'total_execution_time': total_execution_time,
                        'max_memory_used_kb': max_memory_used_kb,
                        'failed_test_input': test_case.input_data,
                        'expected_output': test_case.expected_output,
                        'actual_output': result.get('output', '')
                    }
                
                if result['status'] != 'SUCCESS':
                    return {
                        'status': result['status'],
                        'message': f'Test case {i+1} failed: {result.get("error", "Unknown error")}',
                        'passed_tests': passed_tests,
                        'total_tests': len(test_cases),
                        'total_execution_time': total_execution_time,
                        'max_memory_used_kb': max_memory_used_kb,
                        'failed_test_input': test_case.input_data,
                        'expected_output': test_case.expected_output,
                        'actual_output': result.get('output', '')
                    }
                
                actual_output = result.get('output', '').strip()
                expected_output = test_case.expected_output.strip()
                
                logger.info(f"Test case {i+1}: expected '{expected_output}', got '{actual_output}'")
                
                if actual_output == expected_output:
                    passed_tests += 1
                    logger.info(f"Test case {i+1} passed")
                else:
                    failed_test = {
                        'test_case_number': i + 1,
                        'input': test_case.input_data,
                        'expected': expected_output,
                        'actual': actual_output
                    }
                    logger.info(f"Test case {i+1} failed: expected '{expected_output}', got '{actual_output}'")
                    break
            
            if passed_tests == len(test_cases):
                return {
                    'status': 'ACCEPTED',
                    'message': 'All test cases passed',
                    'passed_tests': passed_tests,
                    'total_tests': len(test_cases),
                    'total_execution_time': total_execution_time,
                    'max_memory_used_kb': max_memory_used_kb
                }
            else:
                return {
                    'status': 'WRONG_ANSWER',
                    'message': f'Test case {failed_test["test_case_number"]} failed',
                    'passed_tests': passed_tests,
                    'total_tests': len(test_cases),
                    'total_execution_time': total_execution_time,
                    'max_memory_used_kb': max_memory_used_kb,
                    'failed_test_input': failed_test['input'],
                    'expected_output': failed_test['expected'],
                    'actual_output': failed_test['actual']
                }
                
        except Exception as e:
            logger.error(f"Error processing test cases: {e}")
            return {
                'status': 'INTERNAL_ERROR',
                'message': f'Error processing test cases: {str(e)}',
                'passed_tests': 0,
                'total_tests': 0,
                'total_execution_time': 0,
                'max_memory_used_kb': 0
            }

def update_submission_status(submission_id, status, is_complete, run_time=None, memory_used_kb=None):
    """Обновить статус submission в БД"""
    with app.app_context():
        try:
            submission = Submission.query.get(submission_id)
            if submission:
                submission.status = status
                submission.is_complete = is_complete
                if run_time is not None:
                    submission.run_time = run_time
                if memory_used_kb is not None:
                    submission.memory_used = memory_used_kb  # Сохраняем в KB
                db.session.commit()
                logger.info(f"Updated submission {submission_id} status to {status}, memory: {memory_used_kb}KB")
            else:
                logger.error(f"Submission {submission_id} not found")
        except Exception as e:
            logger.error(f"Error updating submission {submission_id}: {e}")

def start_runner_consumer():
    """Запуск потребителя с полной проверкой тестов"""
    logger.info("Starting Code Runner Service Consumer with full test validation")
    
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    port=Config.RABBITMQ_PORT,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            
            channel = connection.channel()
            
            channel.queue_declare(queue=Config.RABBITMQ_QUEUE_CODE_RUNNER, durable=True)
            channel.queue_declare(queue=Config.RABBITMQ_QUEUE_RESULTS, durable=True)
            
            channel.basic_qos(prefetch_count=1)
            
            def callback(ch, method, properties, body):
                """Callback для обработки сообщений с полной проверкой тестов"""
                try:
                    task_data = json.loads(body)
                    submission_id = task_data['submission_id']
                    task_id = task_data['task_id']
                    user_id = task_data['user_id']
                    code = task_data['code']
                    language = task_data.get('language', 'python')
                    
                    if submission_id in processing_submissions:
                        logger.warning(f"Submission {submission_id} is already being processed, skipping")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                    
                    processing_submissions[submission_id] = True
                    
                    logger.info(f"Processing submission {submission_id} for task {task_id}")
            
                    with app.app_context():
                        task = Task.query.get(task_id)
                        if not task:
                            logger.error(f"Task {task_id} not found")
                            del processing_submissions[submission_id]
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            return
            
                    test_result = process_test_cases(code, language, task, user_id, submission_id)
                    
                    is_complete = (test_result['status'] == 'ACCEPTED')
                    final_status = test_result['status']
                    
                    # Обновляем статус submission в БД с реальным временем выполнения и памятью
                    update_submission_status(
                        submission_id=submission_id,
                        status=final_status,
                        is_complete=is_complete,
                        run_time=test_result.get('total_execution_time', 0),
                        memory_used_kb=test_result.get('max_memory_used_kb', 0)
                    )
                    
                    next_task_id = None
                    if is_complete:
                        next_task_id = get_next_unsolved_task(task_id, user_id)
                        logger.info(f"Task {task_id} completed, next task: {next_task_id}")
            
                    # Формируем результат С памятью
                    result_data = {
                        'submission_id': submission_id,
                        'user_id': user_id,
                        'task_id': task_id,
                        'status': final_status,
                        'is_complete': is_complete,
                        'run_time': test_result.get('total_execution_time', 0),
                        'memory_used_kb': test_result.get('max_memory_used_kb', 0),
                        'message': test_result['message'],
                        'passed_tests': test_result.get('passed_tests', 0),
                        'total_tests': test_result.get('total_tests', 0),
                        'next_task_id': next_task_id
                    }
                    
                    if final_status == 'WRONG_ANSWER':
                        result_data.update({
                            'failed_test_input': test_result.get('failed_test_input'),
                            'expected_output': test_result.get('expected_output'),
                            'actual_output': test_result.get('actual_output')
                        })
                    
                    channel.basic_publish(
                        exchange='',
                        routing_key=Config.RABBITMQ_QUEUE_RESULTS,
                        body=json.dumps(result_data),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json'
                        )
                    )
                    
                    logger.info(f"Result published for submission {submission_id}. Status: {final_status}, Time: {result_data['run_time']}ms, Memory: {result_data['memory_used_kb']}KB")
                    
                    if submission_id in processing_submissions:
                        del processing_submissions[submission_id]
                    
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"Submission {submission_id} processed successfully")
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    submission_id = json.loads(body).get('submission_id')
                    if submission_id in processing_submissions:
                        del processing_submissions[submission_id]
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        
            channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE_CODE_RUNNER,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info('✅ Code Runner Service is now waiting for messages')
            logger.info(f'📍 Connected to RabbitMQ at {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}')
            
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection error: {e}")
            logger.info("Retrying in 10 seconds...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Unexpected error in consumer: {e}")
            logger.info("Retrying in 10 seconds...")
            time.sleep(10)