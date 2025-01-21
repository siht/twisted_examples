from twisted.internet.protocol import Protocol


class Echo(Protocol):
    def __init__(self, factory):
        # esta clase se contruye cada vez que hay una conexion entrante, asi que se pierden los datos
        self.factory = factory # hay que mantener una referencia al factory entonces donde vamos a guardar datos

    def connectionMade(self):
        # este metodo se llama automagicamente cuando se hace la conexion
        self.factory.numProtocols = self.factory.numProtocols + 1
        self.transport.write("Welcome! There are currently %d open connections.\n" % (self.factory.numProtocols,))

    def connectionLost(self, reason):
        # y este metodo es llamado cuando se desconecta
        self.factory.numProtocols = self.factory.numProtocols - 1

    def dataReceived(self, data):
        # este cada vez que llegan datos
        self.transport.write(data)
