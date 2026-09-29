import argparse
import sys
from pathlib import Path

from .file_io import read_binary_file, write_binary_file
from .modes.ecb import decrypt_ecb, encrypt_ecb


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cryptocore",
        description="AES-128 ECB encryption/decryption tool."
    )

    parser.add_argument(
        "--algorithm",
        required=True,
        choices=["aes"],
        help="Алгоритм шифрования. Для Sprint 1: aes."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["ecb"],
        help="Режим работы. Для Sprint 1: ecb."
    )

    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument(
        "--encrypt",
        action="store_true",
        help="Зашифровать входной файл."
    )
    operation.add_argument(
        "--decrypt",
        action="store_true",
        help="Расшифровать входной файл."
    )

    parser.add_argument(
        "--key",
        required=True,
        help="AES-128 ключ в HEX-формате, ровно 32 шестнадцатеричных символа."
    )
    parser.add_argument(
        "--input",
        required=True,
        dest="input_file",
        help="Путь к входному файлу."
    )
    parser.add_argument(
        "--output",
        dest="output_file",
        help="Путь к выходному файлу."
    )

    return parser


def parse_key(key_text: str) -> bytes:
    if len(key_text) != 32:
        raise ValueError(
            "Ключ AES-128 должен содержать ровно 32 шестнадцатеричных символа."
        )

    try:
        key = bytes.fromhex(key_text)
    except ValueError:
        raise ValueError("Ключ должен быть указан в HEX-формате.")

    if len(key) != 16:
        raise ValueError("Ключ AES-128 должен иметь размер 16 байт.")

    return key


def get_output_path(
    input_path: str,
    decrypt: bool,
    output_path: str | None
) -> str:
    if output_path:
        return output_path

    if decrypt:
        return f"{input_path}.dec"

    return f"{input_path}.enc"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    print(
        "Предупреждение: передача ключа через командную строку "
        "может быть небезопасной.",
        file=sys.stderr
    )

    try:
        key = parse_key(args.key)

        input_data = read_binary_file(args.input_file)

        output_path = get_output_path(
            args.input_file,
            args.decrypt,
            args.output_file
        )

        if args.encrypt:
            result = encrypt_ecb(input_data, key)
        else:
            result = decrypt_ecb(input_data, key)

        write_binary_file(output_path, result)

        print(f"Готово: {output_path}")
        return 0

    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
