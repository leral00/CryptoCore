import hashlib
import hmac as stdlib_hmac
import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = str(Path(__file__).resolve().parents[1] / "src")

KEY = "00112233445566778899aabbccddeeff"
OTHER_KEY = "ffeeddccbbaa99887766554433221100"


def run_dgst(*arguments, stdin_data=None):
    existing = os.environ.get("PYTHONPATH")
    env = {
        **os.environ,
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": SRC + (os.pathsep + existing if existing else ""),
    }

    result = subprocess.run(
        [sys.executable, "-m", "cryptocore.cli_parser", "dgst", *arguments],
        input=stdin_data,
        capture_output=True,
        env=env,
    )

    stdout = result.stdout.decode("utf-8").replace("\r\n", "\n")
    stderr = result.stderr.decode("utf-8").replace("\r\n", "\n")

    return result.returncode, stdout, stderr


def hmac_args(path, key=KEY, *extra):
    return ("--algorithm", "sha256", "--hmac", "--key", key, "--input", str(path), *extra)


def test_rfc_4231_test_case_1_via_cli(tmp_path: Path):
    path = tmp_path / "test_file.txt"
    path.write_bytes(b"Hi There")

    code, out, _ = run_dgst(*hmac_args(path, "0b" * 20))

    assert code == 0
    assert out == (
        "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
        f"  {path}\n"
    )


def test_output_format(tmp_path: Path):
    path = tmp_path / "m.txt"
    path.write_bytes(b"message")

    code, out, _ = run_dgst(*hmac_args(path))
    expected = stdlib_hmac.new(bytes.fromhex(KEY), b"message", hashlib.sha256).hexdigest()

    assert code == 0
    assert out == f"{expected}  {path}\n"


def test_verify_success(tmp_path: Path):
    path = tmp_path / "message.bin"
    path.write_bytes(b"original content\n")
    mac_file = tmp_path / "file.hmac"

    code, _, _ = run_dgst(*hmac_args(path, KEY, "--output", str(mac_file)))
    assert code == 0

    code, out, err = run_dgst(*hmac_args(path, KEY, "--verify", str(mac_file)))

    assert code == 0
    assert out == "[OK] HMAC verification successful\n"
    assert err == ""


def test_tamper_detection_file(tmp_path: Path):
    path = tmp_path / "message.bin"
    path.write_bytes(b"original content\n")
    mac_file = tmp_path / "file.hmac"

    run_dgst(*hmac_args(path, KEY, "--output", str(mac_file)))

    data = bytearray(path.read_bytes())
    data[3] ^= 0x01
    path.write_bytes(bytes(data))

    code, out, err = run_dgst(*hmac_args(path, KEY, "--verify", str(mac_file)))

    assert code == 1
    assert out == ""
    assert "[ERROR] HMAC verification failed" in err


def test_tamper_detection_key(tmp_path: Path):
    path = tmp_path / "message.bin"
    path.write_bytes(b"original content\n")
    mac_file = tmp_path / "file.hmac"

    run_dgst(*hmac_args(path, KEY, "--output", str(mac_file)))

    code, _, err = run_dgst(*hmac_args(path, OTHER_KEY, "--verify", str(mac_file)))

    assert code == 1
    assert "[ERROR] HMAC verification failed" in err


@pytest.mark.parametrize("key_length", [16, 64, 100])
def test_key_sizes(tmp_path: Path, key_length):
    key = os.urandom(key_length)
    path = tmp_path / "f.bin"
    path.write_bytes(b"some data" * 100)

    code, out, _ = run_dgst(*hmac_args(path, key.hex()))
    expected = stdlib_hmac.new(key, path.read_bytes(), hashlib.sha256).hexdigest()

    assert code == 0
    assert out.split()[0] == expected


def test_empty_file(tmp_path: Path):
    path = tmp_path / "empty"
    path.write_bytes(b"")

    code, out, _ = run_dgst(*hmac_args(path))

    assert code == 0
    assert out.split()[0] == stdlib_hmac.new(
        bytes.fromhex(KEY), b"", hashlib.sha256
    ).hexdigest()


def test_multi_chunk_file(tmp_path: Path):
    data = os.urandom(200_000)
    path = tmp_path / "big.bin"
    path.write_bytes(data)

    code, out, _ = run_dgst(*hmac_args(path))

    assert code == 0
    assert out.split()[0] == stdlib_hmac.new(
        bytes.fromhex(KEY), data, hashlib.sha256
    ).hexdigest()


def test_stdin_input():
    code, out, _ = run_dgst(
        "--algorithm", "sha256", "--hmac", "--key", "4a656665", "--input", "-",
        stdin_data=b"what do ya want for nothing?",
    )

    assert code == 0
    assert out.split()[0] == (
        "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
    )


