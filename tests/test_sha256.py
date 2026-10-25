import hashlib
import io
import os

import pytest

from cryptocore.hash import CHUNK_SIZE, SHA256, hash_stream
from cryptocore.hash.sha256 import _H0, _K

M448 = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"
M896 = (
    b"abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmno"
    b"ijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu"
)

KNOWN_ANSWERS = [
    (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    (M448, "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
    (M896, "cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1"),
    (b"a" * 1_000_000, "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"),
]


@pytest.mark.parametrize("case", KNOWN_ANSWERS)
def test_known_answers(case):
    message, expected = case
    assert SHA256(message).hexdigest() == expected


def test_empty_input():
    assert SHA256().hexdigest() == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_constants_are_computed_correctly():
    assert len(_H0) == 8 and len(_K) == 64
    assert _H0[0] == 0x6A09E667 and _H0[7] == 0x5BE0CD19
    assert _K[0] == 0x428A2F98 and _K[1] == 0x71374491
    assert _K[63] == 0xC67178F2


def test_matches_hashlib_for_all_padding_boundaries():
    for length in range(0, 200):
        data = os.urandom(length)
        assert SHA256(data).hexdigest() == hashlib.sha256(data).hexdigest(), length


def test_padding_layout():
    padded = SHA256().padding(b"abc")

    assert len(padded) == 64
    assert padded[:3] == b"abc"
    assert padded[3] == 0x80
    assert padded[-8:] == (24).to_bytes(8, "big")


def test_hexdigest_is_lowercase_64_chars():
    result = SHA256(b"abc").hexdigest()

    assert len(result) == 64
    assert result == result.lower()


def test_chunked_update_equals_single_update():
    data = os.urandom(5000)
    expected = hashlib.sha256(data).hexdigest()

    for step in (1, 7, 63, 64, 65, 1000):
        hasher = SHA256()

        for offset in range(0, len(data), step):
            hasher.update(data[offset:offset + step])

        assert hasher.hexdigest() == expected, step


def test_digest_does_not_change_state():
    hasher = SHA256(b"hello ")
    first = hasher.hexdigest()

    assert hasher.hexdigest() == first

    hasher.update(b"world")
    assert hasher.hexdigest() == hashlib.sha256(b"hello world").hexdigest()


def test_hash_method_resets_state():
    hasher = SHA256(b"garbage")

    assert hasher.hash(b"abc") == KNOWN_ANSWERS[1][1]
    assert hasher.hash(b"abc") == KNOWN_ANSWERS[1][1]


def test_hash_stream_processes_file_in_chunks():
    data = os.urandom(100_000)

    result = hash_stream(SHA256(), io.BytesIO(data), 4096)

    assert result == hashlib.sha256(data).hexdigest()


def test_update_rejects_text():
    with pytest.raises(TypeError):
        SHA256().update("abc")


@pytest.mark.skipif(
    os.getenv("CRYPTOCORE_RUN_LARGE_HASH_TEST") != "1",
    reason="Большой тест (около 80 минут на чистом Python) запускается только по запросу",
)
def test_hash_stream_processes_file_larger_than_1gb(tmp_path):
    file_path = tmp_path / "large_file.bin"
    size_mb = 1100
    block = os.urandom(1024 * 1024)

    expected_hasher = hashlib.sha256()

    with open(file_path, "wb") as file:
        for _ in range(size_mb):
            file.write(block)
            expected_hasher.update(block)

    with open(file_path, "rb") as file:
        actual_hash = hash_stream(SHA256(), file, CHUNK_SIZE)

    assert actual_hash == expected_hasher.hexdigest()
