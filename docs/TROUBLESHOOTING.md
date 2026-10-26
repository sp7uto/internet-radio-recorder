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


## IRR UPDATE DEFERRED: Nie mozna sprawdzic FFmpeg

W pierwszej wersji aktualizatora użyto `docker top Internet-Radio-Recorder -eo args`. Na referencyjnym `irr-vps` polecenie to kończyło się błędem, dlatego mechanizm zgodnie z zasadą bezpieczeństwa blokował aktualizację.

**Naprawiono w [PR #8](https://github.com/sp7uto/internet-radio-recorder/pull/8)**: aktualny `deploy/irr-update-guard.py` sprawdza `/proc/*/cmdline` wewnątrz kontenera przez `docker exec`. Jeśli na VPS błąd powraca, sprawdź, czy zainstalowany skrypt zawiera `FFMPEG_SCAN`:

```bash
grep -n 'FFMPEG_SCAN' /usr/local/sbin/irr-update-guard.py
sudo python3 -B /usr/local/sbin/irr-update-guard.py
```

Jeżeli lokalny plik jest stary, uaktualnij **wyłącznie** ten skrypt po wykonaniu kopii zapasowej, bez restartu kontenera. Nie uruchamiaj całego instalatora ponownie bez potrzeby.

## Permission denied: /tmp/__pycache__ podczas testu poprawki

Błąd `python3 -m py_compile` dla pliku utworzonego przez `mktemp` wynikał z braku możliwości zapisania pliku `.pyc` w `/tmp/__pycache__`. Nie jest to błąd nagrywania. Sprawdź składnię **bez generowania .pyc**:

```bash
python3 -B -c '
import ast, sys
with open(sys.argv[1], encoding="utf-8") as f:
    ast.parse(f.read())
print("Skladnia: OK")
' /usr/local/sbin/irr-update-guard.py
```

Nie trzeba zmieniać praw całego `/tmp` ani usuwać cudzych plików.

## Timer aktywny, ale w journalctl brak wpisów

`journalctl -f` czeka na nowe logi; nie jest to zawieszenie. Jeżeli termin w `systemctl list-timers --all irr-docker-update.timer` jest jeszcze w przyszłości, usługa mogła się jeszcze nie wykonać. Po terminie użyj:

```bash
date -Is
systemctl list-timers --all irr-docker-update.timer --no-pager
sudo journalctl -u irr-docker-update.service -n 50 --no-pager
docker inspect -f 'Obraz: {{.Config.Image}} | Stan: {{.State.Status}}' Internet-Radio-Recorder
```

Na `irr-vps` pierwsza automatyczna aktualizacja zakończyła się `SUKCES` **2026-10-26 01:30:39 CET**. Sam wynik `IRR UPDATE ALLOWED` nie znaczy, że obraz był już aktualizowany — to tylko pozytywna kontrola warunków.
