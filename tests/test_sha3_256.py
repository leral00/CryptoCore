import hashlib
import io
import os

import pytest

from cryptocore.hash import SHA3_256, hash_stream
from cryptocore.hash.sha3_256 import ROUND_CONSTANTS

M448 = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"
M896 = (
    b"abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmno"
    b"ijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu"
)

KNOWN_ANSWERS = [
    (b"", "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"),
    (b"abc", "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"),
    (M448, "41c0dba2a9d6240849100376a8235e2c82e1b9998a999e21db32dd97496d3376"),
    (M896, "916f6061fe879741ca6469b43971dfdb28b1a32dc36cb3254e812be27aad1d18"),
    (b"a" * 1_000_000, "5c8875ae474a3634ba4fd55ec85bffd661f32aca75c6d699d0cdcb6c115891c1"),
]


@pytest.mark.parametrize("case", KNOWN_ANSWERS)
def test_known_answers(case):
    message, expected = case
    assert SHA3_256(message).hexdigest() == expected


def test_empty_input():
    assert SHA3_256().hexdigest() == (
        "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
    )


def test_round_constants_are_computed_correctly():
    assert len(ROUND_CONSTANTS) == 24
    assert ROUND_CONSTANTS[0] == 0x0000000000000001
    assert ROUND_CONSTANTS[1] == 0x0000000000008082
    assert ROUND_CONSTANTS[2] == 0x800000000000808A
    assert ROUND_CONSTANTS[23] == 0x8000000080008008


def test_matches_hashlib_for_all_padding_boundaries():
    for length in list(range(0, 300)) + [407, 408, 409]:
        data = os.urandom(length)
        assert SHA3_256(data).hexdigest() == hashlib.sha3_256(data).hexdigest(), length


def test_padding_layout():
    padded = SHA3_256().padding(b"abc")

    assert len(padded) == 136
    assert padded[:3] == b"abc"
    assert padded[3] == 0x06
    assert padded[-1] == 0x80

    assert SHA3_256().padding(b"a" * 135)[-1] == 0x86


def test_hexdigest_is_lowercase_64_chars():
    result = SHA3_256(b"abc").hexdigest()

    assert len(result) == 64
    assert result == result.lower()


def test_chunked_update_equals_single_update():
    data = os.urandom(3000)
    expected = hashlib.sha3_256(data).hexdigest()

    for step in (1, 7, 135, 136, 137, 1000):
        hasher = SHA3_256()

        for offset in range(0, len(data), step):
            hasher.update(data[offset:offset + step])

        assert hasher.hexdigest() == expected, step


def test_digest_does_not_change_state():
    hasher = SHA3_256(b"hello ")
    first = hasher.hexdigest()

    assert hasher.hexdigest() == first

    hasher.update(b"world")
    assert hasher.hexdigest() == hashlib.sha3_256(b"hello world").hexdigest()


def test_hash_stream_processes_file_in_chunks():
    data = os.urandom(50_000)

    result = hash_stream(SHA3_256(), io.BytesIO(data), 4096)

    assert result == hashlib.sha3_256(data).hexdigest()
