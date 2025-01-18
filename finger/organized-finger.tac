# organized-finger.tac
# eg: twistd -ny organized-finger.tac
import sys
sys.path.append('.')
import finger
from twisted.application import internet, service, strports
from twisted.internet import endpoints, reactor
from twisted.spread import pb
from twisted.web import resource, server


def main():
    global application
    application = service.Application("finger", uid=1, gid=1)
    f = finger.FingerService("/etc/users")
    serviceCollection = service.IServiceCollection(application)
    f.setServiceParent(serviceCollection)
    strports.service("tcp:79", finger.IFingerFactory(f)).setServiceParent(serviceCollection)
    site = server.Site(resource.IResource(f))
    strports.service("tcp:8000", site).setServiceParent(serviceCollection)
    strports.service("ssl:port=443:certKey=cert.pem:privateKey=key.pem", site).setServiceParent(serviceCollection)
    i = finger.IIRCClientFactory(f)
    i.nickname = "fingerbot"
    internet.ClientService(endpoints.clientFromString(reactor, "tcp:127.0.0.1:6667"), i).setServiceParent(serviceCollection)
    strports.service("tcp:8889", pb.PBServerFactory(finger.IPerspectiveFinger(f))).setServiceParent(serviceCollection)


if __name__ == 'builtins':
    main()
