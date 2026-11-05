import ast
import inspect

import pytest

from cryptocore import csprng
from cryptocore.csprng import CSPRNGError, generate_random_bytes


def test_returns_requested_length():
    for size in (1, 16, 32, 4096):
        data = generate_random_bytes(size)
        assert isinstance(data, bytes)
        assert len(data) == size


@pytest.mark.parametrize("bad", [0, -1, 1.5, "16", None, True])
def test_rejects_invalid_size(bad):
    with pytest.raises(ValueError):
        generate_random_bytes(bad)


def test_key_uniqueness():
    num_keys = 1000
    keys = {generate_random_bytes(16).hex() for _ in range(num_keys)}
    assert len(keys) == num_keys


def test_basic_distribution_hamming_weight():
    num_keys = 1000
    ones = sum(
        bin(int.from_bytes(generate_random_bytes(16), "big")).count("1")
        for _ in range(num_keys)
    )
    ratio = ones / (num_keys * 128)
    assert 0.48 <= ratio <= 0.52, f"Доля единиц: {ratio:.4f}"


def test_os_failure_raises_clear_error(monkeypatch):
    def broken(_):
        raise OSError("device unavailable")

    monkeypatch.setattr(csprng.os, "urandom", broken)

    with pytest.raises(CSPRNGError) as info:
        generate_random_bytes(16)

    assert "urandom" in str(info.value)


def test_short_read_is_detected(monkeypatch):
    monkeypatch.setattr(csprng.os, "urandom", lambda n: b"\x00" * (n - 1))

    with pytest.raises(CSPRNGError):
        generate_random_bytes(16)


def test_module_does_not_use_random_module():
    tree = ast.parse(inspect.getsource(csprng))
    imported = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    assert "random" not in imported
    assert "os" in imported
