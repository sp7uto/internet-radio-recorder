# Internet Radio Recorder v2.2.2 — atomowa blokada serwisowa

## Najważniejsza zmiana

Nowy mechanizm `flock` koordynuje uruchamianie nagrań z automatyczną
aktualizacją kontenera Docker. Wspólny plik blokady:
`/config/.irr-maintenance.lock` (host: bind mount tego samego katalogu).

- Każdy worker IRR zakłada **blokadę współdzieloną** przed FFprobe i
  zachowuje ją podczas nagrywania FFmpeg aż do zamknięcia procesu.
- Aktualizator na VPS wymaga **blokady wyłącznej** przed odtworzeniem
  kontenera i utrzymuje ją do końca kontroli nowego obrazu/rollbacku.
- Aktywne nagranie lub trwający FFprobe powoduje odroczenie aktualizacji.
- W trakcie blokady wyłącznej nowy worker nie uruchomi FFprobe ani FFmpeg;
  po zwolnieniu blokady wróci do sprawdzania harmonogramu.
- Skrypt VPS sprawdza rzeczywistą zgodność katalogu `/config`, drugi
  raz sprawdza stan nagrywania oraz weryfikuje dostępność nowego modułu
  blokady po wdrożeniu.

## Testy i bezpieczeństwo

Dodano testy wykluczania blokad `flock` między procesami, kilku
jednoczesnych nagrań, reakcji workera na blokadę i zwalniania zasobu.
Błędy dostępu do pliku blokady **nie zezwalają na rozpoczęcie nagrania**.

**Nie jest to gwarancja ciągłego nagrywania przy wszystkich restartach.**
Jeśli audycja wypada dokładnie podczas krótkiego restartu, jej początek
może nie zostać zapisany. Mechanizm eliminuje wyścig w przyznawaniu blokad,
a nie zapewnia pracy dwóch równoległych rejestratorów.

**Etap przejściowy z v2.2.1:** dotychczasowy rejestrator nie uczestniczył
we współdzielonym `flock`. Przed pierwszym restartem chronią go nadal
dwie kontrole procesów FFmpeg i harmonogramu. Atomowe współdziałanie obu
stron rozpoczyna się dopiero po uruchomieniu obrazu v2.2.2.

## Zgodność

Bez zmian w formacie `stations.json`, portach, harmonogramie, interfejsie
i lokalizacjach `/config`, `/recordings`. Starych plików nagrań nie
migrujemy ani nie modyfikujemy. Skrypt aktualizatora na VPS powinien być
zainstalowany **przed** pierwszym wdrożeniem tego wydania.

Szczegóły: [Atomowa blokada serwisowa](docs/ATOMIC_MAINTENANCE.md)
i [Automatyczne aktualizacje VPS](docs/AUTOMATIC_UPDATES.md).
