from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from qotd_protocols import QOTD


class QOTDFactory(Factory):
    def buildProtocol(self, addr):
        return QOTD() # es en este metodo que se puede regresar un protocolo muy personalizado


def main():
    # 8007 is the port you want to run under. Choose something >1024
    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(QOTDFactory())
    reactor.run()


if __name__ == '__main__':
    main()
