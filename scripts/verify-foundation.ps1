$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$total = 0
foreach ($name in @('matt-pocock', 'pstack')) {
    $base = Join-Path $projectRoot ".agents/skills/$name"
    $sourceRoot = [IO.Path]::GetFullPath((Join-Path $base 'references/upstream'))
    $manifest = Get-Content -Raw -LiteralPath (Join-Path $base 'source-manifest.json') | ConvertFrom-Json
    $seen = @{}
    foreach ($entry in $manifest.files) {
        $path = [IO.Path]::GetFullPath((Join-Path $sourceRoot $entry.path))
        if (!$path.StartsWith($sourceRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Manifest path escapes source root: $($entry.path)"
        }
        if ($seen.ContainsKey($path)) { throw "Duplicate manifest path: $($entry.path)" }
        $seen[$path] = $true
        $item = Get-Item -LiteralPath $path -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Unexpected link: $path" }
        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        $blob = git hash-object --no-filters -- $path
        if ($LASTEXITCODE -ne 0 -or $blob -ne $entry.gitBlob -or $hash -ne $entry.sha256 -or $item.Length -ne $entry.bytes) {
            throw "Vendored source mismatch: $($entry.path)"
        }
        if ($item.Name -ne 'LICENSE' -and $item.Extension -notin @('.md', '.tsv')) {
            throw "Unexpected source file type: $($entry.path)"
        }
    }
    $actual = @(Get-ChildItem -LiteralPath $sourceRoot -Recurse -File -Force)
    if ($actual.Count -ne $seen.Count) { throw "Unmanifested source file in $name" }
    foreach ($item in $actual) {
        if (!$seen.ContainsKey($item.FullName)) { throw "Unmanifested source file: $($item.FullName)" }
    }
    $catalog = Get-Content -Raw -LiteralPath (Join-Path $base 'catalog.json') | ConvertFrom-Json
    foreach ($entry in $catalog) {
        if (!(Test-Path -LiteralPath (Join-Path $base $entry.path) -PathType Leaf)) {
            throw "Missing catalog source: $($entry.path)"
        }
    }
    $total += $actual.Count
    Write-Output "$name`: $($actual.Count) source files verified; $(@($catalog).Count) catalog entries"
}
Write-Output "PASS: $total preserved source files match pinned SHA-256 and Git blob hashes."
