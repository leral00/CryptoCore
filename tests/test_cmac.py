import os

import pytest

pytest.importorskip("Crypto")

from cryptocore.mac import CMAC

KEY = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
MESSAGE = bytes.fromhex(
    "6bc1bee22e409f96e93d7e117393172a"
    "ae2d8a571e03ac9c9eb76fac45af8e51"
    "30c81c46a35ce411e5fbc1191a0a52ef"
    "f69f2445df4f9b17ad2b417be66c3710"
)

NIST_VECTORS = [
    (0, "bb1d6929e95937287fa37d129b756746"),
    (16, "070a16b46b4d4144f79bdd9dd04a287c"),
    (40, "dfa66747de9ae63030ca32611497c827"),
    (64, "51f0bebf7e3b9d92fc49741779363cfe"),
]


def test_subkeys():
    cmac = CMAC(KEY)

    assert cmac.k1.hex() == "fbeed618357133667c85e08f7236a8de"
    assert cmac.k2.hex() == "f7ddac306ae266ccf90bc11ee46d513b"


@pytest.mark.parametrize("length,expected", NIST_VECTORS)
def test_nist_vectors(length, expected):
    assert CMAC(KEY).compute(MESSAGE[:length]) == expected


@pytest.mark.parametrize("length,expected", NIST_VECTORS)
def test_streaming_in_odd_chunks(length, expected):
    cmac = CMAC(KEY)
    data = MESSAGE[:length]

    for offset in range(0, len(data), 7):
        cmac.update(data[offset:offset + 7])

    assert cmac.hexdigest() == expected


def test_matches_pycryptodome_for_many_lengths():
    from Crypto.Hash import CMAC as RefCMAC
    from Crypto.Cipher import AES

    key = os.urandom(16)

    for length in list(range(0, 100)) + [1000, 4096, 4097]:
        data = os.urandom(length)
        reference = RefCMAC.new(key, ciphermod=AES)
        reference.update(data)

        assert CMAC(key).compute(data) == reference.hexdigest()


def test_tamper_detection():
    cmac = CMAC(KEY)
    tag = cmac.compute(b"hello")

    assert cmac.verify(tag, b"hello")
    assert not cmac.verify(tag, b"hellp")


def test_key_must_be_16_bytes():
    with pytest.raises(ValueError):
        CMAC(b"short")
