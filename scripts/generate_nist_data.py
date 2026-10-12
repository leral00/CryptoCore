import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cryptocore.csprng import generate_random_bytes  # noqa: E402


def main() -> None:
    size_mb = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    output = sys.argv[2] if len(sys.argv) > 2 else "nist_test_data.bin"

    total = size_mb * 1_000_000
    written = 0

    with open(output, "wb") as file:
        while written < total:
            chunk = min(4096, total - written)
            file.write(generate_random_bytes(chunk))
            written += chunk

    print(f"Записано {written} байт ({written * 8} бит) в '{output}'")


if __name__ == "__main__":
    main()
