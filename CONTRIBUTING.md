# Contributing

Zmiany są mile widziane w postaci małych, czytelnych pull requestów.

Przed wysłaniem PR:

```bash
python3 -m compileall -q recorder.py web.py tests
python3 -m unittest discover -s tests -v
```

Prośba o zachowanie kompatybilności formatu `stations.json` powinna być traktowana jako ważne kryterium zmian. Jeżeli modyfikacja wymaga migracji konfiguracji, opisz ją wyraźnie w PR i `CHANGELOG.md`.

W kodzie harmonogramu szczególnie ważne są testy granic czasu: `pre/post`, sąsiednie audycje oraz przejście przez północ.
