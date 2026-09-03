# CryptoCore

Консольный инструмент для шифрования и расшифрования файлов с использованием AES-128 в режиме ECB.

## Возможности

- AES-128;
- режим ECB;
- PKCS#7 padding;
- шифрование и расшифрование текстовых и бинарных файлов;
- ключ в формате HEX;
- работа через командную строку;
- понятная обработка ошибок;
- проверка полного цикла «шифрование → расшифрование».

## Требования

- Python 3.9 или новее;
- pycryptodome;
- pytest для запуска тестов;
- Git для работы с репозиторием.

## Установка

Откройте терминал в корневой папке проекта.

### 1. Создание виртуального окружения

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Установка зависимостей

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

После установки команда `cryptocore` становится доступна в терминале.

## Использование

### Шифрование

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
```

### Расшифрование

```powershell
cryptocore --algorithm aes --mode ecb --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
```

Если `--output` не указан:

- при шифровании будет использовано имя `<input>.enc`;
- при расшифровании будет использовано имя `<input>.dec`.

## Проверка

Запуск тестов:

```powershell
pytest -q
```

Основная проверка:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input original_file.txt --output ciphertext.bin
cryptocore --algorithm aes --mode ecb --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
```

Затем сравните файлы:

```powershell
fc /b original_file.txt decrypted.txt
```

Команда не должна обнаружить различий.

## Проверка с OpenSSL

Для файла, размер которого уже кратен 16 байтам, можно сравнить шифртекст с OpenSSL:

```powershell
openssl enc -aes-128-ecb -K 000102030405060708090a0b0c0d0e0f -in plaintext.bin -out ciphertext_openssl.bin -nopad
```

Параметр `-nopad` здесь используется только для данных, размер которых кратен 16 байтам. CryptoCore самостоятельно реализует PKCS#7.

## Структура проекта

```text
CryptoCore/
├── src/
│   └── cryptocore/
│       ├── __init__.py
│       ├── cli_parser.py
│       ├── file_io.py
│       └── modes/
│           ├── __init__.py
│           └── ecb.py
├── tests/
│   ├── test_ecb.py
│   └── test_cli.py
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```
