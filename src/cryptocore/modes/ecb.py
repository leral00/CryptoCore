from Crypto.Cipher import AES


BLOCK_SIZE = 16


def pkcs7_pad(data: bytes) -> bytes:
    padding_length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([padding_length]) * padding_length


def pkcs7_unpad(data: bytes) -> bytes:
    if not data or len(data) % BLOCK_SIZE != 0:
        raise ValueError("Некорректные данные для PKCS#7 padding.")

    padding_length = data[-1]

    if padding_length < 1 or padding_length > BLOCK_SIZE:
        raise ValueError("Некорректный PKCS#7 padding.")

    if data[-padding_length:] != bytes([padding_length]) * padding_length:
        raise ValueError("Некорректный PKCS#7 padding.")

    return data[:-padding_length]


def encrypt_ecb(data: bytes, key: bytes) -> bytes:
    if len(key) != 16:
        raise ValueError("Для AES-128 ключ должен иметь размер 16 байт.")

    padded_data = pkcs7_pad(data)
    cipher = AES.new(key, AES.MODE_ECB)

    encrypted = bytearray()

    for position in range(0, len(padded_data), BLOCK_SIZE):
        block = padded_data[position:position + BLOCK_SIZE]
        encrypted.extend(cipher.encrypt(block))

    return bytes(encrypted)


def decrypt_ecb(data: bytes, key: bytes) -> bytes:
    if len(key) != 16:
        raise ValueError("Для AES-128 ключ должен иметь размер 16 байт.")

    if not data or len(data) % BLOCK_SIZE != 0:
        raise ValueError("Размер зашифрованных данных должен быть кратен 16 байтам.")

    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = bytearray()

    for position in range(0, len(data), BLOCK_SIZE):
        block = data[position:position + BLOCK_SIZE]
        decrypted.extend(cipher.decrypt(block))

    return pkcs7_unpad(bytes(decrypted))
