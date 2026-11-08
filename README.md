## CryptoCore

Консольный инструмент для шифрования и расшифрования файлов с использованием AES-128 (режимы ECB, CBC, CFB, OFB и CTR) для вычисления хешей файлов (SHA-256 и SHA3-256, реализованы с нуля) и для проверки аутентичности и целостности данных с помощью HMAC (RFC 2104) и AES-CMAC (NIST SP 800-38B).

## Возможности

- AES-128, режимы ECB, CBC, CFB, OFB и CTR;
- PKCS#7 padding для ECB и CBC, без padding для CFB, OFB и CTR;
- автоматическая генерация IV для CBC, CFB, OFB и CTR (хранится в первых 16 байтах файла);
- автоматическая генерация случайного ключа, если `--key` не указан при шифровании;
- собственный CSPRNG-модуль на основе `os.urandom()`;
- предупреждение о слабых ключах;
- команда `dgst`: SHA-256 и SHA3-256, реализованные с нуля (FIPS 180-4 и FIPS 202);
- потоковое хеширование: файлы любого размера и stdin обрабатываются порциями, память не зависит от размера данных;
- HMAC (RFC 2104), реализованный с нуля поверх собственных SHA-256 / SHA3-256: `dgst --hmac --key KEY`;
- ключи HMAC произвольной длины, потоковая обработка файла (постоянная память), проверка `--verify` с кодом возврата 0 / 1;
- бонус: AES-128-CMAC (NIST SP 800-38B): `dgst --cmac --key KEY`;
- проверка совместимости с OpenSSL, `sha256sum` и `sha3sum`.

## Требования

- Python 3.9 или новее;
- PyCryptodome;
- pytest;
- OpenSSL для проверки совместимости шифрования;
- `sha256sum` и `sha3sum` для проверки совместимости хеширования (необязательно, тесты пропускаются без них);
- Git.

## Установка

Откройте терминал в корневой папке проекта.

### 1. Создание виртуального окружения

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Установка зависимостей

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
```

После установки команда `cryptocore` доступна в терминале. Шаг `pip install -e .` нужен для команды `cryptocore` и для `pytest`; скриптам из `scripts/` он не требуется: они сами добавляют `src` в путь поиска модулей.

## Использование: шифрование

### Шифрование

ECB:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
```

CBC:

```powershell
cryptocore --algorithm aes --mode cbc --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
```

Для режимов CBC, CFB, OFB и CTR IV генерируется автоматически.

### Расшифрование

ECB:

```powershell
cryptocore --algorithm aes --mode ecb --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
```

Для CBC, CFB, OFB и CTR IV автоматически считывается из первых 16 байт зашифрованного файла:

```powershell
cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
```

IV можно указать вручную параметром `--iv`:

```powershell
cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --iv 101112131415161718191a1b1c1d1e1f --input ciphertext.bin --output decrypted.txt
```

Для AES-128 ключ должен иметь размер 16 байт, то есть 32 шестнадцатеричных символа.

## Генерация ключа (`--key` необязателен при шифровании)

При **шифровании** параметр `--key` можно не указывать. Тогда CryptoCore генерирует случайный 16-байтовый ключ через CSPRNG, выводит его в `stdout` в HEX-формате один раз и шифрует файл этим ключом:

```powershell
cryptocore --algorithm aes --mode ctr --encrypt --input plaintext.txt --output ciphertext.bin
```

```text
[INFO] Generated random key: 1a2b3c4d5e6f7890fedcba9876543210
Готово: ciphertext.bin
```

**Запишите ключ!** Он не сохраняется в выходной файл, и без него данные расшифровать нельзя.

При **расшифровании** `--key` обязателен: без него программа выведет ошибку и завершится с ненулевым кодом.

Если ключ указан вручную, он используется как есть. Если ключ выглядит слабым (все байты одинаковые или идут подряд, например `000102...0f`), в `stderr` выводится предупреждение; шифрование при этом выполняется.

## Хеширование (команда `dgst`)

Команда `dgst` вычисляет хеш файла. Она отделена от шифрования и не принимает его параметры.

```text
cryptocore dgst --algorithm {sha256,sha3-256} --input FILE [--output FILE]
cryptocore dgst --algorithm {sha256,sha3-256} --hmac --key HEX --input FILE [--output FILE | --verify FILE]
cryptocore dgst --cmac --key HEX32 --input FILE [--output FILE | --verify FILE]
```

