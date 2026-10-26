# Internet Radio Recorder v2.2.3 — poprawka opisu wolumenu

## Zmieniono

- Etykieta zajętości dysku nie sugeruje już konkretnej platformy NAS:
  **„Zajętość wolumenu Synology” → „Zajętość wolumenu”**.
- Napis zmieniono w obu kopiach interfejsu (`templates/index.html` oraz `web.py`) w [PR #17](https://github.com/sp7uto/internet-radio-recorder/pull/17).

## Zgodność

Jest to kosmetyczne wydanie serwisowe, bez zmian w obsłudze strumieni, nagrań MP3/AAC, FFmpeg, harmonogramach, API, formacie `stations.json`, portach oraz wolumenach `/config` i `/recordings`.

Mechanizm atomowej blokady serwisowej (`flock-v1`) z v2.2.2 pozostaje bez zmian.

## Aktualizacja

Publiczne obrazy są publikowane automatycznie w GHCR pod tagami `v2.2.3` i `stable`. Na referencyjnym VPS aktualizator może wdrożyć nowy obraz po wykryciu wydania i sprawdzeniu bezpiecznego okna. Sama publikacja **nie potwierdza wdrożenia na VPS**.

- [Zasady bezpiecznych aktualizacji](docs/AUTOMATIC_UPDATES.md)
- [Informacje o v2.2.2](RELEASE_NOTES_v2.2.2.md)
