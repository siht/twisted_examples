from twisted.internet.protocol import Protocol


class QOTD(Protocol):
    '''protocolo que escribe una frase y se desconecta'''
    def connectionMade(self):
        self.transport.write("An apple a day keeps the doctor away\r\n")
        self.transport.loseConnection()
