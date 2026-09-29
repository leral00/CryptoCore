from Crypto.Cipher import AES

from .ecb import BLOCK_SIZE


def _validate(key: bytes, iv: bytes) -> None:
    if len(key) != BLOCK_SIZE:
        raise ValueError("Для AES-128 ключ должен иметь размер 16 байт.")

    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV должен иметь размер 16 байт.")


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def crypt_ctr(data: bytes, key: bytes, iv: bytes) -> bytes:
    _validate(key, iv)

    cipher = AES.new(key, AES.MODE_ECB)

    counter = int.from_bytes(iv, byteorder="big")
    result = bytearray()

    for position in range(0, len(data), BLOCK_SIZE):
        counter_block = counter.to_bytes(
            BLOCK_SIZE,
            byteorder="big"
        )

        keystream = cipher.encrypt(counter_block)

        block = data[position:position + BLOCK_SIZE]

        result.extend(
            _xor_bytes(
                block,
                keystream[:len(block)]
            )
        )

        counter = (counter + 1) % (1 << 128)

    return bytes(result)


encrypt_ctr = crypt_ctr
decrypt_ctr = crypt_ctr