| Параметр | Обязателен | Описание |
|---|---|---|
| `--algorithm` | да | `sha256` или `sha3-256` |
| `--input` | да | путь к файлу; `-` означает стандартный ввод |
| `--output` | нет | записать результат в файл вместо вывода на экран |
| `--hmac` | нет | вычислить HMAC выбранного `--algorithm` (см. раздел ниже) |
| `--cmac` | нет | вычислить AES-128-CMAC; `--algorithm` не нужен |
| `--key` | с `--hmac` / `--cmac` | ключ в hex; без `--hmac` или `--cmac` не принимается |
| `--verify` | нет | файл с ожидаемым MAC; сравнить, а не печатать |

Параметры `--mode`, `--encrypt`, `--decrypt` и `--iv` в `dgst` не принимаются: при их указании программа завершается с кодом 2 и сообщением `unrecognized arguments`. Параметр `--key` допустим только вместе с `--hmac` или `--cmac`.

### Формат вывода

Как у `sha256sum`: хеш в нижнем регистре, **два пробела**, путь к файлу.

```text
<hex-хеш>  <путь>
```

С `--output` в файл записывается ровно та же строка, что вывелась бы на экран.

### Примеры

Хеш файла:

```powershell
cryptocore dgst --algorithm sha256 --input document.pdf
```

SHA3-256 с записью в файл:

```powershell
cryptocore dgst --algorithm sha3-256 --input backup.tar --output backup.sha3
```

Хеш из stdin (Linux / macOS):

```bash
echo -n "abc" | cryptocore dgst --algorithm sha256 --input -
```

```text
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad  -
```

Хеш пустого файла (SHA-256):

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Сверка с системной утилитой:

```bash
cryptocore dgst --algorithm sha256 --input large_file.iso > my_hash.txt
sha256sum large_file.iso > system_hash.txt
diff my_hash.txt system_hash.txt   # различий быть не должно
```

Для SHA3-256 системная команда: `sha3sum -a 256 FILE`; если в системе нет `sha3sum` с ключом `-a`, подойдёт `openssl dgst -sha3-256 FILE`.

### Ошибки

| Ситуация | Код возврата | Сообщение |
|---|---|---|
| файла нет | 1 | `Входной файл не найден` |
| указан каталог | 1 | `Указан каталог, а не файл` |
| нет прав на чтение | 1 | `Нет доступа к входному файлу` |
| неизвестный алгоритм или лишний аргумент | 2 | сообщение argparse |
| `--hmac` / `--cmac` без `--key`, `--key` / `--verify` без MAC-режима, `--hmac` вместе с `--cmac`, `--verify` вместе с `--output` | 2 | сообщение argparse |
| ключ не в hex-формате, нечётной длины или пустой; для `--cmac` длина не 16 байт | 1 | `Ключ ...` |
| файл `--verify` не найден, пуст или не содержит MAC нужной длины | 1 | `Ошибка: ...` |
| MAC не совпал | 1 | `[ERROR] HMAC verification failed` (в `stderr`) |

### Как устроено хеширование

- Файл читается в бинарном режиме (`rb`) порциями по 8192 байта. Хешер хранит только внутреннее состояние и неполный блок, поэтому память постоянна для любого размера файла.
- Оба алгоритма наследуют общий класс `BlockHash` (`update`, `digest`, `hexdigest`, `padding`, `process_block`, `hash`).
- `digest()` работает на копии состояния, поэтому после него можно продолжать `update()`.
- Результат всегда выводится строкой из строчных hex-символов.

## Аутентификация сообщений: HMAC и AES-CMAC

Хеш защищает от случайных искажений, но злоумышленник, изменивший файл, просто пересчитает хеш. **Код аутентификации сообщения (MAC)** зависит ещё и от секретного ключа: подделать его без ключа нельзя. Он обеспечивает сразу **целостность** (файл не изменён) и **аутентичность** (MAC создал владелец ключа).

### Генерация HMAC

```text
cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input message.txt
```

```text
<hex-HMAC>  message.txt
```

