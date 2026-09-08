# API i endpointy

API jest wewnętrznym interfejsem panelu WWW. W 2.1.12 nie ma mechanizmu logowania — patrz `SECURITY.md`.

## Odczyt

| Endpoint | Opis |
|---|---|
| `GET /api/data` | konfiguracja stacji i bieżący stan workerów |
| `GET /api/health` | diagnostyka strumieni |
| `GET /api/executions` | historia wykonań |
| `GET /api/overview` | statystyki globalne i zajętość |
| `GET /api/library` | lista nagrań |
| `GET /api/stats` | statystyki per stacja |
| `GET /api/backup` | pobranie backupu konfiguracji |
| `GET /calendar.ics?token=...` | subskrybowalny kalendarz ICS |
| `GET /media?path=...` | odsłuch pliku; parametr `download=1` wymusza pobranie |

## Zapis / akcje

| Endpoint | Opis |
|---|---|
| `POST /api/save` | zapis listy stacji |
| `POST /api/test` | test URL strumienia przez FFprobe |
| `POST /api/start?name=...` | ręczne REC |
| `POST /api/stop?name=...` | ręczne STOP |
| `POST /api/delete?path=...` | usunięcie nagrania |
| `POST /api/import-backup?mode=merge` | Import / scal |
| `POST /api/import-backup?mode=replace` | pełne przywrócenie backupu |

API nie jest obecnie wersjonowane i może się zmieniać pomiędzy wydaniami.
