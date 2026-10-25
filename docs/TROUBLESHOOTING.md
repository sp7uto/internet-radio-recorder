# Rozwiązywanie problemów

## Nie zapisuje `stations.json`

Sprawdź, czy katalog podmontowany jako `/config` jest zapisywalny dla UID `1000`. Panel powinien pokazać konkretny komunikat błędu.

## Stacja jest OFFLINE

1. Kliknij **Test streamu**.
2. Sprawdź bezpośredni URL — strona WWW stacji nie jest tym samym co URL audio.
3. Zajrzyj do zakładki **Strumienie** i pola ostatniego błędu.
4. Sprawdź, czy URL działa z hosta Dockerowego.

## Nagranie nie zatrzymuje się o czasie

W wersjach starszych niż 2.1.9 występował krytyczny błąd związany z blokującym odczytem `stderr` FFmpeg. Użyj 2.1.12 lub nowszej.

## Dwie sąsiednie audycje trafiają do jednego pliku

Upewnij się, że:

- używasz wersji co najmniej 2.1.10,
- opcja **1 plik / audycję** jest włączona,
- audycje są osobnymi wpisami harmonogramu.

## Po aktualizacji panel wygląda jak wcześniej

Wykonaj pełne odświeżenie (`Ctrl+F5`) lub usuń cache strony.

## Kalendarz ICS nie działa w Google Calendar

Google pobiera subskrypcję ze swoich serwerów. Adres `localhost` lub prywatny `192.168.x.x` nie jest dla niego dostępny. Potrzebny jest osiągalny z Internetu adres HTTPS albo ręczne pobranie/import pliku ICS.

## Brak nagrań mimo działającego harmonogramu

Sprawdź:

- `enabled` stacji,
- strefę `TZ`,
- prawa do `/recordings`,
- zakładkę Historia i `stop_reason`,
- logi kontenera,
- wynik Test streamu.

## Nagrania MP3 pojawiają się jako puste AAC

Problem opisany w zgłoszeniu [#1](https://github.com/sp7uto/internet-radio-recorder/issues/1) został objęty wydaniem **2.2.1**. Użyj wersji co najmniej 2.2.1, sprawdź historię wykonania i raport FFprobe. Nie naprawiaj problemu przez automatyczne przemianowanie pustych plików AAC na MP3.

## Aktualizator Docker nie wdraża nowego obrazu

Zobacz [Automatyczne aktualizacje](AUTOMATIC_UPDATES.md): sprawdź, czy GHCR jest osiągalny, czy kontrola harmonogramu pozwala na restart, oraz czy usługa nie jest zablokowana plikiem `HOLD`. Nigdy nie zatrzymuj ręcznie pracującego FFmpeg wyłącznie po to, aby wymusić aktualizację.
