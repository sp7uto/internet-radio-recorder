# Rozwiązywanie problemów

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Troubleshooting)

Najpierw zajrzyj do **Historii** i **Stanu strumieni**. Nie usuwaj danych ani nie odtwarzaj kontenera bez ustalenia przyczyny.

| Objaw | Pierwsza kontrola |
| --- | --- |
| Nie zapisuje stacji | Czy UID `1000` może zapisywać w `/config`? |
| Stacja nie nadaje | Sprawdź bezpośredni URL i wykonaj **Test strumienia** |
| Brak pliku | Włączona stacja, plan, Historia, prawa `/recordings` |
| Puste pliki MP3/AAC | Sprawdź wersję co najmniej 2.2.1 oraz diagnostykę FFprobe/FFmpeg |
| Nieoczekiwany czas nagrania | Strefa `TZ`, marginesy, sąsiednie audycje i przejście przez północ |
| ICS niedostępny z zewnątrz | Usługa kalendarzowa nie widzi prywatnego adresu LAN |
| Dawny panel po aktualizacji | Obraz faktycznie uruchomiony oraz pamięć podręczna przeglądarki |
| Aktualizator odkłada wdrożenie | Zbliżająca się lub trwająca audycja może uzasadniać opóźnienie |

Przed zgłoszeniem błędu usuń tokeny, hasła i prywatne adresy z logów.

[Pełny poradnik diagnostyczny](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/TROUBLESHOOTING.md) · [Zgłoszenia](https://github.com/sp7uto/internet-radio-recorder/issues)
