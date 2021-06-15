import protocol

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

port = 2000

factory = ServerFactory()
factory.protocol = protocol.chat_proto
factory.clients = []
factory.users = set()

reactor.listenTCP(port, factory)
reactor.run()
