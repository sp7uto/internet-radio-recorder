# Internet Radio Recorder v2.1.12 — Station Order

Wydanie 2.1.12 skupia się na wygodniejszym zarządzaniu większą liczbą stacji.

## Najważniejsza nowość

Stacje w panelu można teraz ustawiać w dowolnej kolejności:

- przeciągając kartę za uchwyt `☰`,
- albo używając przycisków `↑` i `↓`.

Zmiana nie narusza konfiguracji stacji ani harmonogramu. Po kliknięciu `ZAPISZ ZMIANY` kolejność trafia do `stations.json` i pozostaje taka sama po restarcie kontenera.

## W pakiecie są również funkcje 2.1.9–2.1.11

- poprawne kończenie nagrania o zadanej porze,
- osobny plik dla sąsiednich audycji tej samej stacji,
- prawidłowa obsługa `pre/post` i przejścia przez północ,
- bezpieczny **Import / scal** zachowujący istniejące stacje i harmonogramy,
- datowana kopia konfiguracji przed importem.

## Aktualizacja z 2.1.11

1. Zachowaj swój `/config/stations.json`.
2. Podmień pliki aplikacji na wersję 2.1.12.
3. Zbuduj obraz:

```bash
docker build --no-cache -t internet-radio-recorder:2.1.12 .
```

4. Zmień obraz kontenera na `internet-radio-recorder:2.1.12` i wykonaj redeploy.
5. W przeglądarce wykonaj pełne odświeżenie (`Ctrl+F5`).

Format `stations.json` nie zmienił się.

## Uwaga bezpieczeństwa

Panel administracyjny nie ma własnego logowania. Nie wystawiaj go bezpośrednio do Internetu; stosuj VPN/Tailscale lub reverse proxy z uwierzytelnieniem i HTTPS.
