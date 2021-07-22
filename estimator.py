import relops
from device import Device


def cost(op: relops.Operator, device: Device):
    return op.cost(device)
