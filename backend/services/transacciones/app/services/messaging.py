# transactions_service/app/services/messaging.py
import pika
import json
import logging
import time  # Necesitamos 'time' para los reintentos

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Definimos el nombre de la cola
TRANSACTION_QUEUE = 'fraud_detection_queue'

class RabbitMQPublisher:
    def __init__(self, host='rabbitmq', max_retries=15, retry_delay=5):
        """
        Inicializa la conexión con reintentos.
        """
        self.host = host
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None
        
        # --- CAMBIO CLAVE: Llamamos a conectar con reintentos ---
        self.connect()

    def connect(self):
        """
        Lógica de conexión con reintentos.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                # --- CORRECCIÓN: heartbeat (no heartbeart) ---
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, heartbeat=600, blocked_connection_timeout=300)
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=TRANSACTION_QUEUE, durable=True)
                logger.info("✅ Conexión con RabbitMQ establecida exitosamente.")
                return  # ¡Éxito! Salimos del bucle.
            
            except pika.exceptions.AMQPConnectionError as e:
                retries += 1
                logger.warning(f"❌ Error al conectar con RabbitMQ (intento {retries}/{self.max_retries}): {e}")
                logger.info(f"Reintentando en {self.retry_delay} segundos...")
                time.sleep(self.retry_delay)
        
        logger.error("🚫 No se pudo conectar con RabbitMQ después de varios intentos.")
        # Si falla después de todos los reintentos, lanzamos un error
        # para que el servicio se detenga.
        raise ConnectionError("No se pudo conectar a RabbitMQ.")

    def publish_message(self, message_body: dict):
        """
        Publica un mensaje en la cola de transacciones.
        """
        try:
            # Verificamos si la conexión está viva. Si no, reconectamos.
            if not self.connection or self.connection.is_closed or not self.channel or self.channel.is_closed:
                logger.warning("Conexión perdida. Intentando reconectar...")
                self.connect()

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
            # Si publicar falla, cerramos la conexión para forzar reconexión
            if self.connection and self.connection.is_open:
                self.connection.close()

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Conexión con RabbitMQ cerrada.")