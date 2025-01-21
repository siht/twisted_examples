# Easy configuration
# makeService from finger module
import encodings.idna # este import no debería estar, pero si no, no funciona
from twisted.application import service
from twisted.application import internet, service, strports
from twisted.internet import endpoints, reactor
from twisted.spread import pb
from twisted.web import resource, server
from finger import FingerService, IFingerFactory, IIRCClientFactory, IPerspectiveFinger


def makeService(config):
    # finger on port 79
    serviceCollection = service.MultiService()
    f = FingerService(config["file"])
    f.setServiceParent(serviceCollection)
    h = strports.service("tcp:79", IFingerFactory(f))
    h.setServiceParent(serviceCollection)
    # website on port 8000
    r = resource.IResource(f)
    r.templateDirectory = config["templates"]
    site = server.Site(r)
    j = strports.service("tcp:8000", site)
    j.setServiceParent(serviceCollection)
    # ssl on port 443
    if config.get("ssl"):
        k = strports.service("ssl:port=443:certKey=cert.pem:privateKey=key.pem", site)
        k.setServiceParent(serviceCollection)
    # irc fingerbot
    if "ircnick" in config:
        i = IIRCClientFactory(f)
        i.nickname = config["ircnick"]
        ircserver = config["ircserver"]
        b = internet.ClientService(
            endpoints.HostnameEndpoint(reactor, ircserver, 6667), i
        )
        b.setServiceParent(serviceCollection)
    # Pespective Broker on port 8889
    if "pbport" in config:
        m = internet.StreamServerEndpointService(
        endpoints.TCP4ServerEndpoint(reactor, int(config["pbport"])),
            pb.PBServerFactory(IPerspectiveFinger(f)),
        )
        m.setServiceParent(serviceCollection)
    return serviceCollection
