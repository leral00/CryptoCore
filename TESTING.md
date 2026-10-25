# Тестирование CryptoCore

## 1. Автоматические тесты

```bash
pytest -q tests/test_csprng.py   # уникальность 1000 ключей, доля единичных битов, ошибки
pytest -q tests/test_cli.py      # генерация ключа, шифрование -> расшифрование
pytest -q                        # все тесты, включая совместимость с OpenSSL (Sprint 2)
```

## 2. NIST Statistical Test Suite (STS)

### 2.1. Генерация тестовых данных

```bash
python scripts/generate_nist_data.py 10 nist_test_data.bin
```

Создаётся файл 10 МБ (80 000 000 бит) с выходом `generate_random_bytes`.
Допустимо 1–100 МБ.

### 2.2. Установка NIST STS

Скачайте STS с сайта NIST (https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software),
распакуйте и соберите (Linux / WSL / MSYS2):

```bash
cd sts-2.1.2
make
```

### 2.3. Запуск

```bash
./assess 1000000
```

Ответы на интерактивные запросы:

1. `0` — Input File;
2. путь к `nist_test_data.bin`;
3. `1` — применить все 15 тестов;
4. параметры по умолчанию (`0`);
5. количество потоков (bitstreams): `80`;
6. `1` — двоичный формат файла.

10 МБ = 80 000 000 бит = 80 потоков по 1 000 000 бит.
Для другого размера файла число потоков = размер_в_битах / 1 000 000.

### 2.4. Результаты

Отчёт: `experiments/AlgorithmTesting/finalAnalysisReport.txt`.

Критерий успеха: p-value >= 0.01 для большинства тестов (доля прошедших потоков
должна быть в допустимом интервале, указанном в отчёте). Единичные провалы
статистически ожидаемы (при уровне значимости 0.01 примерно 1% потоков), массовые — нет.

### 2.5. Результаты запуска

**Условия запуска**

| Параметр | Значение |
|---|---|
| Дата запуска | 12.10.2026 |
| Тестируемый генератор | `cryptocore.csprng.generate_random_bytes` (`os.urandom`) |
| Файл данных | `nist_test_data.bin`, 10 000 000 байт (80 000 000 бит), создан `scripts/generate_nist_data.py` |
| Инструмент | NIST Statistical Test Suite 2.1.2 |
| Окружение | Ubuntu (WSL) на Windows, gcc 15.2.0 |
| Команда | `./assess 1000000` |
| Режим | Input File, формат Binary, применены все 15 тестов |
| Число потоков / длина потока | 80 / 1 000 000 бит |

**Итог**

| Показатель | Результат |
|---|---|
| Тестов, помеченных `*` (провал) в `finalAnalysisReport.txt` | 0 (`grep -c "\*" finalAnalysisReport.txt` вернул `0`) |
| Минимальный P-VALUE среди строк, приведённых ниже | 0.016431 (NonOverlappingTemplate), что не меньше порога 0.01 |
| Минимальная доля прошедших потоков среди строк, приведённых ниже | 78/80 |
| Допустимая доля прошедших потоков для 80 потоков | около 0.957, то есть не менее 77 из 80 (формула STS: p ± 3·sqrt(p(1−p)/m), p = 0.99) |

**Вывод.** Ни один из применённых тестов не выявил отклонений от случайности: P-value
равномерно распределены (значения выше 0.01), доля прошедших потоков во всех приведённых строках (78–80 из 80)
выше допустимого порога. Значения 78/80 и 79/80 статистически ожидаемы при уровне
значимости 0.01. Критерий успеха (p-value ≥ 0.01 для большинства тестов) выполнен.

**Выдержка из `experiments/AlgorithmTesting/finalAnalysisReport.txt`** (первые строки отчёта):

