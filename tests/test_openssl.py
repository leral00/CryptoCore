import shutil
import subprocess

import pytest


KEY = "000102030405060708090a0b0c0d0e0f"


def test_ecb_matches_openssl(tmp_path):
    openssl = shutil.which("openssl")

    if openssl is None:
        pytest.skip("OpenSSL не установлен или не найден в PATH.")

    plaintext = tmp_path / "plaintext.bin"
    cryptocore_output = tmp_path / "cryptocore.bin"
    openssl_output = tmp_path / "openssl.bin"

    plaintext.write_bytes(
        bytes.fromhex(
            "00112233445566778899aabbccddeeff"
        )
    )

    from cryptocore.modes.ecb import encrypt_ecb

    encrypted = encrypt_ecb(
        plaintext.read_bytes(),
        bytes.fromhex(KEY)
    )

    cryptocore_output.write_bytes(encrypted)

    result = subprocess.run(
        [
            openssl,
            "enc",
            "-aes-128-ecb",
            "-K",
            KEY,
            "-in",
            str(plaintext),
            "-out",
            str(openssl_output),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"OpenSSL завершился с ошибкой:\n"
        f"{result.stderr}"
    )

    assert cryptocore_output.read_bytes() == openssl_output.read_bytes()
