from __future__ import annotations

from .hmac import constant_time_equal

BLOCK_SIZE = 16
_RB = 0x87


def _aes_block_encryptor(key: bytes):
    from Crypto.Cipher import AES

    return AES.new(key, AES.MODE_ECB).encrypt


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _shift_left_one(block: bytes) -> bytes:
    value = int.from_bytes(block, "big")
    return ((value << 1) & ((1 << 128) - 1)).to_bytes(BLOCK_SIZE, "big")


def _double(block: bytes) -> bytes:
    shifted = _shift_left_one(block)

    if block[0] & 0x80:
        shifted = shifted[:-1] + bytes([shifted[-1] ^ _RB])

    return shifted


class CMAC:

    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("Для AES-CMAC ключ должен иметь размер 16 байт (AES-128).")

        self._encrypt = _aes_block_encryptor(bytes(key))

        l_value = self._encrypt(b"\x00" * BLOCK_SIZE)
        self.k1 = _double(l_value)
        self.k2 = _double(self.k1)

        self._state = b"\x00" * BLOCK_SIZE
        self._buffer = b""

    def update(self, data: bytes) -> None:
        data = self._buffer + bytes(data)

        if len(data) <= BLOCK_SIZE:
            self._buffer = data
            return

        keep = len(data) % BLOCK_SIZE or BLOCK_SIZE
        process_len = len(data) - keep

        state = self._state
        encrypt = self._encrypt

        for offset in range(0, process_len, BLOCK_SIZE):
            state = encrypt(_xor(state, data[offset:offset + BLOCK_SIZE]))

        self._state = state
        self._buffer = data[process_len:]

    def digest(self) -> bytes:
        last = self._buffer

        if len(last) == BLOCK_SIZE:
            last_block = _xor(last, self.k1)
        else:
            padded = last + b"\x80" + b"\x00" * (BLOCK_SIZE - len(last) - 1)
            last_block = _xor(padded, self.k2)

        return self._encrypt(_xor(self._state, last_block))

    def hexdigest(self) -> str:
        return self.digest().hex()

    def compute(self, message: bytes) -> str:
        clone = CMAC.__new__(CMAC)
        clone._encrypt = self._encrypt
        clone.k1, clone.k2 = self.k1, self.k2
        clone._state = self._state
        clone._buffer = self._buffer
        clone.update(message)
        return clone.hexdigest()

    def verify(self, expected_hex: str, message: bytes) -> bool:
        computed = bytes.fromhex(self.compute(message))
        return constant_time_equal(computed, bytes.fromhex(expected_hex))
