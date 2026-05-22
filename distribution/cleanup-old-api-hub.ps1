$ErrorActionPreference = 'Stop'

$repoRoot = 'c:\Users\Dalatmilkshop\Documents\GitHub\saasverdict.com'
$oldGuides = Join-Path $repoRoot 'guides\multilogin-api-knowledge-hub'
$oldAssets = Join-Path $repoRoot 'assets\img\guides\multilogin-api-knowledge-hub'

if (Test-Path -LiteralPath $oldGuides) {
    Remove-Item -LiteralPath $oldGuides -Recurse -Force
}
if (Test-Path -LiteralPath $oldAssets) {
    Remove-Item -LiteralPath $oldAssets -Recurse -Force
}

Write-Output 'cleanup=done'
