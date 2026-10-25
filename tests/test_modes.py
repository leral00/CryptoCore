from Crypto.Cipher import AES

from cryptocore.modes.cbc import decrypt_cbc, encrypt_cbc
from cryptocore.modes.cfb import decrypt_cfb, encrypt_cfb
from cryptocore.modes.ctr import decrypt_ctr, encrypt_ctr
from cryptocore.modes.ofb import decrypt_ofb, encrypt_ofb


KEY = bytes.fromhex(
    "000102030405060708090a0b0c0d0e0f"
)

IV = bytes.fromhex(
    "101112131415161718191a1b1c1d1e1f"
)


def test_cbc_round_trip():
    data = b"Hello CryptoCore CBC!"

    encrypted = encrypt_cbc(data, KEY, IV)
    decrypted = decrypt_cbc(encrypted, KEY, IV)

    assert decrypted == data


def test_cfb_round_trip():
    data = b"Hello CryptoCore CFB!"

    encrypted = encrypt_cfb(data, KEY, IV)
    decrypted = decrypt_cfb(encrypted, KEY, IV)

    assert decrypted == data


def test_ofb_round_trip():
    data = b"Hello CryptoCore OFB!"

    encrypted = encrypt_ofb(data, KEY, IV)
    decrypted = decrypt_ofb(encrypted, KEY, IV)

    assert decrypted == data


def test_ctr_round_trip():
    data = b"Hello CryptoCore CTR!"

    encrypted = encrypt_ctr(data, KEY, IV)
    decrypted = decrypt_ctr(encrypted, KEY, IV)

    assert decrypted == data


def test_cbc_matches_aes():
    data = bytes.fromhex(
        "00112233445566778899aabbccddeeff"
    )

    expected = AES.new(
        KEY,
        AES.MODE_CBC,
        IV
    ).encrypt(
        data + bytes([16]) * 16
    )

    assert encrypt_cbc(data, KEY, IV) == expected


def test_stream_modes_keep_plaintext_length():
    data = b"12345"

    assert len(
        encrypt_cfb(data, KEY, IV)
    ) == len(data)

    assert len(
        encrypt_ofb(data, KEY, IV)
    ) == len(data)

    assert len(
        encrypt_ctr(data, KEY, IV)
    ) == len(data)
