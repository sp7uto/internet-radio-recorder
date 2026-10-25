# Automatyczne aktualizacje IRR: GitHub → GHCR → VPS

**Stan:** mechanizm zapisany jako kod do przeglądu. Dodanie dokumentacji i workflow do GitHuba **nie oznacza**, że produkcyjny VPS został zaktualizowany ani że timer jest włączony. Wdrożenie na VPS wymaga osobnego, kontrolowanego etapu.

## 1. Publikowanie obrazów

- `.github/workflows/ci.yml`: kontrola kodu Python, testów i budowy Docker.
- `.github/workflows/release.yml`: przy nowym numerze w `VERSION` publikuje GitHub Release i dołącza archiwa z sumami SHA256.
- `.github/workflows/publish-docker.yml`: jako reusable workflow po utworzeniu Release publikuje obrazy do GitHub Container Registry, bez polegania na zdarzeniu `release` wywołanym przez `GITHUB_TOKEN`.
- Obrazy dla AMD64: `ghcr.io/sp7uto/internet-radio-recorder:vX.Y.Z` oraz `:stable`.

Dla istniejącej wersji `v2.2.1` po zaakceptowaniu PR i sprawdzeniu uprawnień do pakietów można ręcznie uruchomić **GitHub Actions → Publish Docker image → Run workflow**, wskazując `release_tag=v2.2.1`. Workflow sprawdza, czy wybrany tag jest najnowszym stabilnym wydaniem, żeby nie cofnąć `:stable`.

Pakiet GHCR trzeba udostępnić publicznie albo bezpiecznie skonfigurować poświadczenia odczytu na VPS. Tokenów nie zapisuje się w Compose ani repozytorium.

## 2. Plan bezpiecznych aktualizacji na VPS

Pliki do ewentualnej instalacji:

```text
deploy/compose.ghcr.yaml
deploy/irr-update-guard.py
deploy/irr-docker-update
deploy/systemd/irr-docker-update.service
deploy/systemd/irr-docker-update.timer
tools/test_update_guard.py
```

Timer co pół godziny uruchamia usługę jednorazową. Jej zadaniem jest:

1. Założyć blokadę `flock`, sprawdzić brak blokady `HOLD` po nieudanym wdrożeniu.
2. Odczytać istniejące pliki Docker Compose i sprawdzić, czy wskazują dokładnie produkcyjny projekt i usługę.
3. Pobrać nowy obraz GHCR poleceniem `docker pull` bez zatrzymywania kontenera.
4. Jeśli obraz jest inny: sprawdzić API `/api/data` oraz żywe procesy FFmpeg w kontenerze. Wątpliwość, aktywne nagranie, nieznany stan lub bliski start audycji (poniżej 20 min) **blokują** aktualizację.
5. Zachować stary obraz jako `irr-rollback:...`, sprawdzić nagrywanie ponownie, a następnie odtworzyć usługę z nakładką GHCR. Zachować dotychczasowe wolumeny i pliki `.env`.
6. Sprawdzić API nowego kontenera. Po błędzie spróbować przywrócić poprzedni obraz oraz włączyć `HOLD`, aby kolejne automatyczne wdrożenia nie powodowały pętli.

**Istotne ograniczenie:** odczyt harmonogramu i statusu nie jest blokadą atomową. Pomiędzy kontrolą a odtworzeniem kontenera może zacząć się nagranie. Zmniejsza to ryzyko, ale nie daje gwarancji bezprzerwowej rejestracji. Pełna gwarancja wymagałaby blokady konserwacyjnej w IRR lub drugiego rejestratora.

## 3. Specyfika instalacji irr-vps

Produkcja działa w `/srv/irr/app`, na obrazie `internet-radio-recorder:2.2.1`. Lokalny katalog Git pozostał na commicie wersji 2.2.0, ma własne zmiany w Compose i `compose.override.yaml`. **Nie wolno wykonywać automatycznego `git pull` w katalogu produkcyjnym**. Nie dotykamy zadań synchronizacji VPS → QNAP → Synology. Kontener IRR na QNAP jest celowo zatrzymany.

Przed instalacją usługi zweryfikuj rzeczywiste etykiety projektu Compose, końcową konfigurację `docker compose config`, kopie bezpieczeństwa oraz uprawnienia do GHCR. Samego workflow GitHub nie należy mylić z uruchomieniem aktualizacji.

Docelowe lokalizacje plików na VPS, **po osobnym zatwierdzeniu**:

```text
/etc/irr-updater/compose.ghcr.yaml
/usr/local/sbin/irr-update-guard.py
/usr/local/sbin/irr-docker-update
/etc/systemd/system/irr-docker-update.service
/etc/systemd/system/irr-docker-update.timer
/var/lib/irr-updater/
```

Po kontrolowanej instalacji, pierwszym teście bez aktywnych nagrań i potwierdzeniu poprawności aktualizacji można włączyć timer `systemctl enable --now irr-docker-update.timer`. Wcześniej NIE uruchamiaj timera automatycznie.

## 4. Diagnostyka i wycofanie

- Wyłączenie automatyki: `sudo systemctl disable --now irr-docker-update.timer`.
- Kontrola usługi: `sudo journalctl -u irr-docker-update.service -n 100 --no-pager`.
- Status timera: `sudo systemctl status irr-docker-update.timer`.
- Blokada po nieudanym wdrożeniu: `/var/lib/irr-updater/HOLD`. Nie usuwaj jej bez zbadania przyczyny.
- Obraz awaryjny pozostaje lokalnie oznaczony `irr-rollback:...`. Zachowanie `/config` oraz `/recordings` jest warunkiem każdego wdrożenia.

Zobacz także [Instalacja](INSTALLATION.md), [GitHub Publishing](GITHUB_PUBLISHING.md) i [Security](../SECURITY.md).
