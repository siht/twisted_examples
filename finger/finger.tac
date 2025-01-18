from email import policy # no se porque no lo importa rpc internamente ya que se necesita

import html
from twisted.application import internet, service, strports
from twisted.internet import defer, endpoints, protocol, reactor
from twisted.protocols import basic
from twisted.web import resource, server, static, xmlrpc
from twisted.words.protocols import irc


def catchError(err):
    return "Internal error in server"


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        d = self.factory.getUser(user)
        d.addErrback(catchError)
        def writeValue(message):
            self.transport.write(message + b"\r\n")
            self.transport.loseConnection()
        d.addCallback(writeValue)


class IRCReplyBot(irc.IRCClient):
    def connectionMade(self):
        self.nickname = self.factory.nickname
        irc.IRCClient.connectionMade(self)

    def privmsg(self, user, channel, msg):
        user = user.split("!")[0]
        if self.nickname.lower() == channel.lower():
            d = self.factory.getUser(msg.encode("ascii"))
            def onError(err):
                return b"Internal error in server"
            d.addErrback(onError)
            def writeResponse(message):
                message = message.decode("ascii")
                irc.IRCClient.msg(self, user, msg + ": " + message)
            d.addCallback(writeResponse)


class UserStatusTree(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        d = self.service.getUsers()
        def formatUsers(users):
            print(users)
            l = [f'<li><a href="{user.decode('utf-8')}">{user.decode('utf-8')}</a></li>' for user in users]
            print(l)
            return "<ul>" + "".join(l) + "</ul>"
        d.addCallback(formatUsers)
        d.addCallback(lambda s: s.encode())
        d.addCallback(request.write)
        d.addCallback(lambda _: request.finish())
        return server.NOT_DONE_YET

    def getChild(self, path, request):
        if path == b"":
            return UserStatusTree(self.service)
        else:
            return UserStatus(path, self.service)


class UserStatus(resource.Resource):
    def __init__(self, user, service):
        resource.Resource.__init__(self)
        self.user = user
        self.service = service

    def render_GET(self, request):
        d = self.service.getUser(self.user)
        d.addCallback(lambda x: x.decode('utf-8'))
        d.addCallback(html.escape)
        d.addCallback(lambda m: "<h1>%s</h1>" % self.user.decode('utf-8') + "<p>%s</p>" % m)
        d.addCallback(lambda x: x.encode())
        d.addCallback(request.write)
        d.addCallback(lambda _: request.finish())
        return server.NOT_DONE_YET


class UserStatusXR(xmlrpc.XMLRPC):
    def __init__(self, service):
        xmlrpc.XMLRPC.__init__(self)
        self.service = service

    def xmlrpc_getUser(self, user):
        return self.service.getUser(user)


class FingerService(service.Service):
    def __init__(self, filename):
        self.users = {}
        self.filename = filename
    
    def _read(self):
        self.users.clear()
        with open(self.filename, "rb") as f:
            for line in f:
                user, status = line.split(b":", 1)
                user = user.strip()
                status = status.strip()
                self.users[user] = status
        self.call = reactor.callLater(30, self._read)

    def startService(self):
        self._read()
        service.Service.startService(self)

    def stopService(self):
        service.Service.stopService(self)
        self.call.cancel()

    def getUser(self, user):
        if isinstance(user, str):
            user = user.encode()
        return defer.succeed(self.users.get(user, b"No such user"))

    def getUsers(self):
        return defer.succeed(list(self.users.keys()))

    def getFingerFactory(self):
        f = protocol.ServerFactory()
        f.protocol = FingerProtocol
        f.getUser = self.getUser
        return f

    def getResource(self):
        r = UserStatusTree(self)
        x = UserStatusXR(self)
        r.putChild(b"RPC2", x)
        return r

    def getIRCBot(self, nickname):
        f = protocol.ClientFactory()
        f.protocol = IRCReplyBot
        f.nickname = nickname
        f.getUser = self.getUser
        return f


def main():
    # sudo /your_venv/twisted/bin/twistd -ny finger.tac
    global application
    application = service.Application("finger", uid=1, gid=1)
    f = FingerService("/etc/users")
    serviceCollection = service.IServiceCollection(application)
    f.setServiceParent(serviceCollection)
    strports.service("tcp:79", f.getFingerFactory()).setServiceParent(serviceCollection)
    strports.service("tcp:8000", server.Site(f.getResource())).setServiceParent(serviceCollection)
    internet.ClientService(
        endpoints.clientFromString(reactor, "tcp:127.0.0.1:6667"),
        f.getIRCBot("fingerbot"),
    ).setServiceParent(serviceCollection)


if __name__ == 'builtins':
    main()
