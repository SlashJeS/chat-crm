import redis
from django.conf import settings
from django.utils import timezone

_redis_client = None


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30,
        )
    return _redis_client


def get_presence_key(user_id):
    return f"presence:user:{user_id}"


def heartbeat(user):
    client = get_redis_client()
    client.setex(get_presence_key(user.id), settings.PRESENCE_GRACE_SECONDS, "1")
    user.profile.last_seen_at = timezone.now()
    user.profile.save(update_fields=["last_seen_at", "updated_at"])
    return user.profile.last_seen_at


def is_online(user_id):
    return get_redis_client().exists(get_presence_key(user_id)) == 1


def get_online_user_ids(user_ids):
    if not user_ids:
        return set()

    client = get_redis_client()
    pipe = client.pipeline()
    for user_id in user_ids:
        pipe.exists(get_presence_key(user_id))
    results = pipe.execute()
    return {user_id for user_id, exists in zip(user_ids, results, strict=True) if exists}
