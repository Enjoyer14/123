import pika
import json
from config import Config
import time

# Функция для публикации сообщения в очередь
def publish_submission_task(submission_id, task_id, user_id, code, language):

    # Подключаемся к rabbitmq
    while True:
        try:
            # Создаем параметры подключения
            connection_params = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST, 
                port=Config.RABBITMQ_PORT
            )
            conn = pika.BlockingConnection(connection_params)
            ch = conn.channel()
            print("Успешно подключились к RabbitMQ")
            break # Успешно подключаемся
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Ошибка подключения к RabbitMQ.")
            time.sleep(5)

    # объявляем очередь
    # durable=True - гарантирует, что очередь выживет после перезапуска RabbitMQ
    ch.queue_declare(queue=Config.RABBITMQ_QUEUE_CODE_RUNNER, durable=True)

    # данные для передачи в rabbit
    message = {
        'submission_id': submission_id,
        'task_id': task_id,
        'user_id': user_id,
        'code': code,
        'language': language
    }
    
    #публикация сообщения
    ch.basic_publish(
        exchange='', # Пустой exchange означает что сообщение идет напрямую в очередь по имени
        routing_key=Config.RABBITMQ_QUEUE_CODE_RUNNER,
        body=json.dumps(message),
        # delivery_mode = 2 делает сообщение устойчивым: RabbitMQ сохранит его на диск
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.DeliveryMode.Persistent 
        )
    )

    conn.close()
    return True