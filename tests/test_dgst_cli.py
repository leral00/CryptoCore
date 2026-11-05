import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SRC = str(Path(__file__).resolve().parents[1] / "src")


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


def test_sha256_output_format(tmp_path: Path):
    path = tmp_path / "abc.txt"
    path.write_bytes(b"abc")

    code, out, _ = run_dgst("--algorithm", "sha256", "--input", str(path))

    assert code == 0
    assert out == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        f"  {path}\n"
    )


def test_sha3_256_output(tmp_path: Path):
    path = tmp_path / "abc.txt"
    path.write_bytes(b"abc")

    code, out, _ = run_dgst("--algorithm", "sha3-256", "--input", str(path))

    assert code == 0
    assert out.split()[0] == (
        "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"
    )


def test_empty_file(tmp_path: Path):
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")

    code, out, _ = run_dgst("--algorithm", "sha256", "--input", str(path))

    assert code == 0
    assert out.split()[0] == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_stdin_input():
    code, out, _ = run_dgst("--algorithm", "sha256", "--input", "-", stdin_data=b"abc")

    assert code == 0
    assert out.strip() == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad  -"
    )


def test_nist_448_bit_vector_via_stdin():
    message = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"

    code, out, _ = run_dgst("--algorithm", "sha256", "--input", "-", stdin_data=message)

    assert code == 0
    assert out.split()[0] == (
        "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
    )


def test_output_flag_writes_same_line_to_file(tmp_path: Path):
    path = tmp_path / "data.bin"
    path.write_bytes(b"abc")
    out_path = tmp_path / "data.sha"

    code, out, _ = run_dgst(
        "--algorithm", "sha256", "--input", str(path), "--output", str(out_path)
    )

    _, printed, _ = run_dgst("--algorithm", "sha256", "--input", str(path))

    assert code == 0
    assert out == ""
    assert out_path.read_bytes() == printed.encode("utf-8")


@pytest.mark.parametrize("algorithm", ["sha256", "sha3-256"])
def test_multi_chunk_file_matches_hashlib(tmp_path: Path, algorithm):
    data = os.urandom(300_000) + b"tail"
    path = tmp_path / "big.bin"
    path.write_bytes(data)

    reference = hashlib.sha256 if algorithm == "sha256" else hashlib.sha3_256

    code, out, _ = run_dgst("--algorithm", algorithm, "--input", str(path))

    assert code == 0
    assert out.split()[0] == reference(data).hexdigest()


def test_missing_input_file(tmp_path: Path):
    code, out, err = run_dgst("--algorithm", "sha256", "--input", str(tmp_path / "no.txt"))

    assert code == 1
    assert out == ""
    assert "не найден" in err


def test_directory_as_input(tmp_path: Path):
    code, _, err = run_dgst("--algorithm", "sha256", "--input", str(tmp_path))

    assert code == 1
    assert "каталог" in err


@pytest.mark.parametrize(
    "extra",
    [["--mode", "cbc"], ["--encrypt"], ["--decrypt"], ["--iv", "00" * 16]],
)
def test_dgst_rejects_encryption_arguments(tmp_path: Path, extra):
    path = tmp_path / "a.txt"
    path.write_bytes(b"abc")

    code, out, err = run_dgst("--algorithm", "sha256", "--input", str(path), *extra)

    assert code == 2
    assert out == ""
    assert "unrecognized arguments" in err


def test_unknown_algorithm_rejected(tmp_path: Path):
    path = tmp_path / "a.txt"
    path.write_bytes(b"abc")

    code, _, err = run_dgst("--algorithm", "md5", "--input", str(path))

    assert code == 2
    assert "invalid choice" in err


@pytest.mark.skipif(shutil.which("sha256sum") is None, reason="sha256sum недоступен")
def test_interoperability_with_sha256sum(tmp_path: Path):
    path = tmp_path / "file.bin"
    path.write_bytes(os.urandom(20_000))

    code, out, _ = run_dgst("--algorithm", "sha256", "--input", str(path))
    system = subprocess.run(["sha256sum", str(path)], capture_output=True, text=True).stdout

    assert code == 0
    assert out == system


@pytest.mark.skipif(shutil.which("sha3sum") is None, reason="sha3sum недоступен")
def test_interoperability_with_sha3sum(tmp_path: Path):
    path = tmp_path / "file.bin"
    path.write_bytes(os.urandom(20_000))

    code, out, _ = run_dgst("--algorithm", "sha3-256", "--input", str(path))
    completed = subprocess.run(
        ["sha3sum", "-a", "256", str(path)], capture_output=True, text=True
    )

    if completed.returncode != 0:
        pytest.skip("установленный sha3sum не поддерживает ключ -a 256")

    assert code == 0
    assert out.split()[0] == completed.stdout.split()[0]
