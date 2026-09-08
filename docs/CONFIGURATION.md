# Konfiguracja

Główny plik to `/config/stations.json`:

```json
{
  "stations": [
    {
      "name": "Przykładowe Radio",
      "url": "https://example.invalid/live.mp3",
      "codec": "mp3",
      "detected_ext": "mp3",
      "segment_minutes": 60,
      "retention_days": 90,
      "max_storage_gb": 20,
      "one_file_per_program": true,
      "enabled": true,
      "schedule": {
        "mon": [],
        "tue": [],
        "wed": [],
        "thu": [],
        "fri": [],
        "sat": [],
        "sun": []
      }
    }
  ]
}
```

Najwygodniej zarządzać konfiguracją z panelu WWW.

## Pola stacji

- `name` — unikalna nazwa stacji,
- `url` — bezpośredni URL strumienia,
- `codec` / `detected_ext` — format pliku; panel może wykryć go przez Test streamu,
- `segment_minutes` — długość segmentu, gdy nie używasz trybu 1 plik / audycję,
- `retention_days` — automatyczne usuwanie starszych nagrań; `0` = nigdy,
- `max_storage_gb` — maksymalne miejsce dla stacji; `0` = bez limitu,
- `one_file_per_program` — osobny plik dla wpisu harmonogramu,
- `enabled` — aktywność stacji,
- `schedule` — tygodniowy harmonogram.

## Zapis konfiguracji

Zapis jest atomowy. Przed podmianą `stations.json` poprzednia wersja jest kopiowana do `stations.json.bak`, a po zapisie plik jest ponownie odczytywany kontrolnie.

## Kolejność stacji

W 2.1.12 kolejność elementów tablicy `stations` jest równocześnie kolejnością kart w panelu. Można ją zmieniać przez `☰`, `↑` i `↓`, a następnie zapisać przyciskiem `ZAPISZ ZMIANY`.
