# Contributing

[🇵🇱 Polski](CONTRIBUTING.md) · **🇬🇧 English**

Small, focused, readable pull requests are welcome.

Before submitting a PR, run:

```bash
python3 -m compileall -q recorder.py api.py schedules.py tests
python3 -m unittest discover -s tests -v
```

Preserving backwards compatibility of `stations.json` is an important change criterion. If a modification needs configuration migration, describe it clearly in the PR and `CHANGELOG.md`.

For scheduling code, tests of boundary conditions are particularly important: `pre/post` margins, adjacent programmes and midnight-crossing schedules.

Documentation changes should keep both Polish and English versions in sync, including wiki pages, README and technical references.
