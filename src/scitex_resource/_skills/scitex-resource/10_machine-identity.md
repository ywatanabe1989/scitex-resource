---
description: |
  [TOPIC] Canonical machine identity
  [DETAILS] Resolution cascade used by `get_machine_name()` and
  `get_machine_config()` to give every scitex-* package the same
  canonical name regardless of OS-level hostname drift.
tags: [scitex-resource-machine-identity]
---

# Canonical host identity

scitex-resource owns the question "what host am I running on?".
Other scitex-* packages (scitex-orochi, scitex-hpc, scitex-agent-container)
consume `get_host_name()` so every package agrees on one canonical
name regardless of how the OS reports it (FQDN drift,
`Yusukes-MacBook-Air` vs `mba`, login-node vs compute-node, etc.).

## Resolution cascade

Highest precedence first:

1. `$SCITEX_RESOURCE_HOST` env var
   (legacy `$SCITEX_RESOURCE_MACHINE` is still honoured as a fallback)
2. `<project>/.scitex/resource/config.yaml` -- `host.canonical_name`
   (falls back to legacy `machine.canonical_name`)
3. `~/.scitex/resource/config.yaml` -- `host.canonical_name`
   (falls back to legacy `machine.canonical_name`)
4. Short hostname (`socket.gethostname().split(".", 1)[0]`)

The same chain applies to `get_host_config()` which returns the
full `host:` block including `aliases`, `role`, `hpc.*`.

## Config schema

`~/.scitex/resource/config.yaml` -- example for a SLURM login node:

```yaml
host:
  canonical_name: spartan
  aliases:
    - spartan-login1.hpc.example.edu
    - spartan-login1
  role: hpc-login
  hpc:
    cluster: spartan
    login_only: true        # don't surface login-node CPU as available
    partitions: [physical, sapphire]
```

(Deprecated ``machine:`` block is still accepted but triggers a one-time
``DeprecationWarning``.)

## CLI

```bash
$ scitex-resource hosts show              # prints canonical name
$ scitex-resource hosts show --json
$ scitex-resource hosts config show --yaml   # full host: block
$ scitex-resource hosts config set host.canonical_name spartan --yes
```

(Deprecated ``scitex-resource machine ...`` alias still works but emits
a ``DeprecationWarning``.)

## Why this matters

A multi-cluster ecosystem cannot trust raw `socket.gethostname()` --
compute nodes report different names from login nodes, FQDNs drift,
laptops get renamed. The cascade lets the user pin one canonical name
once (`~/.scitex/resource/config.yaml`) and every downstream package
agrees automatically.