```text
------------------------------------------------------------------------------
RESULTS FOR THE UNIFORMITY OF P-VALUES AND THE PROPORTION OF PASSING SEQUENCES
------------------------------------------------------------------------------
   generator is <nist_test_data.bin>
------------------------------------------------------------------------------
 C1  C2  C3  C4  C5  C6  C7  C8  C9 C10  P-VALUE  PROPORTION  STATISTICAL TEST
------------------------------------------------------------------------------
  9   5   7   7  16   5   9   7   9   6  0.242986     80/80      Frequency
  7  15   4   2   5   8  10  13  10   6  0.029796     79/80      BlockFrequency
  9  10   4   6   6   5  10  10  10  10  0.663130     80/80      CumulativeSums
  6  10   9   8   5  12   3   6  11  10  0.392456     80/80      CumulativeSums
  6   7  11   9   3   8   7   7  12  10  0.559523     80/80      Runs
 11   6   7   7   5  10  10   7   8   9  0.894201     79/80      LongestRun
  5   7  11  12   9   3  12   6   7   8  0.330628     80/80      Rank
  4   6  10  11   7   7   6  10   7  12  0.585209     80/80      FFT
  8   6  10   9   8  12   5  11   5   6  0.637119     80/80      NonOverlappingTemplate
  9   6   8  12   8   9   9   7   7   5  0.894201     80/80      NonOverlappingTemplate
  8  10   8  10   8  12   7   6   9   2  0.509162     79/80      NonOverlappingTemplate
  5  12   6  10   9   5   4  14  12   3  0.048716     80/80      NonOverlappingTemplate
 10   8   8   7   6   8   8   6  11   8  0.973388     79/80      NonOverlappingTemplate
 10   8   8   7   6   9  11   6   5  10  0.875539     80/80      NonOverlappingTemplate
  6   9   8   6   6   9  10   7  13   6  0.739918     80/80      NonOverlappingTemplate
  6   3   8   9  10   9   9  11   9   6  0.714660     79/80      NonOverlappingTemplate
  7  13  12   8   6   2  10   8   8   6  0.258961     79/80      NonOverlappingTemplate
  6   7   8   4   8  10   9  14   9   5  0.437274     79/80      NonOverlappingTemplate
 10   6   6   8   8   4   6  11  11  10  0.663130     79/80      NonOverlappingTemplate
  7   5  10   7  13   7   8   5  13   5  0.311542     80/80      NonOverlappingTemplate
 11   9   3   6   8  12   6   7   9   9  0.559523     79/80      NonOverlappingTemplate
 11   4  14   7   8   7   5   6  12   6  0.213309     79/80      NonOverlappingTemplate
 12   6  11   8   6   6   8   7   7   9  0.834308     79/80      NonOverlappingTemplate
  6  11  10   6   6   4  16   8   8   5  0.113706     80/80      NonOverlappingTemplate
 13   8   7   5   9   8   5   9  10   6  0.663130     79/80      NonOverlappingTemplate
  4  11   7   3   7   9  14  13   8   4  0.061841     80/80      NonOverlappingTemplate
  7   6   8   4   6  10   8   9  13   9  0.637119     79/80      NonOverlappingTemplate
  4   5  10  10   3   7  12   7  15   7  0.072289     79/80      NonOverlappingTemplate
 10  12  12   7   6   8   5   8   7   5  0.585209     79/80      NonOverlappingTemplate
 12   5   6   6   7   6  15  10   7   6  0.213309     78/80      NonOverlappingTemplate
 10  11  11   4   9   5  11   6   3  10  0.258961     80/80      NonOverlappingTemplate
 11   8  15   7   3   2  13  10   5   6  0.016431     78/80      NonOverlappingTemplate
 10  11   4  11   8  11   5   4  10   6  0.350485     80/80      NonOverlappingTemplate
```

Полный отчёт содержит результаты всех 15 тестов (188 строк); при проверке
`grep -c "\*" finalAnalysisReport.txt` не нашёл ни одной строки с пометкой `*`.

## 3. Ручная проверка CLI

Команды для PowerShell, запускаются в корне проекта с активированным `.venv`.

### 3.1. Подготовка

```powershell
echo "hello" > plaintext.txt
```

### 3.2. Шифрование без `--key` (CLI-3, KEY-1, KEY-2)

```powershell
cryptocore --algorithm aes --mode ctr --encrypt --input plaintext.txt --output ciphertext.bin
```

Результат запуска:

```text
[INFO] Generated random key: 282cc504d55e6320e392b5bc1d51ca77
Готово: ciphertext.bin
```

Ключ выведен ровно один раз, его длина 32 hex-символа (16 байт), предупреждение про
передачу ключа через командную строку не выводится, так как `--key` не указывался.

### 3.3. Расшифрование сгенерированным ключом (TEST-1)

```powershell
cryptocore --algorithm aes --mode ctr --decrypt --key 282cc504d55e6320e392b5bc1d51ca77 --input ciphertext.bin --output decrypted.txt
fc.exe /b plaintext.txt decrypted.txt
(Get-FileHash plaintext.txt).Hash -eq (Get-FileHash decrypted.txt).Hash
```

Результат запуска:

```text
Предупреждение: передача ключа через командную строку может быть небезопасной.
Готово: decrypted.txt
Сравнение файлов plaintext.txt и DECRYPTED.TXT
FC: различия не найдены
True
```

