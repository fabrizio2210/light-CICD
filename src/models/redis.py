import redis


class RedisModel():
  client = None 

  @classmethod
  def init(cls, host):
    cls.client = redis.Redis(host=host)

  @classmethod
  def enque(cls, queue, msg):
    cls.client.rpush(queue, msg)
