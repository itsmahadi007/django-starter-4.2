# from pms.settings import REDIS_HOST, REDIS_PORT
from backend.settings import REDIS_HOST, REDIS_PORT

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
