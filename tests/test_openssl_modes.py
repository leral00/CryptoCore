import shutil
import subprocess
import sys
from pathlib import Path

import pytest


KEY = "000102030405060708090a0b0c0d0e0f"
IV = "101112131415161718191a1b1c1d1e1f"

MODES = ["cbc", "cfb", "ofb", "ctr"]


def run_openssl(
    mode: str,
    key: str,
    iv: str,
    input_file: Path,
    output_file: Path,
    decrypt: bool = False,
):
    openssl = shutil.which("openssl")

    if openssl is None:
        pytest.skip("OpenSSL не установлен или не найден в PATH.")

    command = [
        openssl,
        "enc",
        f"-aes-128-{mode}",
        "-K",
        key,
        "-iv",
        iv,
        "-in",
        str(input_file),
        "-out",
        str(output_file),
    ]

    if decrypt:
        command.append("-d")

    return subprocess.run(
        command,
        capture_output=True,
        text=False,
    )


def run_cryptocore(
    mode: str,
    encrypt: bool,
    key: str,
    input_file: Path,
    output_file: Path,
    iv: str | None = None,
):
    command = [
        sys.executable,
        "-m",
        "cryptocore.cli_parser",
        "--algorithm",
        "aes",
        "--mode",
        mode,
        "--key",
        key,
        "--input",
        str(input_file),
        "--output",
        str(output_file),
    ]

    if encrypt:
        command.append("--encrypt")
    else:
        command.append("--decrypt")

    if iv is not None:
        command.extend(["--iv", iv])

    return subprocess.run(
        command,
        capture_output=True,
        text=False,
    )


@pytest.mark.parametrize("mode", MODES)
def test_cryptocore_encrypt_openssl_decrypt(
    mode: str,
    tmp_path: Path,
):
    plaintext = tmp_path / "plaintext.bin"
    cryptocore_output = tmp_path / "cryptocore.bin"
    openssl_output = tmp_path / "openssl.bin"

    data = b"CryptoCore Sprint 2 OpenSSL test!"

    plaintext.write_bytes(data)

    result = run_cryptocore(
        mode=mode,
        encrypt=True,
        key=KEY,
        input_file=plaintext,
        output_file=cryptocore_output,
    )

    assert result.returncode == 0, (
        f"CryptoCore завершился с ошибкой:\n"
        f"{result.stderr!r}"
    )

    encrypted_data = cryptocore_output.read_bytes()

    assert len(encrypted_data) >= 16

    generated_iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    assert len(generated_iv) == 16

    ciphertext_file = tmp_path / "ciphertext.bin"
    ciphertext_file.write_bytes(ciphertext)

    generated_iv_hex = generated_iv.hex()

    result = run_openssl(
        mode=mode,
        key=KEY,
        iv=generated_iv_hex,
        input_file=ciphertext_file,
        output_file=openssl_output,
        decrypt=True,
    )

    assert result.returncode == 0, (
        f"OpenSSL завершился с ошибкой:\n"
        f"{result.stderr!r}"
    )

    assert openssl_output.read_bytes() == data


@pytest.mark.parametrize("mode", MODES)
def test_openssl_encrypt_cryptocore_decrypt(
    mode: str,
    tmp_path: Path,
):
    plaintext = tmp_path / "plaintext.bin"
    openssl_output = tmp_path / "openssl.bin"
    cryptocore_output = tmp_path / "cryptocore.bin"

    data = b"OpenSSL Sprint 2 interoperability test!"

    plaintext.write_bytes(data)

    result = run_openssl(
        mode=mode,
        key=KEY,
        iv=IV,
        input_file=plaintext,
        output_file=openssl_output,
        decrypt=False,
    )

    assert result.returncode == 0, (
        f"OpenSSL завершился с ошибкой:\n"
        f"{result.stderr!r}"
    )

    result = run_cryptocore(
        mode=mode,
        encrypt=False,
        key=KEY,
        input_file=openssl_output,
        output_file=cryptocore_output,
        iv=IV,
    )

    assert result.returncode == 0, (
        f"CryptoCore завершился с ошибкой:\n"
        f"{result.stderr!r}"
    )

    assert cryptocore_output.read_bytes() == data
