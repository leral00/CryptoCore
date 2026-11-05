import hashlib
import hmac as stdlib_hmac
import io
import os
import tracemalloc

import pytest

from cryptocore.mac import HMAC, constant_time_equal

RFC_4231 = [
    (
        "0b" * 20,
        "4869205468657265",
        "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7",
    ),
    (
        "4a656665",
        "7768617420646f2079612077616e7420666f72206e6f7468696e673f",
        "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843",
    ),
    (
        "aa" * 20,
        "dd" * 50,
        "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe",
    ),
    (
        "".join(f"{i:02x}" for i in range(1, 26)),
        "cd" * 50,
        "82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b",
    ),
    (
        "aa" * 131,
        "54657374205573696e67204c6172676572205468616e20426c6f636b2d53697a"
        "65204b6579202d2048617368204b6579204669727374",
        "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54",
    ),
    (
        "aa" * 131,
        "5468697320697320612074657374207573696e672061206c6172676572207468"
        "616e20626c6f636b2d73697a65206b657920616e642061206c61726765722074"
        "68616e20626c6f636b2d73697a6520646174612e20546865206b6579206e6565"
        "647320746f20626520686173686564206265666f7265206265696e6720757365"
        "642062792074686520484d414320616c676f726974686d2e",
        "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2",
    ),
]


@pytest.mark.parametrize("case", RFC_4231, ids=["tc1", "tc2", "tc3", "tc4", "tc6", "tc7"])
def test_rfc_4231(case):
    key_hex, data_hex, expected = case

    mac = HMAC(bytes.fromhex(key_hex), "sha256")

    assert mac.compute(bytes.fromhex(data_hex)) == expected


@pytest.mark.parametrize("key_length", [0, 1, 16, 63, 64, 65, 100, 131, 200])
@pytest.mark.parametrize("message_length", [0, 1, 55, 56, 63, 64, 65, 1000])
def test_matches_stdlib_for_all_key_sizes(key_length, message_length):
    key = os.urandom(key_length)
    message = os.urandom(message_length)

    expected = stdlib_hmac.new(key, message, hashlib.sha256).hexdigest()

    assert HMAC(key, "sha256").compute(message) == expected


@pytest.mark.parametrize("key_length", [16, 64, 100])
def test_sha3_256_matches_stdlib(key_length):
    key = os.urandom(key_length)
    message = os.urandom(500)

    expected = stdlib_hmac.new(key, message, hashlib.sha3_256).hexdigest()

    assert HMAC(key, "sha3-256").compute(message) == expected


def test_key_equal_to_block_size_is_not_hashed():
    mac = HMAC(b"\x01" * 64)

    assert mac.key == b"\x01" * 64


def test_long_key_is_hashed_first():
    key = b"\x02" * 100
    mac = HMAC(key)

    assert mac.key == hashlib.sha256(key).digest() + b"\x00" * 32


def test_short_key_is_zero_padded():
    mac = HMAC(b"\x03" * 16)

    assert mac.key == b"\x03" * 16 + b"\x00" * 48


def test_empty_message():
    key = bytes.fromhex("00112233445566778899aabbccddeeff")

    assert HMAC(key).compute(b"") == stdlib_hmac.new(key, b"", hashlib.sha256).hexdigest()


def test_streaming_equals_one_shot():
    key = os.urandom(20)
    data = os.urandom(10_000)

    mac = HMAC(key)

    for offset in range(0, len(data), 777):
        mac.update(data[offset:offset + 777])

    assert mac.hexdigest() == HMAC(key).compute(data)
    assert mac.hexdigest() == HMAC(key).compute(data)


def test_compute_stream():
    key = os.urandom(32)
    data = os.urandom(50_000)

    assert HMAC(key).compute_stream(io.BytesIO(data), 1000) == HMAC(key).compute(data)


def test_compute_does_not_mutate_instance():
    mac = HMAC(b"key")

    first = mac.compute(b"abc")
    second = mac.compute(b"abc")

    assert first == second == stdlib_hmac.new(b"key", b"abc", hashlib.sha256).hexdigest()


def test_different_key_gives_different_mac():
    assert HMAC(b"key-one").compute(b"msg") != HMAC(b"key-two").compute(b"msg")


def test_one_bit_message_change_changes_mac():
    key = os.urandom(16)

    assert HMAC(key).compute(b"message") != HMAC(key).compute(b"messagf")


def test_verify_method():
    mac = HMAC(b"secret")
    tag = mac.compute(b"data")

    assert mac.verify(tag, b"data")
    assert not mac.verify(tag, b"datA")


def test_unknown_hash_rejected():
    with pytest.raises(ValueError):
        HMAC(b"key", "md5")


def test_key_must_be_bytes():
    with pytest.raises(TypeError):
        HMAC("строка")


def test_constant_time_equal():
    assert constant_time_equal(b"abc", b"abc")
    assert not constant_time_equal(b"abc", b"abd")
    assert not constant_time_equal(b"abc", b"ab")
    assert constant_time_equal(b"", b"")


def test_streaming_memory_is_constant():
    key = os.urandom(16)

    class ZeroStream:
        def __init__(self, size):
            self.remaining = size

        def read(self, n):
            n = min(n, self.remaining)
            self.remaining -= n
            return b"\x00" * n

    def peak(size):
        tracemalloc.start()
        HMAC(key).compute_stream(ZeroStream(size), 8192)
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak_bytes

    small = peak(64 * 1024)
    large = peak(2 * 1024 * 1024)

    assert large < small + 64 * 1024
    assert large < 512 * 1024