- `--key` — hex-строка **любой длины** (от 1 байта); длину ключа программа не ограничивает.
- Формат вывода тот же, что у обычного хеша: MAC, **два пробела**, путь. С `--output FILE` в файл пишется ровно эта строка.
- `--algorithm` задаёт хеш-функцию HMAC: `sha256` (основной режим, RFC 4231) или `sha3-256` (блок 136 байт, как в NIST FIPS 202).
- Вход `-` (stdin) работает так же, как для хеширования.

### Проверка HMAC (`--verify`)

```bash
cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input message.bin --output file.hmac

cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input message.bin --verify file.hmac
```

```text
[OK] HMAC verification successful          (код возврата 0)
[ERROR] HMAC verification failed           (stderr, код возврата 1)
```

Файл `--verify` разбирается гибко: берётся первое слово первой непустой строки (остальное, то есть имя файла, игнорируется), регистр hex не важен, лишние пробелы и пустые строки допустимы, BOM и UTF-16 распознаются. Если там нет hex-значения нужной длины (64 символа для SHA-256), программа завершается с кодом 1 и пояснением — это не «MAC не совпал», а ошибка входных данных. Сравнение выполняется за время, не зависящее от позиции первого различия, чтобы не открывать побочный канал.

Альтернатива без `--verify`:

```bash
cryptocore dgst --algorithm sha256 --hmac --key KEY --input message.bin > computed.txt
diff computed.txt expected.txt
```

Пример обнаружения подмены:

```bash
echo "original content" > message.bin
cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input message.bin --output original.hmac
echo "modified content" > message.bin
cryptocore dgst --algorithm sha256 --hmac --key 00112233445566778899aabbccddeeff --input message.bin --verify original.hmac
# [ERROR] HMAC verification failed, код возврата 1
```

Та же ошибка возникает при неверном ключе: по результату невозможно отличить «файл изменён» от «ключ другой», и так задумано.

### Как устроен HMAC

Реализация в `src/cryptocore/mac/hmac.py` написана по RFC 2104 поверх собственного SHA-256 из `hash/sha256.py`:

```text
HMAC(K, m) = H( (K' ⊕ opad) ‖ H( (K' ⊕ ipad) ‖ m ) )
```

- `H` — хеш-функция; размер блока `B` = 64 байта для SHA-256 (136 для SHA3-256);
- `K'` — ключ, приведённый к размеру блока: **длиннее `B` → заменяется на `H(K)`, короче `B` → дополняется нулями справа**, ровно `B` → без изменений;
- `ipad` = `0x36` и `opad` = `0x5c`, каждый повторён `B` раз;
- вычисление потоковое: после `K' ⊕ ipad` в хешер подаются порции файла по 8192 байта, поэтому память постоянна для файла любого размера; `digest()` работает на копии состояния.

### Свойства безопасности HMAC

- **Нет атаки удлинения сообщения.** `SHA256(key ‖ m)` уязвим: зная хеш, можно дописать данные и посчитать хеш продолжения, не зная ключа. Двойное хеширование с разными ключами `ipad`/`opad` это исключает.
- **Стойкость к подделке** сводится к стойкости сжимающей функции хеша как PRF; без ключа найти MAC для нового сообщения практически невозможно, даже при наличии пар «сообщение — MAC».
- **Ключ.** Стойкость ограничена энтропией ключа и длиной выхода (256 бит). Ключ короче 16 байт программа принимает (так требует RFC), но он слабый; рекомендуется случайный ключ не короче 32 байт. Ключи длиннее блока не повышают стойкость: они сжимаются до `H(K)`.
- **Сравнение MAC** должно быть постоянным по времени, иначе по времени ответа можно подбирать MAC побайтно.
- HMAC **не шифрует** данные и **не защищает от повторной отправки** старого сообщения с верным MAC: для этого нужны счётчики или метки времени внутри сообщения.
- Ключ в командной строке виден в списке процессов и истории оболочки; для реальных задач используйте файл ключа или менеджер секретов.

### AES-CMAC 

```text
cryptocore dgst --cmac --key 2b7e151628aed2a6abf7158809cf4f3c --input message.bin
cryptocore dgst --cmac --key 2b7e151628aed2a6abf7158809cf4f3c --input message.bin --verify message.cmac
```

