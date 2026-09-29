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

Для автоматической проверки совместимости с OpenSSL используют отдельные тесты.

### ECB

Запуск теста:

```powershell
pytest -q tests/test_openssl.py
```

Если OpenSSL установлен и доступен в `PATH`, тест должен завершиться успешно:

```text
1 passed
```

Если OpenSSL отсутствует:

```text
1 skipped
```

### CBC, CFB, OFB и CTR

Запуск тестов совместимости:
```powershell
pytest -q tests/test_openssl_modes.py
```

Тесты проверяют два направления:
1. CryptoCore → OpenSSL;
2. OpenSSL → CryptoCore.

Проверяются следующие режимы:

-CBC;
-CFB;
-OFB;
-CTR.

## Ручная проверка OpenSSL

### ECB

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

### CBC

Зашифровать файл через CryptoCore:
```powershell
cryptocore --algorithm aes --mode cbc --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output cipher.bin
```

Полученный файл содержит:
```text
[16 байт IV][ciphertext]
```

Первые 16 байт являются IV, остальные данные — шифротекст.

После извлечения IV и шифротекста их можно использовать для расшифрования через OpenSSL:
```powershell
openssl enc -aes-128-cbc -d -K 000102030405060708090a0b0c0d0e0f -iv 101112131415161718191a1b1c1d1e1f -in ciphertext_only.bin -out decrypted_openssl.txt
```

### OpenSSL → CryptoCore

Зашифровать файл через OpenSSL:
```powershell
openssl enc -aes-128-cbc -K 000102030405060708090a0b0c0d0e0f -iv 101112131415161718191a1b1c1d1e1f -in plain.txt -out openssl_cipher.bin
```

Расшифровать через CryptoCore:
```powershell
cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --iv 101112131415161718191a1b1c1d1e1f --input openssl_cipher.bin --output decrypted_cryptocore.txt
```

Для проверки режимов CFB, OFB и CTR в командах OpenSSL необходимо заменить:
```text
-aes-128-cbc
```

на соответствующий режим:
```text
-aes-128-cfb
-aes-128-ofb
-aes-128-ctr
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
- `requirements-dev.txt` — озависимости для разработки и тестирования.

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

Для проверки корректности работы и совместимости со стандартной утилитой OpenSSL CLI используются тесты для режимов `cbc`, `cfb`, `ofb` и `ctr`.

### Тест 1: Шифрование через CryptoCore → Расшифровка через OpenSSL

1. Зашифруйте файл с помощью CryptoCore:
   ```bash
   cryptocore --algorithm aes --mode cbc --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output cipher.bin

При шифровании CryptoCore автоматически генерирует IV и записывает его в первые 16 байт файла `cipher.bin`.

2. Извлеките 16 байт сгенерированного IV и сам шифротекст в отдельные файлы:
   ```powershell
   $data = [System.IO.File]::ReadAllBytes("cipher.bin")
   [System.IO.File]::WriteAllBytes("iv.bin", $data[0..15])
   [System.IO.File]::WriteAllBytes("ciphertext_only.bin", $data[16..($data.Length - 1)])
   ```

3. Получите IV в HEX-формате:
   ```powershell
   $iv = -join ((Get-Content -Encoding Byte iv.bin | ForEach-Object { $_.ToString("x2") }))
   ```
   
4. Расшифруйте шифротекст с помощью OpenSSL:
   ```bash
   openssl enc -aes-128-cbc -d -K 000102030405060708090a0b0c0d0e0f -iv $iv -in ciphertext_only.bin -out decrypted_openssl.txt
   ```

5. Сравните исходный и расшифрованный файлы:
   ```powershell
   fc.exe /b plaintext.txt decrypted_openssl.txt
   ```

Если файлы совпадают, команда `fc.exe` сообщает:
```text
FC: no differences encountered
```

### Тест 2: Шифрование через OpenSSL -> Расшифровка через CryptoCore

1. Зашифруйте файл с помощью OpenSSL:
   ```bash
   openssl enc -aes-128-cbc -K 000102030405060708090a0b0c0d0e0f -iv AABBCCDDEEFF00112233445566778899 -in plaintext.txt -out openssl_cipher.bin

2. Расшифруйте файл с помощью CryptoCore (передав тот же IV):
   ```bash
   cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --iv AABBCCDDEEFF00112233445566778899 --input openssl_cipher.bin --output decrypted_cryptocore.txt
   
3. Убедитесь, что расшифрованный файл совпадает с исходным:
   ```powershell
   fc.exe /b plaintext.txt decrypted_cryptocore.txt
   ```

## Проверка других режимов

Для проверки режимов `cfb`, `ofb` и `ctr` в командах OpenSSL необходимо заменить:
```text
-aes-128-cbc
```

на соответствующий режим:
```text
-aes-128-cfb
-aes-128-ofb
-aes-128-ctr
```

В каждом случае используется тот же принцип:

-CryptoCore генерирует IV при шифровании;
-IV сохраняется в первых 16 байтах зашифрованного файла;
-при расшифровании через CryptoCore IV можно передать через параметр --iv;
-результат сравнивается с исходным файлом.
