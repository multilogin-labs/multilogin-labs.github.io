param(
    [string]$RepoRoot = 'c:\Users\Dalatmilkshop\Documents\GitHub\saasverdict.com',
    [string]$ManifestRelativePath = 'distribution\multilogin-api-knowledge-import-manifest.csv',
    [string]$SitemapRelativePath = 'sitemap.xml',
    [string]$SiteBaseUrl = 'https://saasverdict.com',
    [string]$GuidesHubSlug = 'mlx-api-hub'
)

$ErrorActionPreference = 'Stop'

$manifestPath = Join-Path $RepoRoot $ManifestRelativePath
$sitemapPath = Join-Path $RepoRoot $SitemapRelativePath

if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Manifest not found: $manifestPath"
}
if (-not (Test-Path -LiteralPath $sitemapPath)) {
    throw "Sitemap not found: $sitemapPath"
}

$rows = Import-Csv -LiteralPath $manifestPath
if (-not $rows -or $rows.Count -eq 0) {
    throw "Manifest has no rows: $manifestPath"
}

function Normalize-Url([string]$url) {
    if ([string]::IsNullOrWhiteSpace($url)) { return '' }
    $u = $url.Trim()
    if (-not $u.EndsWith('/')) { $u = $u + '/' }
    return $u
}

$sitemapXml = Get-Content -Raw -LiteralPath $sitemapPath
$existing = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

$locMatches = [regex]::Matches($sitemapXml, '(?is)<loc>\s*(.*?)\s*</loc>')
foreach ($m in $locMatches) {
    $loc = Normalize-Url($m.Groups[1].Value)
    if ($loc) { $existing.Add($loc) | Out-Null }
}

$urlsToAdd = [System.Collections.Generic.List[string]]::new()
$hubUrl = Normalize-Url("$SiteBaseUrl/guides/$GuidesHubSlug/")
$urlsToAdd.Add($hubUrl)

$categorySlugs = $rows | Select-Object -ExpandProperty category_slug -Unique | Sort-Object
foreach ($cat in $categorySlugs) {
    $urlsToAdd.Add((Normalize-Url("$SiteBaseUrl/guides/$GuidesHubSlug/$cat/")))
}

foreach ($row in $rows) {
    $u = Normalize-Url($row.target_url)
    if ($u) {
        $urlsToAdd.Add($u)
    }
}

$addedBlocks = [System.Collections.Generic.List[string]]::new()
$today = Get-Date -Format 'yyyy-MM-dd'

foreach ($url in $urlsToAdd | Select-Object -Unique) {
    if ($existing.Contains($url)) { continue }

    $priority = '0.80'
    if ($url -eq $hubUrl) {
        $priority = '0.87'
    }
    elseif ($url -match ('^' + [regex]::Escape("$SiteBaseUrl/guides/$GuidesHubSlug/") + '[^/]+/$')) {
        $priority = '0.84'
    }

    $block = @"
  <url>
    <loc>$url</loc>
    <lastmod>$today</lastmod>
    <priority>$priority</priority>
  </url>
"@
    $addedBlocks.Add($block)
    $existing.Add($url) | Out-Null
}

if ($addedBlocks.Count -gt 0) {
    $insertion = ($addedBlocks -join "`r`n") + "`r`n"
    $updated = $sitemapXml -replace '</urlset>', ($insertion + '</urlset>')
    Set-Content -LiteralPath $sitemapPath -Value $updated -Encoding UTF8
}

Write-Output ('added=' + $addedBlocks.Count)
Write-Output ('sitemap=' + $sitemapPath)
