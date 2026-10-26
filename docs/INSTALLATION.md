# Instalacja i aktualizacja IRR

Stan dokumentacji: **v2.2.1** (2026-09-15). Zakładamy Docker Compose v2.

## Zwykła instalacja

```bash
git clone https://github.com/sp7uto/internet-radio-recorder.git
cd internet-radio-recorder
cp .env.example .env
cp config/stations.example.json config/stations.json
# Ustaw silny CALENDAR_TOKEN i poprawne katalogi/URL stacji.
docker compose up -d --build
```

Panel nasłuchuje na porcie 8080. Nie udostępniaj go bezpośrednio w Internecie: [SECURITY.md](../SECURITY.md).

## Dane trwałe

- `/config` — konfiguracja, historia i pliki stanu; zachowaj `stations.json`,
- `/recordings` — nagrania i ich katalogi.

Kontener działa z UID 1000; zapewnij mu uprawnienia do obu katalogów. Nie używaj pochopnie `chmod 777`.

## Aktualizacja instalacji budowanej lokalnie

1. Zrób kopię plików Compose, `.env` i katalogu `config`.
2. Sprawdź aktywne nagrania; nie restartuj kontenera w czasie audycji.
3. Użyj odpowiedniego wydania/tagu, nie podmieniaj `stations.json` przykładowym plikiem.
4. Po bezpiecznej przerwie wykonaj `docker compose up -d --build`; sprawdź `/api/data`, Historię i nowo powstałe pliki.

## Synology / Portainer

Plik `docker-compose-portainer.yml` jest **przykładem**, nie konfiguracją produkcyjną. Typowe katalogi przykładowe: `/volume1/docker/internet-radio-recorder/config` oraz `/volume1/docker/radio`. Dopasuj je do swojej instalacji i ustaw obraz `internet-radio-recorder:2.2.1` dopiero po jego lokalnym zbudowaniu. Nie nadpisuj danych ani nie uruchamiaj dodatkowego rejestratora przypadkowo.

## Automatyczna aktualizacja przez GHCR

**Dostępne i przetestowane** dla instalacji referencyjnej `irr-vps`: publiczny obraz GHCR `ghcr.io/sp7uto/internet-radio-recorder:stable`, timer `systemd`, kontrola FFmpeg i harmonogramu oraz rollback. Pierwsze automatyczne wdrożenie zakończyło się sukcesem **26.10.2026 o 01:30 CET**. Patrz [AUTOMATIC_UPDATES.md](AUTOMATIC_UPDATES.md).

W zwykłej instalacji Docker Compose **timer nie jest instalowany automatycznie**. Skrypt `deploy/install-vps.sh` jest dostosowany do konkretnego układu `irr-vps`; nie uruchamiaj go na Synology/QNAP ani na innym serwerze bez weryfikacji projektu, ścieżek i usług. Samo scalenie zmian na GitHubie nie włącza aktualizatora na kolejnych serwerach.

## Zmienne

| Zmienna | Znaczenie |
|---|---|
| `TZ` | strefa czasowa, zwykle Europe/Warsaw |
| `CONFIG_FILE` | plik konfiguracji, zwykle /config/stations.json |
| `RECORDINGS_DIR` | katalog nagrań, zwykle /recordings |
| `WEB_PORT` | port HTTP (8080) |
| `RETRY_DELAY` | opóźnienie ponowienia strumienia |
| `RETENTION_CHECK_MINUTES` | interwał retencji |
| `HEALTHCHECK_SECONDS` | interwał diagnostyki strumieni |
| `CALENDAR_TOKEN` | sekretny token dostępu do ICS |
| `NTFY_URL`, `WEBHOOK_URL` | opcjonalne adresy powiadomień |
| `NOTIFY_ON_COMPLETE` | powiadamianie o zakończeniu nagrania |