Ключ — ровно 16 байт (32 hex-символа), `--algorithm` не нужен, формат вывода и `--verify` те же, что у HMAC (сообщения `[OK] CMAC ...` / `[ERROR] CMAC ...`). Реализация `src/cryptocore/mac/cmac.py` по NIST SP 800-38B:

1. `L = AES_K(0¹²⁸)`;
2. подключи `K1 = double(L)`, `K2 = double(K1)`, где `double` — сдвиг на бит влево с XOR на `0x87`, если старший бит был 1;
3. сообщение режется на блоки по 16 байт, цепочка CBC-MAC с нулевым IV;
4. **последний** блок: полный → XOR с `K1`; неполный или пустое сообщение → дополнение `0x80 00…00` и XOR с `K2`; затем последнее шифрование.

От блочной операции AES используется только шифрование одного блока (PyCryptodome, как и в режимах проекта). Файл обрабатывается потоково, в буфере всегда остаётся последний блок (1–16 байт). CMAC безопасен как MAC для сообщений любой длины (в отличие от «голого» CBC-MAC); разные длины различаются благодаря разным подключам `K1` и `K2`.

## Реализованные алгоритмы и их свойства

### SHA-256 (FIPS 180-4)

- Семейство SHA-2, конструкция Меркла–Дамгора, блок 512 бит, 64 раунда, вывод 256 бит.
- Паддинг: бит `1`, нули до 448 бит по модулю 512, затем 64-битная длина сообщения в битах.
- Начальные значения `H0` и константы `K` вычисляются в коде как дробные части квадратных и кубических корней простых чисел (через целочисленные `isqrt` и кубический корень), а не вставлены таблицей.
- Стойкость: около 2^128 операций для поиска коллизии, около 2^256 для поиска прообраза.
- Уязвим к атаке удлинения сообщения: `SHA256(key || message)` нельзя использовать как MAC, для этого нужен HMAC (`dgst --hmac`, см. выше).

### SHA3-256 (FIPS 202)

- Конструкция губки Keccak: перестановка Keccak-f[1600], скорость 1088 бит (136 байт), ёмкость 512 бит, вывод 256 бит.
- Суффикс домена `01`, затем pad10*1: байты `0x06 ... 0x80` (или один `0x86`, если остаётся 1 байт).
- Константы раундов вычисляются через LFSR из FIPS 202, а не заданы таблицей.
- Тот же уровень стойкости (около 2^128 против коллизий), но **к атаке удлинения сообщения не уязвим**, и устроен иначе, чем SHA-2, что полезно как независимая альтернатива.

### Общие замечания

- Хеш защищает **целостность** только если сам хеш получен по доверенному каналу. Без ключа он не обеспечивает аутентичность.
- Простые хеши не подходят для хранения паролей: нужна функция с настраиваемой стоимостью (PBKDF2, scrypt, Argon2).
- Реализации учебные: они не выполняются за постоянное время и на порядки медленнее `hashlib`. Для реальных задач используйте проверенные библиотеки.

## Безопасность CSPRNG

Модуль `src/cryptocore/csprng.py` содержит функцию `generate_random_bytes(num_bytes: int) -> bytes`.

- Источник случайности: `os.urandom()` (`getrandom()` / `/dev/urandom` в Linux и macOS, `BCryptGenRandom` в Windows).
- Модуль `random` (Mersenne Twister) **не используется**: его выход предсказуем.
- Функция применяется для генерации ключа (если `--key` не указан) и **всех** IV.
- При сбое источника случайности выбрасывается `CSPRNGError`, программа завершается с ошибкой и не использует слабую случайность.
- Некорректный аргумент (`num_bytes <= 0`, не `int`) приводит к `ValueError`.
- 16 байт = 128 бит энтропии: вероятность совпадения двух ключей пренебрежимо мала.

## Статистическое тестирование (NIST STS)

Подробная инструкция и шаблон отчёта в [TESTING.md](TESTING.md). Кратко:

```powershell
python scripts/generate_nist_data.py 10 nist_test_data.bin
```

Полученный файл подаётся на вход NIST Statistical Test Suite (`./assess 1000000`).

## Работа с IV

Для CBC, CFB, OFB и CTR при шифровании IV (16 байт) генерируется через `cryptocore.csprng.generate_random_bytes()` и записывается в начало файла:

```text
[16 байт IV][зашифрованные данные]
```

