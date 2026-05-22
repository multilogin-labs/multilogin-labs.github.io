param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$BaseUrl = 'https://saasverdict.com'
)

$ErrorActionPreference = 'Stop'

function Get-PageTitle {
    param([string]$Html, [string]$UrlPath)

    $m = [regex]::Match($Html, '(?is)<title>\s*(.*?)\s*</title>')
    if ($m.Success) {
        return $m.Groups[1].Value.Trim()
    }

    if ($UrlPath -eq '/') {
        return 'Home'
    }

    $slug = (Split-Path $UrlPath.Trim('/') -Leaf)
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return 'Untitled'
    }

    return ($slug -replace '-', ' ').Trim()
}

function Get-SectionName {
    param([string]$UrlPath)

    if ($UrlPath -eq '/') {
        return 'Core Hubs'
    }

    $seg = ($UrlPath.Trim('/') -split '/')[0].ToLowerInvariant()
    switch ($seg) {
        'tools' { return 'Tools' }
        'compare' { return 'Comparisons' }
        'guides' { return 'Guides' }
        'promo' { return 'Promo Pages' }
        'about' { return 'Company and Policies' }
        'contact' { return 'Company and Policies' }
        'editorial-policy' { return 'Company and Policies' }
        'privacy-policy' { return 'Company and Policies' }
        'terms' { return 'Company and Policies' }
        default { return 'Other' }
    }
}

$sectionOrder = @(
    'Core Hubs',
    'Tools',
    'Comparisons',
    'Guides',
    'Promo Pages',
    'Company and Policies',
    'Other'
)

$files = Get-ChildItem -Path $Root -Recurse -File -Filter 'index.html' |
    Where-Object {
        $_.FullName -notmatch '\\assets\\' -and
        $_.FullName -notmatch '\\distribution\\' -and
        $_.FullName -notmatch '\\sitemap\\index.html$'
    }

$pages = [System.Collections.Generic.List[object]]::new()
foreach ($file in $files) {
    $rel = $file.FullName.Substring($Root.Length + 1).Replace('\\', '/')

    if ($rel -eq 'index.html') {
        $urlPath = '/'
    }
    else {
        $parent = (Split-Path $rel -Parent).Replace('\\', '/').Trim('/')
        $urlPath = '/' + $parent + '/'
    }

    $html = [System.IO.File]::ReadAllText($file.FullName)
    $title = Get-PageTitle -Html $html -UrlPath $urlPath
    $section = Get-SectionName -UrlPath $urlPath

    $pages.Add([pscustomobject]@{
        title = $title
        urlPath = $urlPath
        url = ($BaseUrl + $urlPath)
        section = $section
    })
}

$pages = $pages | Sort-Object section, urlPath

