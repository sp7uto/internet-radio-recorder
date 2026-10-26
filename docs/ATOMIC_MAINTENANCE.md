# Atomowa blokada serwisowa IRR — projekt i procedura wdrożenia

> **Status 26.10.2026:** implementacja i testy zapisane w kodzie repozytorium.
> Nie oznacza to automatycznie, że funkcja działa na produkcyjnym `irr-vps`.
> Obecnie opublikowany obraz `v2.2.1` nie ma tej blokady. Nie twórz nowego
> wydania przed instalacją zgodnego skryptu aktualizatora na VPS.

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
2. Wgraj **tylko nowy** `/usr/local/sbin/irr-docker-update` na VPS,
   wykonując kopię poprzedniej wersji; podczas podmiany zatrzymaj timer
   i upewnij się, że usługa nie pracuje. Nie uruchamiaj updatera ręcznie.
3. Sprawdź, czy `/config` w kontenerze jest bind mount tego samego
   katalogu `/srv/irr/app/config`; inaczej aktualizator powinien
   zakończyć się błędem, a blokada nie będzie poprawna.
4. Dopiero po potwierdzeniu kroku 2 i 3 utwórz wydanie z nową wersją
   rejestratora (planowane `v2.2.2`), aby GitHub opublikował obraz GHCR.
5. Pierwsze przejście z `v2.2.1` na nowe wydanie jest etapem bootstrap:
   stara wersja rejestratora **jeszcze nie trzyma** współdzielonych blokad.
   Aktualizator wykonuje dlatego dwukrotny guard FFmpeg/harmonogramu i
   wybiera bezpieczne okno. Dopiero **po uruchomieniu nowego obrazu** obie
   strony używają atomowej blokady — kolejne aktualizacje są synchronizowane.
6. Sprawdź dziennik `systemd` i aktualny obraz; szczególnie komunikaty
   `Atomowa blokada serwisowa zalozona` i
   `atomowa blokada serwisowa aktywna`.

**Z uwagi na pierwszy etap przejściowy, nie wolno twierdzić, że obecnie
działający obraz v2.2.1 zapewnia tę gwarancję.**

## Diagnostyka wyłącznie do odczytu na irr-vps

```bash
systemctl is-active irr-docker-update.timer
sudo journalctl -u irr-docker-update.service -n 80 --no-pager

docker inspect -f 'Obraz: {{.Config.Image}} | Stan: {{.State.Status}}' Internet-Radio-Recorder
docker inspect -f '{{range .Mounts}}{{if eq .Destination "/config"}}CONFIG={{.Source}}{{end}}{{end}}' Internet-Radio-Recorder
```

`IRR UPDATE DEFERRED` to poprawny wynik, gdy nagrywa stacja lub
nie da się bezpiecznie wykonać aktualizacji. Po awarii wdrożenia skrypt
nadal korzysta z mechanizmu `HOLD` i `irr-rollback:...`.

Zobacz też [Automatyczne aktualizacje](AUTOMATIC_UPDATES.md)
i [Rozwiązywanie problemów](TROUBLESHOOTING.md).
