# Publikowanie wydań na GitHubie

Repozytorium: [sp7uto/internet-radio-recorder](https://github.com/sp7uto/internet-radio-recorder); gałąź produkcyjna: `main`.

## Zasady

- Kod i dokumentację rozwijaj na osobnej gałęzi, testy uruchamiaj w PR.
- Nie publikuj `.env`, produkcyjnego `stations.json`, tokenów, prywatnych adresów ani nagrań.
- Zmiany przygotowuj wraz z dokumentacją; zapis `VERSION` jest źródłem numeru wydania.
- `.github/workflows/ci.yml` sprawdza składnię, testy Python i budowę obrazu Docker.
- `.github/workflows/release.yml` publikuje archiwa i SHA256 dla nowego numeru wersji.
- Ten sam workflow po utworzeniu nowego wydania wywołuje `publish-docker.yml` w celu opublikowania obrazu GHCR.

## Nowe wydanie

1. Zaktualizuj `VERSION`, znaczniki obrazu w plikach Compose i wszelkie wyświetlane numery wersji.
2. Dodaj opis do `CHANGELOG.md` oraz `RELEASE_NOTES_vX.Y.Z.md`.
3. Otwórz PR; sprawdź CI i przetestuj migrację na kopii konfiguracji.
4. Scal do `main` dopiero po akceptacji.
5. Sprawdź GitHub Release, archiwa, sumy kontrolne i GHCR.
6. Dopiero po weryfikacji pakietu dopuść jego wdrożenie na serwerze.

## Pierwszy obraz dla istniejącego wydania

Istniejące wydanie `v2.2.1` utworzono zanim uruchomiono publikowanie GHCR. Po zatwierdzeniu nowego workflow obraz dla tej wersji można opublikować ręcznie przez GitHub Actions **Publish Docker image → Run workflow** z wejściem `release_tag=v2.2.1`. Ręczne uruchamianie dla starszych tagów może cofnąć wskazanie `:stable`; używaj wyłącznie najnowszego stabilnego wydania.

## Dostęp

Workflow wymaga `contents: read` i `packages: write`. Pakiet GHCR musi być dostępny dla kontenera VPS (publicznie albo przez bezpieczny mechanizm `docker login`). Szczegóły wdrożenia: [AUTOMATIC_UPDATES.md](AUTOMATIC_UPDATES.md).
