import redis
import requests
import json
r_server = redis.Redis("localhost")
r_server.delete("test")
print(r_server.get("dfgdfgdffggfdg"))
l = ["hello","world"]
name = "test" + str(1)
r_server.rpush(name, *l)
print(r_server.lrange(name,0, -1))
