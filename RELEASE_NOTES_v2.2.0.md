# Internet Radio Recorder v2.2.0 — Architecture Refresh

Wydanie 2.2.0 porządkuje fundamenty aplikacji bez zmiany jej przeznaczenia ani formatu konfiguracji.

## Najważniejsze zmiany

- Flask zastępuje ręczny serwer oparty na `BaseHTTPRequestHandler`.
- Waitress obsługuje wielowątkowy serwer HTTP/WSGI bez rozdzielania stanu workerów nagrywania.
- Endpointy API przeniesiono do `api.py`.
- Logikę scalania konfiguracji wydzielono do `schedules.py`.
- HTML, CSS i JavaScript są osobnymi plikami w `templates/` i `static/`.
- Naprawiono przełączanie widoków Dzisiaj, Kalendarz i Historia.
- Dodano pięć testów API, w tym test ochrony przed path traversal.

## Zgodność

- Bez zmian w formacie `stations.json`.
- Bez zmian portu `8080` i zmiennych środowiskowych.
- Bez zmian wolumenów `/config` oraz `/recordings`.
- Aktualizacja zachowuje dotychczasowe stacje, harmonogramy i nagrania.

## Aktualizacja na Synology

Zachowaj katalogi `/config` i `/recordings`, pobierz kod wydania i zbuduj nowy obraz:

```bash
docker build --no-cache -t internet-radio-recorder:2.2.0 .
```

Następnie ustaw obraz `internet-radio-recorder:2.2.0` w Portainerze i wykonaj redeploy.
