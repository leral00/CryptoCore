import pytest

from cryptocore.modes.ecb import decrypt_ecb, encrypt_ecb, pkcs7_pad, pkcs7_unpad


KEY = bytes.fromhex("000102030405060708090a0b0c0d0e0f")


def test_pkcs7_pad():
    assert pkcs7_pad(b"123456789012345") == b"123456789012345\x01"
    assert pkcs7_pad(b"") == bytes([16]) * 16


def test_pkcs7_unpad():
    assert pkcs7_unpad(b"123456789012345\x01") == b"123456789012345"


def test_pkcs7_invalid_padding():
    with pytest.raises(ValueError):
        pkcs7_unpad(b"123456789012345\x02")


def test_aes_128_ecb_known_vector():
    # 16 байт исходных данных; при реальной работе CryptoCore
    # добавляет ещё один блок PKCS#7.
    plaintext = bytes.fromhex("00112233445566778899aabbccddeeff")
    expected_ciphertext = bytes.fromhex(
        "69c4e0d86a7b0430d8cdb78070b4c55a"
        "954f64f2e4e86e9eee82d20216684899"
    )

    assert encrypt_ecb(plaintext, KEY) == expected_ciphertext


def test_round_trip_text():
    plaintext = "Привет, CryptoCore!".encode("utf-8")
    encrypted = encrypt_ecb(plaintext, KEY)
    decrypted = decrypt_ecb(encrypted, KEY)

    assert decrypted == plaintext


def test_round_trip_binary():
    plaintext = bytes(range(256))
    encrypted = encrypt_ecb(plaintext, KEY)
    decrypted = decrypt_ecb(encrypted, KEY)

    assert decrypted == plaintext
