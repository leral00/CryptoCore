from Crypto.Cipher import AES

from .ecb import BLOCK_SIZE


def _validate(key: bytes, iv: bytes) -> None:
    if len(key) != BLOCK_SIZE:
        raise ValueError("Для AES-128 ключ должен иметь размер 16 байт.")

    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV должен иметь размер 16 байт.")


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def crypt_ofb(data: bytes, key: bytes, iv: bytes) -> bytes:
    _validate(key, iv)

    cipher = AES.new(key, AES.MODE_ECB)

    register = iv
    result = bytearray()

    for position in range(0, len(data), BLOCK_SIZE):
        register = cipher.encrypt(register)

        block = data[position:position + BLOCK_SIZE]

        result.extend(
            _xor_bytes(
                block,
                register[:len(block)]
            )
        )

    return bytes(result)


encrypt_ofb = crypt_ofb
decrypt_ofb = crypt_ofb

