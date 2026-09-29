from Crypto.Cipher import AES

from .ecb import BLOCK_SIZE, pkcs7_pad, pkcs7_unpad


def _validate_key(key: bytes) -> None:
    if len(key) != BLOCK_SIZE:
        raise ValueError("Для AES-128 ключ должен иметь размер 16 байт.")


def _validate_iv(iv: bytes) -> None:
    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV должен иметь размер 16 байт.")


def _xor_blocks(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_cbc(data: bytes, key: bytes, iv: bytes) -> bytes:
    _validate_key(key)
    _validate_iv(iv)

    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = pkcs7_pad(data)

    previous = iv
    result = bytearray()

    for position in range(0, len(padded_data), BLOCK_SIZE):
        block = padded_data[position:position + BLOCK_SIZE]

        encrypted = cipher.encrypt(
            _xor_blocks(block, previous)
        )

        result.extend(encrypted)
        previous = encrypted

    return bytes(result)


def decrypt_cbc(data: bytes, key: bytes, iv: bytes) -> bytes:
    _validate_key(key)
    _validate_iv(iv)

    if not data or len(data) % BLOCK_SIZE != 0:
        raise ValueError(
            "Размер зашифрованных данных должен быть кратен 16 байтам."
        )

    cipher = AES.new(key, AES.MODE_ECB)

    previous = iv
    result = bytearray()

    for position in range(0, len(data), BLOCK_SIZE):
        block = data[position:position + BLOCK_SIZE]

        decrypted = _xor_blocks(
            cipher.decrypt(block),
            previous
        )

        result.extend(decrypted)
        previous = block

    return pkcs7_unpad(bytes(result))
