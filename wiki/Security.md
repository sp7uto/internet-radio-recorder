# Security

> [!CAUTION]
> **The IRR administration panel has no built-in authentication.** Do **not** expose its HTTP port 8080 directly to the public Internet.

Anybody who can access the admin UI may be able to modify stations, start/stop recordings, or delete files from the library.

## Safer access patterns

- Keep IRR on a **trusted LAN**.
- For remote access, use **Tailscale** or another VPN.
- Alternatively, use a reverse proxy providing **HTTPS and authentication**.
- Limit firewall access to the network or authenticated users who actually need control of recordings.

## Calendar and notifications

Use a long random `CALENDAR_TOKEN`; treat the full ICS URL including the token as a secret. **The ICS token is not a password for the web panel or the API.**

Keep webhook secrets, NTFY tokens and credentials out of issue reports, screenshots and any public Wiki pages.

## Before publishing diagnostics

Remove actual private stream URLs (where relevant), credentials, access tokens, addresses you do not wish to publish, and unrelated personal data.

Read the full [SECURITY.md](https://github.com/sp7uto/internet-radio-recorder/blob/main/SECURITY.md) and use the project's designated reporting method for security issues.
