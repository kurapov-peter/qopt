from device import Device


class Operator(object):
    def cost(self, d: Device):
        return 0

    def __str__(self):
        return str(hex(id(self))) + ' ' + self._name

    def __repr__(self):
        return str(hex(id(self))) + ' ' + self._name


class Dummy(Operator):
    def __init__(self):
        self._name = "Dummy"


class RelOp(Operator):
    pass


class RelScan(RelOp):
    def __init__(self):
        self._name = "RelScan"


class RelProject(RelOp):
    def __init__(self):
        self._name = "RelProject"


class RelFilter(RelOp):
    def __init__(self):
        self._name = "RelFilter"


class RelAgg(RelOp):
    def __init__(self):
        self._name = "RelAgg"


class RelJoin(RelOp):
    def __init__(self):
        self._name = "RelJoin"


class RelSort(RelOp):
    def __init__(self):
        self._name = "RelSort"


class RelLogical(RelOp):
    def __init__(self):
        self._name = "RelLogic"


class Router(Operator):
    def __init__(self):
        self._name = "Router"
        self._coeff = 0

    @property
    def gpu_data_coeff(self):
        return self._coeff


class CPU2GPU(Operator):
    def __init__(self):
        self._name = "cpu2gpu"


class GPU2CPU(Operator):
    def __init__(self):
        self._name = "gpu2cpu"


class MemCpy(Operator):
    def __init__(self):
        self._name = "memcpy"

