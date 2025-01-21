from twisted.internet.protocol import Protocol


class QOTD(Protocol):
    '''protocolo que escribe una frase y se desconecta'''
    def connectionMade(self):
        self.transport.write(b"An apple a day keeps the doctor away\r\n")
        self.transport.loseConnection()


class QOTDPersonalized(Protocol):
    def connectionMade(self):
        # self.factory was set by the factory's default buildProtocol:
        self.transport.write(self.factory.quote + b'\r\n') # esto será añadido por el factory en la construccion
        self.transport.loseConnection()
