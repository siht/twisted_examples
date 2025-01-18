from twisted.internet import endpoints, protocol, reactor


class FingerProtocol(protocol.Protocol):
    pass


class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol


def main():
    fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
    fingerEndpoint.listen(FingerFactory())
    reactor.run()


if __name__ == '__main__':
    main()
