# Pamięć i kopie zapasowe

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Storage-and-Backups)

## Dane trwałe

| Ścieżka w kontenerze | Zawartość |
| --- | --- |
| `/config` | Stacje, konfiguracja, historia, kopie |
| `/recordings` | Pliki audio |

Domyślny przykład Compose wykorzystuje katalogi `./config` i `./recordings`. Użytkownik o UID `1000` musi móc w nich zapisywać.

## Limity
Dla stacji można określić czas przechowywania i dopuszczalną pojemność. Postęp i zajętość sprawdzisz w **Bibliotece** i **Statystykach**.

## Kopia, scalanie i przywracanie

| Operacja | Wynik |
| --- | --- |
| Backup | Pobranie `stations.json` |
| Import / scal | Dołączenie niekolidujących stacji i audycji |
| Przywróć backup | **Zastąpienie całej konfiguracji** |

Przed importem IRR zapisuje kopię `stations.before-import-YYYYMMDD-HHMMSS.json`. Przed migracją zachowaj również `.env` oraz pliki Compose. Nagrania obejmij oddzielną kopią danych.

[Zasady importu](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/BACKUP_AND_MERGE.md)
