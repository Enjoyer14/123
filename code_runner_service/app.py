from rabbitmq_consumer import start_runner_consumer
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("🚀 Starting Code Runner Service...")
    
    # Даем время RabbitMQ и другим сервисам запуститься
    time.sleep(20)
    
    # Бесконечный цикл для переподключения
    while True:
        try:
            logger.info("Starting RabbitMQ consumer...")
            start_runner_consumer()
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            break
        except Exception as e:
            logger.error(f"RabbitMQ consumer failed: {e}")
            logger.info("Restarting RabbitMQ consumer in 10 seconds...")
            time.sleep(10)