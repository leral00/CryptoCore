from struct import pack, unpack

from .base import BlockHash


def _lfsr_bit(t: int) -> int:
    t %= 255

    if t == 0:
        return 1

    register = 1

    for _ in range(t):
        register <<= 1

        if register & 0x100:
            register ^= 0x171

    return register & 1


def _round_constants() -> tuple:
    constants = []

    for round_index in range(24):
        value = 0

        for j in range(7):
            if _lfsr_bit(j + 7 * round_index):
                value |= 1 << ((1 << j) - 1)

        constants.append(value)

    return tuple(constants)


ROUND_CONSTANTS = _round_constants()


def keccak_f1600(state):
    M = 0xFFFFFFFFFFFFFFFF
    a00, a10, a20, a30, a40, a01, a11, a21, a31, a41, a02, a12, a22, a32, a42, a03, a13, a23, a33, a43, a04, a14, a24, a34, a44 = state

    for rc in ROUND_CONSTANTS:
        # theta
        c0 = a00 ^ a01 ^ a02 ^ a03 ^ a04
        c1 = a10 ^ a11 ^ a12 ^ a13 ^ a14
        c2 = a20 ^ a21 ^ a22 ^ a23 ^ a24
        c3 = a30 ^ a31 ^ a32 ^ a33 ^ a34
        c4 = a40 ^ a41 ^ a42 ^ a43 ^ a44
        d0 = c4 ^ (((c1 << 1) | (c1 >> 63)) & M)
        d1 = c0 ^ (((c2 << 1) | (c2 >> 63)) & M)
        d2 = c1 ^ (((c3 << 1) | (c3 >> 63)) & M)
        d3 = c2 ^ (((c4 << 1) | (c4 >> 63)) & M)
        d4 = c3 ^ (((c0 << 1) | (c0 >> 63)) & M)
        # rho и pi: B[y, 2x+3y] = ROL(A[x, y] ^ D[x], r[x, y])
        b00 = (a00 ^ d0)
        b02 = (((a10 ^ d1) << 1) | ((a10 ^ d1) >> 63)) & M
        b04 = (((a20 ^ d2) << 62) | ((a20 ^ d2) >> 2)) & M
        b01 = (((a30 ^ d3) << 28) | ((a30 ^ d3) >> 36)) & M
        b03 = (((a40 ^ d4) << 27) | ((a40 ^ d4) >> 37)) & M
        b13 = (((a01 ^ d0) << 36) | ((a01 ^ d0) >> 28)) & M
        b10 = (((a11 ^ d1) << 44) | ((a11 ^ d1) >> 20)) & M
        b12 = (((a21 ^ d2) << 6) | ((a21 ^ d2) >> 58)) & M
        b14 = (((a31 ^ d3) << 55) | ((a31 ^ d3) >> 9)) & M
        b11 = (((a41 ^ d4) << 20) | ((a41 ^ d4) >> 44)) & M
        b21 = (((a02 ^ d0) << 3) | ((a02 ^ d0) >> 61)) & M
        b23 = (((a12 ^ d1) << 10) | ((a12 ^ d1) >> 54)) & M
        b20 = (((a22 ^ d2) << 43) | ((a22 ^ d2) >> 21)) & M
        b22 = (((a32 ^ d3) << 25) | ((a32 ^ d3) >> 39)) & M
        b24 = (((a42 ^ d4) << 39) | ((a42 ^ d4) >> 25)) & M
        b34 = (((a03 ^ d0) << 41) | ((a03 ^ d0) >> 23)) & M
        b31 = (((a13 ^ d1) << 45) | ((a13 ^ d1) >> 19)) & M
        b33 = (((a23 ^ d2) << 15) | ((a23 ^ d2) >> 49)) & M
        b30 = (((a33 ^ d3) << 21) | ((a33 ^ d3) >> 43)) & M
        b32 = (((a43 ^ d4) << 8) | ((a43 ^ d4) >> 56)) & M
        b42 = (((a04 ^ d0) << 18) | ((a04 ^ d0) >> 46)) & M
        b44 = (((a14 ^ d1) << 2) | ((a14 ^ d1) >> 62)) & M
        b41 = (((a24 ^ d2) << 61) | ((a24 ^ d2) >> 3)) & M
        b43 = (((a34 ^ d3) << 56) | ((a34 ^ d3) >> 8)) & M
        b40 = (((a44 ^ d4) << 14) | ((a44 ^ d4) >> 50)) & M
        # chi
        a00 = b00 ^ (~b10 & b20)
        a10 = b10 ^ (~b20 & b30)
        a20 = b20 ^ (~b30 & b40)
        a30 = b30 ^ (~b40 & b00)
        a40 = b40 ^ (~b00 & b10)
        a01 = b01 ^ (~b11 & b21)
        a11 = b11 ^ (~b21 & b31)
        a21 = b21 ^ (~b31 & b41)
        a31 = b31 ^ (~b41 & b01)
        a41 = b41 ^ (~b01 & b11)
        a02 = b02 ^ (~b12 & b22)
        a12 = b12 ^ (~b22 & b32)
        a22 = b22 ^ (~b32 & b42)
        a32 = b32 ^ (~b42 & b02)
        a42 = b42 ^ (~b02 & b12)
        a03 = b03 ^ (~b13 & b23)
        a13 = b13 ^ (~b23 & b33)
        a23 = b23 ^ (~b33 & b43)
        a33 = b33 ^ (~b43 & b03)
        a43 = b43 ^ (~b03 & b13)
        a04 = b04 ^ (~b14 & b24)
        a14 = b14 ^ (~b24 & b34)
        a24 = b24 ^ (~b34 & b44)
        a34 = b34 ^ (~b44 & b04)
        a44 = b44 ^ (~b04 & b14)
        # iota
        a00 ^= rc

    return [a00, a10, a20, a30, a40, a01, a11, a21, a31, a41, a02, a12, a22, a32, a42, a03, a13, a23, a33, a43, a04, a14, a24, a34, a44]


class SHA3_256(BlockHash):
    block_size = 136
    digest_size = 32
    name = "sha3-256"

    _STATE_ATTRS = ("lanes",)

    def _init_state(self) -> None:
        self.lanes = [0] * 25

    def _padding(self, length: int) -> bytes:
        pad_length = self.block_size - (length % self.block_size)

        if pad_length == 1:
            return b"\x86"

        return b"\x06" + b"\x00" * (pad_length - 2) + b"\x80"

    def process_block(self, block) -> None:
        words = unpack("<17Q", block)
        lanes = self.lanes

        for i in range(17):
            lanes[i] ^= words[i]

        self.lanes = keccak_f1600(lanes)

    def _output(self) -> bytes:
        return pack("<4Q", *self.lanes[:4])
