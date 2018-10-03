########################
# Dennis MUD           #
# telnet-backend.py    #
# Copyright 2018       #
# Michael D. Reiley    #
########################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

# Codebase borrowed from https://github.com/TKeesh/WebSocketChat

import console
import database
import json
import sys

from twisted.python import log
from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver

# Read the config file.
with open("telnet.config.json") as f:
    config = json.load(f)

# Open the Dennis main database.
dbman = database.DatabaseManager(config["database"]["host"], config["database"]["port"], config["database"]["name"])

# Reset users.
rooms = dbman.rooms.find()
if rooms.count():
    for r in rooms:
        r["users"] = []
        dbman.upsert_room(r)
users = dbman.users.find()
if users.count():
    for u in users:
        u["online"] = False
        dbman.upsert_user(u)


class Router:
    def __init__(self):
        self.users = {}
        self.chatfactory = None

    def __contains__(self, item):
        if item in self.users:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.users[item]
        else:
            return None

    def __iter__(self):
        return self.users.items()

    def register(self, peer):
        print(peer)
        self.users[peer] = console.Console(dbman, peer, self)

    def unregister(self, peer):
        self.users[peer].command("logout")
        del self.users[peer]

    def message(self, peer, msg):
        self.chatfactory.communicate(peer, msg.encode())

    def broadcast_all(self, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            self.chatfactory.communicate(self.users[u].rname, msg.encode())

    def broadcast_room(self, room, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            if self.users[u].user["room"] == room:
                self.chatfactory.communicate(self.users[u].rname, msg.encode())


class ChatProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.peer = None

    def connectionMade(self):
        p = self.transport.getPeer()
        self.peer = p.host + ':' + str(p.port)
        print("Client connecting: {0}".format(self.peer))
        self.factory.register(self)
        print("Client connected: {0}".format(self.peer))

    def connectionLost(self, reason):
        self.factory.unregister(self)
        print("Client disconnected: {0}".format(self.peer))

    def lineReceived(self, line):
        # self.factory.communicate(self, payload, isBinary)
        print("Client {0} sending message: {1}".format(self.peer, line))
        self.factory.router[self.peer].command(line.decode())


class ChatFactory(protocol.Factory):

    def __init__(self, router, *args, **kwargs):
        self.router = router
        self.router.chatfactory = self
        super(ChatFactory, self).__init__(*args)
        self.clients = []

    def buildProtocol(self, addr):
        return ChatProtocol(self)

    def register(self, client):
        self.clients.append({'client-peer': client.peer, 'client': client})
        router.register(client.peer)

    def unregister(self, client):
        router.unregister(client.peer)
        for c in self.clients:
            if c['client-peer'] == client.peer:
                self.clients.remove(c)

    def communicate(self, peer, payload):
        client = None
        for c in self.clients:
            if c['client-peer'] == peer:
                client = c['client']
        if client:
            client.sendLine(payload)


if __name__ == "__main__":
    router = Router()

    log.startLogging(sys.stdout)

    factory = ChatFactory(router)

    reactor.listenTCP(config["server"]["port"], ChatFactory(router))
    reactor.run()