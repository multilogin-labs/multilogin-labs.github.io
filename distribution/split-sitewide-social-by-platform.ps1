param(
    [string]$InputCsv = 'distribution/sitewide-social-scripts-en.csv',
    [string]$OutputDir = 'distribution/sitewide-social-scripts-en-by-platform'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$inputPath = Join-Path $repoRoot $InputCsv
$outputPath = Join-Path $repoRoot $OutputDir

if (-not (Test-Path -LiteralPath $inputPath)) {
    throw "Input CSV not found: $inputPath"
}

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

$data = Import-Csv -LiteralPath $inputPath
$groups = $data | Group-Object -Property platform | Sort-Object Name

foreach ($group in $groups) {
    $platformName = $group.Name
    $slug = $platformName.ToLowerInvariant() -replace '[^a-z0-9]+', '-'
    $slug = $slug.Trim('-')

    $csvPath = Join-Path $outputPath ($slug + '-en.csv')
    $txtPath = Join-Path $outputPath ($slug + '-en.txt')

    $group.Group | Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath $csvPath

    $lines = [System.Collections.Generic.List[string]]::new()
    $lines.Add('PLATFORM: ' + $platformName)
    $lines.Add('TOTAL_SCRIPTS: ' + $group.Count)
    $lines.Add('GENERATED_AT: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
    $lines.Add('')

    foreach ($row in $group.Group) {
        $lines.Add('PAGE_ID: ' + $row.page_id)
        $lines.Add('TITLE: ' + $row.page_title)
        $lines.Add('URL: ' + $row.page_url)
        $lines.Add('FORMAT: ' + $row.format)
        $lines.Add('POST_COPY:')
        $lines.Add($row.post_copy)
        $lines.Add('')
    }

    Set-Content -LiteralPath $txtPath -Value $lines -Encoding UTF8

    Write-Output ('platform=' + $platformName + ';count=' + $group.Count + ';csv=' + $csvPath + ';txt=' + $txtPath)
}

Write-Output ('output_dir=' + $outputPath)
