# Instalacja i aktualizacja

## 1. Docker Compose — instalacja ogólna

```bash
cp .env.example .env
cp config/stations.example.json config/stations.json
docker compose up -d --build
```

Domyślny panel: `http://adres-serwera:8080`.

### Katalogi

- `./config` → `/config` — konfiguracja i pliki stanu,
- `./recordings` → `/recordings` — nagrania.

Kontener działa z UID `1000`. Oba katalogi muszą być zapisywalne dla tego użytkownika.

## 2. Synology / Portainer

Przykładowa struktura:

```text
/volume1/docker/internet-radio-recorder/
├── config/
├── Dockerfile
├── recorder.py
├── web.py
└── static/

/volume1/docker/radio/
```

Zbuduj obraz:

```bash
cd /volume1/docker/internet-radio-recorder
docker build --no-cache -t internet-radio-recorder:2.1.12 .
```

Następnie utwórz/redeployuj kontener na podstawie `docker-compose-portainer.yml` lub w Portainerze ustaw obraz `internet-radio-recorder:2.1.12`.

## 3. Aktualizacja z wcześniejszej wersji

Najważniejsza zasada: **nie nadpisuj własnego `config/stations.json` plikiem przykładowym**.

Przed aktualizacją warto pobrać Backup z panelu. Następnie:

```bash
docker build --no-cache -t internet-radio-recorder:2.1.12 .
```

Zmień tag obrazu kontenera i wykonaj redeploy. Po aktualizacji wykonaj pełne odświeżenie strony (`Ctrl+F5`).

## 4. Zmienne środowiskowe

| Zmienna | Domyślnie | Znaczenie |
|---|---:|---|
| `TZ` | `Europe/Warsaw` | strefa czasowa kontenera |
| `CONFIG_FILE` | `/config/stations.json` | plik konfiguracji |
| `RECORDINGS_DIR` | `/recordings` | katalog nagrań |
| `WEB_PORT` | `8080` | port panelu WWW |
| `RETRY_DELAY` | `15` | opóźnienie po nieoczekiwanym przerwaniu strumienia |
| `RETENTION_CHECK_MINUTES` | `30` | odstęp kontroli retencji i limitów miejsca |
| `HEALTHCHECK_SECONDS` | `60` | odstęp testów strumieni (minimum 30 s) |
| `NTFY_URL` | puste | endpoint NTFY dla powiadomień |
| `WEBHOOK_URL` | puste | webhook JSON dla powiadomień |
| `CALENDAR_TOKEN` | puste / warto ustawić | token dostępu do `/calendar.ics` |

## 5. Uprawnienia na Synology

Jeśli panel zgłasza błąd zapisu `stations.json`, sprawdź prawa do katalogu podmontowanego jako `/config`. Jeżeli nagrania nie powstają, sprawdź analogicznie katalog `/recordings`.

Nie zmieniaj praw w ciemno na `777`; lepiej dopasować właściciela/ACL do UID używanego przez kontener.
