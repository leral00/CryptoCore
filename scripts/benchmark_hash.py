import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cryptocore.hash import CHUNK_SIZE, SHA256, SHA3_256

MB = 1024 * 1024

ALGORITHMS = [
    ("sha256", SHA256, hashlib.sha256),
    ("sha3-256", SHA3_256, hashlib.sha3_256),
]


def run(factory, data: bytes) -> float:
    started = time.perf_counter()
    hasher = factory()

    for offset in range(0, len(data), CHUNK_SIZE):
        hasher.update(data[offset:offset + CHUNK_SIZE])

    hasher.digest()
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser(description="Сравнение скорости SHA-256 и SHA3-256 с hashlib.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[1, 5, 10],
                        help="Размеры тестовых данных в МБ.")
    args = parser.parse_args()

    print("| Алгоритм | Размер, МБ | CryptoCore, с | CryptoCore, МБ/с | hashlib, с | Медленнее в |")
    print("|---|---|---|---|---|---|")

    for name, ours, system in ALGORITHMS:
        for size in args.sizes:
            data = os.urandom(size * MB)

            ours_time = run(ours, data)
            system_time = max(run(system, data), 1e-9)

            sample = data[:1000]
            assert ours().hash(sample) == system(sample).hexdigest()

            print(
                f"| {name} | {size} | {ours_time:.2f} | {size / ours_time:.2f} | "
                f"{system_time:.4f} | {ours_time / system_time:,.0f}x |"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())