$outDir = Join-Path $Root 'sitemap'
$outFile = Join-Path $outDir 'index.html'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$sb = New-Object System.Text.StringBuilder
$null = $sb.AppendLine('<!DOCTYPE html>')
$null = $sb.AppendLine('<html lang="en">')
$null = $sb.AppendLine('<head>')
$null = $sb.AppendLine('    <meta charset="UTF-8">')
$null = $sb.AppendLine('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
$null = $sb.AppendLine('    <title>HTML Sitemap | SaaSVerdict</title>')
$null = $sb.AppendLine('    <meta name="description" content="Human-readable sitemap for SaaSVerdict sections, guides, comparisons, and tools.">')
$null = $sb.AppendLine('    <meta name="robots" content="index,follow">')
$null = $sb.AppendLine('    <link rel="canonical" href="https://saasverdict.com/sitemap/">')
$null = $sb.AppendLine('    <link rel="preconnect" href="https://fonts.googleapis.com">')
$null = $sb.AppendLine('    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
$null = $sb.AppendLine('    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">')
$null = $sb.AppendLine('    <link rel="stylesheet" href="/assets/css/site.css">')
$null = $sb.AppendLine('    <style>')
$null = $sb.AppendLine('        .sitemap-meta { color: var(--text-dim); margin-bottom: 0.85rem; }')
$null = $sb.AppendLine('        .sitemap-section { margin-top: 1rem; }')
$null = $sb.AppendLine('        .sitemap-list { list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 1.4rem; }')
$null = $sb.AppendLine('        .sitemap-list li { break-inside: avoid; margin: 0.22rem 0; }')
$null = $sb.AppendLine('        .sitemap-list a { text-decoration: none; font-weight: 700; }')
$null = $sb.AppendLine('        @media (max-width: 780px) { .sitemap-list { columns: 1; } }')
$null = $sb.AppendLine('    </style>')
$null = $sb.AppendLine('</head>')
$null = $sb.AppendLine('<body>')
$null = $sb.AppendLine('    <a class="skip-link" href="#main-content">Skip to main content</a>')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('    <header class="site-header">')
$null = $sb.AppendLine('        <div class="container nav-wrap">')
$null = $sb.AppendLine('            <a href="/" class="logo">SaaS<span>Verdict</span></a>')
$null = $sb.AppendLine('            <nav class="nav-links" aria-label="Main navigation">')
$null = $sb.AppendLine('                <a href="/tools/">Tools</a>')
$null = $sb.AppendLine('                <a href="/compare/">Compare</a>')
$null = $sb.AppendLine('                <a href="/promo/">Promo</a>')
$null = $sb.AppendLine('                <a href="/guides/">Guides</a>')
$null = $sb.AppendLine('                <a href="/about/">About</a>')
$null = $sb.AppendLine('                <a href="/contact/">Contact</a>')
$null = $sb.AppendLine('            </nav>')
$null = $sb.AppendLine('        </div>')
$null = $sb.AppendLine('    </header>')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('    <main id="main-content">')
$null = $sb.AppendLine('        <section class="hero container">')
$null = $sb.AppendLine('            <span class="badge">Site Navigation</span>')
$null = $sb.AppendLine('            <h1>HTML Sitemap</h1>')
$null = $sb.AppendLine('            <p class="lead">A complete, human-readable map of SaaSVerdict pages. Use this page for fast navigation and full content discovery.</p>')
$null = $sb.AppendLine('            <p class="sitemap-meta">Total pages: ' + $pages.Count + ' | Generated: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + '</p>')
$null = $sb.AppendLine('            <div class="hero-actions">')
$null = $sb.AppendLine('                <a class="btn btn-primary" href="/">Open homepage</a>')
$null = $sb.AppendLine('                <a class="btn btn-ghost" href="/sitemap.xml">Open XML sitemap</a>')
$null = $sb.AppendLine('            </div>')
$null = $sb.AppendLine('        </section>')

foreach ($section in $sectionOrder) {
    $group = $pages | Where-Object { $_.section -eq $section }
    if (-not $group -or $group.Count -eq 0) {
        continue
    }

    $null = $sb.AppendLine('        <section class="section container sitemap-section">')
    $null = $sb.AppendLine('            <div class="panel">')
    $null = $sb.AppendLine('                <h2>' + [System.Net.WebUtility]::HtmlEncode($section) + ' (' + $group.Count + ')</h2>')
    $null = $sb.AppendLine('                <ul class="sitemap-list">')

    foreach ($item in ($group | Sort-Object urlPath)) {
        $title = [System.Net.WebUtility]::HtmlEncode($item.title)
        $path = [System.Net.WebUtility]::HtmlEncode($item.urlPath)
        $null = $sb.AppendLine('                    <li><a href="' + $path + '">' + $title + '</a></li>')
    }

    $null = $sb.AppendLine('                </ul>')
    $null = $sb.AppendLine('            </div>')
    $null = $sb.AppendLine('        </section>')
}

$null = $sb.AppendLine('    </main>')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('    <footer class="site-footer">')
$null = $sb.AppendLine('        <div class="container"><p class="small">&copy; <span data-year></span> SaaSVerdict.</p></div>')
$null = $sb.AppendLine('    </footer>')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('    <script src="/assets/js/site.js" defer></script>')
$null = $sb.AppendLine('</body>')
$null = $sb.AppendLine('</html>')

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($outFile, $sb.ToString(), $utf8NoBom)

Write-Output ('generated=' + $outFile)
Write-Output ('page_count=' + $pages.Count)
