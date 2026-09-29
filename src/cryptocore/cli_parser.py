import argparse
import os
import sys

from .file_io import read_binary_file, write_binary_file
from .modes.ecb import decrypt_ecb, encrypt_ecb
from .modes.cbc import decrypt_cbc, encrypt_cbc
from .modes.cfb import decrypt_cfb, encrypt_cfb
from .modes.ofb import decrypt_ofb, encrypt_ofb
from .modes.ctr import decrypt_ctr, encrypt_ctr


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cryptocore",
        description="AES-128 encryption/decryption tool."
    )

    parser.add_argument(
        "--algorithm",
        required=True,
        choices=["aes"],
        help="Алгоритм шифрования."
    )

    parser.add_argument(
        "--mode",
        required=True,
        choices=["ecb", "cbc", "cfb", "ofb", "ctr"],
        help="Режим работы AES."
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
        help="AES-128 ключ в HEX-формате, ровно 32 символа."
    )

    parser.add_argument(
        "--iv",
        help="IV в HEX-формате. Используется при расшифровке."
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


def parse_iv(iv_text: str) -> bytes:
    if len(iv_text) != 32:
        raise ValueError(
            "IV должен содержать ровно 32 шестнадцатеричных символа."
        )

    try:
        iv = bytes.fromhex(iv_text)
    except ValueError:
        raise ValueError("IV должен быть указан в HEX-формате.")

    if len(iv) != 16:
        raise ValueError("IV должен иметь размер 16 байт.")

    return iv


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


def encrypt_data(
    data: bytes,
    key: bytes,
    mode: str,
    iv: bytes
) -> bytes:

    if mode == "cbc":
        return encrypt_cbc(data, key, iv)

    if mode == "cfb":
        return encrypt_cfb(data, key, iv)

    if mode == "ofb":
        return encrypt_ofb(data, key, iv)

    if mode == "ctr":
        return encrypt_ctr(data, key, iv)

    raise ValueError(f"Неизвестный режим: {mode}")


def decrypt_data(
    data: bytes,
    key: bytes,
    mode: str,
    iv: bytes
) -> bytes:

    if mode == "cbc":
        return decrypt_cbc(data, key, iv)

    if mode == "cfb":
        return decrypt_cfb(data, key, iv)

    if mode == "ofb":
        return decrypt_ofb(data, key, iv)

    if mode == "ctr":
        return decrypt_ctr(data, key, iv)

    raise ValueError(f"Неизвестный режим: {mode}")


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

        # ECB не использует IV
        if args.mode == "ecb":
            if args.encrypt:
                result = encrypt_ecb(input_data, key)
            else:
                result = decrypt_ecb(input_data, key)

            write_binary_file(output_path, result)

            print(f"Готово: {output_path}")
            return 0

        if args.encrypt:
            if args.iv:
                raise ValueError(
                    "--iv нельзя указывать при шифровании. "
                    "IV генерируется автоматически."
                )

            iv = os.urandom(16)

            encrypted_data = encrypt_data(
                input_data,
                key,
                args.mode,
                iv
            )

            # Формат файла:
            # первые 16 байт — IV,
            # остальные байты — ciphertext
            result = iv + encrypted_data

        else:
            if args.iv:
                iv = parse_iv(args.iv)
                ciphertext = input_data
            else:
                if len(input_data) < 16:
                    raise ValueError(
                        "Входной файл должен содержать минимум 16 байт "
                        "для хранения IV."
                    )

                iv = input_data[:16]
                ciphertext = input_data[16:]

            result = decrypt_data(
                ciphertext,
                key,
                args.mode,
                iv
            )

        write_binary_file(output_path, result)

        print(f"Готово: {output_path}")
        return 0

    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
