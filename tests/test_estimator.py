from unittest import TestCase

from data_params import DataParams
import device
import relops
from estimator import cost


class Test(TestCase):
    def test_cost(self):
        self.assertEqual(relops.CPU2GPU.CPU2GPU_overhead, cost(relops.CPU2GPU(), device.CPU(), DataParams(100)))
        self.assertEqual(0, cost(relops.CPU2GPU(), device.CPU(), DataParams(0)))
        self.assertEqual(0, cost(relops.MemCpy(), device.CPU(), DataParams(10)))
        self.assertEqual(1, cost(relops.MemCpy(), device.GPU(), DataParams(10)))
        self.assertEqual(relops.GPU2CPU.GPU2CPU_overhead, cost(relops.GPU2CPU(), device.GPU(), DataParams(100)))
        self.assertEqual(relops.GPU2CPU.GPU2CPU_overhead, cost(relops.GPU2CPU(), device.CPU(), DataParams(100)))
        self.assertEqual(0, cost(relops.GPU2CPU(), device.CPU(), DataParams(0)))
