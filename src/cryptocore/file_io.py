from pathlib import Path


def read_binary_file(path: str) -> bytes:
    file_path = Path(path)

    try:
        with file_path.open("rb") as file:
            return file.read()
    except FileNotFoundError:
        raise OSError(f"Входной файл не найден: {path}")
    except PermissionError:
        raise OSError(f"Нет доступа к входному файлу: {path}")
    except OSError as error:
        raise OSError(f"Не удалось прочитать файл '{path}': {error}")


def write_binary_file(path: str, data: bytes) -> None:
    file_path = Path(path)

    try:
        with file_path.open("wb") as file:
            file.write(data)
    except PermissionError:
        raise OSError(f"Нет доступа для записи в файл: {path}")
    except OSError as error:
        raise OSError(f"Не удалось записать файл '{path}': {error}")
