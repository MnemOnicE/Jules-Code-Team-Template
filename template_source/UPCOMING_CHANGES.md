# Upcoming Changes and Recommendations

This file captures suggested next steps for the repository after the current security hardening and documentation updates.

## Security and Dependency Maintenance

- Review GitHub Security Alerts at `https://github.com/MnemOnicE/Jules-Code-Team-Template/security/dependabot`.
- Add a Python dependency lockfile or pin Python dependency versions in `requirements.txt`.
- Install and run `pip-audit` or `safety` to scan the Python dependency set.
- Consider adding signed update artifacts and verification for `scripts/update.py`.
- Add audit logging to backup/restore and plugin load operations.

## Testing and CI

- Add CI coverage for:
  - `scripts/backup_restore.py` safe restore behavior
  - `scripts/update.py` semver and backup enforcement
  - `.agents/engine/core/plugin_manager.py` allowlist and hash enforcement
- Add regression tests for the `allowed_plugins.json` format and plugin metadata validation.
- Add a workflow that runs `npm audit` and Python dependency checks.

## Documentation

- Add a short security usage guide for developers, including plugin trust and backup restore safety.
- Document the exact supported file names and paths in `.agents/plugins/allowed_plugins.json`.
- Add example `allowed_plugins.json` content to the main README or docs.

## Long-term Improvements

- Replace placeholder update behavior with a signed release channel.
- Add role-based access controls or minimum permission checks for file restores.
- Add stronger runtime isolation for plugin execution.
- Add a repository-level changelog or release notes process.
