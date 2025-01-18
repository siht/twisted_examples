from twisted.internet import (
    endpoints,
    protocol,
    reactor,
)
from twisted.protocols import basic
from twisted.internet.defer import Deferred
from twisted.web.client import (
    Agent,
    Headers,
)

class WebPageDataGetterProtocol(protocol.Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10
        self.buffer = b''
    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            self.buffer += display
            self.remaining -= len(display)
    def connectionLost(self, reason):
        self.finished.callback(self.buffer)

def getPage(url): # hacemos nuestro propio getPage asíncrono con las herramientas de twisted
    agent = Agent(reactor)
    d = agent.request(
        b'GET',
        url,
        Headers({'User-Agent': ['Twisted Web Client Example']}),
        None
    )
    def get_content(response):
        finished = Deferred()
        response.deliverBody(WebPageDataGetterProtocol(finished))
        return finished
    d.addCallback(get_content)
    return d


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        d = self.factory.getUser(user)
        def onError(err):
            return "Internal error in server"
        d.addErrback(onError)
        def writeResponse(message):
            self.transport.write(message + b"\r\n")
            self.transport.loseConnection()
        d.addCallback(writeResponse)


class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def __init__(self, prefix):
        self.prefix = prefix

    def getUser(self, user):
        return getPage(self.prefix % user)


def main():
    # ahora necesita pyOpenSSL y service-identity
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory(prefix=b"https://%s.livejournal.com/"))
    reactor.run()


if __name__ == '__main__':
    main()
