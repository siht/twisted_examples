from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from qotd_protocols import QOTD, QOTDPersonalized


class QOTDFactory(Factory):
    def buildProtocol(self, addr):
        return QOTD() # es en este metodo que se puede regresar un protocolo muy personalizado


class QOTDPersonalizedFactory(Factory):
    # This will be used by the default buildProtocol to create new protocols:
    protocol = QOTDPersonalized # no es necesario reescibir buildProtocol si no vas a hacer algo personalizado

    def __init__(self, quote=None):
        self.quote = quote or b'An apple a day keeps the doctor away' # se va a autoinyectar en el protocolo como self.factory.quote


def main():
    # 8007 is the port you want to run under. Choose something >1024
    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(QOTDPersonalizedFactory(b"configurable quote"))
    reactor.run()


if __name__ == '__main__':
    main()
