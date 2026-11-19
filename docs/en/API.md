# API and endpoints

[🇵🇱 Polski](../API.md) · **🇬🇧 English**

The API is used internally by the IRR web panel. Since 2.2.0, Flask handles routes and Waitress serves the application. **There is no built-in login or authentication for the administration API.** Do not expose it publicly.

## Read endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /api/data` | Stations configuration and current worker status |
| `GET /api/health` | Stream health diagnostics |
| `GET /api/executions` | Execution history |
| `GET /api/overview` | Global overview and disk usage |
| `GET /api/library` | Recordings list |
| `GET /api/stats` | Per-station statistics |
| `GET /api/backup` | Configuration backup download |
| `GET /calendar.ics?token=...` | ICS calendar subscription |
| `GET /media?path=...` | Playback; `download=1` requests download |

## Write and action endpoints

| Endpoint | Purpose |
| --- | --- |
| `POST /api/save` | Save stations |
| `POST /api/test` | Check a stream with FFprobe |
| `POST /api/start?name=...` | Manual REC |
| `POST /api/stop?name=...` | Manual STOP |
| `POST /api/delete?path=...` | Delete a recording |
| `POST /api/import-backup?mode=merge` | Merge imported configuration |
| `POST /api/import-backup?mode=replace` | Replace all configuration from backup |

The API is not currently versioned; endpoints may change between releases.

[Security](../../SECURITY.en.md)
