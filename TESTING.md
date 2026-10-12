# Тестирование CSPRNG

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
| Допустимая доля прошедших потоков для 80 потоков | около 0.957, то есть примерно 76 из 80 (формула STS: p ± 3·sqrt(p(1−p)/m), p = 0.99) |

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

### 3.6. Ключи и IV различаются между запусками (RNG-5, IV-1)

```powershell
cryptocore --algorithm aes --mode cbc --encrypt --input plaintext.txt --output a.bin
cryptocore --algorithm aes --mode cbc --encrypt --input plaintext.txt --output b.bin
```

Ожидается: два разных сгенерированных ключа.

IV (первые 16 байт файла) при одном и том же ключе:

```powershell
$k = "3a1f5c7e9b2d4f6081a3c5e7092b4d6f"
cryptocore --algorithm aes --mode cbc --encrypt --key $k --input plaintext.txt --output i1.bin
cryptocore --algorithm aes --mode cbc --encrypt --key $k --input plaintext.txt --output i2.bin
(Get-Content i1.bin -Encoding Byte -TotalCount 16) -join " "
(Get-Content i2.bin -Encoding Byte -TotalCount 16) -join " "
```

Ожидается: две разные строки из 16 чисел. В PowerShell 7 вместо `-Encoding Byte` используйте `-AsByteStream`.

### 3.7. Сводка

| Требование | Проверка | Результат |
|---|---|---|
| CLI-3, KEY-1, KEY-2 | 3.2: ключ сгенерирован и выведен один раз | пройдено |
| TEST-1 | 3.3: расшифрование возвращает исходный файл | пройдено |
| CLI-4 | 3.4: ошибка без `--key` при расшифровании | пройдено |
| CLI-5 | 3.5: предупреждение о слабом ключе | пройдено (ключ из нулей) |
| IV-1, RNG-5 | 3.6: ключи и IV различаются | пройдено |
