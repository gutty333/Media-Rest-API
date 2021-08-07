import redis
from configurations.properties import REDIS_HOST, REDIS_PORT

server = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
print(server.keys())

for current in server.keys():
    key : str = current.decode("utf-8")
    value : str = server.get(key).decode("utf-8")
    print(f"{key.title()} = {value}")