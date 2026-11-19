# Frequently Asked Questions

## Is IRR free and self-hosted?
Yes. IRR is distributed under the MIT license. Its files and configuration can remain on storage that you control.

## Which platforms can host IRR?
IRR is designed for Docker Compose deployments on a Linux server, NAS or VPS. A Synology/Portainer example is included in the repository. Check filesystem permissions before starting.

## Can IRR record more than one station?
Yes. It supports multiple station definitions and programmes. The number of simultaneous streams your host can reliably handle depends on its resources and available bandwidth.

## Does IRR re-encode every recording?
No. IRR uses FFprobe to inspect audio metadata and uses FFmpeg stream copy for supported MP3/AAC recording paths, avoiding unnecessary transcoding.

## Can I schedule the same programme every week?
Yes. Weekly schedules support titled programmes and optional margins before and after the scheduled broadcast.

## What happens when a programme crosses midnight?
IRR supports overnight schedules. Consult [Scheduling](https://github.com/sp7uto/internet-radio-recorder/wiki/Scheduling) for edge cases and adjacent programmes.

## Where do the audio files go?
Recordings use a persistent host-mounted directory; the default repository Compose workflow uses `./recordings`. Configuration is stored separately in `./config`.

## Can I back up or merge station configurations?
Yes. The web interface supports a configuration download, import/merge and full restore. Restore replaces the configuration, while merge is designed to preserve existing non-conflicting entries. Read [Storage and Backups](https://github.com/sp7uto/internet-radio-recorder/wiki/Storage-and-Backups).

## Can I access IRR from the Internet?
Do not expose its unprotected administration port publicly. The panel has no built-in login. Use a trusted LAN, VPN or an authenticated reverse proxy over HTTPS.

## Can I subscribe to the schedule from a calendar?
Yes. IRR exposes an ICS feed protected by the configured `CALENDAR_TOKEN`. Treat the token-bearing URL as a secret.

## Do automatic Docker updates come enabled?
No. The reference VPS includes a separately documented guarded updater. An ordinary Docker Compose installation does not install that timer.

## What should I inspect when a recording fails?
Begin with Stream Status, programme timing, History, filesystem permissions and available capacity. Then follow [Troubleshooting](https://github.com/sp7uto/internet-radio-recorder/wiki/Troubleshooting).

## Where can I suggest a new station directory or feature?
Use [GitHub Issues](https://github.com/sp7uto/internet-radio-recorder/issues) to propose it. A curated Polish radio stream catalogue is a possible enhancement, not a feature documented here as already released.

---

[Home](https://github.com/sp7uto/internet-radio-recorder/wiki) · [Reference docs](https://github.com/sp7uto/internet-radio-recorder/tree/main/docs) · [Issues](https://github.com/sp7uto/internet-radio-recorder/issues)
