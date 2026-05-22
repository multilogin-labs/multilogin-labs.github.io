$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$pagesRoot = Join-Path $repoRoot 'guides\mlx-api-hub'
$assetsRoot = Join-Path $repoRoot 'assets\img\guides\mlx-api-hub'
$sourceRoot = Join-Path $repoRoot 'Tham Khao 2'
$manifestPath = Join-Path $repoRoot 'distribution\multilogin-api-knowledge-import-manifest.csv'

$pageFiles = @()
if (Test-Path -LiteralPath $pagesRoot) {
    $pageFiles = Get-ChildItem -LiteralPath $pagesRoot -Recurse -File -Filter index.html
}

$missing = [System.Collections.Generic.List[string]]::new()
$totalRefs = 0

foreach ($page in $pageFiles) {
    $html = Get-Content -Raw -LiteralPath $page.FullName
    $matches = [regex]::Matches($html, 'src="/assets/img/guides/mlx-api-hub/([^"]+)"')

    foreach ($m in $matches) {
        $totalRefs++
        $relativeImage = $m.Groups[1].Value -replace '/', '\\'
        $absoluteImage = Join-Path $assetsRoot $relativeImage

        if (-not (Test-Path -LiteralPath $absoluteImage)) {
            $missing.Add($page.FullName + ' => /assets/img/guides/mlx-api-hub/' + $m.Groups[1].Value)
        }
    }
}

$assetFiles = 0
if (Test-Path -LiteralPath $assetsRoot) {
    $assetFiles = (Get-ChildItem -LiteralPath $assetsRoot -Recurse -File | Measure-Object).Count
}

$sourceImageFiles = 0
if (Test-Path -LiteralPath $sourceRoot) {
    $sourceImageFiles = (
        Get-ChildItem -LiteralPath $sourceRoot -Recurse -File |
        Where-Object { $_.Extension.ToLowerInvariant() -in @('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.bmp', '.tif', '.tiff', '.avif') } |
        Measure-Object
    ).Count
}

Write-Output ('mlx_pages=' + $pageFiles.Count)
Write-Output ('mlx_img_refs_in_html=' + $totalRefs)
Write-Output ('mlx_missing_img_refs=' + $missing.Count)
Write-Output ('mlx_asset_files=' + $assetFiles)
Write-Output ('source_image_files_under_tham_khao_2=' + $sourceImageFiles)

if (Test-Path -LiteralPath $manifestPath) {
    $rows = Import-Csv -LiteralPath $manifestPath
    $sum = ($rows | Measure-Object -Property images_copied -Sum).Sum
    Write-Output ('manifest_rows=' + $rows.Count)
    Write-Output ('manifest_images_copied=' + $sum)
}
else {
    Write-Output 'manifest_missing=1'
}

if ($missing.Count -gt 0) {
    Write-Output 'missing_examples:'
    $missing | Select-Object -First 20 | ForEach-Object { Write-Output $_ }
}