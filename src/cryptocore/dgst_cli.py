import argparse
import os
import sys

from .hash import ALGORITHMS, CHUNK_SIZE, hash_stream, new_hasher
from .mac import CMAC, HMAC, constant_time_equal


def build_dgst_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cryptocore dgst",
        description=(
            "Вычисление хеша (message digest) файла, а также кода аутентификации "
            "сообщения: HMAC (--hmac) и AES-CMAC (--cmac). Параметры шифрования "
            "(--mode, --encrypt, --decrypt, --iv) в этой команде не используются; "
            "--key допустим только вместе с --hmac или --cmac."
        )
    )

    parser.add_argument(
        "--algorithm",
        choices=sorted(ALGORITHMS),
        help=(
            "Алгоритм хеширования. Обязателен, кроме режима --cmac. "
            "С --hmac определяет хеш-функцию HMAC."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        dest="input_file",
        help="Путь к входному файлу. '-' означает стандартный ввод."
    )

    parser.add_argument(
        "--output",
        dest="output_file",
        help="Записать результат в файл вместо вывода на экран."
    )

    mode = parser.add_mutually_exclusive_group()

    mode.add_argument(
        "--hmac",
        action="store_true",
        help="Вычислить HMAC (RFC 2104); требует --key."
    )

    mode.add_argument(
        "--cmac",
        action="store_true",
        help="Вычислить AES-128-CMAC (NIST SP 800-38B); требует --key (32 hex-символа)."
    )

    parser.add_argument(
        "--key",
        help=(
            "Ключ в HEX-формате. Для --hmac — произвольной длины, для --cmac — "
            "ровно 16 байт (32 hex-символа)."
        )
    )

    parser.add_argument(
        "--verify",
        metavar="FILE",
        help=(
            "Файл с ожидаемым значением MAC (формат вывода этой команды). "
            "Вычисленный MAC сравнивается с ним; код возврата 0 — совпало, "
            "1 — не совпало. Только вместе с --hmac или --cmac."
        )
    )

    return parser


def validate_args(parser: argparse.ArgumentParser, args) -> None:
    mac_mode = args.hmac or args.cmac

    if args.hmac and args.key is None:
        parser.error("для --hmac параметр --key обязателен.")

    if args.cmac and args.key is None:
        parser.error("для --cmac параметр --key обязателен.")

    if args.key is not None and not mac_mode:
        parser.error("параметр --key допустим только вместе с --hmac или --cmac.")

    if args.verify is not None and not mac_mode:
        parser.error("параметр --verify допустим только вместе с --hmac или --cmac.")

    if args.verify is not None and args.output_file:
        parser.error("параметры --verify и --output нельзя использовать одновременно.")

    if not args.cmac and args.algorithm is None:
        parser.error("the following arguments are required: --algorithm")


def parse_mac_key(key_text: str, exact_length: int = None) -> bytes:
    key_text = key_text.strip()

    if not key_text:
        raise ValueError("Ключ не может быть пустым.")

    if len(key_text) % 2 != 0:
        raise ValueError("Ключ должен содержать чётное число hex-символов.")

    try:
        key = bytes.fromhex(key_text)
    except ValueError:
        raise ValueError("Ключ должен быть указан в HEX-формате.")

    if exact_length is not None and len(key) != exact_length:
        raise ValueError(
            f"Для AES-CMAC ключ должен содержать ровно {exact_length * 2} "
            f"шестнадцатеричных символов ({exact_length} байт)."
        )

    return key


def _open_input(input_path: str):
    if input_path == "-":
        return None

    if os.path.isdir(input_path):
        raise OSError(f"Указан каталог, а не файл: {input_path}")

    try:
        return open(input_path, "rb")
    except FileNotFoundError:
        raise OSError(f"Входной файл не найден: {input_path}")
    except PermissionError:
        raise OSError(f"Нет доступа к входному файлу: {input_path}")
    except OSError as error:
        raise OSError(f"Не удалось прочитать файл '{input_path}': {error}")


def _feed_stream(update, input_path: str) -> None:
    file = _open_input(input_path)

    try:
        stream = sys.stdin.buffer if file is None else file

        while True:
            chunk = stream.read(CHUNK_SIZE)

            if not chunk:
                break

            update(chunk)
    except OSError as error:
        raise OSError(f"Не удалось прочитать файл '{input_path}': {error}")
    finally:
        if file is not None:
            file.close()


def compute_digest(algorithm: str, input_path: str) -> str:
    hasher = new_hasher(algorithm)
    _feed_stream(hasher.update, input_path)
    return hasher.hexdigest()


def compute_hmac(algorithm: str, key: bytes, input_path: str) -> str:
    mac = HMAC(key, algorithm)
    _feed_stream(mac.update, input_path)
    return mac.hexdigest()


def compute_cmac(key: bytes, input_path: str) -> str:
    mac = CMAC(key)
    _feed_stream(mac.update, input_path)
    return mac.hexdigest()


def format_line(digest: str, input_path: str) -> str:
    return f"{digest}  {input_path}"


def _decode_text(raw: bytes) -> str:
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")

    return raw.decode("utf-8-sig", errors="replace")


def read_expected_mac(path: str, digest_size: int, label: str) -> str:
    try:
        with open(path, "rb") as file:
            raw = file.read(1 << 20)
    except FileNotFoundError:
        raise OSError(f"Файл с ожидаемым {label} не найден: {path}")
    except PermissionError:
        raise OSError(f"Нет доступа к файлу с ожидаемым {label}: {path}")
    except OSError as error:
        raise OSError(f"Не удалось прочитать файл '{path}': {error}")

    token = ""

    for line in _decode_text(raw).splitlines():
        parts = line.split()

        if parts:
            token = parts[0]
            break

    if not token:
        raise ValueError(f"Файл с ожидаемым {label} пуст: {path}")

    expected_length = digest_size * 2

    try:
        bytes.fromhex(token)
        valid = len(token) == expected_length
    except ValueError:
        valid = False

    if not valid:
        raise ValueError(
            f"Файл '{path}' не содержит корректного {label}: ожидается "
            f"{expected_length} hex-символов в начале строки."
        )

    return token.lower()


def run_dgst(argv) -> int:
    parser = build_dgst_parser()
    args = parser.parse_args(argv)
    validate_args(parser, args)

    try:
        if args.hmac or args.cmac:
            return run_mac(args)

        digest = compute_digest(args.algorithm, args.input_file)
        line = format_line(digest, args.input_file)
        write_result(line, args.output_file)

        return 0

    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1


def write_result(line: str, output_file) -> None:
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8", newline="\n") as file:
                file.write(line + "\n")
        except OSError as error:
            raise OSError(f"Не удалось записать файл '{output_file}': {error}")
    else:
        print(line)


def run_mac(args) -> int:
    if args.cmac:
        label = "CMAC"
        key = parse_mac_key(args.key, exact_length=16)
        digest_size = 16
    else:
        label = "HMAC"
        key = parse_mac_key(args.key)
        digest_size = HMAC(key, args.algorithm).digest_size

    expected = None

    if args.verify is not None:
        expected = read_expected_mac(args.verify, digest_size, label)

    if args.cmac:
        computed = compute_cmac(key, args.input_file)
    else:
        computed = compute_hmac(args.algorithm, key, args.input_file)

    if expected is None:
        write_result(format_line(computed, args.input_file), args.output_file)
        return 0

    if constant_time_equal(bytes.fromhex(computed), bytes.fromhex(expected)):
        print(f"[OK] {label} verification successful")
        return 0

    print(f"[ERROR] {label} verification failed", file=sys.stderr)
    return 1
