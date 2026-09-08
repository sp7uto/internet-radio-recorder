# Changelog

Wszystkie istotne zmiany projektu Internet Radio Recorder są opisane poniżej.

## [2.1.12] — 2026-09-05

### Dodano
- zmianę kolejności stacji metodą przeciągnij i upuść (`☰`),
- przyciski `↑` i `↓` jako alternatywny sposób zmiany kolejności,
- zapis kolejności do istniejącej tablicy `stations` bez zmiany formatu konfiguracji,
- górny przycisk `ZAPISZ ZMIANY` i komunikat o niezapisanej zmianie kolejności.

### Zachowanie zgodności
- niezapisane pola formularza są odczytywane przed zmianą kolejności,
- backup i pełne przywrócenie zachowują kolejność,
- Import / scal zachowuje kolejność istniejących stacji i dopisuje nowe na końcu.

## [2.1.11]

### Dodano
- domyślny tryb **Import / scal**,
- dopisywanie nowych stacji bez usuwania istniejących,
- scalanie niekolidujących wpisów harmonogramu dla stacji o tej samej nazwie,
- pomijanie dokładnych duplikatów i konfliktów czasowych,
- podsumowanie wyniku scalania,
- datowaną kopię konfiguracji przed importem.

### Zmieniono
- stare zachowanie pełnego zastępowania konfiguracji jest dostępne jako **Przywróć backup**.

## [2.1.10]

### Naprawiono
- rozdzielanie sąsiednich audycji tej samej stacji do osobnych plików,
- priorytet nominalnego czasu audycji nad nakładającym się `pre/post`,
- obsługę harmonogramów przechodzących przez północ,
- zmianę audycji bez liczenia jej jako reconnect/błąd.

## [2.1.9]

### Naprawiono
- krytyczny błąd zatrzymywania nagrań: główny worker nie blokuje się już na `stderr` FFmpeg,
- kontrolę harmonogramu co sekundę,
- SIGTERM i awaryjny SIGKILL po 8 sekundach,
- zatrzymanie procesu po wyłączeniu lub usunięciu stacji,
- rozróżnianie powodów zakończenia nagrania (`stop_reason`).

## [2.1.8]
- wspólny silnik harmonogramu dla Kalendarza i Dzisiejszej rozpiski,
- import backupu JSON,
- automatyczna kopia konfiguracji przed importem.

## [2.1.7]
- audyt przepływu UI,
- przywrócenie `renderCalendar()`,
- poprawne odświeżanie danych i kalendarza po zapisie.

## [2.1.6]
- przywrócenie zakładki Strumienie i endpointu `/api/health`.

## [2.1.5]
- poprawka wywołania nieistniejących modułów UI.

## [2.1.4]
- odporniejszy odczyt formularza i brakujących pól.

## [2.1.3]
- atomowy zapis `stations.json`, kopia `.bak` i kontrolny odczyt po zapisie.

## [2.1.2]
- ujednolicony przycisk Kalendarz ICS.

## [2.1.1]
- endpoint subskrypcji `/calendar.ics?token=...`.

## [2.1]
- monitoring strumieni, historia testów, metadane i opcjonalne powiadomienia.

## [2.0]
- widok Dzisiaj, historia wykonań i eksport kalendarza.

## [1.9]
- tygodniowy Kalendarz i lista najbliższych zadań.

## [1.8.1]
- wizualne wskaźniki bieżącego nagrania i zajętości dysku.

## [1.8]
- odliczanie do następnego nagrania, diagnostyka, filtry biblioteki i statystyki.
