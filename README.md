# CryptoCore

Консольный инструмент для шифрования и расшифрования файлов с использованием AES-128 в режиме ECB.

## Возможности

- AES-128;
- режим ECB;
- PKCS#7 padding;
- шифрование и расшифрование текстовых и бинарных файлов;
- ключ в формате HEX;
- работа через командную строку;
- обработка ошибок;
- проверка полного цикла «шифрование → расшифрование»;
- проверка совместимости с OpenSSL.

## Требования

- Python 3.9 или новее;
- PyCryptodome;
- pytest;
- OpenSSL для проверки совместимости;
- Git.

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

Для AES-128 ключ должен иметь размер 16 байт, то есть 32 шестнадцатеричных символа.

Проверить совпадение исходного и расшифрованного файлов в Windows можно командой:

```powershell
fc /b plaintext.txt decrypted.txt
```

## Работа с бинарным файлом

CryptoCore работает с текстовыми и бинарными файлами.

Для проверки OpenSSL можно создать бинарный файл размером ровно 16 байт:

```powershell
python -c "open('plaintext.bin', 'wb').write(bytes.fromhex('00112233445566778899aabbccddeeff'))"
```

Проверка размера файла:

```powershell
(Get-Item plaintext.bin).Length
```

Результат:

```text
16
```

Для файла размером 16 байт можно выполнить шифрование CryptoCore:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.bin --output ciphertext.bin
```

CryptoCore использует PKCS#7 padding, поэтому к исходному блоку из 16 байт будет добавлен дополнительный блок padding.

## Проверка совместимости с OpenSSL

Для автоматической проверки результата CryptoCore используется OpenSSL.

Запуск автотеста:

```powershell
pytest -q tests/test_openssl.py
```

Если OpenSSL установлен и доступен в `PATH`, тест должен завершиться успешно:

```text
1 passed
```

Если OpenSSL отсутствует, тест будет пропущен:

```text
1 skipped
```

### Ручная проверка OpenSSL

Для файла размером 16 байт можно использовать OpenSSL без добавления padding:

```powershell
openssl enc -aes-128-ecb -K 000102030405060708090a0b0c0d0e0f -in plaintext.bin -out ciphertext_openssl.bin -nopad
```

Параметр `-nopad` используется, потому что размер исходного файла уже кратен размеру блока AES — 16 байтам.

Проверить размер результата:

```powershell
(Get-Item ciphertext_openssl.bin).Length
```

Результат:

```text
16
```

Для полной проверки совместимости используется автоматический тест:

```powershell
pytest -q tests/test_openssl.py
```

## Проверка полного цикла

Полный цикл работы программы:

```text
исходный файл
     ↓
  шифрование
     ↓
зашифрованный файл
     ↓
 расшифрование
     ↓
восстановленный файл
```

Пример:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
cryptocore --algorithm aes --mode ecb --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
fc /b plaintext.txt decrypted.txt
```

## Запуск тестов

Все тесты:

```powershell
pytest -q
```

Тесты ECB:

```powershell
pytest -q tests/test_ecb.py
```

Тесты CLI:

```powershell
pytest -q tests/test_cli.py
```

Тест совместимости с OpenSSL:

```powershell
pytest -q tests/test_openssl.py
```

## Обработка ошибок

Программа проверяет корректность входных параметров.

Например, неверный ключ:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 1234 --input plaintext.txt
```

В этом случае программа завершится с ошибкой и сообщит о некорректном размере ключа.

Одновременное использование `--encrypt` и `--decrypt` также является ошибкой.

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
│   ├── test_cli.py
│   └── test_openssl.py
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Назначение основных файлов

- `cli_parser.py` — обработка аргументов командной строки;
- `file_io.py` — чтение и запись файлов;
- `modes/ecb.py` — реализация AES-128 ECB и PKCS#7 padding;
- `tests/test_ecb.py` — тесты ECB и padding;
- `tests/test_cli.py` — тестирование командной строки и обработки ошибок;
- `tests/test_openssl.py` — автоматическая проверка результата CryptoCore с OpenSSL;
- `pyproject.toml` — настройки сборки и установки проекта;
- `requirements.txt` — зависимости проекта.

## Зависимости

Основная криптографическая библиотека:

```text
pycryptodome
```

Для автоматического тестирования:

```text
pytest
```

Для проверки совместимости:

```text
OpenSSL
```

## Лицензия

Проект распространяется под лицензией MIT.
