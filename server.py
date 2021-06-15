'''
TODO:

* Spam mitigations (!kick/!lock, ...) -> server up
* Edit readme
* Subset of colors
* Timestamps
* Review pull request
'''

import string
import time

import colored
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineOnlyReceiver

port = 2000

class chat_proto(LineOnlyReceiver):
    MAX_LENGTH = 256
    delimiter = b'\n'
    username_prompt = colored.attr('bold').encode() + b'Username:' + colored.attr(0).encode()
    ratelimit_interval = 1
    ratelimit_maxwarn = 8

    def __init__(self):
        self.username = None
        self.color = 2
        self.lastmsgtime = time.time()
        self.ratelimit_warn = 0

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
        line = self.strip(line)

        if not self.username:
            if len(line) == 0:
                self.sendLine(chat_proto.username_prompt)
            elif line in self.factory.users:
                self.sendLine(line + b' is in use')
                self.sendLine(chat_proto.username_prompt)
            else:
                self.username = line
                self.factory.clients.append(self)
                self.factory.users.add(self.username)

                valid_username = True
                for c in self.username:
                    if chr(c) not in string.ascii_letters + string.digits:
                        valid_username = False

                if valid_username:
                    self.sendLine(b'\nYou are connected to the chat ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())
                    self.sendLine(b'Type !users for a list of online users\n')
                    self.msg(b'-> ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())
                else:
                    self.sendLine(b'\nUsername can only contain letters and digits')
                    self.sendLine(chat_proto.username_prompt)
                    self.username = None
        elif len(line) == 0:
            self.sendLine(b'Not sent: Blank line')
        elif line.lower() == b'!users':
            for user in self.factory.users:
                self.sendLine(user)
            self.sendLine(b'')
        else:
            if time.time() - self.lastmsgtime >= chat_proto.ratelimit_interval:
                self.msg(colored.fg(self.color).encode() + self.username + colored.attr(0).encode() + b' ' + line)
                self.lastmsgtime = time.time()
            else:
                self.sendLine(b'Not sent: To quick (' + str(self.ratelimit_warn).encode() + b'/' + str(chat_proto.ratelimit_maxwarn).encode() + b')')

                self.ratelimit_warn += 1

                if self.ratelimit_warn == chat_proto.ratelimit_maxwarn:
                    self.dc(b'Rate limit exceeded')

    def lineLengthExceeded(self, line):
        self.dc(b'Message length exceeded')

    def dc(self, reason):
        self.sendLine(reason)
        self.connectionLost(reason)
        self.transport.loseConnection()

    def msg(self, line):
        for client in self.factory.clients:
            if client != self:
                client.transport.write(line + b'\n')

    def strip(self, line):
        sline = b''

        for c in line:
            if c >= 32 and c <= 126:
                sline += chr(c).encode()

        return sline.strip()

factory = ServerFactory()
factory.protocol = chat_proto
factory.clients = []
factory.users = set()

reactor.listenTCP(port, factory)
reactor.run()
