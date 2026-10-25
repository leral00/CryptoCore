import argparse
import os
import sys

from .hash import ALGORITHMS, CHUNK_SIZE, hash_stream, new_hasher


def build_dgst_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cryptocore dgst",
        description=(
            "Вычисление хеша (message digest) файла. "
            "Параметры шифрования (--key, --mode, --encrypt, --decrypt, --iv) "
            "в этой команде не используются."
        )
    )

    parser.add_argument(
        "--algorithm",
        required=True,
        choices=sorted(ALGORITHMS),
        help="Алгоритм хеширования."
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

    return parser


def compute_digest(algorithm: str, input_path: str) -> str:
    hasher = new_hasher(algorithm)

    if input_path == "-":
        return hash_stream(hasher, sys.stdin.buffer, CHUNK_SIZE)

    if os.path.isdir(input_path):
        raise OSError(f"Указан каталог, а не файл: {input_path}")

    try:
        with open(input_path, "rb") as file:
            return hash_stream(hasher, file, CHUNK_SIZE)
    except FileNotFoundError:
        raise OSError(f"Входной файл не найден: {input_path}")
    except PermissionError:
        raise OSError(f"Нет доступа к входному файлу: {input_path}")
    except OSError as error:
        raise OSError(f"Не удалось прочитать файл '{input_path}': {error}")


def format_line(digest: str, input_path: str) -> str:
    return f"{digest}  {input_path}"


def run_dgst(argv) -> int:
    args = build_dgst_parser().parse_args(argv)

    try:
        digest = compute_digest(args.algorithm, args.input_file)
        line = format_line(digest, args.input_file)

        if args.output_file:
            try:
                with open(args.output_file, "w", encoding="utf-8", newline="\n") as file:
                    file.write(line + "\n")
            except OSError as error:
                raise OSError(f"Не удалось записать файл '{args.output_file}': {error}")
        else:
            print(line)

        return 0

    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1