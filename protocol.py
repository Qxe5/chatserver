import random
import string
import time

import colored
from twisted.protocols.basic import LineOnlyReceiver

class chat_proto(LineOnlyReceiver):
    MAX_LENGTH = 256
    delimiter = b'\n'
    username_prompt = colored.attr('bold').encode() + b'Username:' + colored.attr(0).encode()
    avail_colors = list(range(1, 7))
    ratelimit_interval = 1
    ratelimit_maxwarn = 8

    def __init__(self):
        self.username = None
        self.color = random.choice(chat_proto.avail_colors)
        self.lastmsgtime = time.time()
        self.ratelimit_warn = 0

    def connectionMade(self):
        self.sendLine(b'\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        self.sendLine(b'Welcome!')
        self.sendLine(b'- You are connected to the server')
        self.sendLine(b'- Shitposting mildly tolerated')
        self.sendLine(b'- Source code: https://github.com/Qxe5/chatserver')
        self.sendLine(b'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        self.sendLine(chat_proto.username_prompt)

    def connectionLost(self, reason):
        if self in self.factory.clients:
            self.factory.clients.remove(self)
            self.factory.users.remove(self.username)

            self.msg(b'<- ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())

    def lineReceived(self, line):
        if not self.username:
            if len(line) == 0:
                self.sendLine(chat_proto.username_prompt)
            elif line in self.factory.users:
                self.sendLine(line + b' is in use')
                self.sendLine(chat_proto.username_prompt)
            else:
                valid_username = True
                for c in line:
                    if chr(c) not in string.ascii_letters + string.digits:
                        valid_username = False

                if valid_username:
                    self.username = line
                    self.factory.clients.append(self)
                    self.factory.users.append(self.username)

                    self.sendLine(b'\nYou are connected to the chat ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())
                    self.sendLine(b'Type !users for a list of online users\n')

                    self.msg(b'-> ' + colored.fg(self.color).encode() + self.username + colored.attr(0).encode())
                else:
                    self.sendLine(b'\nUsername can only contain letters and digits')
                    self.sendLine(chat_proto.username_prompt)
        elif len(line) == 0:
            self.sendLine(b'Not sent: Blank line')
        elif line.lower() == b'!users':
            for user in self.factory.users:
                self.sendLine(user)
            self.sendLine(b'')
        elif line.lower() == b'!kick':
            with open('kicklist', 'r+b') as kicklist:
                users = [user.strip() for user in kicklist.readlines()]

                for user in users:
                    if user in self.factory.users:
                        self.factory.clients[self.factory.users.index(user)].dc(b'Kicked')

                kicklist.truncate(0)
        else:
            if time.time() - self.lastmsgtime >= chat_proto.ratelimit_interval:
                self.msg(colored.fg(self.color).encode() + self.username + colored.attr(0).encode() + b' ' + self.strip(line))
                self.lastmsgtime = time.time()
            else:
                self.ratelimit_warn += 1

                self.sendLine(b'Not sent: To quick (' + str(self.ratelimit_warn).encode() + b'/' + str(chat_proto.ratelimit_maxwarn).encode() + b')')

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
                client.transport.write(b'[' + time.strftime('%H:%M %d-%m').encode() + b'] ' + line + b'\n')

    def strip(self, line):
        sline = b''

        for c in line:
            if c >= 32 and c <= 126:
                sline += chr(c).encode()

        return sline.strip()
