# messaging.py
import pika
import json
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definimos el nombre de la cola (debe ser el mismo que escucha el fraud_service)
TRANSACTION_QUEUE = 'fraud_detection_queue'

class RabbitMQPublisher:
    def __init__(self, host='localhost'):
        """
        Inicializa la conexión y el canal de RabbitMQ.
        """
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host)
            )
            self.channel = self.connection.channel()
            # Declaramos la cola para asegurarnos de que exista
            self.channel.queue_declare(queue=TRANSACTION_QUEUE, durable=True)
            logger.info("✅ Conexión con RabbitMQ establecida.")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"❌ Error al conectar con RabbitMQ: {e}")
            self.connection = None
            self.channel = None

    def publish_message(self, message_body: dict):
        """
        Publica un mensaje en la cola de transacciones.
        El message_body debe ser un diccionario (serializado de Pydantic).
        """
        if not self.channel or not self.connection or self.connection.is_closed:
            logger.error("No se puede publicar, no hay conexión de RabbitMQ.")
            # Aquí podrías intentar reconectar o lanzar una excepción
            return

        try:
            # Convertimos el dict a JSON string
            message_str = json.dumps(message_body, default=str)

            self.channel.basic_publish(
                exchange='',
                routing_key=TRANSACTION_QUEUE,
                body=message_str,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Hacer el mensaje persistente
                )
            )
            logger.info(f"📤 Mensaje publicado en '{TRANSACTION_QUEUE}': {message_str}")
        except Exception as e:
            logger.error(f"❌ Error al publicar mensaje: {e}")

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Conexión con RabbitMQ cerrada.")

# Instancia global (o mejor, inyectada como dependencia en FastAPI)
# Por simplicidad, la creamos aquí.
publisher = RabbitMQPublisher(host='localhost') # 'rabbitmq' si usas docker-compose