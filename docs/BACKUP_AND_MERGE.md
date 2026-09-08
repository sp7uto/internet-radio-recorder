# Backup, Import / scal i Przywróć backup

## Backup

Przycisk **Backup** pobiera JSON w formacie:

```json
{
  "stations": [ ... ]
}
```

## Import / scal

To bezpieczny domyślny tryb importu.

1. Obecne stacje pozostają na miejscu.
2. Nowa stacja jest dopisywana w całości na końcu listy.
3. Stacja o tej samej nazwie (bez rozróżniania wielkości liter) zachowuje swoje obecne ustawienia.
4. Z importowanego pliku dopisywane są jej nowe, niekolidujące wpisy harmonogramu.
5. Dokładny duplikat `start + end + title` jest pomijany.
6. Wpis nakładający się nominalnym czasem z istniejącym wpisem tego samego dnia jest pomijany.

Po operacji panel podaje liczbę nowych stacji, nowych zadań, pominiętych duplikatów i konfliktów.

## Przywróć backup

Ten tryb **zastępuje całą konfigurację** zawartością pliku. Używaj go świadomie.

## Automatyczna kopia

Przed obydwoma rodzajami importu aktualny plik jest kopiowany do:

```text
/config/stations.before-import-YYYYMMDD-HHMMSS.json
```

Zwykły zapis z panelu tworzy dodatkowo `stations.json.bak`.