При расшифровании IV можно получить из первых 16 байт входного файла или передать через `--iv` (тогда файл целиком считается шифртекстом). Параметр `--iv` при шифровании запрещён.

## Padding

Для ECB и CBC используется PKCS#7. Для CFB, OFB и CTR padding нет, поэтому размер данных сохраняется.

## Проверка совместимости с OpenSSL

Автоматически:

```bash
pytest -q tests/test_openssl.py tests/test_openssl_modes.py
```

Тесты проверяют оба направления: CryptoCore → OpenSSL и OpenSSL → CryptoCore, для ECB, CBC, CFB, OFB и CTR. Успех — совпадение расшифрованного файла с исходным.

### Вручную: CryptoCore → OpenSSL (CBC)

```powershell
python -m cryptocore.cli_parser `
    --algorithm aes `
    --mode cbc `
    --encrypt `
    --key 000102030405060708090a0b0c0d0e0f `
    --input plaintext.bin `
    --output cipher.bin
```

`cipher.bin` содержит IV и шифртекст. Извлеките IV и расшифруйте через OpenSSL (PowerShell):

```powershell
$data = [System.IO.File]::ReadAllBytes("cipher.bin")
[System.IO.File]::WriteAllBytes("ciphertext_only.bin", $data[16..($data.Length - 1)])
$iv = -join ($data[0..15] | ForEach-Object { $_.ToString("x2") })

openssl enc -aes-128-cbc -d `
    -K 000102030405060708090a0b0c0d0e0f `
    -iv $iv `
    -in ciphertext_only.bin `
    -out decrypted.bin
```

`decrypted.bin` должен совпасть с `plaintext.bin`. Для остальных режимов меняется только `-aes-128-cfb`, `-aes-128-ofb`, `-aes-128-ctr` (padding не используется).

### Вручную: OpenSSL → CryptoCore (CBC)

```powershell
openssl enc -aes-128-cbc `
    -K 000102030405060708090a0b0c0d0e0f `
    -iv 101112131415161718191a1b1c1d1e1f `
    -in plaintext.bin `
    -out openssl_cipher.bin

python -m cryptocore.cli_parser `
    --algorithm aes `
    --mode cbc `
    --decrypt `
    --key 000102030405060708090a0b0c0d0e0f `
    --iv 101112131415161718191a1b1c1d1e1f `
    --input openssl_cipher.bin `
    --output decrypted.bin
```

### Вручную: ECB

```powershell
python -m cryptocore.cli_parser `
    --algorithm aes `
    --mode ecb `
    --encrypt `
    --key 000102030405060708090a0b0c0d0e0f `
    --input plaintext.bin `
    --output cipher.bin

openssl enc -aes-128-ecb -d `
    -K 000102030405060708090a0b0c0d0e0f `
    -in cipher.bin `
    -out decrypted.bin
```

