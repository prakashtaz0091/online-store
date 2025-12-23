import os
import redis
import json

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def publish_event(event_type, payload):
    event = {
        "type": event_type,
        "data": payload,
    }
    r.publish("order_events", json.dumps(event))
