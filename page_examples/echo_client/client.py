from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout


__all__ = (
    'Echo',
)


class Echo(Protocol):
    def dataReceived(self, data:bytes):
        s_data = data.decode('utf-8')
        stdout.write(s_data)


class EchoClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return Echo()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)


def main():
    reactor.connectTCP('localhost', 1234, EchoClientFactory())
    reactor.run()


if __name__ == '__main__':
    main()
