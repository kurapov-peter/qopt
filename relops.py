from device import Device, CPU, GPU
from data_params import DataParams


class Operator(object):
    def cost(self, d: Device, data: DataParams) -> int:
        if isinstance(d, CPU):
            result = data.bytes
        else:
            result = data.bytes / 2
        return result

    def input_scale(self, data: DataParams, device: Device) -> DataParams:
        return data

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
    def __init__(self, table_name, table_data: DataParams):
        self._name = "RelScan"
        self._table_name = table_name
        self._table = table_data

    def table_name(self):
        return self._table_name

    def table(self):
        return self._table


class RelProject(RelOp):
    # todo: add scaling for columns projection
    def __init__(self):
        self._name = "RelProject"


class RelFilter(RelOp):
    def __init__(self):
        self._name = "RelFilter"
        self._sel = 1

    @property
    def selectivity(self):
        return self._sel

    def input_scale(self, data: DataParams, device: Device):
        return DataParams(data.bytes * self._sel)


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
    router_overhead = 10

    def __init__(self):
        self._name = "Router"
        self._cpu_coeff = 1
        self._gpu_coeff = 0

    def get_input_coeff_for_device(self, device: Device):
        if isinstance(device, CPU):
            return self._cpu_coeff
        if isinstance(device, GPU):
            return self._gpu_coeff
        raise AttributeError("Unsupported device type: ", device)

    def set_input_coeff(self, coeff: dict):
        self._cpu_coeff = coeff[CPU()]
        self._gpu_coeff = coeff[GPU()]

    def cost(self, d: Device, data: DataParams):
        if data.empty():
            return 0
        return self.router_overhead

    def input_scale(self, data: DataParams, device: Device) -> DataParams:
        # Will induce fp errors, fixme
        output_bytes = int(round(data.bytes * self.get_input_coeff_for_device(device)))
        if output_bytes < 1:
            output_bytes = 0
        return DataParams(output_bytes)


class CPU2GPU(Operator):
    CPU2GPU_overhead = 10

    def __init__(self):
        self._name = "cpu2gpu"

    def cost(self, d: Device, data: DataParams):
        if data.empty():
            return 0
        return self.CPU2GPU_overhead


class GPU2CPU(Operator):
    GPU2CPU_overhead = 10

    def __init__(self):
        self._name = "gpu2cpu"

    def cost(self, d: Device, data: DataParams):
        if data.empty():
            return 0
        return self.GPU2CPU_overhead


class MemCpy(Operator):
    def __init__(self):
        self._name = "memcpy"

    def cost(self, d: Device, data: DataParams):
        if isinstance(d, CPU):
            return 0
        return data.bytes / 10