В bash вместо обратного апострофа в конце строки ставится `\`.

## Проверка полного цикла

```powershell
cryptocore --algorithm aes --mode cbc --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output ciphertext.bin
cryptocore --algorithm aes --mode cbc --decrypt --key 000102030405060708090a0b0c0d0e0f --input ciphertext.bin --output decrypted.txt
fc.exe /b plaintext.txt decrypted.txt
```

(в Linux / macOS сравнение: `cmp plaintext.txt decrypted.txt`).

## Запуск тестов

Перед запуском выполните `pip install -e .`.

| Что проверяем | Команда |
|---|---|
| все тесты | `pytest -q` |
| ECB | `pytest -q tests/test_ecb.py` |
| CBC, CFB, OFB, CTR | `pytest -q tests/test_modes.py` |
| CLI шифрования | `pytest -q tests/test_cli.py` |
| CSPRNG | `pytest -q tests/test_csprng.py` |
| совместимость с OpenSSL | `pytest -q tests/test_openssl.py tests/test_openssl_modes.py` |
| SHA-256 (векторы NIST, границы паддинга, чанки; тест на 1 ГБ по запросу) | `pytest -q tests/test_sha256.py` |
| SHA3-256 | `pytest -q tests/test_sha3_256.py` |
| команда `dgst` (формат, stdin, ошибки, `sha256sum`/`sha3sum`) | `pytest -q tests/test_dgst_cli.py` |
| лавинный эффект | `pytest -q tests/test_hash_avalanche.py` |
| HMAC: векторы RFC 4231, размеры ключей, потоковость, память | `pytest -q tests/test_hmac_vectors.py` |
| `dgst --hmac` / `--cmac` / `--verify` (подмена файла и ключа, пустой файл, формат файла MAC) | `pytest -q tests/test_hmac_cli.py` |
| AES-CMAC (векторы NIST SP 800-38B) | `pytest -q tests/test_cmac.py` |

Тесты совместимости с `sha256sum` и `sha3sum` пропускаются, если утилиты не установлены (например, в Windows). Для полной проверки TEST-3 запустите их в Linux, macOS или WSL.

### HMAC на большом файле (TEST-7)

```powershell
python scripts/large_file_hmac_test.py --size-mb 2
python scripts/large_file_hmac_test.py --size-mb 1100 --no-memory-trace
```

Скрипт создаёт файл из случайных данных, считает HMAC реализацией проекта порциями, сверяет его с `hmac` + `hashlib`. Первый запуск дополнительно измеряет пик памяти: он не зависит от размера файла (около 27 КиБ), но `tracemalloc` замедляет чистый Python в десятки раз, поэтому для больших файлов (больше доступной памяти) используйте `--no-memory-trace`. Скорость без трассировки около 0,25 МБ/с, файл 1 ГБ считается более часа.

### Тест на файле больше 1 ГБ (TEST-4)

```bash
python scripts/large_file_test.py --algorithm sha256 --size-mb 1100
python scripts/large_file_test.py --algorithm sha3-256 --size-mb 1100
```

Скрипт создаёт временный файл на 1100 МБ, считает эталон через `hashlib` и сравнивает с результатом проекта. Чистый Python работает медленно: прогон на SHA-256 занимает больше часа, и нужно около 1.1 ГБ свободного места.

Результаты прогонов (SHA-256, Windows, Python из `.venv`):

| Размер файла | Время, с | Скорость, МБ/с | Эталон `hashlib` совпал с результатом |
|---|---|---|---|
| 10 МБ | 37,0 | 0,27 | да |
| 1100 МБ (1 153 433 600 байт, 1.07 ГиБ) | 4718,6 (около 79 минут) | 0,23 | да |

Полный вывод скрипта приведён в [TESTING.md](TESTING.md), раздел 4.3. Для SHA3-256 файл больше 1 ГБ отдельно не прогонялся: чтение порциями общее для обоих алгоритмов, а границы блоков SHA3-256 покрыты тестами.

Тест pytest `test_hash_stream_processes_file_larger_than_1gb` делает то же самое с классом `SHA256` проекта и по умолчанию пропускается; запуск:

```powershell
$env:CRYPTOCORE_RUN_LARGE_HASH_TEST="1"
pytest -q tests/test_sha256.py
```

### Производительность (TEST-6)

```bash
python scripts/benchmark_hash.py --sizes 1 5 10
```

Скрипт выводит таблицу сравнения со стандартным `hashlib`. Результат прогона (Windows, Python из `.venv`):

| Алгоритм | Размер, МБ | CryptoCore, с | CryptoCore, МБ/с | hashlib, с | Медленнее в |
|---|---|---|---|---|---|
| sha256 | 1 | 3.96 | 0.25 | 0.0010 | 3,889x |
| sha256 | 5 | 19.71 | 0.25 | 0.0039 | 5,055x |
| sha256 | 10 | 35.53 | 0.28 | 0.0072 | 4,909x |
| sha3-256 | 1 | 2.69 | 0.37 | 0.0029 | 934x |
| sha3-256 | 5 | 13.12 | 0.38 | 0.0144 | 910x |
| sha3-256 | 10 | 26.87 | 0.37 | 0.0287 | 937x |

Реализации на чистом Python держат около 0,25–0,28 МБ/с (SHA-256) и 0,37 МБ/с (SHA3-256) и на три-четыре порядка медленнее `hashlib`. Время растёт линейно с размером данных. Сравнение сделано с `hashlib`, а не с `sha256sum`.

## Обработка ошибок

Программа проверяет входные параметры. Например, ключ неверной длины:

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 1234 --input plaintext.txt
```

