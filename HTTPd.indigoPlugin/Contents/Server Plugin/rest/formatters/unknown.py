from formatter import Formatter

class Unknown(Formatter):
    def can_format(self, device):
        return True