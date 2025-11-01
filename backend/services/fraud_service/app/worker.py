import aio_pika
import asyncio
import json
import httpx

# Importamos la configuración (settings) y la lógica (reglas)
from .config import settings
from .logic import aplicar_reglas_fraude

async def procesar_mensaje(message: aio_pika.IncomingMessage):
    """
    Esta es la función 'callback'. Se ejecuta por cada mensaje que
    llega a la cola 'cola_analisis_fraude'.
    """
    
    # 'message.process()' maneja el ACK/NACK automáticamente.
    # Si el código dentro del 'with' falla, el mensaje no se 
    # borra de la cola (NACK) y se reintentará.
    async with message.process():
        try:
            datos = json.loads(message.body.decode())
            id_trans = datos.get("id_transaccion")
            
            if not id_trans:
                print(f" [!] Mensaje inválido, sin ID. Descartando.")
                return # El 'process()' descarta el mensaje (ACK)

            print(f" [o] Recibido mensaje para transacción {id_trans}")

            # 1. Aplicar el Cerebro (Motor de Reglas)
            estado_final = aplicar_reglas_fraude(datos)
            
            print(f" [>] Transacción {id_trans} clasificada como: {estado_final}")

            # 2. Reportar el resultado al Servicio de Transacciones
            # Creamos un cliente HTTP asíncrono
            async with httpx.AsyncClient() as client:
                url = f"{settings.TRANSACTIONS_SERVICE_URL}/transacciones/internas/{id_trans}/estado"
                
                # Preparamos el cuerpo del PATCH (según el schema 'EstadoUpdate')
                payload = {"estado": estado_final}
                
                response = await client.patch(url, json=payload)
                
                if response.status_code != 200:
                    # Si falla la actualización, forzamos un error
                    # para que el mensaje se reintente (NACK).
                    raise Exception(f"Error al actualizar {id_trans}. Status: {response.status_code}")
                
                print(f" [✓] Transacción {id_trans} actualizada en la BD.")
        
        except Exception as e:
            print(f" [!] Error fatal procesando mensaje {id_trans}: {e}")
            # Al salir del 'with' con una excepción, el mensaje
            # no será confirmado (NACK) y RabbitMQ lo re-enviará.

async def main():
    """
    Función principal que inicia el worker.
    Se conecta a RabbitMQ y se queda escuchando.
    """
    print("Iniciando worker de fraude...")
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    
    async with connection:
        channel = await connection.channel()
        
        # Define un límite de mensajes 'en vuelo' (calidad de servicio)
        # Esto evita que el worker se sature si hay 1 millón de mensajes.
        await channel.set_qos(prefetch_count=10)
        
        # Declara la misma cola (para asegurarse de que existe)
        queue = await channel.declare_queue(
            'cola_analisis_fraude', 
            durable=True # La cola sobrevive a reinicios de RabbitMQ
        )
        
        print(" [*] Esperando mensajes. Para salir presiona CTRL+C")
        
        # Empieza a consumir (escuchar)
        # Asigna la función 'procesar_mensaje' como el callback
        await queue.consume(procesar_mensaje)
        
        # Mantiene el script corriendo indefinidamente
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Cerrando worker...")