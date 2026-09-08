internet-radio · radio-recorder · self-hosted · docker · ffmpeg · python · synology · nas · scheduler · web-ui

# Internet Radio Recorder

Self-hosted Internet radio recorder with a web interface, weekly schedules, stream monitoring, recording library, ICS calendar support, configuration backup/merge, and Docker/Synology deployment.

Internet Radio Recorder was created as a simple way to record selected Internet radio programmes automatically on a NAS or home server without maintaining cron jobs or running a full broadcast automation stack.

Current release: **v2.1.12**

## Features

* multiple Internet radio stations,
* weekly recording schedules,
* programme titles,
* configurable `pre` / `post` recording margins,
* one file per programme,
* correct handling of adjacent programmes,
* support for programmes crossing midnight,
* recording without re-encoding using `ffmpeg -c:a copy`,
* manual `REC` / `STOP`,
* per-station retention limits,
* per-station storage limits,
* Today view,
* Calendar view,
* History,
* Stream monitoring,
* Recording Library,
* Statistics,
* stream availability testing,
* codec and bitrate diagnostics,
* optional NTFY notifications,
* optional webhook notifications,
* ICS calendar subscription,
* configuration backup,
* safe configuration import / merge,
* station reordering using drag-and-drop or `↑` / `↓`,
* Docker Compose deployment,
* Synology / Portainer configuration example.

<!-- SCREENSHOTS_START -->

## Screenshots

### Today — Scheduled Recordings

![Today — Scheduled Recordings](docs/screenshots/IRR01.png)

### Calendar

![Calendar](docs/screenshots/IRR02.png)

### Stations

![Stations](docs/screenshots/IRR03.png)

### Stream Status

![Stream Status](docs/screenshots/IRR04.png)

### Recording Library

![Recording Library](docs/screenshots/IRR05.png)

### Statistics

![Statistics](docs/screenshots/IRR06.png)

<!-- SCREENSHOTS_END -->

## Quick Start

Requirements:

* Docker
* Docker Compose v2

Clone the repository:

```bash
git clone https://github.com/sp7uto/internet-radio-recorder.git
cd internet-radio-recorder
```

Create your local configuration:

```bash
cp .env.example .env
cp config/stations.example.json config/stations.json
```

Edit `.env` and at minimum change:

```text
CALENDAR_TOKEN
```

Then start the application:

```bash
docker compose up -d --build
```

The web interface is available by default at:

```text
http://server-address:8080
```

Recordings are stored in:

```text
./recordings
```

Application configuration is stored in:

```text
./config
```

## Synology / Portainer

A separate example configuration is included:

```text
docker-compose-portainer.yml
```

Example Synology paths:

```text
/volume1/docker/internet-radio-recorder/config
/volume1/docker/radio
```

See:

```text
docs/INSTALLATION.md
```

for detailed installation and upgrade instructions.

## Scheduling

Each station can contain multiple schedule entries for every day of the week.

Example:

```json
{
  "start": "20:00",
  "end": "21:00",
  "title": "Programme Name",
  "pre": 2,
  "post": 3
}
```

`pre` and `post` specify recording margins in minutes before and after the scheduled programme.

Programmes crossing midnight are supported.

When **one file per programme** is enabled, the nominal start of the next scheduled programme takes priority over overlapping recording margins.

More information:

```text
docs/SCHEDULING.md
```

## Backup and Import

The web interface provides several configuration management options.

**Backup**

Downloads the current `stations.json`.

**Import / Merge**

Keeps existing stations and schedules while adding new, non-conflicting entries.

**Restore Backup**

Replaces the complete configuration.

Before an import operation, Internet Radio Recorder automatically creates a timestamped backup:

```text
stations.before-import-YYYYMMDD-HHMMSS.json
```

More information:

```text
docs/BACKUP_AND_MERGE.md
```

## ICS Calendar

The recording schedule can be subscribed to as an ICS calendar.

Example:

```text
http://server-address:8080/calendar.ics?token=YOUR_TOKEN
```

The access token is configured using:

