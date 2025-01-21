from twisted.internet.protocol import Protocol


class Echo(Protocol):
    def dataReceived(self, data):
        # lo que recibe como datos lo envía de vuelta
        self.transport.write(data) # transport es una variable interna que sólo existe cuando hay un factory y un endpoint


def main():
    # los protocoloes no hacen nada por si mismos deben estar
    # en un factory o en caso de udp parece ser no necesario
    # el ejemplo no incluye este main informativo
    pass


if __name__ == '__main__':
    main()
