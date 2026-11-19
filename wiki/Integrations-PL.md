# Integracje: kalendarz i powiadomienia

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Integrations)

## Kalendarz ICS
Subskrypcja harmonogramu:

```text
http://adres-serwera:8080/calendar.ics?token=TWOJ_TOKEN
```

Nadaj długą losową wartość `CALENDAR_TOKEN`. Token chroni **tylko kalendarz ICS**, nie panel administracyjny.

Zewnętrzne serwisy kalendarzowe, np. Google Calendar, pobierają dane ze swoich serwerów i zwykle nie mają dostępu do `localhost` ani do prywatnych adresów LAN. Nie rozwiązuj tego przez publiczne wystawienie niechronionego panelu; alternatywą jest ręczny import ICS lub odrębnie zabezpieczony punkt dostępu.

## Powiadomienia
IRR może korzystać z NTFY i webhooków. `NOTIFY_ON_COMPLETE=true` włącza komunikaty po udanym nagraniu. Gdy skonfigurowano odbiorcę, brakujący lub pusty plik może wywołać alarm.

Nie publikuj adresów zawierających tokeny ani danych dostępowych.

[Instalacja i zmienne](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md)
