# Troubleshooting

[🇵🇱 Polski](../TROUBLESHOOTING.md) · **🇬🇧 English**

Begin with **History** and **Stream Status**, rather than deleting data or recreating containers.

## Cannot save `stations.json`

Verify write permissions for UID `1000` on the directory mounted as `/config`. The interface should display a specific error.

## Station is OFFLINE

1. Click **Test stream**.
2. Verify the *direct audio stream URL*, not merely the station's website.
3. Inspect the last error in **Stream Status**.
4. Check connectivity from the Docker host.

## Recording fails to stop

Versions before 2.1.9 had a critical FFmpeg stderr handling issue. Use a current release.

## Two neighbouring programmes enter the same file

Make sure you use at least 2.1.10, have enabled **one file per programme**, and created separate schedule entries.

## Interface looks unchanged after upgrade

Hard-refresh the browser (`Ctrl+F5`) and verify the actually running container image.

## ICS does not appear in Google Calendar

Google fetches subscribed calendars from its own servers. It cannot reach `localhost` or private LAN addresses. Use a properly secured public calendar endpoint or import an ICS file manually. Never expose the unprotected admin interface to make ICS work.

## No output despite an active schedule

Check `enabled`, `TZ`, write permissions for `/recordings`, History and `stop_reason`, container logs and stream-test results.

## MP3 output appears as empty AAC

Issue [#1](https://github.com/sp7uto/internet-radio-recorder/issues/1) was addressed in release 2.2.1. Use at least that version, inspect FFprobe/FFmpeg details and check History.

## Automated updater postpones deployment

A pending or active recording may cause a correct deferral. Review [Automatic updates](AUTOMATIC_UPDATES.md).

## When reporting a problem

Provide the version, reproducible steps, deployment type and relevant logs **after removing secrets**. [GitHub Issues](https://github.com/sp7uto/internet-radio-recorder/issues).
