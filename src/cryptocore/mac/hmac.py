from __future__ import annotations

from ..hash import ALGORITHMS

IPAD_BYTE = 0x36
OPAD_BYTE = 0x5C


def constant_time_equal(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False

    diff = 0

    for x, y in zip(a, b):
        diff |= x ^ y

    return diff == 0


def get_hash_function(name: str):
    try:
        return ALGORITHMS[name]
    except KeyError:
        raise ValueError(
            f"Неподдерживаемый алгоритм хеширования для HMAC: {name}. "
            f"Доступно: {', '.join(sorted(ALGORITHMS))}."
        )


class HMAC:

    def __init__(self, key: bytes, hash_function: str = "sha256"):
        if not isinstance(key, (bytes, bytearray, memoryview)):
            raise TypeError("Ключ HMAC должен быть bytes.")

        self.hash_class = get_hash_function(hash_function)
        self.hash_name = hash_function
        self.block_size = self.hash_class.block_size
        self.digest_size = self.hash_class.digest_size
        self.key = self._process_key(bytes(key))

        ipad = self._xor_bytes(self.key, bytes([IPAD_BYTE]) * self.block_size)
        self._opad = self._xor_bytes(self.key, bytes([OPAD_BYTE]) * self.block_size)

        self._inner = self.hash_class()
        self._inner.update(ipad)

    def _process_key(self, key: bytes) -> bytes:
        if len(key) > self.block_size:
            key = self.hash_class(key).digest()

        if len(key) < self.block_size:
            key = key + b"\x00" * (self.block_size - len(key))

        return key

    @staticmethod
    def _xor_bytes(a: bytes, b: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(a, b))

    def update(self, data: bytes) -> None:
        self._inner.update(data)

    def copy(self) -> "HMAC":
        clone = object.__new__(HMAC)
        clone.hash_class = self.hash_class
        clone.hash_name = self.hash_name
        clone.block_size = self.block_size
        clone.digest_size = self.digest_size
        clone.key = self.key
        clone._opad = self._opad
        clone._inner = self._inner.copy()
        return clone

    def digest(self) -> bytes:
        inner_hash = self._inner.digest()

        outer = self.hash_class()
        outer.update(self._opad)
        outer.update(inner_hash)
        return outer.digest()

    def hexdigest(self) -> str:
        return self.digest().hex()

    def compute(self, message: bytes) -> str:
        mac = self.copy()
        mac.update(message)
        return mac.hexdigest()

    def compute_stream(self, stream, chunk_size: int = 8192) -> str:
        mac = self.copy()

        while True:
            chunk = stream.read(chunk_size)

            if not chunk:
                break

            mac.update(chunk)

        return mac.hexdigest()

    def verify(self, expected_hex: str, message: bytes) -> bool:
        computed = bytes.fromhex(self.compute(message))
        return constant_time_equal(computed, bytes.fromhex(expected_hex))
