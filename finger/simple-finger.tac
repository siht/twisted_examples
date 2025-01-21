# simple-finger.tac
# eg: twistd -ny simple-finger.tac
import sys
sys.path.append('.')
import finger_config
from twisted.application import service


def main():
    global application
    options = {
        "file": "/etc/users",
        "templates": "/usr/share/finger/templates",
        "ircnick": "fingerbot",
        "ircserver": "127.0.0.1",
        "pbport": 8889,
        "ssl": "ssl=0",
    }
    application = service.Application("finger", uid=1, gid=1)
    serviceCollection = finger_config.makeService(options)
    serviceCollection.setServiceParent(service.IServiceCollection(application))


if __name__ == 'builtins':
    main()
