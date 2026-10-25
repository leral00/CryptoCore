from .sha256 import SHA256
from .sha3_256 import SHA3_256

CHUNK_SIZE = 8192

ALGORITHMS = {
    "sha256": SHA256,
    "sha3-256": SHA3_256,
}


def new_hasher(algorithm: str):
    try:
        return ALGORITHMS[algorithm]()
    except KeyError:
        raise ValueError(
            f"Неподдерживаемый алгоритм хеширования: {algorithm}. "
            f"Доступно: {', '.join(sorted(ALGORITHMS))}."
        )


def hash_stream(hasher, stream, chunk_size: int = CHUNK_SIZE) -> str:
    """Хеширует бинарный поток порциями: память не зависит от размера данных."""
    while True:
        chunk = stream.read(chunk_size)

        if not chunk:
            break

        hasher.update(chunk)

    return hasher.hexdigest()


__all__ = ["SHA256", "SHA3_256", "ALGORITHMS", "CHUNK_SIZE", "new_hasher", "hash_stream"]
