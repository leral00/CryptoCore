import argparse
import hashlib
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cryptocore.hash import CHUNK_SIZE, hash_stream, new_hasher

MB = 1024 * 1024
REFERENCE = {"sha256": hashlib.sha256, "sha3-256": hashlib.sha3_256}


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка хеширования файла больше 1 ГБ.")
    parser.add_argument("--algorithm", choices=sorted(REFERENCE), default="sha256")
    parser.add_argument("--size-mb", type=int, default=1100)
    parser.add_argument("--path", help="Куда создать временный файл.")
    parser.add_argument("--keep", action="store_true", help="Не удалять файл.")
    args = parser.parse_args()

    path = args.path or os.path.join(tempfile.gettempdir(), "cryptocore_large_test.bin")
    reference = REFERENCE[args.algorithm]()

    try:
        print(f"Создаю файл {args.size_mb} МБ: {path}", flush=True)
        with open(path, "wb") as file:
            for _ in range(args.size_mb):
                block = os.urandom(MB)
                file.write(block)
                reference.update(block)

        expected = reference.hexdigest()
        size = os.path.getsize(path)
        print(f"Размер файла: {size} байт ({size / 1024 ** 3:.2f} ГиБ)")
        print(f"Эталон (hashlib): {expected}")

        print(
            f"Считаю {args.algorithm} реализацией проекта "
            f"(порции по {CHUNK_SIZE} байт)...",
            flush=True,
        )
        started = time.perf_counter()

        with open(path, "rb") as file:
            actual = hash_stream(new_hasher(args.algorithm), file, CHUNK_SIZE)

        elapsed = time.perf_counter() - started
        print(f"Результат:        {actual}")
        print(f"Время: {elapsed:.1f} с, скорость: {size / MB / elapsed:.2f} МБ/с")
    finally:
        if not args.keep and os.path.exists(path):
            os.remove(path)

    if actual == expected:
        print("OK: хеши совпадают.")
        return 0

    print("ОШИБКА: хеши не совпадают!")
    return 1


if __name__ == "__main__":
    sys.exit(main())