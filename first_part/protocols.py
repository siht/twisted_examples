from twisted.internet.protocol import Protocol, ServerFactory


class Echo(Protocol):
    def dataReceived(self, data):
        # lo que recibe como datos lo envía de vuelta
        self.transport.write(data) # transport es una variable interna que sólo existe cuando hay un factory y un endpoint


def main():
    from twisted.internet.endpoints import TCP4ServerEndpoint
    from twisted.internet import reactor
    
    class EchoFactory(ServerFactory):
        protocol = Echo # en este momento aun no hay un transport en el protocolo

    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(EchoFactory()) # en este momento es cuando en el factory se pone el transport que eventualmente lo sabrá protocol
    reactor.run()


if __name__ == '__main__':
    main()
