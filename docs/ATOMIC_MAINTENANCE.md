# Atomowa blokada serwisowa IRR — projekt i procedura wdrożenia

> **Status 26.10.2026: WDROŻONE NA `irr-vps`.** GitHub opublikował
> wydanie i obraz **v2.2.2**. Timer produkcyjnego VPS automatycznie
> wdrożył obraz i zakończył o **03:01:21 CET** ze statusem `SUKCES`.
> W logach potwierdzono blokadę wyłączną aktualizatora, zaś nowy
> kontener działa i zgłasza `flock-v1`. Nie uruchamiano aktualizacji ręcznie.

## Na czym polega gwarancja

IRR i aktualizator otwierają **ten sam nieusuwany plik**:
- w kontenerze: `/config/.irr-maintenance.lock`,
- na hostowym `irr-vps`: `/srv/irr/app/config/.irr-maintenance.lock`.

Plik jest wspólny dzięki istniejącemu montowaniu `/config`. Blokady
`flock` dotyczą **tego samego inode na hoście**, nie tylko nazwy pliku.

Każdy worker nagrywania otwiera plik i pobiera **współdzieloną, nieblokującą**
blokadę `LOCK_SH | LOCK_NB` **zanim uruchomi FFprobe**. Trzyma ją podczas
FFprobe, FFmpeg i oczekiwania na zakończenie procesu. Kilka jednoczesnych
nagrań może mieć kilka blokad współdzielonych.

Aktualizator po pobraniu obrazu i wstępnej kontroli uzyskuje **wyłączną,
nieblokującą** blokadę `LOCK_EX | LOCK_NB`. Jeśli jakikolwiek worker ma
aktywną blokadę, aktualizacja jest **odroczona**. Jeżeli aktualizator
uzyska wyłączność, nowy worker **nie może rozpocząć FFprobe ani FFmpeg**.
Worker oznacza stan jako `maintenance`, czeka sekundę i ponawia próbę.
Po udanym wdrożeniu (albo rollbacku) aktualizator zwalnia blokadę,
a rejestrator wznawia normalną obsługę harmonogramu.

**To eliminuje wyścig przy przyznawaniu uprawnienia do startu procesu:**
worker i aktualizator nie mogą jednocześnie uzyskać sprzecznych blokad
na tym samym pliku. Zwykłe sprawdzanie `/api/data` i procesów FFmpeg
pozostaje jako dodatkowa ochrona, nie jako jedyna synchronizacja.

**Ważne ograniczenia:** `flock` nie zapewnia nieprzerwanego nagrania.
Jeżeli audycja zostanie zaplanowana dokładnie podczas wdrażania,
nowy proces nagrywania zacznie ją dopiero po zwolnieniu blokady. Aby
gwarantować każdy fragment audycji, potrzebny jest drugi rejestrator
lub architektura nagrywania bez restartu. Flock ma zastosowanie wyłącznie
wtedy, gdy **obie** wersje oprogramowania (rejestrator i hostowy updater)
używają tej samej blokady. Nie należy usuwać pliku blokady; usunięcie
i odtworzenie tworzy nowe inode i łamie synchronizację. Brak możliwości
otwarcia blokady jest błędem i **nie może uruchamiać FFmpeg**.

## Co zmienia wdrożenie

Pliki rejestratora:
- `maintenance_gate.py` — funkcje `acquire_shared`, `release_shared`.
- `recorder.py` — wywołania przed FFprobe i po zakończeniu FFmpeg.
- `Dockerfile` — dołączenie modułu.
- `tests/test_maintenance_gate.py` — testy współdzielenia/wyłączności
  i procesów współbieżnych.

Plik serwerowy:
- `deploy/irr-docker-update` — hostowy `flock -x` w czasie wdrożenia,
  weryfikacja tego samego bind mount `/config`, drugi guard pod blokadą,
  i sprawdzenie obecności `RECORDING_GATE_VERSION=flock-v1` po restarcie.

**Nie zmienia** `stations.json`, zapisu nagrań, portów, mapowań `/recordings`,
harmonogramów, systemów synchronizacji ani UI.

## Bezpieczna kolejność aktywacji na irr-vps

1. Przejrzyj PR oraz testy CI. Nie zmieniaj obrazu Docker w trakcie nagrań.
2. **Wykonano na `irr-vps` 26.10.2026:** podmieniono wyłącznie
   `/usr/local/sbin/irr-docker-update`, po zatrzymaniu timera i wykonaniu
   kopii `irr-docker-update.bak-20261026-023441`. Timer jest znowu aktywny.
   Nie trzeba powtarzać tej czynności.
3. **Wykonano:** potwierdzono, że `/config` w kontenerze jest bind
   mount dokładnie `/srv/irr/app/config`; nie zmieniano wolumenów.
4. **Wykonano:** GitHub Actions opublikował wersjonowany obraz
   `ghcr.io/sp7uto/internet-radio-recorder:v2.2.2` oraz `:stable`.
   Digest: `sha256:a10d32ef0821ce9cf04ce4e653adc06111feac357c0e2e30e95614e113807fb7`.
5. Pierwsze przejście z `v2.2.1` na nowe wydanie jest etapem bootstrap:
   stara wersja rejestratora **jeszcze nie trzyma** współdzielonych blokad.
   Aktualizator wykonuje dlatego dwukrotny guard FFmpeg/harmonogramu i
   wybiera bezpieczne okno. Dopiero **po uruchomieniu nowego obrazu** obie
   strony używają atomowej blokady — kolejne aktualizacje są synchronizowane.
6. **Wykonano:** aktualizator 26.10.2026 w przedziale **03:00:47–03:01:21 CET**
   pobrał nowy obraz, dwukrotnie uzyskał `IRR UPDATE ALLOWED`,
   następnie zapisał `Atomowa blokada serwisowa zalozona`, odtworzył
   kontener w godzinach **03:01:06–03:01:17** i zakończył komunikatem
   `SUKCES: ... atomowa blokada serwisowa aktywna`. Odczyt z działającego
   kontenera zwrócił `flock-v1`.

Poprzedni obraz zachowano jako `irr-rollback:20261026-020106`.
Pełna koordynacja blokad zaczęła działać po uruchomieniu v2.2.2.
Przyszłe aktualizacje nadal nie gwarantują zapisu od pierwszej sekundy
audycji rozpoczynającej się w trakcie restartu.

## Diagnostyka wyłącznie do odczytu na irr-vps

```bash
systemctl is-active irr-docker-update.timer
sudo journalctl -u irr-docker-update.service -n 80 --no-pager

docker inspect -f 'Obraz: {{.Config.Image}} | Stan: {{.State.Status}}' Internet-Radio-Recorder
docker exec Internet-Radio-Recorder python3 -c 'from maintenance_gate import RECORDING_GATE_VERSION; print(RECORDING_GATE_VERSION)'
docker inspect -f '{{range .Mounts}}{{if eq .Destination "/config"}}CONFIG={{.Source}}{{end}}{{end}}' Internet-Radio-Recorder
```

`IRR UPDATE DEFERRED` to poprawny wynik, gdy nagrywa stacja lub
nie da się bezpiecznie wykonać aktualizacji. Po awarii wdrożenia skrypt
nadal korzysta z mechanizmu `HOLD` i `irr-rollback:...`.

Zobacz też [Automatyczne aktualizacje](AUTOMATIC_UPDATES.md)
i [Rozwiązywanie problemów](TROUBLESHOOTING.md).
