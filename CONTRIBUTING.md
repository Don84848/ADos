# Contributing to ADos

Thank you for your interest in contributing to ADos — the open-source mobile security OS builder!

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ADos.git`
3. Create a feature branch: `git checkout -b feat/my-feature`
4. Make your changes following the guidelines below
5. Run tests: `python -m unittest discover -s tests`
6. Commit: `git commit -m "feat(scope): description"`
7. Push: `git push origin feat/my-feature`
8. Open a Pull Request against `main`

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use for |
|--------|---------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation only |
| `chore` | Build/CI/tooling changes |
| `test` | Adding or fixing tests |
| `refactor` | Code refactoring (no behavior change) |

## Adding a New Device

1. Add the device profile to `config/devices.json`
2. If Samsung: add to `devices/samsung/samsung_profiles.json`
3. Add a test in `tests/test_devices_config.py`
4. Update `docs/INSTALL_GUIDE.md` with the new device

## Adding a New Tool

1. Add the tool entry to `config/toolsets.json` under the appropriate category
2. Add the install line to `scripts/install-tools.sh`
3. Add a menu entry to `scripts/ados-menu.sh` if it's a primary tool
4. Update `README.md` tool matrix

## Code Style

- Python: Follow PEP 8, max line length 100
- Shell scripts: Use `#!/bin/bash`, `set -e`, quote all variables
- JSON: 4-space indent, alphabetical keys where possible

## Testing

All changes must pass the full test suite:
```bash
python -m unittest discover -s tests
# Expected: Ran 28 tests in X.XXXs OK
```

## Security Policy

This project is for **authorized security research only**. Do not submit tools or payloads that:
- Target specific real-world systems without consent
- Include personally identifiable information
- Violate any applicable laws

See [SECURITY.md](SECURITY.md) for responsible disclosure.

## Questions?

Open a GitHub Discussion or Issue. We respond within 48 hours.
