from twisted.internet import endpoints, protocol, reactor
from twisted.protocols import basic


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        self.transport.write(self.factory.getUser(user) + b"\r\n")
        self.transport.loseConnection()


class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def getUser(self, user):
        return b"No such user"


def main():
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory())
    reactor.run()


if __name__ == '__main__':
    main()
