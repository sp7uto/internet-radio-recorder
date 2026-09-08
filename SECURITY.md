# Security

## Panel WWW

Internet Radio Recorder 2.1.12 nie implementuje własnego logowania ani zarządzania użytkownikami. Każda osoba mająca dostęp do portu WWW może m.in. zmieniać stacje i harmonogram, uruchamiać nagrania, importować konfigurację oraz usuwać pliki z biblioteki.

**Nie wystawiaj portu 8080 bezpośrednio do publicznego Internetu.**

Zalecane rozwiązania:

- dostęp przez Tailscale/WireGuard/VPN,
- reverse proxy z HTTPS i warstwą uwierzytelnienia,
- reguły firewall ograniczające dostęp do zaufanych sieci/hostów.

## Kalendarz ICS

Ustaw długi, losowy `CALENDAR_TOKEN`. Traktuj pełny URL z tokenem jak sekret. Sam token chroni endpoint ICS, ale **nie chroni panelu administracyjnego ani `/api/*`**.

## Webhooki

`NTFY_URL` i `WEBHOOK_URL` mogą zawierać dane dostępowe. Przechowuj je w zmiennych środowiskowych, nie publikuj w repozytorium i nie zapisuj w publicznych plikach Compose.

## Zgłaszanie problemów

Jeżeli odkryjesz podatność, nie publikuj danych dostępowych, prywatnych adresów strumieni ani tokenów w publicznym issue. Do czasu ustalenia kanału prywatnych zgłoszeń najlepiej opisać problem bez sekretów i bez gotowego exploita.
