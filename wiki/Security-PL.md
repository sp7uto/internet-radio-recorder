# Bezpieczeństwo

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Security)

> [!CAUTION]
> **Panel IRR nie ma wbudowanego uwierzytelniania.** Nigdy nie udostępniaj portu 8080 bezpośrednio w Internecie.

Każdy, kto otrzyma dostęp do panelu, może zmieniać harmonogram, uruchamiać lub kończyć nagrania i usuwać pliki.

## Bezpieczny dostęp
- Zaufana sieć lokalna.
- Tailscale lub inny VPN dla zdalnych administratorów.
- Reverse proxy z HTTPS **i uwierzytelnianiem**.
- Reguły zapory ograniczające dostęp tylko do uprawnionych hostów.

## Sekrety
`CALENDAR_TOKEN` zabezpiecza adres subskrypcji ICS, **nie zabezpiecza panelu ani API**. Chroń też dane dostępowe NTFY i webhooków oraz pliki `.env`.

Przed publikacją zgłoszenia usuń poufne adresy strumieni, tokeny, dane osobowe i hasła.

[Pełna polityka bezpieczeństwa](https://github.com/sp7uto/internet-radio-recorder/blob/main/SECURITY.md)
