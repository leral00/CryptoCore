from Crypto.Cipher import AES

from .ecb import BLOCK_SIZE


def _validate(key: bytes, iv: bytes) -> None:
    if len(key) != BLOCK_SIZE:
        raise ValueError("Для AES-128 ключ должен иметь размер 16 байт.")

    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV должен иметь размер 16 байт.")


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_cfb(data: bytes, key: bytes, iv: bytes) -> bytes:
    _validate(key, iv)

    cipher = AES.new(key, AES.MODE_ECB)

    register = iv
    result = bytearray()

    for position in range(0, len(data), BLOCK_SIZE):
        block = data[position:position + BLOCK_SIZE]

        keystream = cipher.encrypt(register)

        encrypted = _xor_bytes(
            block,
            keystream[:len(block)]
        )

        result.extend(encrypted)

        if len(block) == BLOCK_SIZE:
            register = encrypted

    return bytes(result)


def decrypt_cfb(data: bytes, key: bytes, iv: bytes) -> bytes:
    _validate(key, iv)

    cipher = AES.new(key, AES.MODE_ECB)

    register = iv
    result = bytearray()

    for position in range(0, len(data), BLOCK_SIZE):
        block = data[position:position + BLOCK_SIZE]

        keystream = cipher.encrypt(register)

        decrypted = _xor_bytes(
            block,
            keystream[:len(block)]
        )

        result.extend(decrypted)

        if len(block) == BLOCK_SIZE:
            register = block

    return bytes(result)

