import redis
from twisted.internet import reactor

class RedisPubSub(object):
    
    def __init__(self, _redis, channel):
        self._redis = _redis
        self.pubsub = _redis.pubsub()
        self.channel = channel
        self.pubsub.subscribe(self.channel)

    def listen(self):
        try:
            msg = self.pubsub.listen().next()
        except StopIteration:
            return reactor.callLater(0, ps.listen)

        print msg
        return reactor.callLater(0, ps.listen)  
           


if __name__ == '__main__':
    
    r = redis.Redis(port=6710)

    ps = RedisPubSub(r, 'process_feedback_channel')

    ps.listen()

    reactor.run()
