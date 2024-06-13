class ZezeziError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class ZezeziWarning(Warning):
    pass
