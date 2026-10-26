# Automatyczne aktualizacje IRR — GitHub → GHCR → VPS

## Aktualny stan (26 października 2026)

**Wdrożone i potwierdzone na `irr-vps`:** publikacja GHCR, timer `systemd`, kontrola FFmpeg/harmonogramu, wdrożenia v2.2.1 i **v2.2.2**. Nowy obraz v2.2.2 został automatycznie uruchomiony **26.10.2026 o 03:01:21 CET**; logi potwierdziły blokadę wyłączną hostowego aktualizatora, a kontener zgłosił `flock-v1`.

| Element | Stan |
|---|---|
| Repozytorium | [sp7uto/internet-radio-recorder](https://github.com/sp7uto/internet-radio-recorder) |
| Stabilne wydanie (wdrożone na VPS) | `v2.2.2` |
| Publiczny rejestr | [GHCR: internet-radio-recorder](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder) |
| Obraz śledzony przez VPS | `ghcr.io/sp7uto/internet-radio-recorder:stable` |
| Wersjonowany obraz | `ghcr.io/sp7uto/internet-radio-recorder:v2.2.2` (opublikowany i wdrożony) |
| Lokalizacja aplikacji na VPS | `/srv/irr/app` |
| Kontener | `Internet-Radio-Recorder` |
| Timer | `irr-docker-update.timer`; dwa terminy na godzinę, z losowym opóźnieniem do 60 s |
| Automatyczne aktualizacje QNAP/Synology | **Nie wdrożono**; działają dotychczasowe synchronizacje |

### Potwierdzone pierwsze wdrożenie

Dziennik `irr-vps` z **2026-10-26**, czas lokalny **CET**:

- **01:30:22** — uruchomienie przez `systemd`, pobranie / weryfikacja obrazu `:stable`.
- **01:30:23–01:30:24** — dwukrotne `IRR UPDATE ALLOWED` po sprawdzeniu procesów i harmonogramu.
- **01:30:24–01:30:35** — odtworzenie kontenera Docker i jego uruchomienie.
- **01:30:39** — `[IRR UPDATE] SUKCES` oraz `status=0/SUCCESS` usługi.

Zarejestrowany identyfikator obrazu: `sha256:54a13eb676dce6e4e40a9f72a4a9d920c3989634ea50116bd029c9d8c92ae3f2`. Zachowany obraz awaryjny: `irr-rollback:20261026-003023` (znacznik czasu w nazwie jest w **UTC**, czyli 00:30:23 UTC = 01:30:23 CET).

Ten zapis dokumentuje konkretny test na VPS; **nie jest gwarancją**, że przyszłe aktualizacje będą trwały tyle samo albo że start nowej audycji nie zbiegnie się z restartem.

## Atomowa blokada serwisowa — status wdrożenia

Atomowa blokada serwisowa działa już produkcyjnie w **v2.2.2**. Skrypt hostowego aktualizatora na `irr-vps` został zaktualizowany 26.10.2026 i potwierdzono zgodność katalogu `/config`. Po automatycznym uruchomieniu nowego obrazu rejestrator zgłosił `flock-v1`. Współdzielony `flock` pracowników IRR i wyłączny `flock` aktualizatora korzystają z tego samego pliku `/config/.irr-maintenance.lock`, wykluczając jednoczesne przyznanie sprzecznych blokad. Podczas pierwszego przejścia z `v2.2.1` wykonano również dwie dotychczasowe kontrole FFmpeg/harmonogramu.

**Potwierdzone wdrożenie v2.2.2:** `2026-10-26 03:00:47–03:01:21 CET` (34 s), odtworzenie kontenera `03:01:06–03:01:17` (11 s), wynik `SUKCES`, obraz awaryjny `irr-rollback:20261026-020106`; digest nowego obrazu `sha256:a10d32ef0821ce9cf04ce4e653adc06111feac357c0e2e30e95614e113807fb7`. Szczegóły i ograniczenia: [ATOMIC_MAINTENANCE.md](ATOMIC_MAINTENANCE.md).

## GitHub Actions i publikowanie obrazów

- `.github/workflows/ci.yml` — testy Pythona, aktualizatora, składni powłoki i budowy Dockera.
- `.github/workflows/release.yml` — przygotowuje nowe GitHub Release przy nowej wersji określonej w `VERSION`, po czym wywołuje workflow publikacji Docker.
- `.github/workflows/publish-docker.yml` — publikuje obraz po wywołaniu przez `release.yml`; obsługuje też ręczne uruchomienie oraz uruchomienie po zmianie własnego pliku na `main`. Odczytuje aktualne stabilne wydanie, buduje z **tagu wydania**, a nie z późniejszych commitów dokumentacyjnych.
- Rejestr GHCR jest publiczny; dla `irr-vps` nie jest potrzebny prywatny token odczytu. Workflow publikujący korzysta z `GITHUB_TOKEN` z prawem `packages: write`.

Znaczniki `vX.Y.Z` są wersjonowane, natomiast `:stable` wskazuje ostatnie opublikowane stabilne wydanie. Automatyczny VPS śledzi `:stable`.

## Jak pracuje aktualizator na VPS

1. Timer wywołuje usługę jednorazową `/usr/local/sbin/irr-docker-update`.
2. Skrypt uzyskuje blokadę `flock`, sprawdza brak `/var/lib/irr-updater/HOLD` i zgodność projektu/usługi Docker Compose.
3. Pobiera obraz GHCR **bez zatrzymywania nagrywania**. Gdy identyfikator obrazu jest identyczny z uruchomionym, kończy bez restartu.
4. Wykonuje kontrolę przez `/usr/local/sbin/irr-update-guard.py`: procesy `ffmpeg` są sprawdzane przez `/proc/*/cmdline` **wewnątrz kontenera**, a stan stacji i kolejne terminy przez `/api/data`. Nie używa już hostowego `docker top -eo args` (poprawka [PR #8](https://github.com/sp7uto/internet-radio-recorder/pull/8)).
5. Aktualizacja jest odraczana przy nagrywaniu, nieznanym stanie, błędzie odczytu albo zbyt bliskiej audycji. Minimalny odstęp od następnego nagrania: **20 minut**. Kontrola jest wykonywana ponownie tuż przed odtworzeniem kontenera.
6. Przed wdrożeniem zapisuje poprzedni obraz jako `irr-rollback:YYYYMMDD-HHMMSS` (UTC), aktualizuje **wyłącznie usługę IRR**, sprawdza jej API i w razie błędu próbuje automatycznie wrócić do poprzedniego obrazu oraz tworzy `HOLD`.

**Ograniczenie:** w v2.2.2 blokada `flock` zapewnia atomową koordynację przyznania prawa do uruchomienia FFprobe/FFmpeg i wyłączności aktualizatora. **Nie gwarantuje jednak nagrywania bez żadnej przerwy:** audycja zaplanowana dokładnie podczas odtwarzania kontenera może rozpocząć zapis z opóźnieniem. Pełna ciągłość wymagałaby drugiego rejestratora lub architektury pozwalającej aktualizować aplikację bez przerwania procesu nagrywania.

## Pliki zainstalowane na irr-vps

```text
/srv/irr/app/                                # produkcyjny Compose i pliki danych
/etc/irr-updater/compose.ghcr.yaml           # dodatkowa nakładka: obraz GHCR
/usr/local/sbin/irr-update-guard.py          # kontrola FFmpeg/API/harmonogramu
/usr/local/sbin/irr-docker-update            # wdrożenie / rollback
/etc/systemd/system/irr-docker-update.service
/etc/systemd/system/irr-docker-update.timer
/var/lib/irr-updater/                        # stan, lock, HOLD po awarii
/var/backups/irr-updater/                    # kopie plików instalatora
```

Instalator znajduje się w [`deploy/install-vps.sh`](../deploy/install-vps.sh). **Jest już wykonany na `irr-vps`; nie uruchamiaj go ponownie tylko po to, by sprawdzić status.** Nie zmienia on istniejącego Compose i nie restartuje kontenera podczas instalacji. Na VPS lokalny Git w `/srv/irr/app` pozostaje niezależny od działającego obrazu i ma lokalne zmiany; automatyzacja **nie wykonuje `git pull`** w tym katalogu.

Dotychczasowy łańcuch synchronizacji **VPS → QNAP → Synology** pozostał bez zmian. Kontener IRR na QNAP jest celowo zatrzymany.

## Sprawdzenie statusu (tylko odczyt, na irr-vps)

```bash
echo "===== TIMER ====="
systemctl is-enabled irr-docker-update.timer
systemctl is-active irr-docker-update.timer
systemctl list-timers --all irr-docker-update.timer --no-pager

echo "===== OSTATNIE WYKONANIE ====="
sudo systemctl status irr-docker-update.service --no-pager -l || true
sudo journalctl -u irr-docker-update.service -n 60 --no-pager

echo "===== DZIALAJACY OBRAZ ====="
docker inspect -f 'Obraz: {{.Config.Image}} | Stan: {{.State.Status}} | Start: {{.State.StartedAt}}' Internet-Radio-Recorder

echo "===== WERYFIKACJA KONTROLI BEZ RESTARTU ====="
sudo python3 -B /usr/local/sbin/irr-update-guard.py
echo "Kod kontroli: $?"
```

Wynik `IRR UPDATE ALLOWED` oznacza jedynie, że aktualne warunki **wydają się bezpieczne**; polecenie kontrolne nie aktualizuje obrazu. Wynik `IRR UPDATE DEFERRED` jest prawidłowy przy aktywnej audycji, zbliżającym się zadaniu lub nieznanym stanie.

`journalctl -f` obserwuje na żywo i **nie kończy się samoczynnie**; do jednorazowego sprawdzenia używaj `-n ... --no-pager`.

## Awaryjne wyłączenie i wycofanie

- Wyłączenie **samej automatyki**, bez zatrzymywania kontenera: `sudo systemctl disable --now irr-docker-update.timer`.
- Weryfikacja ostatnich uruchomień: `sudo journalctl -u irr-docker-update.service -n 100 --no-pager`.
- W razie nieudanej aktualizacji skrypt podejmuje próbę rollbacku i zapisuje `/var/lib/irr-updater/HOLD`. Nie usuwaj pliku `HOLD` bez diagnozy błędu.
- Lokalny poprzedni obraz jest dostępny pod znacznikiem `irr-rollback:...`; jego przywrócenie powinno odbywać się w bezpiecznym oknie i z zachowaniem `/config` oraz `/recordings`.
- Automatyczne testy API nie weryfikują jakości wszystkich przyszłych nagrań. Po ważnym wydaniu sprawdź również Historię i nowe pliki audio.

Więcej: [Instalacja](INSTALLATION.md), [Publikowanie GitHub](GITHUB_PUBLISHING.md), [Rozwiązywanie problemów](TROUBLESHOOTING.md), [Bezpieczeństwo](../SECURITY.md).
