# CryptoCore

Консольный инструмент для шифрования и расшифрования файлов с использованием AES-128 в режиме ECB, CBC, CFB, OFB и CTR.

## Возможности

- AES-128;
- режим ECB, CBC, CFB, OFB и CTR;
- PKCS#7 padding для режимов ECB и CBC;
- работа без padding для режимов CFB, OFB и CTR;
- автоматическая генерация IV для CBC, CFB, OFB и CTR;
- хранение IV в первых 16 байтах зашифрованного файла;
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
pip install -r requirements-dev.txt
pip install -e .
```

После установки команда `cryptocore` становится доступна в терминале.

## Использование

### Шифрование

Пример для ECB:
```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
```

Пример для CBC:
```powershell
cryptocore --algorithm aes --mode cbc --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
```

Для режимов CBC, CFB, OFB и CTR IV генерируется автоматически.

### Расшифрование

Пример для ECB:
```powershell
cryptocore --algorithm aes --mode ecb --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
```

Для CBC, CFB, OFB и CTR IV автоматически считывается из первых 16 байт зашифрованного файла:
```powershell
cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
```

Также IV можно указать вручную с помощью параметра --iv:
```powershell
cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --iv 101112131415161718191a1b1c1d1e1f --input ciphertext.bin --output decrypted.txt
```

Для AES-128 ключ должен иметь размер 16 байт, то есть 32 шестнадцатеричных символа.

## Работа с IV

Для режимов CBC, CFB, OFB и CTR при шифровании IV генерируется автоматически с использованием
```text
os.urandom().
```
Размер IV составляет 16 байт.

Зашифрованный файл имеет следующий формат:
```text
[16 байт IV][зашифрованные данные]
```

При расшифровании IV можно:
1. автоматически получить из первых 16 байт входного файла;
2. передать вручную через параметр --iv.

Параметр --iv используется только при расшифровании.

## Padding

Для режимов ECB и CBC используется PKCS#7 padding.

Для режимов CFB, OFB и CTR padding не используется. Поэтому после шифрования размер данных в этих режимах сохраняется.

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

Для файла размером 16 байт можно выполнить шифрование ECB:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.bin --output ciphertext.bin
```

CryptoCore использует PKCS#7 padding, поэтому к исходному блоку из 16 байт будет добавлен дополнительный блок padding.

## Проверка совместимости с OpenSSL

Для проверки совместимости CryptoCore с OpenSSL используются автоматические тесты и ручные команды.

### Автоматическая проверка

Для запуска всех тестов:

```bash
pytest -q
```

Запуск тестов совместимости:

```powershell
pytest -q tests/test_openssl_modes.py
```

```markdown
Файл `tests/test_openssl_modes.py` автоматически проверяет совместимость CBC, CFB, OFB и CTR с OpenSSL.
```

Тесты проверяют два направления:
1. CryptoCore шифрует файл → OpenSSL расшифровывает файл.
2. OpenSSL шифрует файл → CryptoCore расшифровывает файл.

Проверяются следующие режимы:

1. CBC;
2. CFB;
3. OFB;
4. CTR.

Для режимов CBC, CFB, OFB и CTR CryptoCore автоматически генерирует случайный IV размером 16 байт. При шифровании IV записывается в первые 16 байт выходного файла:
```text
[16 байт IV][зашифрованные данные]
```

При расшифровании CryptoCore может получить IV двумя способами:

1. прочитать первые 16 байт входного файла;
2. получить IV через параметр --iv.

### CryptoCore → OpenSSL

Сначала зашифруем файл с помощью CryptoCore:
```bash
python -m cryptocore.cli_parser ^
    --algorithm aes ^
    --mode cbc ^
    --encrypt ^
    --key 000102030405060708090a0b0c0d0e0f ^
    --input plaintext.bin ^
    --output cipher.bin
```

В результате `cipher.bin` содержит IV и зашифрованные данные.

Для проверки необходимо извлечь первые 16 байт как IV.

В PowerShell:
```powershell
$data = [System.IO.File]::ReadAllBytes("cipher.bin")

[System.IO.File]::WriteAllBytes(
    "ciphertext_only.bin",
    $data[16..($data.Length - 1)]
)

$iv = -join (
    $data[0..15] |
    ForEach-Object { $_.ToString("x2") }
)
```

После этого расшифруем данные через OpenSSL:
```powershell
openssl enc -aes-128-cbc -d `
    -K 000102030405060708090a0b0c0d0e0f `
    -iv $iv `
    -in ciphertext_only.bin `
    -out decrypted.bin
```

