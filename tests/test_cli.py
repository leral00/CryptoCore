import os
import subprocess
import sys
from pathlib import Path


KEY = "000102030405060708090a0b0c0d0e0f"


def run_cli(*arguments):
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

    return subprocess.run(
        [sys.executable, "-m", "cryptocore.cli_parser", *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
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

import re

KEY_PATTERN = re.compile(r"\[INFO\] Generated random key: ([0-9a-f]{32})")


def test_encrypt_without_key_generates_key_and_round_trips(tmp_path: Path):
    """TEST-1 / CLI-3 / KEY-1 / KEY-2."""
    original = tmp_path / "plain.txt"
    encrypted = tmp_path / "cipher.bin"
    decrypted = tmp_path / "decrypted.txt"
    data = b"CryptoCore sprint 3 " * 10
    original.write_bytes(data)

    for mode in ("ecb", "cbc", "cfb", "ofb", "ctr"):
        result = run_cli(
            "--algorithm", "aes", "--mode", mode, "--encrypt",
            "--input", str(original), "--output", str(encrypted),
        )
        assert result.returncode == 0, result.stderr

        matches = KEY_PATTERN.findall(result.stdout)
        assert len(matches) == 1
        key_hex = matches[0]

        assert bytes.fromhex(key_hex) not in encrypted.read_bytes()

        result = run_cli(
            "--algorithm", "aes", "--mode", mode, "--decrypt",
            "--key", key_hex,
            "--input", str(encrypted), "--output", str(decrypted),
        )
        assert result.returncode == 0, result.stderr
        assert decrypted.read_bytes() == data


def test_generated_keys_differ_between_runs(tmp_path: Path):
    original = tmp_path / "plain.txt"
    original.write_bytes(b"data")

    keys = set()
    for _ in range(5):
        result = run_cli(
            "--algorithm", "aes", "--mode", "cbc", "--encrypt",
            "--input", str(original), "--output", str(tmp_path / "c.bin"),
        )
        keys.add(KEY_PATTERN.search(result.stdout).group(1))

    assert len(keys) == 5


def test_decrypt_without_key_fails(tmp_path: Path):
    """CLI-4."""
    cipher = tmp_path / "cipher.bin"
    cipher.write_bytes(bytes(48))

    result = run_cli(
        "--algorithm", "aes", "--mode", "cbc", "--decrypt",
        "--input", str(cipher), "--output", str(tmp_path / "out.bin"),
    )

    assert result.returncode != 0
    assert "--key" in result.stderr
    assert not (tmp_path / "out.bin").exists()


def test_provided_key_is_used_and_not_printed(tmp_path: Path):
    """CLI-2: заданный ключ используется как раньше, [INFO] не выводится."""
    original = tmp_path / "plain.txt"
    original.write_bytes(b"data")

    result = run_cli(
        "--algorithm", "aes", "--mode", "ecb", "--encrypt",
        "--key", "3a1f5c7e9b2d4f6081a3c5e7092b4d6f",
        "--input", str(original), "--output", str(tmp_path / "c.bin"),
    )

    assert result.returncode == 0
    assert "Generated random key" not in result.stdout


def test_weak_key_warning(tmp_path: Path):
    """CLI-5."""
    original = tmp_path / "plain.txt"
    original.write_bytes(b"data")

    for weak in ("00" * 16, "ab" * 16, KEY):
        result = run_cli(
            "--algorithm", "aes", "--mode", "ecb", "--encrypt",
            "--key", weak,
            "--input", str(original), "--output", str(tmp_path / "c.bin"),
        )
        assert result.returncode == 0
        assert "слаб" in result.stderr.lower()


def test_iv_with_encrypt_fails_before_key_is_printed(tmp_path: Path):
    original = tmp_path / "plain.txt"
    original.write_bytes(b"data")

    result = run_cli(
        "--algorithm", "aes", "--mode", "cbc", "--encrypt",
        "--iv", "00" * 16,
        "--input", str(original),
    )

    assert result.returncode != 0
    assert "Generated random key" not in result.stdout
