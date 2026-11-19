# Aktualizacje i odzyskiwanie

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Updates-and-Recovery)

## Standardowy Docker Compose
1. Zabezpiecz `.env`, Compose oraz `/config`.
2. Sprawdź, czy nie trwa nagranie i czy najbliższa audycja nie rozpocznie się podczas aktualizacji.
3. Pobierz przeznaczone do wdrożenia wydanie lub obraz.
4. Odtwórz kontener zgodnie z użytym sposobem instalacji.
5. Sprawdź panel, stacje, harmonogram i pierwsze nagrania.

Nie nadpisuj produkcyjnego `stations.json` przykładową konfiguracją.

## Opcjonalny aktualizator VPS
Referencyjny VPS ma osobny mechanizm systemd: sprawdzanie harmonogramu i aktywności FFmpeg, odraczanie aktualizacji w niebezpiecznym momencie oraz zachowanie obrazu do wycofania zmian. Od v2.2.2 recorder i aktualizator koordynują pracę poprzez wspólną blokadę `flock`.

**Nie uruchamiaj `deploy/install-vps.sh` na innym NAS lub serwerze bez dostosowania.** Blokada zapobiega wyścigowi podczas rozpoczynania nagrania, lecz nie obiecuje bezstratnej rejestracji podczas restartu.

[Automatyczne aktualizacje](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/AUTOMATIC_UPDATES.md) · [Blokada serwisowa](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/ATOMIC_MAINTENANCE.md)