Полученный `decrypted.bin` должен совпадать с исходным `plaintext.bin`.

Для CFB, OFB и CTR используется тот же принцип. Меняется только режим:
```text
-aes-128-cfb
-aes-128-ofb
-aes-128-ctr
```

Для этих режимов padding не используется.

### OpenSSL → CryptoCore

Сначала зашифруем файл через OpenSSL:
```powershell
openssl enc -aes-128-cbc `
    -K 000102030405060708090a0b0c0d0e0f `
    -iv 101112131415161718191a1b1c1d1e1f `
    -in plaintext.bin `
    -out openssl_cipher.bin
```

После этого расшифруем его с помощью CryptoCore:
```bash
python -m cryptocore.cli_parser ^
    --algorithm aes ^
    --mode cbc ^
    --decrypt ^
    --key 000102030405060708090a0b0c0d0e0f ^
    --iv 101112131415161718191a1b1c1d1e1f ^
    --input openssl_cipher.bin ^
    --output decrypted.bin
```

Полученный `decrypted.bin` должен совпадать с `plaintext.bin`.

Для CFB, OFB и CTR аналогично меняется значение --mode и алгоритм OpenSSL:
```text
CFB: -aes-128-cfb
OFB: -aes-128-ofb
CTR: -aes-128-ctr
```

### ECB

ECB не использует IV.

Пример шифрования:
```bash
python -m cryptocore.cli_parser ^
    --algorithm aes ^
    --mode ecb ^
    --encrypt ^
    --key 000102030405060708090a0b0c0d0e0f ^
    --input plaintext.bin ^
    --output cipher.bin
```

Для проверки результата через OpenSSL:
```bash
openssl enc -aes-128-ecb -d ^
    -K 000102030405060708090a0b0c0d0e0f ^
    -in cipher.bin ^
    -out decrypted.bin
```

### Результат проверки

Совместимость проверяется автоматически в файле:
```text
tests/test_openssl.py
tests/test_openssl_modes.py
```

Проверка выполняется для ECB, CBC, CFB, OFB и CTR в обоих направлениях. Успешным результатом является совпадение расшифрованного файла с исходным.

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
cryptocore --algorithm aes --mode cbc --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
```

Проверить совпадение исходного и расшифрованного файлов в Windows можно командой:
```powershell
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

Тесты режимов CBC, CFB, OFB и CTR:

```powershell
pytest -q tests/test_modes.py
```

Тесты CLI:

```powershell
pytest -q tests/test_cli.py
```

Тест совместимости ECB с OpenSSL:

```powershell
pytest -q tests/test_openssl.py
```

Тесты совместимости CBC, CFB, OFB и CTR с OpenSSL:

```powershell
pytest -q tests/test_openssl_modes.py
```

## Обработка ошибок

Программа проверяет корректность входных параметров.

Например, неверный ключ:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 1234 --input plaintext.txt
```

В этом случае программа завершится с ошибкой и сообщит о некорректном размере ключа.

Одновременное использование `--encrypt` и `--decrypt` также является ошибкой.

При попытке передать --iv во время шифрования программа выдаёт ошибку, так как IV генерируется автоматически.

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
│           ├── ecb.py
│           ├── cbc.py
│           ├── cfb.py
│           ├── ofb.py
│           └── ctr.py    
├── tests/  
│   ├── test_ecb.py
│   ├── test_cli.py
│   ├── test_modes.py
│   ├── test_openssl.py
│   └── test_openssl_modes.py
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Назначение основных файлов

- `cli_parser.py` — обработка аргументов командной строки;
- `file_io.py` — чтение и запись файлов;
- `modes/ecb.py` — реализация AES-128 ECB и PKCS#7 padding;
- `modes/cbc.py` — реализация режима CBC;
- `modes/cfb.py` — реализация режима CFB;
- `modes/ofb.py` — реализация режима OFB;
- `modes/ctr.py` — реализация режима CTR;
- `tests/test_ecb.py` — тесты ECB и padding;
- `tests/test_cli.py` — тестирование командной строки и обработки ошибок;
- `tests/test_modes.py` — тесты новых режимов CBC, CFB, OFB и CTR;
- `tests/test_openssl.py` — автоматическая проверка ECB с OpenSSL;
- `tests/test_openssl_modes.py` — проверка совместимости CBC, CFB, OFB и CTR с OpenSSL;
- `pyproject.toml` — настройки сборки и установки проекта;
- `requirements.txt` — зависимости проекта;
- `requirements-dev.txt` — зависимости для разработки и тестирования.

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
