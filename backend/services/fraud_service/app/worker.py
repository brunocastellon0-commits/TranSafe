import aio_pika
import asyncio
import json
import httpx
from .config import settings
from .logic import aplicar_reglas_fraude

async def procesar_mensaje(message: aio_pika.IncomingMessage):
    """
    Callback que procesa cada mensaje de la cola.
    """
    async with message.process():
        try:
            datos = json.loads(message.body.decode())
            # El mensaje publicado tiene "id", no "id_transaccion"
            id_trans = datos.get("id")
            
            if not id_trans:
                print(f" [!] Mensaje inválido, sin ID: {datos}")
                return

            print(f" [o] 📨 Recibido mensaje para transacción {id_trans}")

            # 1. Aplicar reglas de fraude
            estado_final = aplicar_reglas_fraude(datos)
            print(f" [>] 🔍 Transacción {id_trans} clasificada como: {estado_final}")

            # 2. Actualizar estado en el servicio de transacciones
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Verifica que esta URL coincida con tu endpoint
                url = f"{settings.TRANSACTIONS_SERVICE_URL}/transactions/{id_trans}/status"
                payload = {"status": estado_final}
                
                print(f" [→] Actualizando transacción en: {url}")
                response = await client.patch(url, json=payload)
                
                if response.status_code != 200:
                    error_msg = f"Error al actualizar. Status: {response.status_code}, Body: {response.text}"
                    print(f" [!] ❌ {error_msg}")
                    raise Exception(error_msg)
                
                print(f" [✓] ✅ Transacción {id_trans} actualizada correctamente: {estado_final}")
        
        except json.JSONDecodeError as e:
            print(f" [!] ❌ Error decodificando JSON: {e}")
        except Exception as e:
            print(f" [!] ❌ Error procesando mensaje: {e}")
            raise  # Re-lanza para NACK y reintento

async def main():
    """
    Función principal con lógica de reconexión.
    """
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Intento {attempt + 1}/{max_retries} - Conectando a RabbitMQ ({settings.RABBITMQ_URL})...")
            
            connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                timeout=30
            )
            
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)
                
                queue = await channel.declare_queue(
                    'fraud_detection_queue', 
                    durable=True
                )
                
                print("=" * 60)
                print("✅ WORKER DE FRAUDE INICIADO CORRECTAMENTE")
                print(f"📡 Conectado a: {settings.RABBITMQ_URL}")
                print(f"📥 Escuchando cola: fraud_detection_queue")
                print(f"🎯 URL de transacciones: {settings.TRANSACTIONS_SERVICE_URL}")
                print("=" * 60)
                
                await queue.consume(procesar_mensaje)
                
                # Mantiene el worker corriendo indefinidamente
                await asyncio.Future()
                
        except aio_pika.exceptions.AMQPConnectionError as e:
            print(f"❌ Error de conexión a RabbitMQ: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Reintentando en {retry_delay} segundos...")
                await asyncio.sleep(retry_delay)
            else:
                print("💀 Máximo de reintentos alcanzado. Saliendo.")
                raise
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Reintentando en {retry_delay} segundos...")
                await asyncio.sleep(retry_delay)
            else:
                raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Worker detenido por el usuario")
    except Exception as e:
        print(f"\n💀 Worker terminado con error: {e}")