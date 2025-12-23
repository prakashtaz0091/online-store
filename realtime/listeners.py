import redis
import json
import os
import django
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

channel_layer = get_channel_layer()

pubsub = r.pubsub()
pubsub.subscribe("order_events")

print("Listening for order events...")
for message in pubsub.listen():
    if message["type"] != "message":
        continue
    data = json.loads(message["data"])
    async_to_sync(channel_layer.group_send)(
        "dashboard",
        {
            "type": "order.event",
            "data": data,
        },
    )
