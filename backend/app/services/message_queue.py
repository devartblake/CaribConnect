import asyncio
import logging

import aio_pika

from app.core.config import settings

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"

logger = logging.getLogger(__name__)

async def get_connection():
    return await aio_pika.connect_robust(host= settings.RABBITMQ_URL)

async def send_message_async(queue_name: str, message_body: str):
    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(body=message_body.encode()), routing_key=queue.name
        )

def send_message(queue_name: str, message_body: str):
    asyncio.run(send_message_async(queue_name, message_body))

async def setup_rabbitmq():
    """Initialize RabbitMQ connection, channel, and queue."""
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()  # Create a channel
    await channel.set_qos(prefetch_count=1)  # Set prefetch for fair dispatch

    exchange = await channel.declare_exchange("my_exchange", aio_pika.ExchangeType.DIRECT)
    queue = await channel.declare_queue("my_queue", durable=True)
    await queue.bind(exchange, routing_key="test")

    return connection, channel, queue


async def consume_from_stream(queue):
    """Function to consume messages from RabbitMQ."""
    async def message_handler(message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                logger.info(f"Received message: {message.body}")
                # Process message here
                await process_message(message.body)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    await queue.consume(message_handler, no_ack=False)


async def process_message(message_body):
    """Process message and perform desired task."""
    print(f"Processing message: {message_body}")
    # Here you can add custom logic depending on your app's needs
    # For example, if the message body is JSON, you can deserialize it and take appropriate action


async def publish_message(channel, message_body):
    """Function to publish a message to RabbitMQ."""
    exchange = await channel.get_exchange("my_exchange")
    message = aio_pika.Message(body=message_body.encode())
    await exchange.publish(message, routing_key="test")
    logger.info(f"Published message: {message_body}")


async def main():
    """Main function to set up RabbitMQ and start consuming/publishing messages."""
    connection, channel, queue = await setup_rabbitmq()

    # Start the consumer to listen for messages
    consumer_task = asyncio.create_task(consume_from_stream(queue))

    # Publish a test message (you can remove or adjust this part as needed)
    await publish_message(channel, "Hello, RabbitMQ with aio-pika!")

    await consumer_task  # Wait for the consumer to finish (it will run indefinitely)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted, shutting down.")
