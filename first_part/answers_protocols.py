from twisted.protocols.basic import LineReceiver # line receiver ya tiene metodos aparte de dataReceived


class Answer(LineReceiver):
    answers = {'How are you?': 'Fine', None: "I don't know what you mean"}

    def lineReceived(self, line): # por ejemplo lineReceived
        if line in self.answers:
            self.sendLine(self.answers[line]) # o sendLine
        else:
            self.sendLine(self.answers[None])
