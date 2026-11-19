# Stacje i nagrywanie

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Stations-and-Recording)

## Dodawanie stacji
W zakładce **Stacje** wpisz nazwę oraz **bezpośredni adres strumienia audio**. Strona internetowa rozgłośni nie musi być prawidłowym adresem strumienia. Użyj **Test strumienia**, aby sprawdzić połączenie, kodek i bitrate.

Kolejność stacji zmienisz przez przeciąganie lub przyciski strzałek; zachowaj ustawienia przyciskiem zapisu.

## Rozpoznawanie formatu
Przed nagraniem IRR używa **FFprobe**, aby ustalić właściwości strumienia. Obsługiwane MP3/AAC zapisuje za pośrednictwem FFmpeg bez ponownego kodowania. Nie polega wyłącznie na dawnych polach `codec` i `detected_ext` w konfiguracji. Brak pliku lub pusty plik są zgłaszane jako błędy.

## Gdzie szukać informacji

| Widok | Przeznaczenie |
| --- | --- |
| REC / STOP | Ręczne rozpoczęcie i zatrzymanie nagrywania |
| Dzisiaj | Plan i bieżąca aktywność |
| Historia | Zakończone zadania i błędy |
| Stan strumieni | Diagnostyka adresów źródłowych |
| Biblioteka nagrań | Przegląd zapisanych plików |
| Statystyki | Zestawienia i zajętość pamięci |

Konfigurację stacji przechowuje zwykle `/config/stations.json`; zabezpieczaj ją przed masowymi zmianami.

[Konfiguracja](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/CONFIGURATION.md) · [Problemy](https://github.com/sp7uto/internet-radio-recorder/wiki/Troubleshooting-PL)
