# Changelog

All notable changes to `scitex-resource` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

- feat(cpus): ``get_usable_cpus()`` / ``get_cpu_sources()`` — how many CPUs
  THIS process may run on, as opposed to how big the machine is. Cascade is
  kernel affinity mask → ``SLURM_CPUS_PER_TASK`` / ``SLURM_CPUS_ON_NODE`` →
  ``os.cpu_count()``. Use it to size worker pools; ``get_metrics()["cpu_count"]``
  answers the inventory question and over-reports inside any allocation.
- feat(cli): ``scitex-resource cpus show`` — human table, ``--json``, ``--yaml``,
  and ``--count`` for a bare integer a shell can interpolate. Reports every
  source rather than only the winner, so a disagreement lands in the log.
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
