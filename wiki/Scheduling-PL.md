# Harmonogram

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Scheduling)

Każda stacja może mieć wiele audycji w tygodniowym planie. Dostępne są marginesy nagrywania i audycje przechodzące przez północ.

## Przykładowy wpis

```json
{
  "start": "20:00",
  "end": "21:00",
  "title": "Nazwa audycji",
  "pre": 2,
  "post": 3
}
```

- `start` oraz `end`: godziny nominalne.
- `title`: nazwa audycji.
- `pre`: minuty przed rozpoczęciem.
- `post`: minuty po zakończeniu.

## Audycje sąsiadujące
Przy opcji **1 plik na audycję** początek następnego programu ma pierwszeństwo przed zachodzącym na niego marginesem poprzedniego nagrania.

## Przejście przez północ
Przykładowo 22:30–01:00 oznacza nagranie kończące się następnego dnia. Obsługiwane są również marginesy.

## Kontrola
Sprawdź strefę czasową, właściwy dzień, widok **Dzisiaj**, a po emisji — **Historię**. Test strumienia nie gwarantuje jego dostępności w przyszłości.

[Szczegółowe reguły harmonogramu](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/SCHEDULING.md)
