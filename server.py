'''
TODO:

* Subset of colors
'''

import colored
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineOnlyReceiver

port = 2000

class chat_proto(LineOnlyReceiver):
    delimiter = b'\n'
    username_prompt = colored.attr('bold').encode() + b'Username:' + colored.attr(0).encode()

    def __init__(self):
        self.username = None
        self.color = 2

    def connectionMade(self):
        self.sendLine(b'\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        self.sendLine(b'Welcome!')
        self.sendLine(b'- You are connected to the server')
        self.sendLine(b'- Shitposting mildly tolerated')
        self.sendLine(b'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        self.sendLine(chat_proto.username_prompt)

    def connectionLost(self, reason):
        if self in self.factory.clients:
            self.factory.clients.remove(self)
            self.factory.users.remove(self.username)

            self.msg(b'<- ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())

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

                self.msg(b'-> ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())
        elif sline.lower() == b'!users':
            for user in self.factory.users:
                self.sendLine(user)
            self.sendLine(b'')
        else:
            self.msg(colored.fg(self.color).encode() + self.username + colored.attr(0).encode() + b' ' + line)

    def msg(self, line):
        for client in self.factory.clients:
            if client != self:
                client.transport.write(line + b'\n')

factory = ServerFactory()
factory.protocol = chat_proto
factory.clients = []
factory.users = set()

reactor.listenTCP(port, factory)
reactor.run()
