from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory



class LoggingProtocol(LineReceiver):
    def lineReceived(self, line):
        self.factory.fp.write(line.decode('utf-8') + '\n')


class LogfileFactory(Factory):
    protocol = LoggingProtocol

    def __init__(self, fileName):
        self.file = fileName

    def startFactory(self):
        self.fp = open(self.file, 'a')

    def stopFactory(self):
        # escribe los datos una vez terminado este proceso
        # si quieres que sea en cada linea recibida hay que hacer un flush
        self.fp.close()


def main():
    # 8007 is the port you want to run under. Choose something >1024
    endpoint = TCP4ServerEndpoint(reactor, 8009)
    endpoint.listen(LogfileFactory('log.txt'))
    reactor.run()

if __name__ == '__main__':
    main()
