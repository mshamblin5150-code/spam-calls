# Local publication candidate evidence

## Scope and integration

Repository: `https://github.com/mshamblin5150-code/spam-calls.git`.
Local candidate branch: `cloud/publication-candidate`. Publication, PR creation,
merge, and deployment have not been performed.

The separate reviewed branches diverged from
`c3913bfe423aede57a9dd0b5a6bdc8fe342b0861`:

- Smoke tests: `cloud/storage-ui-smoke`,
  `e4d8aee09f06944f0b4a3a5f2adcf07d3b1cb0ce`.
- Verifier correction: `cloud/verifier-hidden-source`,
  `16e9edd028052e855a854a00e4f4bd6284d1a59a`.

Neither branch contained both changes. The candidate was created from the
smoke branch, then the two verifier commits were cherry-picked locally. The
source integration checkpoint is
`7254692cb90af925312dc8991a3f6c30b54bc597`; subsequent candidate changes only
add this evidence document and historical-checkpoint pointers. Both original
branches and their ignored execution records remain intact. A read-only
`git ls-remote origin refs/heads/main` returned the common baseline above during
candidate preparation; the remote base should be checked again if it changes
before publication.

The combined change adds optional browser and verifier regression tests,
corrects hidden-item inclusion in the foundation verifier, and documents
results. Application files, runtime dependencies, vendored source bytes,
manifests, catalogs, and third-party notices are unchanged.

## Executed checks

The approved temporary official PowerShell 7.6.9 runtime matched archive SHA-256
`1da6d6d6035d651f20e70ddee7c4c15ac6ab8b9fb40ee92240d91263f28a884b`
before extraction/execution. Its executable SHA-256 was
`c561baa659f1d0a5e9482684fc26e377b6fb8178b74f5e4fbb0ba0ea38f6a126`.
The runtime was confined to `/tmp/custos-pwsh-7.6.9._r0bynoi`, with owned
configuration/cache/data/temp paths, telemetry disabled, and update checks off.
No system-wide installation, dependency, credential, or access-policy change was
made. That directory was removed and independently confirmed absent.

The baseline hidden-directory fixture failed with the original line-28
`Unmanifested source file in matt-pocock` error. The corrected verifier then
passed all eight regression tests in 10.479s, including true extra/missing
files, byte/SHA-256/Git-blob/size drift, unsupported types, and missing catalog
targets. Hidden manifested directories and files both passed. The actual
corrected verifier on `16e9edd` exited 0 with this output:

```text
7.6.9
matt-pocock: 133 source files verified; 38 catalog entries
pstack: 130 source files verified; 53 catalog entries
PASS: 263 preserved source files match pinned SHA-256 and Git blob hashes.
```

The outer execution wrapper subsequently exited 1 because its own assertion
incorrectly expected 50 P-Stack catalog entries. The unchanged catalog has 53:
50 main entries plus three dormant Benny entries. This wrapper failure remains
in the original record; it was not edited or treated as a successful wrapper
run. A separate audit checked the actual verifier's exit 0, all eight test
passes, unchanged catalog count, exact identities, and cleanup. No runtime or
verifier rerun was used to resolve the wrapper's incorrect assertion.

Local ignored receipts, preserved separately from source publication:

| Receipt | SHA-256 |
| --- | --- |
| `.scratch/custos-pwsh-verifier-20261028-oms27m0l.json` — initial unchanged-verifier failure | `093a0b2be85affaa8ff20a7b4891b2fc51af17822b9ce74a337921bf39190b49` |
| `.scratch/custos-verifier-bundle-16e9edd-elxf_z7i.json` — actual run, including wrapper failure | `2acbf352c2e74f9501ad3fb2b9a38cdf48d6a8ee04485b7ecad48827c9a2b406` |
| `.scratch/custos-verifier-bundle-16e9edd-elxf_z7i.audit.json` — separate outcome audit | `697d0965f9476f58263202b47a4842927bb0e9b33fd791bf1069b61d646a5175` |

The integrated source also reran `python test/browser_storage_smoke.py`
(six passing headless storage/import checks) and `npm test` (14 passing Node
checks). These do not execute or install PowerShell. The verifier fixture tests
require an explicitly supplied existing authorized `pwsh` executable; the
application and default Node suite remain dependency-free.

## Exact equivalence to executed verifier inputs

No PowerShell run was made on the integrated commit. Instead, byte comparisons
against the executed verifier branch establish these unchanged inputs:

| Input | Identity on candidate and executed `16e9edd` |
| --- | --- |
| `scripts/verify-foundation.ps1` SHA-256 | `3c7c26ea71ac981ef3e8ee138d24873ac284f501a335cf7ee022e60177eb66b3` |
| `test/verifier_regression.py` SHA-256 | `3de32265ad069452a54669ec7f9fa91bed5a3c5800757dbf37f601facadedd1a` |
| Entire `.agents` Git tree, including routers, manifests, catalogs and sources | `4c1a0a74037f509b240c1e9d0d51995d9186cb4b` |

The verifier resolves only that source tree from its unchanged script location
and uses the same manifest/catalog formats and Git hashing behavior. The
integrated application, index, package configuration, and third-party notices
are also byte-identical to the executed verifier branch. The only combined
additions outside the tested verifier inputs are the previously tested browser
test file and documentation. The browser test SHA-256 remains
`38060ed1a4954bb43866bcbb70c6d407bfe72b48d8d0536e052f87c1ab0ece73`,
identical to the independently reviewed smoke branch.

Upstream identities are unchanged: Matt Pocock
`49dd158d1076134a641b33efb035946536778336` and P-Stack
`e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. The successful actual script result
is carried forward by exact input equivalence, not represented as a new
integrated-commit runtime execution or replaced with Python verification.

## Native acceptance and publication boundary

The owner-approved native-dialog criterion concerns inaccessible background
application controls while modal, correct actions, and focus restoration;
browser chrome focus may occur. Strict uninterrupted Tab wrapping is not
required. These headless tests do not establish native-window focus destination,
reentry, or modal background-control inaccessibility. Those limitations remain
open; no denied native capture/binding route or local Alienware work occurred.

Earlier documents are preserved as historical checkpoints, including their
then-pending runtime and review statements. This document records subsequent
execution and integration; it does not rewrite the original logs. Final
independent Spec/Standards outcomes, exact candidate commit, full index-versus-
publication-base inspection, and the draft PR payload are reported separately
so that recording review results does not alter the reviewed commit.

Before any external publication, inspect the complete candidate file list and
diff as required by AGENTS.md, not merely the latest documentation commit.
Approve an exact source revision, repository, branch, base, and publication
action. This preparation grants no authority to push, create a PR, merge, or
deploy, and makes no claim that the remaining native acceptance was proven.