def test_hmac_sha3_256(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")

    code, out, _ = run_dgst(
        "--algorithm", "sha3-256", "--hmac", "--key", KEY, "--input", str(path)
    )

    assert code == 0
    assert out.split()[0] == stdlib_hmac.new(
        bytes.fromhex(KEY), b"abc", hashlib.sha3_256
    ).hexdigest()


def test_verify_flexible_expected_file(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")
    tag = stdlib_hmac.new(bytes.fromhex(KEY), b"abc", hashlib.sha256).hexdigest()

    variants = {
        "tag_only": f"{tag}\n",
        "upper": f"{tag.upper()}  other_name.txt\n",
        "spaces_and_blank_lines": f"\n   {tag}   whatever\r\n\r\n",
        "bom": "\ufeff" + f"{tag}  x\n",
    }

    for name, content in variants.items():
        expected_file = tmp_path / f"{name}.hmac"
        expected_file.write_bytes(content.encode("utf-8"))

        code, out, err = run_dgst(*hmac_args(path, KEY, "--verify", str(expected_file)))

        assert code == 0, (name, err)


def test_verify_utf16_expected_file(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")
    tag = stdlib_hmac.new(bytes.fromhex(KEY), b"abc", hashlib.sha256).hexdigest()
    expected_file = tmp_path / "e.hmac"
    expected_file.write_bytes(f"{tag}  f\r\n".encode("utf-16"))

    code, _, err = run_dgst(*hmac_args(path, KEY, "--verify", str(expected_file)))

    assert code == 0, err


def test_verify_malformed_expected_file(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")
    expected_file = tmp_path / "bad.hmac"
    expected_file.write_text("not-a-hex-value  f\n")

    code, _, err = run_dgst(*hmac_args(path, KEY, "--verify", str(expected_file)))

    assert code == 1
    assert "Ошибка" in err


def test_verify_empty_and_missing_expected_file(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")
    empty = tmp_path / "empty.hmac"
    empty.write_bytes(b"")

    code, _, err = run_dgst(*hmac_args(path, KEY, "--verify", str(empty)))
    assert code == 1 and "пуст" in err

    code, _, err = run_dgst(*hmac_args(path, KEY, "--verify", str(tmp_path / "nope")))
    assert code == 1 and "не найден" in err


def test_hmac_requires_key(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")

    code, out, err = run_dgst("--algorithm", "sha256", "--hmac", "--input", str(path))

    assert code == 2
    assert out == ""
    assert "--key" in err


def test_key_without_hmac_rejected(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")

    code, _, err = run_dgst("--algorithm", "sha256", "--key", KEY, "--input", str(path))

    assert code == 2
    assert "--hmac" in err


def test_verify_without_hmac_rejected(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")

    code, _, err = run_dgst(
        "--algorithm", "sha256", "--input", str(path), "--verify", str(path)
    )

    assert code == 2


def test_verify_with_output_rejected(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")

    code, _, err = run_dgst(
        *hmac_args(path, KEY, "--verify", str(path), "--output", str(tmp_path / "o"))
    )

    assert code == 2


def test_hmac_and_cmac_are_mutually_exclusive(tmp_path: Path):
    path = tmp_path / "f"
    path.write_bytes(b"abc")

    code, _, _ = run_dgst(
        "--algorithm", "sha256", "--hmac", "--cmac", "--key", KEY, "--input", str(path)
    )

    assert code == 2


@pytest.mark.parametrize("bad_key", ["xyz", "abc", ""])
def test_invalid_hex_key(tmp_path: Path, bad_key):
    path = tmp_path / "f"
    path.write_bytes(b"abc")

    code, out, err = run_dgst(*hmac_args(path, bad_key))

    assert code == 1
    assert out == ""
    assert "Ошибка" in err


def test_hmac_missing_input_file(tmp_path: Path):
    code, _, err = run_dgst(*hmac_args(tmp_path / "missing"))

    assert code == 1
    assert "не найден" in err


def test_output_flag_writes_standard_format(tmp_path: Path):
    path = tmp_path / "data.bin"
    path.write_bytes(b"abc")
    out_path = tmp_path / "data.hmac"

    code, out, _ = run_dgst(*hmac_args(path, KEY, "--output", str(out_path)))
    _, printed, _ = run_dgst(*hmac_args(path))

    assert code == 0
    assert out == ""
    assert out_path.read_bytes() == printed.encode("utf-8")

def test_cmac_cli_nist_vector(tmp_path: Path):
    pytest.importorskip("Crypto")
    path = tmp_path / "m"
    path.write_bytes(bytes.fromhex("6bc1bee22e409f96e93d7e117393172a"))

    code, out, _ = run_dgst(
        "--cmac", "--key", "2b7e151628aed2a6abf7158809cf4f3c", "--input", str(path)
    )

    assert code == 0
    assert out == f"070a16b46b4d4144f79bdd9dd04a287c  {path}\n"


def test_cmac_cli_verify_and_tamper(tmp_path: Path):
    pytest.importorskip("Crypto")
    path = tmp_path / "m"
    path.write_bytes(b"cmac data")
    mac_file = tmp_path / "m.cmac"
    args = ("--cmac", "--key", KEY, "--input", str(path))

    assert run_dgst(*args, "--output", str(mac_file))[0] == 0

    code, out, _ = run_dgst(*args, "--verify", str(mac_file))
    assert code == 0 and out == "[OK] CMAC verification successful\n"

    path.write_bytes(b"cmac datA")
    code, _, err = run_dgst(*args, "--verify", str(mac_file))
    assert code == 1 and "[ERROR] CMAC verification failed" in err


def test_cmac_requires_16_byte_key(tmp_path: Path):
    path = tmp_path / "m"
    path.write_bytes(b"x")

    code, _, err = run_dgst("--cmac", "--key", "00" * 20, "--input", str(path))

    assert code == 1
    assert "32" in err
