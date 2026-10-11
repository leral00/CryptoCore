import os

KEY_SIZE = 16  # AES-128
IV_SIZE = 16


class CSPRNGError(RuntimeError):
    """Не удалось получить случайные байты от операционной системы."""


def generate_random_bytes(num_bytes: int) -> bytes:
    """Возвращает ``num_bytes`` криптографически стойких случайных байт.

    :raises ValueError: если ``num_bytes`` не является положительным целым.
    :raises CSPRNGError: если источник случайности ОС недоступен.
    """
    if isinstance(num_bytes, bool) or not isinstance(num_bytes, int):
        raise ValueError("Количество байт должно быть целым числом.")

    if num_bytes <= 0:
        raise ValueError("Количество байт должно быть положительным.")

    try:
        data = os.urandom(num_bytes)
    except (OSError, NotImplementedError) as error:
        raise CSPRNGError(
            "Не удалось получить случайные байты от операционной системы "
            f"(os.urandom): {error}. Проверьте доступность /dev/urandom "
            "или системного генератора случайных чисел."
        ) from error

    if len(data) != num_bytes:
        raise CSPRNGError(
            f"Источник случайности вернул {len(data)} байт "
            f"вместо {num_bytes}."
        )

    return data


def generate_key() -> bytes:
    """Генерирует случайный 16-байтовый ключ AES-128."""
    return generate_random_bytes(KEY_SIZE)


def generate_iv() -> bytes: 
    """Генерирует случайный 16-байтовый IV."""
    return generate_random_bytes(IV_SIZE)
