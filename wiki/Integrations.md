# Integrations: Calendar and Notifications

## ICS calendar

You can subscribe to the IRR recording schedule from a calendar app using:

```text
http://server-address:8080/calendar.ics?token=YOUR_TOKEN
```

Set a long random `CALENDAR_TOKEN` in your environment. The token protects the ICS feed, **not the administration panel**.

**Calendar connectivity:** apps such as Google Calendar fetch external calendar URLs from their own servers; `localhost` and private LAN IP addresses generally cannot be reached from there. Do not solve this by publicly exposing the unprotected IRR interface. Prefer manual ICS import unless you have separately arranged an appropriately secured endpoint.

## Notifications

Optional integrations include **NTFY** and webhook endpoints. `NOTIFY_ON_COMPLETE=true` enables notifications when a recording completes successfully. Missing/empty output files can generate an error notification when an integration is configured.

Keep webhook URLs and any authentication tokens out of public documentation and screenshots.

References: [Installation and environment settings](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md), [Scheduling](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/SCHEDULING.md), [Security](https://github.com/sp7uto/internet-radio-recorder/blob/main/SECURITY.md).
