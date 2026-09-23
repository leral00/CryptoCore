import subprocess
import sys
from pathlib import Path


KEY = "000102030405060708090a0b0c0d0e0f"


def run_cli(*arguments):
    return subprocess.run(
        [sys.executable, "-m", "cryptocore.cli_parser", *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_cli_round_trip(tmp_path: Path):
    original = tmp_path / "original.bin"
    encrypted = tmp_path / "ciphertext.bin"
    decrypted = tmp_path / "decrypted.bin"

    data = bytes(range(256))
    original.write_bytes(data)

    encrypt_result = run_cli(
        "--algorithm", "aes",
        "--mode", "ecb",
        "--encrypt",
        "--key", KEY,
        "--input", str(original),
        "--output", str(encrypted),
    )

    assert encrypt_result.returncode == 0
    assert encrypted.exists()

    decrypt_result = run_cli(
        "--algorithm", "aes",
        "--mode", "ecb",
        "--decrypt",
        "--key", KEY,
        "--input", str(encrypted),
        "--output", str(decrypted),
    )

    assert decrypt_result.returncode == 0
    assert decrypted.read_bytes() == data


def test_cli_rejects_invalid_key(tmp_path: Path):
    original = tmp_path / "original.txt"
    original.write_bytes(b"test")

    result = run_cli(
        "--algorithm", "aes",
        "--mode", "ecb",
        "--encrypt",
        "--key", "1234",
        "--input", str(original),
    )

    assert result.returncode != 0
    assert "ключ" in result.stderr.lower()


def test_cli_rejects_both_operations(tmp_path: Path):
    original = tmp_path / "original.txt"
    original.write_bytes(b"test")

    result = run_cli(
        "--algorithm", "aes",
        "--mode", "ecb",
        "--encrypt",
        "--decrypt",
        "--key", KEY,
        "--input", str(original),
    )

    assert result.returncode != 0

