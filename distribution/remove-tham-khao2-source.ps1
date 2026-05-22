$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $repoRoot 'Tham Khao 2'

if (Test-Path -LiteralPath $sourceRoot) {
    $fileCount = (Get-ChildItem -LiteralPath $sourceRoot -Recurse -File | Measure-Object).Count
    try {
        Remove-Item -LiteralPath $sourceRoot -Recurse -Force
    }
    catch {
        # Fallback for long Windows paths by mirroring an empty directory.
        $emptyRoot = Join-Path $repoRoot '_empty_for_delete'
        New-Item -ItemType Directory -Force -Path $emptyRoot | Out-Null

        robocopy $emptyRoot $sourceRoot /MIR /R:0 /W:0 /NFL /NDL /NJH /NJS /NP | Out-Null
        $robocopyCode = $LASTEXITCODE

        if ($robocopyCode -gt 7) {
            Write-Output ('robocopy_error=' + $robocopyCode)
        }

        Remove-Item -LiteralPath $sourceRoot -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $emptyRoot -Recurse -Force -ErrorAction SilentlyContinue
    }

    $existsAfter = Test-Path -LiteralPath $sourceRoot

    Write-Output 'removed=1'
    Write-Output ('source_files_removed=' + $fileCount)
    Write-Output ('exists_after=' + ($(if ($existsAfter) { 1 } else { 0 })))
}
else {
    Write-Output 'removed=0'
    Write-Output 'source_files_removed=0'
    Write-Output 'exists_after=0'
}