Расшифрованный файл побайтно совпадает с исходным.

### 3.4. Расшифрование без `--key` (CLI-4)

```powershell
cryptocore --algorithm aes --mode ctr --decrypt --input ciphertext.bin --output x.txt
```

Результат запуска:

```text
Ошибка: Для расшифрования параметр --key обязателен.
```

Программа сообщает об ошибке и не выполняет расшифрование.

### 3.5. Предупреждение о слабом ключе (CLI-5)

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 00000000000000000000000000000000 --input plaintext.txt --output w.bin
```

Результат запуска:

```text
Предупреждение: передача ключа через командную строку может быть небезопасной.
Предупреждение: указанный ключ выглядит слабым (одинаковые или последовательные байты). Используйте случайный ключ.
Готово: w.bin
```

Слабый ключ принимается, в stderr выводится предупреждение, шифрование выполняется.

Дополнительно (последовательные байты):

```powershell
cryptocore --algorithm aes --mode ecb --encrypt --key 000102030405060708090a0b0c0d0e0f --input plaintext.txt --output w2.bin
```

Результат запуска:
```text
Предупреждение: передача ключа через командную строку может быть небезопасной.
Предупреждение: указанный ключ выглядит слабым (одинаковые или последовательные байты). Используйте случайный ключ.
Готово: w2.bin
```

### 3.6. Ключи и IV различаются между запусками (RNG-5, IV-1)

```powershell
cryptocore --algorithm aes --mode cbc --encrypt --input plaintext.txt --output a.bin
cryptocore --algorithm aes --mode cbc --encrypt --input plaintext.txt --output b.bin
```

Ожидается: два разных сгенерированных ключа.

```text
[INFO] Generated random key: 44d652e5eff1f185d8534b1a9867c8b9
Готово: a.bin

[INFO] Generated random key: 6f0f2e46b5cc49bccf608ad371cd7966
Готово: b.bin
```

IV (первые 16 байт файла) при одном и том же ключе:

```powershell
$k = "3a1f5c7e9b2d4f6081a3c5e7092b4d6f"
cryptocore --algorithm aes --mode cbc --encrypt --key $k --input plaintext.txt --output i1.bin
cryptocore --algorithm aes --mode cbc --encrypt --key $k --input plaintext.txt --output i2.bin
(Get-Content i1.bin -Encoding Byte -TotalCount 16) -join " "
(Get-Content i2.bin -Encoding Byte -TotalCount 16) -join " "
```

Ожидается: две разные строки из 16 чисел. В PowerShell 7 вместо `-Encoding Byte` используйте `-AsByteStream`.

```text
Предупреждение: передача ключа через командную строку может быть небезопасной.
Готово: i1.bin

Предупреждение: передача ключа через командную строку может быть небезопасной.
Готово: i2.bin

144 254 87 97 229 228 76 217 180 225 8 90 22 81 38 93

