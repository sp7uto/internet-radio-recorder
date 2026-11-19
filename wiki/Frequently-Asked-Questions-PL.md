# Najczęstsze pytania

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Frequently-Asked-Questions)

## Czy IRR jest darmowy?
Tak. Kod jest udostępniany na licencji MIT; nagrania pozostają na wskazanej przez Ciebie pamięci.

## Na czym można go uruchomić?
Na zgodnym hoście Docker Compose: Linux, VPS lub serwerze NAS.

## Czy nagrywa wiele stacji?
Tak. Można ustawić wiele stacji i audycji. Praktyczny limit jednoczesnych nagrań zależy od zasobów hosta i przepustowości.

## Czy koduje nagrania ponownie?
Dla obsługiwanych źródeł MP3/AAC stosuje FFprobe i kopiowanie strumienia przez FFmpeg bez transkodowania.

## Czy działa harmonogram tygodniowy i nagrania przez północ?
Tak, również z marginesami `pre` i `post` oraz osobnym plikiem na audycję.

## Gdzie zapisywane są pliki?
W trwałym wolumenie `/recordings`, a konfiguracja i stan w `/config`.

## Czy można scalić konfiguracje?
Tak. Dostępne są backup, import/scal i przywrócenie pełnej kopii. Przywracanie zastępuje obecną konfigurację.

## Czy wolno wystawić IRR w Internecie?
Nie bez zabezpieczenia: panel nie ma własnego logowania. Korzystaj z VPN albo reverse proxy HTTPS z uwierzytelnianiem.

## Czy działa kalendarz ICS?
Tak, z tokenem `CALENDAR_TOKEN`; ten token nie zastępuje logowania do panelu.

## Czy automatyczne aktualizacje są domyślne?
Nie. Aktualizator referencyjnego VPS jest opcjonalny i nie instaluje się ze zwykłym Compose.

## Gdzie zgłosić pomysł biblioteki polskich stacji?
W [GitHub Issues](https://github.com/sp7uto/internet-radio-recorder/issues). Katalog polskich strumieni jest propozycją rozszerzenia, a nie funkcją już udostępnioną.

[Strona główna](https://github.com/sp7uto/internet-radio-recorder/wiki/Home-PL) · [Dokumentacja](https://github.com/sp7uto/internet-radio-recorder/tree/main/docs)
