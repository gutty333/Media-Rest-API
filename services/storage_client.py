import redis
from configurations.properties import REDIS_HOST, REDIS_PORT
from typing import Union

server = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
print(server.keys())

for current in server.keys():
    key : str = current.decode("utf-8")
    value : str = server.get(key).decode("utf-8")
    print(f"{key.title()} = {value}")


def cache_request(client_request: str, response: str) -> None:
    server.set(client_request, response)


def check_request_cache(client_request: str) -> Union[None, str]:
    return server.get(client_request)