завершится ошибкой с сообщением о размере ключа. Ошибкой также являются одновременные `--encrypt` и `--decrypt`, расшифрование без `--key` и `--iv` при шифровании.

## Структура проекта

```text
CryptoCore/
├── src/
│   └── cryptocore/
│       ├── __init__.py
│       ├── cli_parser.py
│       ├── dgst_cli.py
│       ├── csprng.py
│       ├── file_io.py
│       ├── mac/
│       │   ├── __init__.py
│       │   ├── hmac.py
│       │   └── cmac.py
│       ├── hash/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── sha256.py
│       │   └── sha3_256.py
│       └── modes/
│           ├── __init__.py
│           ├── ecb.py
│           ├── cbc.py
│           ├── cfb.py
│           ├── ofb.py
│           └── ctr.py
├── scripts/
│   ├── generate_nist_data.py
│   ├── benchmark_hash.py
│   ├── large_file_test.py
│   └── large_file_hmac_test.py
├── tests/
│   ├── test_ecb.py
│   ├── test_cli.py
│   ├── test_csprng.py
│   ├── test_modes.py
│   ├── test_openssl.py
│   ├── test_openssl_modes.py
│   ├── test_sha256.py
│   ├── test_sha3_256.py
│   ├── test_dgst_cli.py
│   ├── test_hmac_vectors.py
│   ├── test_hmac_cli.py
│   ├── test_cmac.py
│   └── test_hash_avalanche.py
├── .gitignore
├── TESTING.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Назначение основных файлов

- `cli_parser.py` — аргументы командной строки; передаёт `dgst` в `dgst_cli.py`;
- `dgst_cli.py` — команда `dgst`: разбор аргументов, чтение файла или stdin, вывод хеша, HMAC / CMAC и `--verify`;
- `csprng.py` — `generate_random_bytes` на основе `os.urandom`;
- `file_io.py` — чтение и запись файлов;
- `hash/__init__.py` — реестр алгоритмов, `new_hasher`, `hash_stream`, `CHUNK_SIZE`;
- `hash/base.py` — общий класс `BlockHash` (буферизация, паддинг, `digest`, `hexdigest`);
- `hash/sha256.py` — SHA-256 с нуля;
- `hash/sha3_256.py` — SHA3-256 (Keccak-f[1600]) с нуля;
- `mac/hmac.py` — HMAC (RFC 2104) с нуля, `constant_time_equal`;
- `mac/cmac.py` — AES-128-CMAC (NIST SP 800-38B), бонус;
- `modes/ecb.py`, `cbc.py`, `cfb.py`, `ofb.py`, `ctr.py` — режимы AES;
- `scripts/generate_nist_data.py` — данные для NIST STS;
- `scripts/benchmark_hash.py` — сравнение скорости с `hashlib` (TEST-6);
- `scripts/large_file_test.py` — тест на файле больше 1 ГБ (TEST-4);
- `scripts/large_file_hmac_test.py` — HMAC на большом файле и пик памяти (TEST-7);
- `tests/test_sha256.py`, `test_sha3_256.py` — тесты векторов NIST и границ паддинга (TEST-1, TEST-2);
- `tests/test_dgst_cli.py` — тесты CLI и совместимости с системными утилитами (TEST-3);
- `tests/test_hash_avalanche.py` — тесты лавинного эффекта (TEST-5);
- `tests/test_hmac_vectors.py`, `test_hmac_cli.py`, `test_cmac.py` — тесты HMAC / CMAC (Sprint 5: TEST-1 … TEST-8);
- остальные тесты относятся к шифрованию (ECB, режимы, CLI, CSPRNG, OpenSSL);
- `TESTING.md` — инструкция и результаты NIST STS;
- `pyproject.toml` — сборка и установка;
- `requirements.txt`, `requirements-dev.txt` — зависимости.

## Зависимости

- `pycryptodome` — шифрование AES (в том числе блочная операция для AES-CMAC);
- `pytest` — тесты;
- OpenSSL — проверка совместимости шифрования;
- `sha256sum`, `sha3sum` — проверка совместимости хеширования (необязательно).

Хеш-функции и HMAC написаны без внешних библиотек; `hashlib` и стандартный `hmac` используются только в тестах и скриптах как эталон.

## Лицензия

Проект распространяется под лицензией MIT.
