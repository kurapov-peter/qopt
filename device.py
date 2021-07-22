class Device(object):
    pass


class CPU(Device):
    def __repr__(self):
        return "cpu"

    def __str__(self):
        return "cpu"


class GPU(Device):
    def __repr__(self):
        return "gpu"

    def __str__(self):
        return "gpu"
