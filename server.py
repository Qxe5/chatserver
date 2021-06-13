'''
TODO:

* Subset of colors
'''

import random

import colored
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineOnlyReceiver

port = 2000

class chat_proto(LineOnlyReceiver):
    username_prompt = colored.attr('bold').encode() + b'Username:' + colored.attr(0).encode()

    def __init__(self):
        self.username = None
        self.color = random.randint(0, 255)

    def connectionMade(self):
        self.sendLine(b'\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        self.sendLine(b'Welcome!')
        self.sendLine(b'- You are connected to the server')
        self.sendLine(b'- Shitposting mildly tolerated')
        self.sendLine(b'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        self.sendLine(chat_proto.username_prompt)

        print('->')

    def connectionLost(self, reason):
        if self in self.factory.clients:
            self.factory.clients.remove(self)
            self.factory.users.remove(self.username)

        print('<-')

    def lineReceived(self, line):
        sline = line.strip()

        if not self.username:
            if len(line) == 0:
                self.sendLine(chat_proto.username_prompt)
            elif sline in self.factory.users:
                self.sendLine(sline + b' is in use')
                self.sendLine(chat_proto.username_prompt)
            else:
                self.username = line
                self.factory.clients.append(self)
                self.factory.users.add(self.username)

                self.sendLine(b'\nYou are connected to the chat ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())
                self.sendLine(b'Type !users for a list of online users\n')
        elif sline.lower() == b'!users':
            for user in self.factory.users:
                self.sendLine(user)
            self.sendLine(b'')
        else:
            for client in self.factory.clients:
                if client != self:
                    client.transport.write(colored.fg(self.color).encode() + self.username + colored.attr(0).encode() + b' ' + line + b'\n')

factory = ServerFactory()
factory.protocol = chat_proto
factory.clients = []
factory.users = set()

reactor.listenTCP(port, factory)
reactor.run()
