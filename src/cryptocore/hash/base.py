import copy


class BlockHash:
    block_size = 64
    digest_size = 32
    name = "hash"

    _STATE_ATTRS = ()

    def __init__(self, data: bytes = b""):
        self._buffer = b""
        self._length = 0
        self._init_state()

        if data:
            self.update(data)

    def _init_state(self) -> None:
        raise NotImplementedError

    def process_block(self, block) -> None:
        raise NotImplementedError

    def _padding(self, length: int) -> bytes:
        raise NotImplementedError

    def _output(self) -> bytes:
        raise NotImplementedError

    def padding(self, message: bytes) -> bytes:
        message = bytes(message)
        return message + self._padding(len(message))

    def update(self, data: bytes) -> None:
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError("Данные для хеширования должны быть bytes.")

        data = bytes(data)
        self._length += len(data)

        if self._buffer:
            data = self._buffer + data

        block_size = self.block_size
        full = len(data) - (len(data) % block_size)
        view = memoryview(data)

        for offset in range(0, full, block_size):
            self.process_block(view[offset:offset + block_size])

        self._buffer = data[full:]

    def copy(self):
        clone = copy.copy(self)

        for name in self._STATE_ATTRS:
            setattr(clone, name, list(getattr(self, name)))

        return clone

    def digest(self) -> bytes:
        clone = self.copy()
        clone.update(self._padding(self._length))
        return clone._output()

    def hexdigest(self) -> str:
        return self.digest().hex()

    def hash(self, data: bytes) -> str:
        self.__init__()
        self.update(data)
        return self.hexdigest()
