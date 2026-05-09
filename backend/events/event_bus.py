from celery import Celery
import redis

redis_client = redis.Redis(host='redis', port=6379)

celery_app = Celery(
    'ai_platform',
    broker='redis://redis:6379/0'
)

class EventBus:
    async def publish(self, channel: str, message: dict):
        redis_client.publish(channel, str(message))

    async def queue_task(self, task_name: str, payload: dict):
        celery_app.send_task(task_name, args=[payload])
