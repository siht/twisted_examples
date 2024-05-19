from twisted.internet import (
    endpoints,
    protocol,
    reactor,
)

__all__ = (
    'Echo',
    'EchoFactory',
)

class Echo(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        print('conexion')
        self.factory.numProtocols = self.factory.numProtocols + 1
        self.transport.write(
            b'Welcome! There are currently %d open connections.\n' %
            (self.factory.numProtocols,))

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols - 1

    def dataReceived(self, data):
        self.transport.write(data)


class EchoFactory(protocol.Factory):
    def __init__(self):
        self.numProtocols = 0

    def buildProtocol(self, addr):
        return Echo(self)


def main():
    endpoints.serverFromString(reactor, 'tcp:1234').listen(EchoFactory())
    reactor.run()


if __name__ == '__main__':
    main()
