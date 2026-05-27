# Changelog

All notable changes to `scitex-resource` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

- fix(local-state): default log path now resolves under ``~/.scitex/resource/runtime/``
  instead of ``/tmp/scitex/``, aligning with the ecosystem local-state-directories
  convention.
- refactor(host): canonical API renamed from ``get_machine_name`` /
  ``get_machine_config`` to ``get_host_name`` / ``get_host_config``. The old
  names still work with a ``DeprecationWarning``.
- feat(cli): ``scitex-resource hosts ...`` group replaces deprecated
  ``scitex-resource machine ...``.
- feat(config): ``hosts config`` CRUD subcommands (show, set, unset, init, edit).
- docs: refresh README, skills bundle, and sphinx index for the current codebase.

## [0.3.3]

- Initial CHANGELOG entry — see git log for prior history.
