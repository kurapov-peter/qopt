import relops
from device import Device
from data_params import DataParams


def cost(op: relops.Operator, device: Device, data: DataParams):
    return op.cost(device, data)


def join_cost(op: relops.RelJoin, device: Device, data: list):
    assert len(data) == 2  # todo: relax
    return op.cost(device, data[0]) * op.cost(device, data[1])  # todo: relops cost
