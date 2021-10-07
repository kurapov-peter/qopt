import numbers

import pandas as pd
import numpy as np


class DataParams:
    def __init__(self, processed_bytes: int):
        assert isinstance(processed_bytes, numbers.Integral)
        self._bytes = processed_bytes

    @property
    def bytes(self) -> int:
        return self._bytes

    @property
    def name(self):
        return None

    @staticmethod
    def plan_input():
        return DataParams(0)

    def empty(self) -> bool:
        return self._bytes == 0

    def get_scaled(self, coeff):
        out_bytes = int(self.bytes * coeff)
        return DataParams(0 if out_bytes < 1 else out_bytes)

    def __repr__(self):
        return '[DataParams:' + str(self.bytes) + ']'


class Table(DataParams):
    def __init__(self, table_name, data=pd.DataFrame()):
        self._name = table_name
        self._data = data
        super().__init__(int(self.bytes))

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def name(self):
        return self._name

    @property
    def bytes(self) -> int:
        # assume int64
        assert all([x.dtype == np.int64 for _, x in self.data.items()])
        return self.data.size * 64

    def empty(self) -> bool:
        return self._data.empty

    def get_scaled(self, coeff):
        np.random.seed(10)  # todo
        new_data = self.data
        remove_n = len(self.data) - int(len(self.data) * coeff)
        assert remove_n >= 0
        indices = np.random.choice(new_data.index, remove_n, replace=False)
        new_data = new_data.drop(indices)
        return Table(self._name, data=new_data)

    def __repr__(self):
        return '[Table:' + self._name + ':' + str(self.bytes) + ']'


def merge(data_params: list) -> DataParams:
    if all(type(x) == DataParams for x in data_params):
        return DataParams(sum(x.bytes for x in data_params))
    if all(type(x) == Table for x in data_params):
        assert all([data_params[0].name == t.name for t in data_params])
        assert all([set(data_params[0].data.columns) == set(t.data.columns) for t in data_params])
        data_lst = [t.data for t in data_params]
        res = pd.concat(data_lst, ignore_index=True, sort=False)
        return Table(data_params[0].name, res)
    assert False  # unreachable
