import pandas as pd


class DataParams:
    def __init__(self, processed_bytes: int):
        assert isinstance(processed_bytes, int)
        self._bytes = processed_bytes

    @property
    def bytes(self) -> int:
        return self._bytes

    @staticmethod
    def plan_input():
        return DataParams(0)

    def empty(self) -> bool:
        return self._bytes == 0

    def get_scaled(self, coeff):
        return DataParams(self.bytes * coeff)

    def __repr__(self):
        return '[DataParams:' + str(self.bytes) + ']'


class Table(DataParams):
    def __init__(self, table_name, data=pd.DataFrame()):
        self._name = table_name
        self._data = data
        super().__init__(int(self.bytes()))

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    def bytes(self) -> int:
        # assume int64
        return self._data.size * 64

    def empty(self) -> bool:
        return self._data.empty

    def __repr__(self):
        return '[Table:' + self._name + ']'

    @data.setter
    def data(self, value):
        self._data = value


def merge(data_params: list) -> DataParams:
    if all(type(x) == DataParams for x in data_params):
        return DataParams(sum(x.bytes for x in data_params))
    if all(type(x) == Table for x in data_params):
        return Table('NOT_IMPLEMENTED')
    assert False  # unreachable
