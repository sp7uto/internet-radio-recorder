# Publikacja na GitHubie

## Proponowane repozytorium

**Nazwa:** `internet-radio-recorder`

**Opis:**

> Self-hosted Internet radio recorder with weekly schedules, web UI, stream health monitoring, ICS calendar, merge import and Synology/Docker support.

**Tematy (topics):**

```text
internet-radio
radio-recorder
self-hosted
docker
ffmpeg
python
synology
nas
scheduler
```

## Przed pierwszą publikacją

1. Wybierz licencję projektu. Dla niewielkiego narzędzia self-hosted najczęściej rozważa się MIT, Apache-2.0 albo GPL-3.0.
2. Upewnij się, że repozytorium nie zawiera:
   - prawdziwego `stations.json`,
   - prywatnych URL-i strumieni,
   - tokenu `CALENDAR_TOKEN`,
   - `NTFY_URL` / `WEBHOOK_URL`,
   - nagrań.
3. Zostaw w repo tylko `config/stations.example.json` i `.env.example`.

`.gitignore` w tej paczce pomija pliki runtime i sekrety.

## Pierwszy commit

```bash
git init
git add .
git commit -m "Release v2.1.12"
git branch -M main
git remote add origin git@github.com:TWOJ_LOGIN/internet-radio-recorder.git
git push -u origin main
```

## Tag

```bash
git tag -a v2.1.12 -m "Internet Radio Recorder v2.1.12"
git push origin v2.1.12
```

## GitHub Release

**Tag:** `v2.1.12`

**Tytuł:**

```text
Internet Radio Recorder v2.1.12 — Station Order
```

Treść wydania można skopiować z `RELEASE_NOTES_v2.1.12.md`.

Jako asset warto dołączyć:

```text
internet-radio-recorder-v2.1.12.zip
```

## Branch protection

Po pierwszej publikacji warto włączyć ochronę `main` i wymagać przejścia workflow `CI` przed scaleniem pull requestów.

## GitHub Actions

Repo zawiera `.github/workflows/ci.yml`. Workflow uruchamia:

- kompilację kontrolną Pythona,
- testy jednostkowe,
- budowę obrazu Docker.

## Kolejne wydania

Przy każdej wersji:

1. zaktualizuj numer w interfejsie, User-Agent, Compose i dokumentacji,
2. dopisz zmiany do `CHANGELOG.md`,
3. uruchom testy,
4. utwórz tag `vX.Y.Z`,
5. opublikuj GitHub Release.
