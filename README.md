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
pip install -r requirements-dev.txt
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

---

## Совместимость с OpenSSL (Interoperability Testing)

Для проверки корректности работы и совместимости со стандартной утилитой OpenSSL CLI вы можете выполнить следующие тесты для каждого из режимов (`cbc`, `cfb`, `ofb`, `ctr`).

### Тест 1: Шифрование через CryptoCore -> Расшифровка через OpenSSL

1. Зашифруйте файл с помощью CryptoCore:
   ```bash
   cryptocore --algorithm aes --mode cbc --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output cipher.bin

2. Извлеките 16 байт сгенерированного IV и сам шифротекст в отдельные файлы:
   ```bash
   dd if=cipher.bin of=iv.bin bs=16 count=1
   dd if=cipher.bin of=ciphertext_only.bin bs=16 skip=1

3. Расшифруйте шифротекст с помощью OpenSSL:
   ```bash
   openssl enc -aes-128-cbc -d -K 000102030405060708090a0b0c0d0e0f -iv $(xxd -p iv.bin | tr -d '\n') -in ciphertext_only.bin -out decrypted_openssl.txt

4. Убедитесь, что расшифрованный файл совпадает с исходным:
   ```diff plain.txt decrypted_openssl.txt

### Тест 2: Шифрование через OpenSSL -> Расшифровка через CryptoCore

1. Зашифруйте файл с помощью OpenSSL:
   ```bash
   openssl enc -aes-128-cbc -K 000102030405060708090a0b0c0d0e0f -iv AABBCCDDEEFF00112233445566778899 -in plain.txt -out openssl_cipher.bin

2. Расшифруйте файл с помощью CryptoCore (передав тот же IV):
   ```bash
   cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --iv AABBCCDDEEFF00112233445566778899 --input openssl_cipher.bin --output decrypted_cryptocore.txt

3. Убедитесь, что расшифрованный файл совпадает с исходным:
   ```bash
   diff plain.txt decrypted_cryptocore.txt

   (Примечание: Для проверки режимов cfb, ofb и ctr замените флаг -aes-128-cbc в командах OpenSSL на -aes-128-cfb, -aes-128-ofb или -aes-128-ctr соответственно).

## Запуск автотестов

Для запуска комплекса модульных и интеграционных тестов выполните:
```bash
pytest