202 15 95 48 145 14 102 20 117 249 220 87 88 154 60 79
```

### 3.7. Сводка

| Требование | Проверка | Результат |
|---|---|---|
| CLI-3, KEY-1, KEY-2 | 3.2: ключ сгенерирован и выведен один раз | пройдено |
| TEST-1 | 3.3: расшифрование возвращает исходный файл | пройдено |
| CLI-4 | 3.4: ошибка без `--key` при расшифровании | пройдено |
| CLI-5 | 3.5: предупреждение о слабом ключе | пройдено (ключ из нулей) |
| IV-1, RNG-5 | 3.6: ключи и IV различаются | пройдено (разные ключи, разные IV) |


## 4. Хеш-функции (Sprint 4)

### 4.1. Автоматические тесты

Перейдите в корневую папку проекта и активируйте виртуальное окружение (пакет должен быть установлен: `pip install -e .`).

Тесты хеш-функций Sprint 4:

```powershell
pytest -q tests/test_sha256.py tests/test_sha3_256.py tests/test_hash_avalanche.py tests/test_dgst_cli.py
```

Все тесты проекта:

```powershell
pytest -q
```

Соответствие тестов требованиям ТЗ:

| Требование | Что проверяется | Где |
|---|---|---|
| TEST-1 | Векторы NIST: пустая строка, `abc`, 448 бит, 896 бит, миллион `a` | `test_sha256.py`, `test_sha3_256.py` |
| TEST-2 | Хеш пустого входа (класс и CLI) | `test_sha256.py`, `test_sha3_256.py`, `test_dgst_cli.py` |
| TEST-3 | Сверка с `sha256sum` / `sha3sum` (пропускается, если утилит нет) | `test_dgst_cli.py` |
| TEST-5 | Лавинный эффект: замена символа и перебор однобитных изменений | `test_hash_avalanche.py` |
| HASH-4/5, IO-2 | Хеширование порциями, многопорционный файл, совпадение с `hashlib` | все четыре файла |
| CLI-3, CLI-4, CLI-5, IO-3, IO-4 | Формат вывода, `--output`, запрет аргументов шифрования, ошибки | `test_dgst_cli.py` |

Результат запуска (`pytest -q`, все тесты проекта):

```text
.....................................ss........................................s.............                                                                                [100%]
90 passed, 3 skipped in 40.11s
```

Три теста пропущены (символы `s` в выводе):

- `test_interoperability_with_sha256sum` и `test_interoperability_with_sha3sum` в `tests/test_dgst_cli.py`: в Windows нет утилит `sha256sum` и `sha3sum`. Эта сверка выполнена отдельно в WSL (раздел 4.2);
- `test_hash_stream_processes_file_larger_than_1gb` в `tests/test_sha256.py`: большой тест запускается только при `CRYPTOCORE_RUN_LARGE_HASH_TEST=1` и занимает около 70 минут. Файл больше 1 ГБ проверяется скриптом `scripts/large_file_test.py` (раздел 4.3).

### 4.2. Сверка результатов хеширования (TEST-3)

Тестовый файл:

```powershell
Set-Content -Path file.txt -Value "hello"
```

SHA-256 сверяется с `Get-FileHash`, SHA3-256 с `hashlib`:

```powershell
cryptocore dgst --algorithm sha256 --input file.txt
Get-FileHash file.txt -Algorithm SHA256

cryptocore dgst --algorithm sha3-256 --input file.txt
python -c "import hashlib,sys; print(hashlib.sha3_256(open(sys.argv[1],'rb').read()).hexdigest())" file.txt
```

Результат запуска:

```text
Проверка SHA-256:

cd2eca3535741f27a8ae40c31b0c41d4057a7a7b912b33b9aed86485d1c84676  file.txt

Get-FileHash:
CD2ECA3535741F27A8AE40C31B0C41D4057A7A7B912B33B9AED86485D1C84676

Проверка SHA3-256:

7a5e1be0535111a63ac42e739b8aa5f28f66109b683e32f18f92c99234b82c64  file.txt

hashlib:
7a5e1be0535111a63ac42e739b8aa5f28f66109b683e32f18f92c99234b82c64
```

Вывод: результаты SHA-256 совпадают с `Get-FileHash`, результаты SHA3-256 с `hashlib`.

Сверка с системными утилитами. Команда `cryptocore` установлена в окружении Windows, а `sha256sum` и `openssl` работают в WSL, поэтому сначала хеши проекта считаются в PowerShell, затем сверяются в WSL на том же файле `file.txt`. Утилита `sha3sum` в используемой системе не поддерживает ключ `-a 256` (установлена другая программа с таким именем), поэтому SHA3-256 сверяется с `openssl dgst -sha3-256`.

**Шаг 1. PowerShell** (в папке проекта):

```powershell
cryptocore dgst --algorithm sha256 --input file.txt --output my_hash.txt
cryptocore dgst --algorithm sha3-256 --input file.txt --output my_sha3.txt
```

Параметр `--output` используется вместо перенаправления `>`: в Windows PowerShell 5.1 оператор `>` пишет файл в UTF-16, из-за чего `diff` показал бы ложные различия.

**Шаг 2. WSL** (та же папка, диск `C:` доступен как `/mnt/c`):

```bash
sha256sum file.txt > system_hash.txt
[ -s my_hash.txt ] && diff my_hash.txt system_hash.txt && echo "OK: SHA-256 совпадает"

openssl dgst -sha3-256 file.txt | sed 's/.*= //' > system_sha3.txt
[ -s my_sha3.txt ] && diff <(cut -d' ' -f1 my_sha3.txt) system_sha3.txt && echo "OK: SHA3-256 совпадает"
```

Проверка `[ -s файл ]` не даёт вывести «OK», если файл с хешем проекта пуст или не создан на шаге 1.

**Шаг 3. WSL**, вывод для отчёта:

```bash
cat my_hash.txt system_hash.txt my_sha3.txt system_sha3.txt
```

Результат запуска:

```text
OK: SHA-256 совпадает
OK: SHA3-256 совпадает

