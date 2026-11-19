# Publishing releases on GitHub

[🇵🇱 Polski](../GITHUB_PUBLISHING.md) · **🇬🇧 English**

Repository: [sp7uto/internet-radio-recorder](https://github.com/sp7uto/internet-radio-recorder). Production branch: `main`.

## Rules

- Develop code and documentation on a separate branch, run checks in a pull request.
- Never commit `.env`, production `stations.json`, tokens, private addresses or recordings.
- Update documentation together with the changes; `VERSION` is the version-number source.
- `.github/workflows/ci.yml` runs Python syntax/tests and Docker build checks.
- `.github/workflows/release.yml` publishes release archives and SHA256 checksums.
- The release workflow triggers `publish-docker.yml` to publish the GHCR image.

## Releasing

1. Update `VERSION`, relevant Compose image tags and displayed version strings.
2. Update `CHANGELOG.md` and release notes.
3. Open a pull request; check CI and test a configuration migration on backup data.
4. Merge into `main` after review.
5. Verify release archives, hashes and GHCR package tags.
6. Allow production deployment only after image verification.

## Distribution

Versioned images and `stable` tags are published to [GHCR](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder). Automatic updates on `irr-vps` are a **separately configured environment-specific service**, not a consequence of publishing a release.

Historical publishing details, exact earlier workflows and incident records are retained in the [Polish reference](../GITHUB_PUBLISHING.md).
