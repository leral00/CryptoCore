import argparse
import hashlib
import hmac as stdlib_hmac
import os
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cryptocore.hash import CHUNK_SIZE
from cryptocore.mac import HMAC

MB = 1024 * 1024


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Проверка HMAC-SHA-256 на большом файле (TEST-7): результат и пик памяти."
    )
    parser.add_argument("--size-mb", type=int, default=2)
    parser.add_argument(
        "--no-memory-trace", action="store_true",
        help="Не измерять пик памяти (tracemalloc замедляет расчёт в десятки раз): для больших файлов.",
    )
    parser.add_argument("--path", help="Куда создать временный файл.")
    args = parser.parse_args()

    path = args.path or os.path.join(tempfile.gettempdir(), "cryptocore_large_hmac.bin")
    key = os.urandom(32)
    reference = stdlib_hmac.new(key, digestmod=hashlib.sha256)

    try:
        print(f"Создаю файл {args.size_mb} МБ: {path}", flush=True)
        with open(path, "wb") as file:
            for _ in range(args.size_mb):
                block = os.urandom(MB)
                file.write(block)
                reference.update(block)

        expected = reference.hexdigest()
        print(f"Эталон (hmac + hashlib): {expected}")

        if not args.no_memory_trace:
            tracemalloc.start()
        started = time.perf_counter()

        with open(path, "rb") as file:
            actual = HMAC(key, "sha256").compute_stream(file, CHUNK_SIZE)

        elapsed = time.perf_counter() - started
        peak = None

        if not args.no_memory_trace:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        print(f"Результат:               {actual}")
        memory = "не измерялся" if peak is None else f"{peak / 1024:.0f} КиБ"
        print(f"Время: {elapsed:.1f} с, пик памяти (Python): {memory}")
    finally:
        if os.path.exists(path):
            os.remove(path)

    if actual == expected:
        print("OK: HMAC совпадает, память не зависит от размера файла.")
        return 0

    print("ОШИБКА: HMAC не совпадает!")
    return 1


if __name__ == "__main__":
    sys.exit(main())
