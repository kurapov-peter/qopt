class Device(object):
    pass


class CPU(Device):
    def __repr__(self):
        return "cpu"

    def __str__(self):
        return "cpu"

    def __eq__(self, other):
        return isinstance(other, CPU)

    def __hash__(self):
        return hash(repr(self))


class GPU(Device):
    def __repr__(self):
        return "gpu"

    def __str__(self):
        return "gpu"

    def __eq__(self, other):
        return isinstance(other, GPU)

    def __hash__(self):
        return hash(repr(self))
