from __future__ import annotations

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

from src.shared.conf import Config
from src.shared.logger import logger


def _get_broker_url():
    """
    Gets the broker URL from environment variables.
    Returns:
        str: The AMQP URL for RabbitMQ.
    """
    url = f"amqp://{Config.broker.RABBIT_MQ_USER}:{Config.broker.RABBIT_MQ_PASSWORD}@{Config.broker.RABBIT_MQ_HOST}:{Config.broker.RABBIT_MQ_PORT}/%2f"
    logger.info(
        f"Connecting to RabbitMQ broker at: {Config.broker.RABBIT_MQ_HOST}:{Config.broker.RABBIT_MQ_PORT}"
    )
    return url


try:
    rabbitmq_broker = RabbitmqBroker(url=_get_broker_url())
    dramatiq.set_broker(rabbitmq_broker)
    logger.info("RabbitMQ broker configured successfully")
except Exception as e:
    logger.error(f"Failed to configure RabbitMQ broker: {e!s}")
    raise
