# scitex-resource runtime/

Per-host regenerable data — logs, caches, PID files, temporary workspaces.
Everything here is automatically excluded from git (see `.gitignore`).

This directory is intentionally empty in fresh clones. Files are created
lazily when the package runs. For the full canonical layout, see the
`local-state-directories` skill in the scitex-* ecosystem.
