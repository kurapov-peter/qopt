class DataParams:
    def __init__(self, processed_bytes: int):
        self._bytes = processed_bytes

    @property
    def bytes(self) -> int:
        return self._bytes

    @staticmethod
    def plan_input():
        return DataParams(0)

    def __repr__(self):
        return '[DataParams:' + str(self.bytes) + ']'
