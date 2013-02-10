import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory
from autobahn.websocket import WebSocketServerProtocol 
from autobahn.websocket import listenWS

import redis
import json


class RedisPubSub(object):
    
    def __init__(self, _redis, channel):
        self._redis = _redis
        self.pubsub = _redis.pubsub()
        self.channel = channel
        self.pubsub.subscribe(self.channel)

class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, msg, binary):
        if not binary:
            self.factory.broadcast("'%s' from %s" % (msg, self.peerstr))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url, debug = False, debugCodePaths = False):
        WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
        self.clients = []
        r = redis.Redis(port=6710)
        self.ps = RedisPubSub(r, 'process_feedback_channel')
        self.tick()


    def tick(self):
        try:
            msg = self.ps.pubsub.listen().next()
        except StopIteration:
            return reactor.callLater(0, self.tick)
        else:
            try:
                msg = msg['data']
                msg = json.dumps(msg)
            except:
                pass

        self.broadcast(msg)
        return reactor.callLater(0, self.tick)  


    def welcome(self, client):
        client.sendMessage('Welcome')

    def register(self, client):
        if not client in self.clients:
            print "registered client " + client.peerstr
            self.clients.append(client)
            self.welcome(client)

    def unregister(self, client):
        if client in self.clients:
            print "unregistered client " + client.peerstr
            self.clients.remove(client)

    def broadcast(self, msg):
        print "broadcasting message '%s' .." % msg
        for c in self.clients:
            c.sendMessage(msg)
            print "message sent to " + c.peerstr


class BroadcastPreparedServerFactory(BroadcastServerFactory):
    """ Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage.
    """

    def broadcast(self, msg):
        print "broadcasting prepared message '%s' .." % msg
        preparedMsg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(preparedMsg)
            print "prepared message sent to " + c.peerstr


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    ServerFactory = BroadcastServerFactory
   #ServerFactory = BroadcastPreparedServerFactory

    factory = ServerFactory("ws://localhost:9000",
                           debug = debug,
                           debugCodePaths = debug)

    factory.protocol = BroadcastServerProtocol
    factory.setProtocolOptions(allowHixie76 = True)
    listenWS(factory)

    reactor.run()
