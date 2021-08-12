import redis
from typing import Union
from configurations.properties import REDIS_HOST, REDIS_PORT

server = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


def manual_save() -> None:
    server.bgsave()


def cache_input(client_request: str, response: str) -> None:
    if not server.exists(client_request):
        server.set(client_request, response)


def check_input_cache(client_request: str) -> Union[None, str]:
    return server.get(client_request)
