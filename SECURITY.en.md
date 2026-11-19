# Security

[🇵🇱 Polski](SECURITY.md) · **🇬🇧 English**

## Administration panel

Internet Radio Recorder does not implement built-in login or user management. Anyone who can access its HTTP panel may change stations and schedules, start or stop recordings, import configuration and delete library files.

**Never expose port 8080 directly to the public Internet.**

Recommended options:
- Tailscale, WireGuard or another VPN;
- HTTPS reverse proxy with an authentication layer;
- firewall rules limiting access to trusted hosts and networks.

## ICS calendar

Configure a strong random `CALENDAR_TOKEN`. Treat the full URL containing the token as secret. **The token protects only the ICS endpoint; it does not protect the administration panel or `/api/*`.**

## Webhooks

`NTFY_URL` and `WEBHOOK_URL` may embed credentials. Store them as environment secrets, and never publish them in the repository or public Compose examples.

## Reporting vulnerabilities

Do not post credentials, private streams, tokens or ready-to-use exploit material in public issues. Report the situation without secrets until a private disclosure channel has been agreed.

## Container images and upgrades

Deploy only verified images from a trusted GHCR repository. Publishing an image does not automatically enable the VPS updater. Verify GHCR permissions, Compose paths, backups and the next scheduled recording before enabling automated deployment. See [Automatic updates](docs/en/AUTOMATIC_UPDATES.md).
