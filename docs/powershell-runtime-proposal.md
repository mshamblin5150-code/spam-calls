# Temporary PowerShell runtime proposal

Proposal only, prepared 2026-10-28. Nothing below has been executed. Installing
or running this runtime is pending separate authorization; publication remains
outside this task.

## Requirement and current blocker

Root `AGENTS.md`, line 13, requires running `scripts/verify-foundation.ps1`
before publishing. The script checks both vendored collections against pinned
manifests and catalog targets using PowerShell filesystem/JSON/hash commands
and local Git. It has no Windows UI, registry, or COM operations. The instruction
requires the actual script, not Windows specifically; Linux `pwsh` is a viable
candidate whose execution still needs verification. The Python integrity check
is supplemental evidence and does not satisfy this gate.

This runner is Debian 13, x86_64. Neither `pwsh` nor `powershell` is on PATH;
standard PowerShell installation directories were absent. No dedicated trusted
cloud PowerShell tool is exposed. Therefore a temporary runtime is needed to
attempt the existing script here. Shell access to GitHub release API metadata
returned proxy `403 Forbidden`; no retry or network-policy change was attempted.
Artifact-download reachability has not been tested. The proposal may therefore
remain blocked by egress even if execution is later authorized.

## Pinned official source

Proposed runtime: PowerShell **7.6.9**, self-contained Linux x64 archive
`powershell-7.6.9-linux-x64.tar.gz`. The official release page lists SHA-256
`1da6d6d6035d651f20e70ddee7c4c15ac6ab8b9fb40ee92240d91263f28a884b`.
The proposal pins that release and hash rather than resolving “latest” during
execution. [Official release and artifact hashes](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.9).

Microsoft documents binary archive installation and notes that native
dependencies must already be available. This proposal adapts extraction to a
fresh temporary directory without system registration.
[Microsoft binary archive guidance](https://learn.microsoft.com/en-us/powershell/scripting/install/alternate-install-methods#install-from-binary-archives).

The runner already has `ca-certificates`, `libc6`, `libgcc-s1`,
`libgssapi-krb5-2`, `libicu76`, `libssl3t64`, `libstdc++6`, `tzdata`, and
`zlib1g`, observed with `dpkg-query -W`.
That matches the Debian 13 native dependency set in Microsoft's .NET guidance,
but runtime compatibility is untested. The archive supplies its managed
runtime; no SDK or package installation is proposed. Stop if startup reports a
missing dependency. [Microsoft .NET Debian dependencies](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian#dependencies).

## Proposed commands, not executed

Run from `/workspace/spam-calls` only after authorization. This is a Bash
subshell; all environment overrides are process-local. Python 3.12+ is already
available and supplies restricted archive extraction, not a replacement for
the verifier.

```sh
(
  set -euo pipefail
  test "$(uname -m)" = x86_64
  custos_pwsh_dir=$(mktemp -d /tmp/custos-pwsh-7.6.9.XXXXXXXX)
  trap 'rm -rf -- "$custos_pwsh_dir"' EXIT
  custos_pwsh_archive="$custos_pwsh_dir/powershell-7.6.9-linux-x64.tar.gz"
  curl --fail --show-error --location --proto '=https' --proto-redir '=https' \
    --connect-timeout 15 --max-time 120 \
    --output "$custos_pwsh_archive" \
    https://github.com/PowerShell/PowerShell/releases/download/v7.6.9/powershell-7.6.9-linux-x64.tar.gz
  printf '%s  %s\n' \
    1da6d6d6035d651f20e70ddee7c4c15ac6ab8b9fb40ee92240d91263f28a884b \
    "$custos_pwsh_archive" | sha256sum --check --strict
  mkdir "$custos_pwsh_dir/runtime" "$custos_pwsh_dir/config" \
    "$custos_pwsh_dir/cache" "$custos_pwsh_dir/data" "$custos_pwsh_dir/tmp"
  python - "$custos_pwsh_archive" "$custos_pwsh_dir/runtime" <<'PY'
import sys
import tarfile
with tarfile.open(sys.argv[1], "r:gz") as archive:
    archive.extractall(sys.argv[2], filter="data")
PY
  chmod u+x "$custos_pwsh_dir/runtime/pwsh"
  env POWERSHELL_TELEMETRY_OPTOUT=1 POWERSHELL_UPDATECHECK=Off \
    XDG_CONFIG_HOME="$custos_pwsh_dir/config" \
    XDG_CACHE_HOME="$custos_pwsh_dir/cache" \
    XDG_DATA_HOME="$custos_pwsh_dir/data" TMPDIR="$custos_pwsh_dir/tmp" \
    "$custos_pwsh_dir/runtime/pwsh" -NoLogo -NoProfile -NonInteractive \
    -Command '$PSVersionTable.PSVersion.ToString(); & ./scripts/verify-foundation.ps1'
)
```

## Effects, removal, and success evidence

Network effects: one HTTPS archive download from GitHub, including its HTTPS
release-asset redirect. No package feeds, apt operations, credentials, accounts,
or cloud services are involved. The command opts out of PowerShell telemetry
and disables update checks before startup, as documented by Microsoft.
[Telemetry setting](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_telemetry),
[update-check setting](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_update_notifications).

Filesystem effects: the archive, extracted executable/runtime, and XDG/temp
files live below the newly allocated `/tmp/custos-pwsh-7.6.9.*` directory.
There is no sudo, global PATH change, symlink registration, profile loading,
execution-policy change, source edit, or dependency installation. The EXIT trap
removes only that allocated directory, on success or ordinary failure. If the
shell is forcibly killed before cleanup, inspect and remove that exact recorded
directory after checking that its process has stopped; do not glob-delete other
temporary directories.

Gate evidence must include the actual reported PowerShell version, verifier
output for both collections and all 263 files, and successful process exit.
A failed download/startup/verifier leaves the gate unpassed. Even a successful
verifier run would not authorize publication: the complete staged list/diff
inspection required by AGENTS.md and an authorized publication target remain
necessary.
