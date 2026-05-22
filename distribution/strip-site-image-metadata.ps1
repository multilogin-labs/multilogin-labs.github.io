param(
    [string]$ImageRoot,
    [switch]$RefreshTimestamps
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ImageRoot)) {
    $ImageRoot = Join-Path $repoRoot 'assets\img'
}

if (-not $PSBoundParameters.ContainsKey('RefreshTimestamps')) {
    $RefreshTimestamps = $true
}

if (-not (Test-Path -LiteralPath $ImageRoot)) {
    throw "Image root does not exist: $ImageRoot"
}

$extensions = @('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tif', '.tiff', '.avif', '.svg')
$files = Get-ChildItem -LiteralPath $ImageRoot -Recurse -File |
    Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() }

$total = $files.Count
if ($total -eq 0) {
    Write-Output ('image_root=' + $ImageRoot)
    Write-Output 'files_total=0'
    Write-Output 'files_processed=0'
    Write-Output 'files_failed=0'
    Write-Output 'svg_metadata_blocks_cleaned=0'
    Write-Output ('timestamps_refreshed=' + ($(if ($RefreshTimestamps) { 1 } else { 0 })))
    Write-Output 'tool_used=none'
    return
}

$exiftoolCmd = Get-Command exiftool -ErrorAction SilentlyContinue
$magickCmd = Get-Command magick -ErrorAction SilentlyContinue

$nonSvgCount = ($files | Where-Object { $_.Extension.ToLowerInvariant() -ne '.svg' } | Measure-Object).Count
if (-not $exiftoolCmd -and -not $magickCmd -and $nonSvgCount -gt 0) {
    throw 'No supported metadata stripping tool found. Install exiftool or ImageMagick.'
}

function Clean-SvgFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath
    )

    $raw = Get-Content -Raw -LiteralPath $FilePath
    $updated = $raw -replace '(?is)<!--.*?-->', ''
    $updated = $updated -replace '(?is)<metadata\b[^>]*>.*?</metadata>', ''

    if ($updated -ne $raw) {
        Set-Content -LiteralPath $FilePath -Value $updated -Encoding UTF8
        return 1
    }

    return 0
}

$processed = 0
$failed = 0
$svgMetadataBlocksCleaned = 0
$toolUsed = 'none'

foreach ($file in $files) {
    try {
        $ext = $file.Extension.ToLowerInvariant()

        if ($ext -eq '.svg') {
            $svgMetadataBlocksCleaned += (Clean-SvgFile -FilePath $file.FullName)

            if ($exiftoolCmd) {
                & $exiftoolCmd.Source -overwrite_original -all= -P -- "$($file.FullName)" | Out-Null
                $toolUsed = 'exiftool+svg-clean'
            }
            elseif ($toolUsed -eq 'none') {
                $toolUsed = 'svg-clean-only'
            }
        }
        else {
            if ($exiftoolCmd) {
                & $exiftoolCmd.Source -overwrite_original -all= -P -- "$($file.FullName)" | Out-Null
                if ($toolUsed -eq 'none' -or $toolUsed -eq 'svg-clean-only') {
                    $toolUsed = 'exiftool'
                }
            }
            elseif ($magickCmd) {
                & $magickCmd.Source mogrify -strip -- "$($file.FullName)" | Out-Null
                if ($toolUsed -eq 'none') {
                    $toolUsed = 'magick'
                }
            }
        }

        if ($RefreshTimestamps) {
            (Get-Item -LiteralPath $file.FullName).LastWriteTime = Get-Date
        }

        $processed++
    }
    catch {
        $failed++
        Write-Output ('failed=' + $file.FullName + ' :: ' + $_.Exception.Message)
    }
}

Write-Output ('image_root=' + $ImageRoot)
Write-Output ('files_total=' + $total)
Write-Output ('files_processed=' + $processed)
Write-Output ('files_failed=' + $failed)
Write-Output ('svg_metadata_blocks_cleaned=' + $svgMetadataBlocksCleaned)
Write-Output ('timestamps_refreshed=' + ($(if ($RefreshTimestamps) { 1 } else { 0 })))
Write-Output ('tool_used=' + $toolUsed)