```text
CALENDAR_TOKEN
```

## Notifications

Optional notifications can be sent using:

* NTFY,
* webhook endpoints.

These can be used to report recording events and application status.

## Security

The web administration panel **does not provide built-in authentication**.

Anyone with access to the web interface may be able to:

* modify station configuration,
* start or stop recordings,
* delete recordings from the library.

Do **not** expose port `8080` directly to the public Internet.

Recommended remote access methods:

* Tailscale,
* VPN,
* reverse proxy with HTTPS and authentication.

See:

```text
SECURITY.md
```

## Documentation

* [Installation and upgrades](docs/INSTALLATION.md)
* [Configuration](docs/CONFIGURATION.md)
* [Scheduling](docs/SCHEDULING.md)
* [Backup and import/merge](docs/BACKUP_AND_MERGE.md)
* [API and endpoints](docs/API.md)
* [Troubleshooting](docs/TROUBLESHOOTING.md)
* [Security](SECURITY.md)
* [Changelog](CHANGELOG.md)

## Technical Details

The Docker image is based on:

```text
debian:bookworm-slim
```

It includes:

* Python 3,
* FFmpeg,
* FFprobe.

The container runs as UID:

```text
1000
```

Mounted `/config` and `/recordings` directories must therefore be writable by that user.

## Latest Release

Current stable release:

```text
v2.1.12
```

Version 2.1.12 adds persistent station ordering and includes fixes for scheduled recording, adjacent programmes, midnight transitions, and safe configuration merging.

See the GitHub Releases section for full release notes and downloadable packages.

## Contributing

Bug reports, feature requests and pull requests are welcome.

Please see:

```text
CONTRIBUTING.md
```

## License

Internet Radio Recorder is released under the **MIT License**.

See:

```text
LICENSE
```

## Feedback

If you already record Internet radio or podcasts on a home server, feedback is especially welcome.

Ideas, bug reports and suggestions can be submitted through GitHub Issues.



# Internet Radio Recorder 2.1.12

Lekki, samodzielny rejestrator internetowych stacji radiowych z tygodniowym harmonogramem, panelem WWW i biblioteką nagrań. Projekt działa w Dockerze i dobrze nadaje się do NAS-ów, w tym Synology.

## Najważniejsze możliwości

- wiele stacji i tygodniowy harmonogram nagrań,
- osobne nazwy audycji oraz marginesy `pre` / `post`,
- tryb **1 plik / audycję** z poprawnym przełączaniem na granicy sąsiednich programów,
- nagrywanie bez ponownego kodowania (`ffmpeg -c:a copy`),
- ręczne `REC` / `STOP`,
- retencja według liczby dni i limit miejsca dla każdej stacji,
- widoki **Dzisiaj**, **Kalendarz**, **Historia**, **Strumienie**, **Biblioteka** i **Statystyki**,
- test strumienia oraz diagnostyka ONLINE/OFFLINE, kodeka, bitrate i stabilności,
- opcjonalne powiadomienia NTFY i webhook,
- kalendarz ICS z tokenem,
- backup konfiguracji,
- **Import / scal** bez kasowania istniejących stacji i harmonogramów,
- przeciąganie stacji oraz przyciski `↑` / `↓` do zmiany ich kolejności.

<!-- SCREENSHOTS_START -->

## Screenshots

### Today — Scheduled Recordings

![Irr01](docs/screenshots/IRR01.png)

### Calendar

![Irr02](docs/screenshots/IRR02.png)

### Stations

![Irr03](docs/screenshots/IRR03.png)

### Stream Status

![Irr04](docs/screenshots/IRR04.png)

### Recording Library

![Irr05](docs/screenshots/IRR05.png)

### Statistics

![Irr06](docs/screenshots/IRR06.png)

<!-- SCREENSHOTS_END -->

## Co nowego w 2.1.12

Wersja 2.1.12 dodaje trwałą zmianę kolejności stacji w panelu WWW. Stacje można przeciągać za uchwyt `☰` albo przesuwać przyciskami `↑` i `↓`. Kolejność jest zapisywana bez zmiany formatu `stations.json`, przeżywa restart i backup, a import scalający zachowuje dotychczasowy układ i dopisuje nowe stacje na końcu.

