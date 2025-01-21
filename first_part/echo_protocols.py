from twisted.internet.protocol import Protocol


class Echo(Protocol):
    def dataReceived(self, data):
        # lo que recibe como datos lo envía de vuelta
        self.transport.write(data) # transport es una variable interna que sólo existe cuando hay un factory y un endpoint

