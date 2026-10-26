#!/usr/bin/env bash
# IRR VPS updater installer. Preserves production Compose, data and recordings.
set -Eeuo pipefail
umask 077

ROOT="/srv/irr/app"
CONTAINER="Internet-Radio-Recorder"
SERVICE="radio-recorder"
IMAGE="ghcr.io/sp7uto/internet-radio-recorder:stable"
SOURCE_COMMIT="e9f84f7be3f4563644f646c5f393297fd6cbf9b2"
BASE="https://raw.githubusercontent.com/sp7uto/internet-radio-recorder/$SOURCE_COMMIT/deploy"

say() { printf '[IRR INSTALL] %s\n' "$*"; }
abort() { say "PRZERWANO: $*" >&2; exit 1; }
[[ "${EUID}" -eq 0 ]] || abort "Uruchom przez sudo"
for cmd in docker curl systemctl python3 install tar; do
  command -v "$cmd" >/dev/null || abort "Brakuje polecenia: $cmd"
done
docker compose version >/dev/null || abort "Wymagany Docker Compose v2"
[[ -f "$ROOT/docker-compose.yml" && -f "$ROOT/.env" ]] || abort "Brak produkcyjnego Compose lub .env"
[[ -d "$ROOT/config" && -d "$ROOT/recordings" ]] || abort "Brak katalogow danych produkcyjnych"
[[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" == true ]] || abort "Kontener produkcyjny nie dziala"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
curl -fsSL --retry 3 "$BASE/compose.ghcr.yaml" -o "$tmp/compose.ghcr.yaml"
curl -fsSL --retry 3 "$BASE/irr-update-guard.py" -o "$tmp/irr-update-guard.py"
curl -fsSL --retry 3 "$BASE/irr-docker-update" -o "$tmp/irr-docker-update"
curl -fsSL --retry 3 "$BASE/systemd/irr-docker-update.service" -o "$tmp/irr-docker-update.service"
curl -fsSL --retry 3 "$BASE/systemd/irr-docker-update.timer" -o "$tmp/irr-docker-update.timer"

bash -n "$tmp/irr-docker-update" || abort "Nieprawidlowy skrypt aktualizacji"
python3 -m py_compile "$tmp/irr-update-guard.py" || abort "Nieprawidlowy skrypt kontroli nagran"
[[ "$(grep -c -F "$IMAGE" "$tmp/compose.ghcr.yaml")" -eq 1 ]] || abort "Nieprawidlowy obraz w nakladce Compose"

files=(-f "$ROOT/docker-compose.yml")
[[ ! -f "$ROOT/compose.override.yaml" ]] || files+=(-f "$ROOT/compose.override.yaml")
files+=(-f "$tmp/compose.ghcr.yaml")
compose() { docker compose --project-directory "$ROOT" "${files[@]}" "$@"; }

say "Kontroluje Compose bez ingerencji w kontener"
images="$(compose config --images)" || abort "Nie mozna odczytac konfiguracji Compose"
[[ "$images" == "$IMAGE" ]] || abort "Konfiguracja wskazuje inne obrazy: $images"
expected_project="$(compose config --format json | python3 -c 'import json,sys; print(json.load(sys.stdin).get("name", ""))')" || abort "Brak nazwy projektu"
actual_project="$(docker inspect -f '{{index .Config.Labels "com.docker.compose.project"}}' "$CONTAINER")" || abort "Brak etykiety projektu"
actual_service="$(docker inspect -f '{{index .Config.Labels "com.docker.compose.service"}}' "$CONTAINER")" || abort "Brak etykiety uslugi"
[[ -n "$expected_project" && "$actual_project" == "$expected_project" && "$actual_service" == "$SERVICE" ]] ||
  abort "Compose nie zgadza sie z istniejacym kontenerem (projekt $actual_project/$expected_project, usluga $actual_service/$SERVICE)"

say "Pobieram gotowy obraz; nagrywanie pozostaje bez zmian"
docker pull "$IMAGE" || abort "Nie udalo sie pobrac obrazu z GHCR"

STAMP="$(date -u +%Y%m%d-%H%M%S)"
BACKUP="/var/backups/irr-updater/$STAMP"
mkdir -p "$BACKUP"
chmod 700 /var/backups/irr-updater "$BACKUP"
for target in \
  /etc/irr-updater/compose.ghcr.yaml \
  /usr/local/sbin/irr-update-guard.py \
  /usr/local/sbin/irr-docker-update \
  /etc/systemd/system/irr-docker-update.service \
  /etc/systemd/system/irr-docker-update.timer; do
  if [[ -e "$target" ]]; then
    cp -a "$target" "$BACKUP/$(basename "$target")"
  fi
done

install -D -m 0644 "$tmp/compose.ghcr.yaml" /etc/irr-updater/compose.ghcr.yaml
install -D -m 0755 "$tmp/irr-update-guard.py" /usr/local/sbin/irr-update-guard.py
install -D -m 0755 "$tmp/irr-docker-update" /usr/local/sbin/irr-docker-update
install -D -m 0644 "$tmp/irr-docker-update.service" /etc/systemd/system/irr-docker-update.service
install -D -m 0644 "$tmp/irr-docker-update.timer" /etc/systemd/system/irr-docker-update.timer
systemctl daemon-reload
systemctl enable --now irr-docker-update.timer

say "Timer zainstalowany; dzialajacy kontener NIE zostal zrestartowany"
say "Weryfikacja: systemctl list-timers irr-docker-update.timer"
say "Logi: journalctl -u irr-docker-update.service -n 100 --no-pager"
say "Awaryjne wylaczenie: systemctl disable --now irr-docker-update.timer"
say "Kopia zastapionych plikow (jesli byly): $BACKUP"
systemctl list-timers irr-docker-update.timer --no-pager
