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

## Stan publikacji obrazów GHCR (26.10.2026)

**Pierwsza publikacja obrazu v2.2.1 została wykonana automatycznie i zakończona sukcesem.** Pakiet jest publiczny: [GHCR Internet Radio Recorder](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder). Oba znaczniki są dostępne: `v2.2.1` i `stable`.

Publikacja istniejącej wersji została uruchomiona przez zmianę samego `.github/workflows/publish-docker.yml` na `main` ([PR #4](https://github.com/sp7uto/internet-radio-recorder/pull/4)); nie było wówczas konieczności tworzenia nowej wersji aplikacji. Rzeczywiste wydanie v2.2.2 zostało przygotowane później dla atomowej blokady serwisowej. Dla przyszłych nowych wydań `release.yml` wywołuje `publish-docker.yml` przez `workflow_call`. Możliwe jest także ręczne uruchomienie `workflow_dispatch`, ale workflow dopuszcza tylko najnowsze stabilne wydanie, aby nie cofnąć `:stable`.

**Ważne:** aktualizacje dokumentacji, instalatora lub workflow nie są nową wersją rejestratora i nie muszą tworzyć kolejnego obrazu aplikacji. Przy przyszłych zmianach kodu przed wydaniem stabilnym aktualizuj równolegle instrukcje, `CHANGELOG.md` i ewentualne testy aktualizatora. Po opublikowaniu sprawdź GitHub Release, status GHCR oraz test odczytu na środowisku docelowym.

## Dostęp

Workflow wymaga `contents: read` i `packages: write`. Pakiet GHCR musi być dostępny dla kontenera VPS (publicznie albo przez bezpieczny mechanizm `docker login`). Szczegóły wdrożenia: [AUTOMATIC_UPDATES.md](AUTOMATIC_UPDATES.md).
