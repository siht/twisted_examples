# -*- test-case-name: calculus.test.test_sched_client -*-
from twisted.internet import defer, reactor
from twisted.protocols import basic


class ClientTimeoutError(Exception):
    pass


class RemoteCalculationClient(basic.LineReceiver):
    callLater = reactor.callLater
    timeOut = 60

    def __init__(self):
        self.results = []

    def lineReceived(self, line):
        d, callID = self.results.pop(0)
        callID.cancel()
        d.callback(int(line))

    def _cancel(self, d):
        d.errback(ClientTimeoutError())

    def _sendOperation(self, op, a, b):
        d = defer.Deferred()
        callID = self.callLater(self.timeOut, self._cancel, d)
        self.results.append((d, callID))
        line = f"{op} {a} {b}".encode()
        self.sendLine(line)
        return d

    def add(self, a, b):
        return self._sendOperation("add", a, b)

    def subtract(self, a, b):
        return self._sendOperation("subtract", a, b)

    def multiply(self, a, b):
        return self._sendOperation("multiply", a, b)

    def divide(self, a, b):
        return self._sendOperation("divide", a, b)
