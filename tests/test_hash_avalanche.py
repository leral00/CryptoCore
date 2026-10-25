import pytest

from cryptocore.hash import SHA256, SHA3_256

ALGORITHMS = [SHA256, SHA3_256]


def count_different_bits(hash1: str, hash2: str) -> int:
    bin1 = bin(int(hash1, 16))[2:].zfill(256)
    bin2 = bin(int(hash2, 16))[2:].zfill(256)

    return sum(bit1 != bit2 for bit1, bit2 in zip(bin1, bin2))


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_avalanche_effect_changed_character(algorithm):
    hash1 = algorithm().hash(b"Hello, world!")
    hash2 = algorithm().hash(b"Hello, world?")

    diff = count_different_bits(hash1, hash2)

    assert 100 < diff < 156, f"Лавинный эффект слабый: изменилось {diff} бит"


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_avalanche_effect_single_bit_flip(algorithm):
    data = bytearray(b"The quick brown fox jumps over the lazy dog")
    base = algorithm().hash(bytes(data))

    total = 0
    flips = 0

    for byte_index in range(len(data)):
        for bit in range(8):
            modified = bytearray(data)
            modified[byte_index] ^= 1 << bit

            total += count_different_bits(base, algorithm().hash(bytes(modified)))
            flips += 1

    average = total / flips

    assert 118 < average < 138, f"Среднее число изменённых бит: {average:.1f}"
