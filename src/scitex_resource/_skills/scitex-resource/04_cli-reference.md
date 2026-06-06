---
description: |
  [TOPIC] CLI reference
  [DETAILS] Concise summary of every `scitex-resource` leaf command.
tags: [scitex-resource-cli-reference]
---

# CLI reference

```bash
scitex-resource [-h|-V|--help-recursive|--json] <noun> <verb> [opts]
```

## Hosts (identity)

| Command | Output |
|---|---|
| `hosts show [--json]` | canonical host name |
| `hosts config show [--json\|--yaml]` | resolved `host:` block |
| `hosts config set KEY VALUE [--user\|--project]` | set a dot-path key |
| `hosts config unset KEY [--user\|--project]` | remove a dot-path key |
| `hosts config init [--user\|--project]` | scaffold a starter config.yaml |
| `hosts config edit [--user\|--project]` | open in $EDITOR |
| `machine ...` | deprecated alias for `hosts ...` |

## Specs / metrics / processor-usages

| Command | Output |
|---|---|
| `specs show [--no-system --no-cpu --no-gpu --no-disk --no-network --json|--yaml]` | rich nested specs |
| `metrics show [--no-gpu --json]` | flat heartbeat dict |
| `processor-usages show [--json|--csv]` | one snapshot |
| `processor-usages log [--interval N --path P --max-rows N --no-init]` | append rows to CSV until max-rows |

## ram-limit

| Command | Output |
|---|---|
| `ram-limit set FACTOR` | applies `RLIMIT_AS` cap; FACTOR in (0, 1] |
| `ram-limit get [--json]` | `MemFree + Buffers + Cached` in KiB |

## Introspection

| Command | Output |
|---|---|
| `--help`, `-h` | usage |
| `--version`, `-V` | version string |
| `--help-recursive` | help for every leaf |
| `list-commands [--json]` | flat list of all leaves |
| `list-python-apis [-v --json]` | public Python API |
| `mcp start | doctor | list-tools | install` | MCP control |
| `skills list | get NAME | install` | bundled markdown |
| `install-shell-completion --shell {bash,zsh,fish}` | wire <TAB> |
| `print-shell-completion --shell {bash,zsh,fish}` | print snippet |

## Examples

```bash
$ scitex-resource hosts show
spartan
$ scitex-resource metrics show --no-gpu --json | jq .mem_used_percent
54.3
$ scitex-resource processor-usages log --interval 2 --max-rows 30
wrote 30 rows to /home/user/.scitex/resource/runtime/processor_usages.csv
```
