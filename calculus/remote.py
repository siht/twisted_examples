# -*- test-case-name: calculus.test.test_remote -*-
from calculus.base import Calculation
from twisted.internet import protocol
from twisted.protocols import basic


class CalculationProxy:
    def __init__(self):
        self.calc = Calculation()
        for m in ["add", "subtract", "multiply", "divide"]:
            setattr(self, f"remote_{m}", getattr(self.calc, m))


class RemoteCalculationProtocol(basic.LineReceiver):
    def __init__(self):
        self.proxy = CalculationProxy()

    def lineReceived(self, line):
        op, a, b = line.decode("utf-8").split()
        a = int(a)
        b = int(b)
        op = getattr(self.proxy, f"remote_{op}")
        result = op(a, b)
        self.sendLine(str(result).encode("utf-8"))


class RemoteCalculationFactory(protocol.Factory):
    protocol = RemoteCalculationProtocol


def main():
    import sys
    from twisted.internet import reactor
    from twisted.python import log
    log.startLogging(sys.stdout)
    reactor.listenTCP(0, RemoteCalculationFactory())
    reactor.run()


if __name__ == "__main__":
    main()