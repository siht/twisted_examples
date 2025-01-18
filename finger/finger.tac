from email import policy # no se porque no lo importa rpc internamente ya que se necesita

from zope.interface import Interface, implementer
from twisted.application import internet, service, strports
from twisted.internet import defer, endpoints, protocol, reactor, utils
from twisted.protocols import basic
from twisted.python import components
from twisted.spread import pb
from twisted.web import resource, server, xmlrpc
from twisted.words.protocols import irc


class IFingerService(Interface):
    def getUser(user):
        """
        Return a deferred returning L{bytes}.
        """

    def getUsers():
        """
        Return a deferred returning a L{list} of L{bytes}.
        """


class IFingerSetterService(Interface):
    def setUser(user, status):
        """
        Set the user's status to something.
        """


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


class IFingerFactory(Interface):
    def getUser(user):
        """
        Return a deferred returning L{bytes}
        """

    def buildProtocol(addr):
        """
        Return a protocol returning L{bytes}
        """


@implementer(IFingerFactory)
class FingerFactoryFromService(protocol.ServerFactory):
    protocol = FingerProtocol
    def __init__(self, service):
        self.service = service

    def getUser(self, user):
        return self.service.getUser(user)


components.registerAdapter(FingerFactoryFromService, IFingerService, IFingerFactory)


class FingerSetterProtocol(basic.LineReceiver):
    def connectionMade(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def connectionLost(self, reason):
        if len(self.lines) == 2:
            self.factory.setUser(*self.lines)


class IFingerSetterFactory(Interface):
    def setUser(user, status):
        """
        Return a deferred returning L{bytes}.
        """

    def buildProtocol(addr):
        """
        Return a protocol returning L{bytes}.
        """


@implementer(IFingerSetterFactory)
class FingerSetterFactoryFromService(protocol.ServerFactory):
    protocol = FingerSetterProtocol

    def __init__(self, service):
        self.service = service

    def setUser(self, user, status):
        self.service.setUser(user, status)


components.registerAdapter(FingerSetterFactoryFromService, IFingerSetterService, IFingerSetterFactory)


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


class IIRCClientFactory(Interface):
    """
    @ivar nickname
    """

    def getUser(user):
        """
        Return a deferred returning a string.
        """

    def buildProtocol(addr):
        """
        Return a protocol.
        """


@implementer(IIRCClientFactory)
class IRCClientFactoryFromService(protocol.ClientFactory):
    protocol = IRCReplyBot
    nickname = None

    def __init__(self, service):
        self.service = service
    def getUser(self, user):
        return self.service.getUser(user)


components.registerAdapter(IRCClientFactoryFromService, IFingerService, IIRCClientFactory)


@implementer(resource.IResource)
class UserStatusTree(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service
        self.putChild(b"RPC2", UserStatusXR(self.service))
        self.putChild(b"", self)

    def _cb_render_GET(self, users, request):
        userOutput = "".join(
            [f'<li><a href="{user.decode('utf-8')}">{user.decode('utf-8')}</a></li>' for user in users]
        )
        html = ("""
            <html><head><title>Users</title></head><body>
            <h1>Users</h1>
            <ul>
            %s
            </ul></body></html>"""
            % userOutput
        )
        request.write(html.encode())
        request.finish()

    def render_GET(self, request):
        d = self.service.getUsers()
        d.addCallback(self._cb_render_GET, request)
        return server.NOT_DONE_YET

    def getChild(self, path, request):
        if path == b"":
            return UserStatusTree(self.service)
        else:
            return UserStatus(path, self.service)


components.registerAdapter(UserStatusTree, IFingerService, resource.IResource)


class UserStatus(resource.Resource):
    def __init__(self, user, service):
        resource.Resource.__init__(self)
        self.user = user
        self.service = service

    def _cb_render_GET(self, status, request):
        request.write(
            b"""<html><head><title>%s</title></head>
            <body><h1>%s</h1>
            <p>%s</p>
            </body></html>"""
            % (self.user, self.user, status)
        )
        request.finish()

    def render_GET(self, request):
        d = self.service.getUser(self.user)
        d.addCallback(self._cb_render_GET, request)
        return server.NOT_DONE_YET


class UserStatusXR(xmlrpc.XMLRPC):
    def __init__(self, service):
        xmlrpc.XMLRPC.__init__(self)
        self.service = service

    def xmlrpc_getUser(self, user):
        return self.service.getUser(user)


class IPerspectiveFinger(Interface):
    def remote_getUser(username):
        """
        Return a user's status.
        """

    def remote_getUsers():
        """
        Return a user's status.
        """


@implementer(IPerspectiveFinger)
class PerspectiveFingerFromService(pb.Root):
    def __init__(self, service):
        self.service = service

    def remote_getUser(self, username):
        return self.service.getUser(username)

    def remote_getUsers(self):
        return self.service.getUsers()


components.registerAdapter(PerspectiveFingerFromService, IFingerService, IPerspectiveFinger)


@implementer(IFingerService)
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


@implementer(IFingerService)
class LocalFingerService(service.Service):
    def getUser(self, user):
        # need a local finger daemon running for this to work
        return utils.getProcessOutput("finger", [user])

    def getUsers(self):
        return defer.succeed([])


def main():
    # sudo /your_venv/twisted/bin/twistd -ny finger.tac
    global application
    application = service.Application("finger", uid=1, gid=1)
    f = FingerService("/etc/users")
    serviceCollection = service.IServiceCollection(application)
    f.setServiceParent(serviceCollection)
    strports.service("tcp:79", IFingerFactory(f)).setServiceParent(serviceCollection)
    site = server.Site(resource.IResource(f))
    strports.service(
        "tcp:8000",
        site,
    ).setServiceParent(serviceCollection)
    strports.service(
        "ssl:port=443:certKey=cert.pem:privateKey=key.pem", site
    ).setServiceParent(serviceCollection)
    i = IIRCClientFactory(f)
    i.nickname = "fingerbot"
    internet.ClientService(
        endpoints.clientFromString(reactor, "tcp:127.0.0.1:6667"), i
    ).setServiceParent(serviceCollection)
    strports.service("tcp:8889", pb.PBServerFactory(IPerspectiveFinger(f))
    ).setServiceParent(serviceCollection)


if __name__ == 'builtins':
    main()
