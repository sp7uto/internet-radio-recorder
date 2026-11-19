# Pierwsze kroki

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Getting-Started)

## Wymagania
Docker z Compose v2, dostęp do Internetu, poprawny adres strumienia radiowego oraz katalogi z możliwością zapisu nagrań i konfiguracji.

## Instalacja na hoście Docker

```bash
git clone https://github.com/sp7uto/internet-radio-recorder.git
cd internet-radio-recorder
cp .env.example .env
cp config/stations.example.json config/stations.json
```

W pliku `.env` zastąp przykładową wartość `CALENDAR_TOKEN` długim losowym tokenem. Następnie uruchom:

```bash
docker compose up -d --build
```

Panel: `http://adres-serwera:8080` w zaufanej sieci.

**Trwałe katalogi:** `./config` na konfigurację i `./recordings` na pliki audio. Proces w kontenerze używa UID `1000`; oba katalogi muszą być dla niego zapisywalne.

## Pierwsze nagranie
1. Otwórz **Stacje** i dodaj nazwę oraz bezpośredni URL strumienia.
2. Wykonaj **Test strumienia** i sprawdź kodek oraz bitrate.
3. Dodaj wpis harmonogramu i sprawdź zakładki **Kalendarz** oraz **Dzisiaj**.
4. Po nagraniu sprawdź **Historię** i **Bibliotekę**.

> [!WARNING]
> Brak uwierzytelniania w panelu. Nigdy nie publikuj portu 8080 bezpośrednio w Internecie.

[Instalacja — szczegóły](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md) · [Bezpieczeństwo](https://github.com/sp7uto/internet-radio-recorder/wiki/Security-PL)
