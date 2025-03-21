import redis


class RedisModel():
  client = None 

  @classmethod
  def init(cls, host):
    cls.client = redis.Redis(host=host)

  @classmethod
  def enque(cls, queue, msg):
    cls.client.rpush(queue, msg)

  @classmethod
  def peek_queue(cls, queue):
    return cls.client.lrange(queue, 0, -1)