Wersja zawiera też wcześniejsze poprawki 2.1.9–2.1.11: prawidłowe zatrzymywanie nagrań, rozdzielanie sąsiednich audycji i bezpieczny import scalający.

Pełna historia: [CHANGELOG.md](CHANGELOG.md).

## Szybki start — Docker Compose

Wymagania: Docker z Compose v2.

```bash
cp .env.example .env
cp config/stations.example.json config/stations.json
# Zmień przede wszystkim CALENDAR_TOKEN w .env oraz stacje w panelu WWW.
docker compose up -d --build
```

Panel domyślnie będzie dostępny pod:

```text
http://adres-serwera:8080
```

Nagrania są zapisywane w `./recordings`, a konfiguracja i dane pomocnicze w `./config`.

## Synology / Portainer

Dla Synology dołączony jest `docker-compose-portainer.yml` z przykładowymi ścieżkami:

```text
/volume1/docker/internet-radio-recorder/config
/volume1/docker/radio
```

Szczegółowa instrukcja: [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Harmonogram

Każda stacja może mieć wiele wpisów w każdym dniu tygodnia:

```json
{
  "start": "20:00",
  "end": "21:00",
  "title": "Nazwa audycji",
  "pre": 2,
  "post": 3
}
```

`pre` i `post` oznaczają minuty zapasu przed i po nominalnym czasie audycji. Programy przechodzące przez północ są obsługiwane. Przy włączonym **1 plik / audycję** nominalna granica kolejnej audycji ma pierwszeństwo przed nakładającymi się zapasami.

Więcej: [docs/SCHEDULING.md](docs/SCHEDULING.md).

## Backup i import

- **Backup** pobiera aktualne `stations.json`.
- **Import / scal** zachowuje istniejące stacje i harmonogramy, dopisując nowe niekolidujące pozycje.
- **Przywróć backup** zastępuje całą konfigurację.
- Przed importem tworzona jest datowana kopia `stations.before-import-YYYYMMDD-HHMMSS.json`.

Więcej: [docs/BACKUP_AND_MERGE.md](docs/BACKUP_AND_MERGE.md).

## Kalendarz ICS

Subskrypcja:

```text
http://adres-serwera:8080/calendar.ics?token=TWÓJ_TOKEN
```

Token ustawia zmienna `CALENDAR_TOKEN`.

## Bezpieczeństwo

**Panel WWW nie ma wbudowanego uwierzytelniania.** Użytkownik mający dostęp do panelu może zmieniać konfigurację, uruchamiać i zatrzymywać nagrania oraz usuwać pliki z biblioteki. Nie wystawiaj portu 8080 bezpośrednio do Internetu.

Zalecany dostęp zdalny: VPN/Tailscale albo reverse proxy z HTTPS i uwierzytelnieniem. Szczegóły: [SECURITY.md](SECURITY.md).

## Dokumentacja

- [Instalacja i aktualizacja](docs/INSTALLATION.md)
- [Konfiguracja](docs/CONFIGURATION.md)
- [Harmonogram i podział audycji](docs/SCHEDULING.md)
- [Backup oraz Import / scal](docs/BACKUP_AND_MERGE.md)
- [API i endpointy](docs/API.md)
- [Rozwiązywanie problemów](docs/TROUBLESHOOTING.md)
- [Zasady bezpieczeństwa](SECURITY.md)
- [Historia zmian](CHANGELOG.md)

## Wymagania techniczne

Obraz bazuje na `debian:bookworm-slim` i zawiera Python 3 oraz FFmpeg/FFprobe. Kontener działa jako użytkownik systemowy o UID `1000`, dlatego katalogi podmontowane jako `/config` i `/recordings` muszą być dla niego zapisywalne.

## Licencja

Projekt jest udostępniany na licencji **MIT**. Zobacz plik [LICENSE](LICENSE).