cd2eca3535741f27a8ae40c31b0c41d4057a7a7b912b33b9aed86485d1c84676  file.txt
cd2eca3535741f27a8ae40c31b0c41d4057a7a7b912b33b9aed86485d1c84676  file.txt
7a5e1be0535111a63ac42e739b8aa5f28f66109b683e32f18f92c99234b82c64  file.txt
7a5e1be0535111a63ac42e739b8aa5f28f66109b683e32f18f92c99234b82c64
```

### 4.3. Проверка потоковой обработки и большого файла (TEST-4)

Скрипт `scripts/large_file_test.py` создаёт случайный файл, считает эталон через `hashlib` по мере записи, затем хеширует файл реализацией проекта порциями по 8192 байта (`CHUNK_SIZE`) и сравнивает результаты. Память при этом не зависит от размера файла.

Предварительный прогон на файле 10 МБ (SHA-256):

```powershell
python scripts/large_file_test.py --algorithm sha256 --size-mb 10
```

Результат запуска:
```text
Создаю файл 10 МБ: C:\Users\TECHPR~1.RU\AppData\Local\Temp\cryptocore_large_test.bin
Размер файла: 10485760 байт (0.01 ГиБ)
Эталон (hashlib): d240ad6d9bc3d7f91d36f92174e59b3db26ae2f42a441dac8d72107e6a6def62
Считаю sha256 реализацией проекта (порции по 8192 байт)...
Результат:        d240ad6d9bc3d7f91d36f92174e59b3db26ae2f42a441dac8d72107e6a6def62
Время: 37.0 с, скорость: 0.27 МБ/с
OK: хеши совпадают.
```

Основной прогон на файле больше 1 ГБ (SHA-256):

```powershell
python scripts/large_file_test.py --algorithm sha256 --size-mb 1100
```

Фактическая скорость на этом компьютере составила около 0,23 МБ/с, поэтому прогон занял около 79 минут (4718,6 с). Файл 1100 МБ (1 153 433 600 байт, 1.07 ГиБ) создаётся во временной папке и удаляется после проверки.

Результат запуска:

```text
Создаю файл 1100 МБ: C:\Users\TECHPR~1.RU\AppData\Local\Temp\cryptocore_large_test.bin
Размер файла: 1153433600 байт (1.07 ГиБ)
Эталон (hashlib): a9d8c7fd5993fd819c8d03f7dbe101636250d16587d835da36b7a6a1cde1ca16
Считаю sha256 реализацией проекта (порции по 8192 байт)...
Результат:        a9d8c7fd5993fd819c8d03f7dbe101636250d16587d835da36b7a6a1cde1ca16
Время: 4718.6 с, скорость: 0.23 МБ/с
OK: хеши совпадают.
```

Для SHA3-256 большой файл отдельно не прогонялся: логика чтения порциями общая для обоих алгоритмов (`hash_stream`, `BlockHash.update`), а границы блоков SHA3-256 покрыты тестами `test_matches_hashlib_for_all_padding_boundaries` и `test_chunked_update_equals_single_update`.

### 4.4. Производительность (TEST-6)

```powershell
python scripts/benchmark_hash.py --sizes 1 5 10
```

Результат запуска (Windows, Python из `.venv`; данные случайные, чтение порциями по 8192 байта):

| Алгоритм | Размер, МБ | CryptoCore, с | CryptoCore, МБ/с | hashlib, с | Медленнее в |
|---|---|---|---|---|---|
| sha256 | 1 | 3.96 | 0.25 | 0.0010 | 3,889x |
| sha256 | 5 | 19.71 | 0.25 | 0.0039 | 5,055x |
| sha256 | 10 | 35.53 | 0.28 | 0.0072 | 4,909x |
| sha3-256 | 1 | 2.69 | 0.37 | 0.0029 | 934x |
| sha3-256 | 5 | 13.12 | 0.38 | 0.0144 | 910x |
| sha3-256 | 10 | 26.87 | 0.37 | 0.0287 | 937x |

Вывод: реализация на чистом Python держит примерно 0,25–0,28 МБ/с для SHA-256 и около 0,37 МБ/с для SHA3-256. `hashlib` (оптимизированный код на C) быстрее примерно в 4000–5000 раз для SHA-256 и в 900–940 раз для SHA3-256. Скорость почти не зависит от размера данных, то есть время растёт линейно, как и должно при потоковой обработке. Разница ожидаема и на корректность результата не влияет. Сравнение выполнено с `hashlib`, а не с `sha256sum`; абсолютные значения зависят от компьютера.
