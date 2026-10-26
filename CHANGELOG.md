# Changelog

Wszystkie istotne zmiany projektu Internet Radio Recorder są opisane poniżej.

## Infrastruktura i dokumentacja — 2026-10-26 (bez zmiany wersji aplikacji)

- uporządkowano dokumentację, usunięto nieaktualne instrukcje i powtórzenia w README,
- uruchomiono automatyczne publikowanie stabilnych obrazów Docker do publicznego GHCR,
- wdrożono na `irr-vps` usługę i timer `systemd` kontrolujące aktualizacje w oknie bez nagrywania,
- naprawiono sprawdzanie procesów FFmpeg: w miejsce niedziałającego `docker top ... -eo args` używany jest odczyt `/proc` wewnątrz kontenera; weryfikacja w CI,
- pierwsze automatyczne wdrożenie obrazu `v2.2.1` z GHCR: **2026-10-26 01:30 CET**, status `SUCCESS`, z zachowaniem lokalnego obrazu rollback.

Nie utworzono nowej wersji programu: `VERSION` nadal ma wartość `2.2.1`. Zmiany dotyczą dystrybucji, aktualizatora i dokumentacji, nie działania rejestratora.

## [2.2.1] — 2026-09-15

### Naprawiono
- przed nagrywaniem FFprobe wykrywa format strumienia; wyjście MP3 lub AAC jest wybierane bez transkodowania,
- stacje importowane lub zapisane bez testu strumienia nie korzystają z nieaktualnego domyślnego formatu AAC,
- brakujące i puste nagrania są zgłaszane jako błędy,
- historia wykonań zawiera polecenie FFmpeg, kod zakończenia oraz wybrany format.

### Dodano
- opcjonalne powiadomienia o zakończonym nagraniu przez `NOTIFY_ON_COMPLETE=true`.

### Zgodność
- bez zmian w formacie `stations.json`, portach i montowanych wolumenach.

## [2.2.0] — 2026-09-14

### Architektura
- zastąpiono `BaseHTTPRequestHandler` aplikacją Flask i routingiem opartym na dekoratorach,
- dodano wielowątkowy serwer WSGI Waitress, działający w tym samym procesie co workery nagrywania,
- rozdzielono backend API, logikę harmonogramów, szablon HTML, CSS i JavaScript,
- usunięto ogromny string zawierający cały interfejs.

### Naprawiono
- niezależne odświeżanie widoków Dzisiaj, Kalendarz i Historia po zmianie zakładki,
- walidację danych przekazywanych do `/api/save`,
- ochronę endpointów odczytu i kasowania nagrań przed path traversal.

### Testy i zgodność
- dodano testy routingu API, zapisu, importu, plików statycznych i ochrony ścieżek,
- zachowano format `stations.json`, endpointy, port `8080` oraz wolumeny `/config` i `/recordings`.

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
