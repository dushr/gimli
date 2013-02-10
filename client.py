import sys
from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, \
                               WebSocketClientProtocol, \
                               connectWS
import redis

class RedisPubSub(object):
    
    def __init__(self, _redis, channel):
        self._redis = _redis
        self.pubsub = _redis.pubsub()
        self.channel = channel

    def listen(self):
        self.pubsub.subscribe(self.channel)

        for message in self.pubsub.listen():
            yield message

class BroadcastClientProtocol(WebSocketClientProtocol):
    """
    Simple client that connects to a WebSocket server, send a HELLO
    message every 2 seconds and print everything it receives.
    """


    def sendHello(self):

        r = redis.Redis(port=6710)

        self.ps = RedisPubSub(r, 'process_feedback_channel')
        self.sendMessage("Hello from Python!")
        for i in self.ps.listen():
            self.sendMessage(str(i))
            



    def onOpen(self):
        self.sendHello()

    def onMessage(self, msg, binary):
        print "Got message: " + msg


if __name__ == '__main__':

    if len(sys.argv) < 2:
      print "Need the WebSocket server address, i.e. ws://localhost:9000"
      sys.exit(1)

    factory = WebSocketClientFactory(sys.argv[1])
    factory.protocol = BroadcastClientProtocol
    connectWS(factory)
    reactor.run()
  

