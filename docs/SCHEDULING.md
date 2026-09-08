# Harmonogram i podział audycji

## Wpis harmonogramu

```json
{
  "start": "20:00",
  "end": "21:00",
  "title": "Biblioteka Dźwięków Ważnych",
  "pre": 2,
  "post": 3
}
```

- `start` / `end` — nominalne godziny audycji,
- `title` — nazwa używana w panelu i nazwie pliku,
- `pre` — minuty nagrania przed startem,
- `post` — minuty po zakończeniu.

## Sąsiednie audycje

Przykład:

```text
20:00–21:00  Audycja A
21:00–23:00  Audycja B
```

Jeżeli obie mają `pre/post`, ich rozszerzone okna mogą się nakładać. Od wersji 2.1.10 nominalny czas programu ma pierwszeństwo: dokładnie o `21:00` aktywna staje się Audycja B.

Przy `one_file_per_program: true` rejestrator zatrzymuje plik A z powodem `program_change` i natychmiast rozpoczyna plik B, bez zwykłego opóźnienia reconnectu.

## Audycje przez północ

Jeżeli `end <= start`, program traktuje wpis jako kończący się następnego dnia, np.:

```text
22:30–01:00
```

Obsługiwane są również marginesy `pre/post` wokół takich audycji.

## Tryb segmentów

Gdy `one_file_per_program` jest wyłączone, FFmpeg dzieli nagranie na segmenty długości `segment_minutes`, z wyrównaniem do czasu zegarowego.

## Nagrywanie ręczne

`REC` ustawia tryb ręczny dla stacji. Nagranie trwa niezależnie od harmonogramu aż do naciśnięcia `STOP` lub wyłączenia/usunięcia stacji.
