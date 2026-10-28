# Verifier hidden-source correctness proposal

## Scope and preserved evidence

This proposal branches from `c3913bfe423aede57a9dd0b5a6bdc8fe342b0861` as
`cloud/verifier-hidden-source`. The independently reviewed smoke-test branch
`cloud/storage-ui-smoke` stays at
`e4d8aee09f06944f0b4a3a5f2adcf07d3b1cb0ce`. Application files, vendored sources,
source manifests, catalogs, notices, and the smoke-test branch are unchanged.

The approved runtime attempt downloaded the official PowerShell 7.6.9 archive,
matched its pinned SHA-256 before execution, reported version 7.6.9, and ran the
unchanged verifier. It failed at line 28 with `Unmanifested source file in
matt-pocock` and exit 1. The owned runtime directory
`/tmp/custos-pwsh-7.6.9.QlqPy7ph` was removed and independently confirmed absent.
The exact command/results remain in the ignored execution record
`.scratch/custos-pwsh-verifier-20261028-oms27m0l.json`, SHA-256
`093a0b2be85affaa8ff20a7b4891b2fc51af17822b9ce74a337921bf39190b49`.
No further runtime was downloaded, installed, or run for this proposal.

## Diagnosis

The actual failure occurs after the per-manifest-entry validation loop. Separate
read-only enumeration found all 133 Matt Pocock manifested files and exactly
133 actual files, with no extra/missing paths or SHA-256 drift. Of those files,
31 are beneath `.agents/`, `.changeset/`, or `.out-of-scope/` directories within
the vendored tree. P-Stack has 130 manifested/actual files and no hidden path
components or SHA-256 drift.

Ranked explanations and predictions:

1. Default PowerShell enumeration excludes hidden directories. The verifier's
   `Get-ChildItem -Recurse -File` therefore misses the 31 files; adding `-Force`
   should reconcile the enumeration without accepting extras. Microsoft
   documents that default enumeration excludes hidden items.
2. True extra/missing paths would produce an actual/manifest set difference.
   Read-only comparison found none, ruling out that explanation for this tree.
3. Byte/hash drift would fail in the earlier validation loop. The observed
   failure was later, and independent hash checks found no drift.

The omission is established by the recorded failure, the tree, and the
documented enumeration contract. The predicted PowerShell counts (102 without
hidden paths, 133 with them) have not been measured in PowerShell. A minimized
fixture red/green run and successful full-tree rerun remain pending.
[Microsoft Get-ChildItem documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem#-hidden).

## Exact proposed production change

```diff
-        $item = Get-Item -LiteralPath $path
+        $item = Get-Item -LiteralPath $path -Force
...
-    $actual = @(Get-ChildItem -LiteralPath $sourceRoot -Recurse -File)
+    $actual = @(Get-ChildItem -LiteralPath $sourceRoot -Recurse -File -Force)
```

`Get-Item -Force` also includes an explicitly manifested hidden file, complementing
the recursive enumeration change. Both operations remain read-only; this flag
does not override filesystem access restrictions. Missing files still throw.
Containment, duplicate paths, reparse-point refusal, SHA-256, Git blob, byte
size, supported file types, exact membership/count, and catalog-target checks
remain intact. No count exception, hidden-path exclusion, manifest regeneration,
or hash relaxation is proposed.
[Microsoft Get-Item documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-item#-force).

## Regression seam and verification status

The requested seam is the actual verifier invoked as a CLI against an isolated
synthetic fixture project. `test/verifier_regression.py` copies the selected
verifier into each fixture's `scripts/` directory, supplies fresh fixture
manifests and catalogs, and invokes an explicitly supplied existing `pwsh`.
It does not emulate PowerShell enumeration or mock verifier internals. Fixture
SHA-256 and Git blob identities are generated from known synthetic bytes using
Python's hashing functions, independently of the verifier's commands.

Eight proposed tests cover manifested hidden directories, manifested hidden
files, true visible/hidden extras, missing files, changed source bytes, wrong
SHA-256/Git-blob/size fields, unsupported file types with otherwise correct
hashes, and missing catalog targets. Negative cases require a nonzero exit,
the relevant rejection diagnostic, and no success marker. Each fixture is
temporary and cleaned up; no repository manifest is modified.

The tests were committed before the production edit. Only Python syntax,
fixture construction/identities, CLI help, diff checks, and the existing Node
suite can be checked without another PowerShell runtime. This is test-first
preparation, not a completed TDD red/green cycle or a claimed fix verification.
The original retained runtime failure is the existing red observation; the new
fixture tests and candidate verifier have not run in PowerShell.

Pocock `diagnosing-bugs` and `tdd` supply the actual-CLI seam and test-first
sequence; P-Stack `principle-prove-it-works` prevents treating static inspection
or Python checks as proof of the PowerShell result. Minimization and green
verification are explicitly deferred because the parent prohibits another
runtime execution now. Independent Spec/Standards review must inspect the final
immutable proposal; its identity and results are reported separately.

## Proposed authorized follow-up, not executed

Reuse only the exact checksum-pinned official 7.6.9 runtime proposal stored at
`e4d8aee09f06944f0b4a3a5f2adcf07d3b1cb0ce:docs/powershell-runtime-proposal.md`.
Do not repeat the denied API route or install dependencies. If approved for a
later run, keep the baseline copy and test fixtures beneath the one owned
runtime directory by supplying `TMPDIR`:

```sh
git show c3913bfe423aede57a9dd0b5a6bdc8fe342b0861:scripts/verify-foundation.ps1 > "$custos_pwsh_dir/baseline-verifier.ps1"
TMPDIR="$custos_pwsh_dir/tmp" python test/verifier_regression.py \
  --pwsh "$custos_pwsh_dir/runtime/pwsh" \
  --verifier "$custos_pwsh_dir/baseline-verifier.ps1" \
  FoundationVerifier.test_manifested_hidden_directories_are_included
```

That focused baseline test must fail specifically with the hidden-directory
fixture and the recorded unmanifested-file diagnostic. An unrelated startup,
Git, or fixture error does not establish red. Then run the candidate suite:

```sh
TMPDIR="$custos_pwsh_dir/tmp" python test/verifier_regression.py \
  --pwsh "$custos_pwsh_dir/runtime/pwsh"
```

All eight tests must pass, including every negative subcase. Finally rerun the
actual candidate `scripts/verify-foundation.ps1` on the unchanged real vendored
tree using the proposal's no-profile/noninteractive command, telemetry/update
settings, and owned XDG/temp paths. It must report 133 Matt Pocock files, 130
P-Stack files, all 263 files verified, and exit 0. Retain exact command/version,
outputs, and exit statuses, then remove only the owned temporary directory.

The pinned download, checksum, local extraction, existing native dependencies,
and cleanup effects can remain the same as the prior disclosed runtime plan.
The fixture suite adds verifier subprocesses and synthetic fixture files within
that directory and executes the newly proposed verifier code. The prior
one-run approval is not assumed to authorize that expanded verification step;
the current instruction explicitly forbids another runtime run. This proposal
therefore stops before it. The publication gate remains failed until an
authorized candidate rerun succeeds. Staged-diff inspection and publication
authorization remain separate requirements. Native-focus limitations are
unchanged; this proposal performs no browser or local Alienware work.
