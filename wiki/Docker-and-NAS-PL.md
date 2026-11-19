# Docker i NAS

**🇵🇱 Polski** · [🇬🇧 English](https://github.com/sp7uto/internet-radio-recorder/wiki/Docker-and-NAS)

IRR może pracować na hoście Linux, VPS albo zgodnym NAS z Dockerem.

| Środowisko | Punkt wyjścia |
| --- | --- |
| Linux / VPS | [Pierwsze kroki](https://github.com/sp7uto/internet-radio-recorder/wiki/Getting-Started-PL) oraz [Compose](https://github.com/sp7uto/internet-radio-recorder/blob/main/docker-compose.yml) |
| Synology / Portainer | [Przykładowy stack](https://github.com/sp7uto/internet-radio-recorder/blob/main/docker-compose-portainer.yml) |
| QNAP / Container Station | [Compose](https://github.com/sp7uto/internet-radio-recorder/blob/main/docker-compose.yml) po dostosowaniu wolumenów i portów |

Plik Portainera to **wzorzec**, a nie gotowa konfiguracja produkcyjna. Nie uruchamiaj równolegle drugiego rejestratora na tych samych harmonogramach bez wyraźnego zamiaru.

## Kontrola przed uruchomieniem
- Podmontuj trwałe katalogi jako `/config` i `/recordings`.
- Sprawdź zapis dla UID `1000`.
- Wystawiaj panel wyłącznie w zaufanej sieci lub przez VPN.
- Zabezpiecz istniejące ustawienia przed odtworzeniem kontenera.

[Obrazy GHCR](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder) · [Instalacja](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md)

**Uwaga:** automatyczny aktualizator referencyjnego VPS nie jest instalowany przez zwykłe Docker Compose.
