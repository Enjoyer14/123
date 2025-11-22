import pika
import json
import threading
import time
import logging
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

socketio = None 

def start_rabbitmq_consumer(app_socketio):
    global socketio
    socketio = app_socketio
    
    thread = threading.Thread(target=run_consumer_loop)
    thread.daemon = True
    thread.start()
    logger.info("✅ RabbitMQ consumer started in background thread")

def run_consumer_loop():
    logger.info("Starting RabbitMQ consumer loop...")
    
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    port=Config.RABBITMQ_PORT,
                    heartbeat=600
                )
            )
            channel = connection.channel()
            
            channel.queue_declare(queue=Config.RABBITMQ_QUEUE_RESULTS, durable=True)
            channel.basic_qos(prefetch_count=1)
            
            logger.info("🔄 Notifier Service waiting for results...")
            
            def callback(ch, method, properties, body):
                process_result_message(ch, method, properties, body)
            
            channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE_RESULTS,
                on_message_callback=callback,
                auto_ack=False
            )
            
            channel.start_consuming()
            
        except Exception as e:
            logger.error(f"RabbitMQ connection error: {e}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

def process_result_message(ch, method, properties, body):
    """Обрабатывает сообщение с результатом и отправляет его через SocketIO."""
    try:
        result_data = json.loads(body)
        user_id = result_data.get('user_id')
        submission_id = result_data.get('submission_id')
        
        logger.info(f"Received result for submission {submission_id}, user {user_id}")
        
        if user_id and socketio:
            # Отправка результата по WebSocket
            socketio.emit(
                'submission_result', 
                result_data, 
                room=f'user_{user_id}',
                namespace='/'
            )
            
            logger.info(f"✅ Sent result for Submission ID {submission_id} to user {user_id}")
        else:
            logger.error(f"❌ Error: Could not send result. user_id: {user_id}, socketio: {socketio}")
            
        # Подтверждение получения сообщения
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"❌ Critical error in result handler: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)