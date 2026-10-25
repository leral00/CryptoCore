from math import isqrt
from struct import pack, unpack

from .base import BlockHash

_MASK = 0xFFFFFFFF


def _first_primes(count: int) -> list:
    primes = []
    candidate = 2

    while len(primes) < count:
        if all(candidate % p for p in primes if p * p <= candidate):
            primes.append(candidate)
        candidate += 1

    return primes


def _icbrt(n: int) -> int:
    if n == 0:
        return 0

    x = 1 << ((n.bit_length() + 2) // 3)

    while True:
        y = (2 * x + n // (x * x)) // 3
        if y >= x:
            return x
        x = y


def _sqrt_fraction_bits(prime: int) -> int:
    return isqrt(prime << 64) & _MASK


def _cbrt_fraction_bits(prime: int) -> int:
    return _icbrt(prime << 96) & _MASK


_H0 = tuple(_sqrt_fraction_bits(p) for p in _first_primes(8))
_K = tuple(_cbrt_fraction_bits(p) for p in _first_primes(64))


class SHA256(BlockHash):
    block_size = 64
    digest_size = 32
    name = "sha256"

    _STATE_ATTRS = ("h",)

    def _init_state(self) -> None:
        self.h = list(_H0)
        self.k = _K

    def _padding(self, length: int) -> bytes:
        zeros = (55 - length) % 64
        return b"\x80" + b"\x00" * zeros + pack(">Q", (length * 8) & 0xFFFFFFFFFFFFFFFF)

    def process_block(self, block) -> None:
        k = self.k

        w = list(unpack(">16I", block))

        for i in range(16, 64):
            x = w[i - 15]
            y = w[i - 2]
            s0 = ((x >> 7) | (x << 25)) ^ ((x >> 18) | (x << 14)) ^ (x >> 3)
            s1 = ((y >> 17) | (y << 15)) ^ ((y >> 19) | (y << 13)) ^ (y >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & _MASK)

        a, b, c, d, e, f, g, h = self.h

        for ki, wi in zip(k, w):
            t1 = (
                h
                + (((e >> 6) | (e << 26)) ^ ((e >> 11) | (e << 21)) ^ ((e >> 25) | (e << 7)))
                + ((e & f) ^ (~e & g))
                + ki
                + wi
            )
            t2 = (
                (((a >> 2) | (a << 30)) ^ ((a >> 13) | (a << 19)) ^ ((a >> 22) | (a << 10)))
                + ((a & b) ^ (a & c) ^ (b & c))
            )

            h = g
            g = f
            f = e
            e = (d + t1) & _MASK
            d = c
            c = b
            b = a
            a = (t1 + t2) & _MASK

        state = self.h
        state[0] = (state[0] + a) & _MASK
        state[1] = (state[1] + b) & _MASK
        state[2] = (state[2] + c) & _MASK
        state[3] = (state[3] + d) & _MASK
        state[4] = (state[4] + e) & _MASK
        state[5] = (state[5] + f) & _MASK
        state[6] = (state[6] + g) & _MASK
        state[7] = (state[7] + h) & _MASK

    def _output(self) -> bytes:
        return pack(">8I", *self.h)
