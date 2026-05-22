param(
    [string]$SourceRoot = 'Tham Khao 2',
    [string]$GuidesHubSlug = 'mlx-api-hub',
    [string]$SiteBaseUrl = 'https://saasverdict.com',
    [int]$CategorySlugMaxLen = 22,
    [int]$ArticleSlugMaxLen = 30,
    [int]$ImageNameHashLen = 6,
    [string[]]$Categories,
    [switch]$AllCategories
)

$ErrorActionPreference = 'Stop'

function Clean-Text([string]$inputText) {
    if ([string]::IsNullOrWhiteSpace($inputText)) { return '' }
    $x = [System.Net.WebUtility]::HtmlDecode($inputText)
    $x = [regex]::Replace($x, '<[^>]+>', ' ')
    $x = $x -replace '\s+', ' '
    return $x.Trim()
}

function Escape-Html([string]$inputText) {
    if ($null -eq $inputText) { return '' }
    return [System.Net.WebUtility]::HtmlEncode($inputText)
}

function Truncate-Slug([string]$slug, [int]$maxLength) {
    if ([string]::IsNullOrWhiteSpace($slug)) { return 'untitled' }
    if ($maxLength -lt 8) { $maxLength = 8 }
    if ($slug.Length -le $maxLength) { return $slug }

    $cut = $slug.Substring(0, $maxLength).Trim('-')
    if ([string]::IsNullOrWhiteSpace($cut)) { return 'untitled' }
    return $cut
}

function Get-ShortHash([string]$inputText, [int]$length = 6) {
    if ([string]::IsNullOrWhiteSpace($inputText)) { return '000000' }
    if ($length -lt 4) { $length = 4 }
    if ($length -gt 12) { $length = 12 }

    $sha1 = [System.Security.Cryptography.SHA1]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($inputText)
        $hashBytes = $sha1.ComputeHash($bytes)
    }
    finally {
        $sha1.Dispose()
    }

    $hex = ([System.BitConverter]::ToString($hashBytes)).Replace('-', '').ToLowerInvariant()
    if ($length -gt $hex.Length) { $length = $hex.Length }
    return $hex.Substring(0, $length)
}

function Slugify([string]$inputText, [int]$MaxLength = 80) {
    $x = Clean-Text($inputText).ToLowerInvariant()
    $x = $x -replace '&', ' and '
    $x = $x -replace '\+', ' plus '
    $x = $x -replace '[^a-z0-9]+', '-'
    $x = $x.Trim('-')
    if ([string]::IsNullOrWhiteSpace($x)) { return 'untitled' }
    return Truncate-Slug -slug $x -maxLength $MaxLength
}

function Ensure-UniqueSlug {
    param(
        [string]$InputText,
        [System.Collections.Generic.HashSet[string]]$UsedSlugs,
        [string]$Seed,
        [int]$MaxLength = 30
    )

    $core = Slugify -inputText $InputText -MaxLength $MaxLength
    if (-not $UsedSlugs.Contains($core)) {
        $UsedSlugs.Add($core) | Out-Null
        return $core
    }

    $hashSuffix = '-' + (Get-ShortHash -inputText $Seed -length 6)
    $baseLimit = [Math]::Max(8, $MaxLength - $hashSuffix.Length)
    $candidate = (Truncate-Slug -slug $core -maxLength $baseLimit) + $hashSuffix
    if (-not $UsedSlugs.Contains($candidate)) {
        $UsedSlugs.Add($candidate) | Out-Null
        return $candidate
    }

    $counter = 2
    while ($true) {
        $counterSuffix = '-' + $counter
        $baseLimit = [Math]::Max(8, $MaxLength - $hashSuffix.Length - $counterSuffix.Length)
        $candidate = (Truncate-Slug -slug $core -maxLength $baseLimit) + $hashSuffix + $counterSuffix
        if (-not $UsedSlugs.Contains($candidate)) {
            $UsedSlugs.Add($candidate) | Out-Null
            return $candidate
        }
        $counter++
    }
}

function Build-ArticlePage {
    param(
        [string]$Title,
        [string]$Description,
        [string]$Canonical,
        [string]$CategoryName,
        [string]$CategorySlug,
        [string]$ArticleSlug,
        [string[]]$Outline,
        [string[]]$ImageWebPaths,
        [string]$SiteBaseUrl,
        [string]$GuidesHubSlug
    )

    $safeTitle = Escape-Html($Title)
    $safeDescription = Escape-Html($Description)
    $safeCategoryName = Escape-Html($CategoryName)
    $safeCanonical = Escape-Html($Canonical)

    $outlineItems = ''
    if ($Outline.Count -gt 0) {
        $outlineItems = ($Outline | ForEach-Object { "                    <li>$(Escape-Html($_))</li>" }) -join "`r`n"
    }
    else {
        $outlineItems = '                    <li>Define the API objective and expected result contract.</li>' + "`r`n" +
                        '                    <li>Map required parameters, authentication context, and timeout policy.</li>' + "`r`n" +
                        '                    <li>Validate outputs with repeat-session evidence and rollback notes.</li>'
    }

    $imageSection = ''
    if ($ImageWebPaths.Count -gt 0) {
        $imageCards = @()
        $index = 0
        foreach ($imgPath in $ImageWebPaths) {
            $index++
            $safeImgPath = Escape-Html($imgPath)
            $safeAlt = Escape-Html("$Title reference visual $index")
            $imageCards += @"
                <figure class="card">
                    <img src="$safeImgPath" alt="$safeAlt" loading="lazy">
                    <figcaption class="small">Reference visual $index adapted into this rewritten playbook.</figcaption>
                </figure>
"@
        }

        $imageSection = @"
        <section class="section">
            <p class="section-kicker">Reference Visual Set</p>
            <h2>Local SEO-Renamed Images</h2>
            <div class="grid-3">
$($imageCards -join "`r`n")
            </div>
        </section>
"@
    }

    return @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$safeTitle | SaaSVerdict</title>
    <meta name="description" content="$safeDescription">
    <meta name="robots" content="index,follow,max-image-preview:large">
    <link rel="canonical" href="$safeCanonical">
    <meta property="og:title" content="$safeTitle | SaaSVerdict">
    <meta property="og:description" content="$safeDescription">
    <meta property="og:url" content="$safeCanonical">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="SaaSVerdict">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="$safeTitle | SaaSVerdict">
    <meta name="twitter:description" content="$safeDescription">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/site.css">
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "TechArticle",
          "headline": "$safeTitle",
          "dateModified": "$(Get-Date -Format 'yyyy-MM-dd')",
          "author": {"@type": "Organization", "name": "SaaSVerdict"},
          "publisher": {"@type": "Organization", "name": "SaaSVerdict"},
          "mainEntityOfPage": "$safeCanonical"
        },
        {
          "@type": "BreadcrumbList",
          "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "$SiteBaseUrl/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": "$SiteBaseUrl/guides/"},
            {"@type": "ListItem", "position": 3, "name": "API Knowledge Hub", "item": "$SiteBaseUrl/guides/$GuidesHubSlug/"},
            {"@type": "ListItem", "position": 4, "name": "$safeCategoryName", "item": "$SiteBaseUrl/guides/$GuidesHubSlug/$CategorySlug/"},
            {"@type": "ListItem", "position": 5, "name": "$safeTitle", "item": "$safeCanonical"}
          ]
        }
      ]
    }
    </script>
</head>
<body>
    <a class="skip-link" href="#main-content">Skip to main content</a>

    <header class="site-header">
        <div class="container nav-wrap">
            <a href="/" class="logo">SaaS<span>Verdict</span></a>
            <nav class="nav-links" aria-label="Main navigation">
                <a href="/tools/">Tools</a>
                <a href="/compare/">Compare</a>
                <a href="/promo/">Promo</a>
                <a href="/guides/" aria-current="page">Guides</a>
                <a href="/about/">About</a>
                <a href="/contact/">Contact</a>
            </nav>
        </div>
    </header>

    <main id="main-content" class="container">
        <p class="breadcrumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / <a href="/guides/$GuidesHubSlug/">API Knowledge Hub</a> / <a href="/guides/$GuidesHubSlug/$CategorySlug/">$safeCategoryName</a> / $safeTitle</p>

        <section class="hero">
            <span class="badge">Rewritten API Playbook</span>
            <h1>$safeTitle</h1>
            <p class="lead">$safeDescription</p>
            <p class="hero-meta">Updated: $(Get-Date -Format 'yyyy-MM-dd') | Source category: $safeCategoryName | This page is an original SaaSVerdict rewrite from internal reference material.</p>
        </section>

        <section class="section">
            <div class="panel">
                <p class="section-kicker">How This Page Was Built</p>
                <h2>Original Rewrite Workflow</h2>
                <p>We extracted topic structure from archived API help material and rewrote this page into an operations-first playbook format for SaaSVerdict readers.</p>
                <div class="timeline">
                    <div class="timeline-step"><b>Step 1:</b> Capture topic intent, endpoints, and setup constraints.</div>
                    <div class="timeline-step"><b>Step 2:</b> Normalize workflow into repeatable implementation sequence.</div>
                    <div class="timeline-step"><b>Step 3:</b> Add reliability checkpoints and failure handling notes.</div>
                    <div class="timeline-step"><b>Step 4:</b> Route to compare and promo pages only after evidence gates pass.</div>
                </div>
            </div>
        </section>

        <section class="section">
            <p class="section-kicker">Extracted Topic Outline</p>
            <h2>Key Concepts to Implement</h2>
            <ul class="clean">
$outlineItems
            </ul>
        </section>

        <section class="section">
            <div class="panel">
                <p class="section-kicker">Implementation Checklist</p>
                <h2>Minimum Production Gates</h2>
                <ul class="clean">
                    <li>Define API payload schema and required auth context before execution.</li>
                    <li>Set timeout and retry classes for start, run, and cleanup phases.</li>
                    <li>Log trace_id, workspace_id, profile_id, and error class per run.</li>
                    <li>Repeat validation sessions before scaling or recommending any tool.</li>
                    <li>Store evidence summary for decision transparency and affiliate trust.</li>
                </ul>
            </div>
        </section>

$imageSection

        <section class="section">
            <div class="panel">
                <p class="section-kicker">Decision Path</p>
                <h2>After Technical Validation</h2>
                <p>When this workflow is stable, route readers into commercial pages with clear criteria to improve conversion quality and reduce low-fit purchases.</p>
                <div class="hero-actions">
                    <a class="btn btn-primary" href="/compare/multilogin-alternatives/">Open alternatives comparison</a>
                    <a class="btn btn-ghost" href="/promo/">Open promo verification hub</a>
                    <a class="btn btn-ghost" href="/guides/antidetect-browser-pricing-playbook/">Open pricing playbook</a>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="panel">
                <h2>Related Pages</h2>
                <div class="related-links" aria-label="Related links">
                    <a href="/guides/$GuidesHubSlug/">API knowledge hub</a>
                    <a href="/guides/$GuidesHubSlug/$CategorySlug/">$safeCategoryName category hub</a>
                    <a href="/guides/multilogin-x-script-runner-playbook/">Script runner playbook</a>
                    <a href="/guides/workspace-id-and-token-setup-runbook/">Workspace and token setup runbook</a>
                    <a href="/tools/evidence-pack-builder/">Evidence pack builder</a>
                </div>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="container"><p class="small">&copy; <span data-year></span> SaaSVerdict.</p></div>
    </footer>

    <script src="/assets/js/site.js" defer></script>
</body>
</html>
"@
}

function Build-CategoryHubPage {
    param(
        [string]$CategoryName,
        [string]$CategorySlug,
        [array]$ArticleRows,
        [string]$SiteBaseUrl,
        [string]$GuidesHubSlug
    )

    $safeCategoryName = Escape-Html($CategoryName)
    $cards = @()
    foreach ($row in $ArticleRows) {
        $cards += @"
                <article class="card">
                    <h3>$(Escape-Html($row.page_title))</h3>
                    <p>$(Escape-Html($row.meta_description))</p>
                    <a href="$($row.target_url_path)">Open playbook</a>
                </article>
"@
    }

    return @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$safeCategoryName API Playbooks | SaaSVerdict</title>
    <meta name="description" content="Rewritten API guides for $safeCategoryName with SEO-renamed local images and operations-first checklists.">
    <meta name="robots" content="index,follow,max-image-preview:large">
    <link rel="canonical" href="$SiteBaseUrl/guides/$GuidesHubSlug/$CategorySlug/">
    <meta property="og:title" content="$safeCategoryName API Playbooks">
    <meta property="og:description" content="Original SaaSVerdict rewrites from internal API reference archives.">
    <meta property="og:url" content="$SiteBaseUrl/guides/$GuidesHubSlug/$CategorySlug/">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="SaaSVerdict">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="$safeCategoryName API Playbooks">
    <meta name="twitter:description" content="Category hub with rewritten operational guides and SEO-organized image assets.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
    <a class="skip-link" href="#main-content">Skip to main content</a>

    <header class="site-header">
        <div class="container nav-wrap">
            <a href="/" class="logo">SaaS<span>Verdict</span></a>
            <nav class="nav-links" aria-label="Main navigation">
                <a href="/tools/">Tools</a>
                <a href="/compare/">Compare</a>
                <a href="/promo/">Promo</a>
                <a href="/guides/" aria-current="page">Guides</a>
                <a href="/about/">About</a>
                <a href="/contact/">Contact</a>
            </nav>
        </div>
    </header>

    <main id="main-content" class="container">
        <p class="breadcrumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / <a href="/guides/$GuidesHubSlug/">API Knowledge Hub</a> / $safeCategoryName</p>

        <section class="hero">
            <span class="badge">Category Hub</span>
            <h1>$safeCategoryName API Playbooks</h1>
            <p class="lead">Rewritten and structured implementation guides for this API category, with SEO-normalized local image assets.</p>
            <p class="hero-meta">Articles: $($ArticleRows.Count) | Updated: $(Get-Date -Format 'yyyy-MM-dd')</p>
        </section>

        <section class="section">
            <p class="section-kicker">Articles</p>
            <h2>Category Guide Set</h2>
            <div class="grid-3">
$($cards -join "`r`n")
            </div>
        </section>

        <section class="section">
            <div class="panel">
                <h2>Related Navigation</h2>
                <div class="related-links" aria-label="Related links">
                    <a href="/guides/$GuidesHubSlug/">API knowledge hub</a>
                    <a href="/guides/multilogin-x-open-source-blueprints/">Open-source blueprints hub</a>
                    <a href="/compare/multilogin-alternatives/">Multilogin alternatives</a>
                    <a href="/promo/">Promo verification hub</a>
                </div>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="container"><p class="small">&copy; <span data-year></span> SaaSVerdict.</p></div>
    </footer>

    <script src="/assets/js/site.js" defer></script>
</body>
</html>
"@
}

function Build-MainHubPage {
    param(
        [array]$CategoryRows,
        [string]$SiteBaseUrl,
        [string]$GuidesHubSlug,
        [int]$TotalArticles,
        [int]$TotalImages
    )

    $cards = @()
    foreach ($row in $CategoryRows) {
        $cards += @"
                <article class="card">
                    <h3>$(Escape-Html($row.category_name))</h3>
                    <p>Articles: $($row.article_count) | Local images: $($row.image_count)</p>
                    <a href="/guides/$GuidesHubSlug/$($row.category_slug)/">Open category hub</a>
                </article>
"@
    }

    return @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multilogin API Knowledge Hub 2026: Rewritten Playbooks | SaaSVerdict</title>
    <meta name="description" content="SaaSVerdict API knowledge hub with rewritten Multilogin-related guide content, SEO-renamed local images, and operations-first implementation checklists.">
    <meta name="robots" content="index,follow,max-image-preview:large">
    <link rel="canonical" href="$SiteBaseUrl/guides/$GuidesHubSlug/">
    <meta property="og:title" content="Multilogin API Knowledge Hub 2026">
    <meta property="og:description" content="Rewritten category-by-category playbooks from internal API reference archives.">
    <meta property="og:url" content="$SiteBaseUrl/guides/$GuidesHubSlug/">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="SaaSVerdict">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Multilogin API Knowledge Hub 2026">
    <meta name="twitter:description" content="Category hubs for CLI, Postman, script runner, browser automation, and migration playbooks.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
    <a class="skip-link" href="#main-content">Skip to main content</a>

    <header class="site-header">
        <div class="container nav-wrap">
            <a href="/" class="logo">SaaS<span>Verdict</span></a>
            <nav class="nav-links" aria-label="Main navigation">
                <a href="/tools/">Tools</a>
                <a href="/compare/">Compare</a>
                <a href="/promo/">Promo</a>
                <a href="/guides/" aria-current="page">Guides</a>
                <a href="/about/">About</a>
                <a href="/contact/">Contact</a>
            </nav>
        </div>
    </header>

    <main id="main-content" class="container">
        <p class="breadcrumb"><a href="/">Home</a> / <a href="/guides/">Guides</a> / API Knowledge Hub</p>

        <section class="hero">
            <span class="badge">Large Content Conversion Hub</span>
            <h1>Multilogin API Knowledge Hub</h1>
            <p class="lead">This hub contains category-by-category rewritten playbooks generated from internal archived API help materials, transformed into SaaSVerdict operational format.</p>
            <p class="hero-meta">Categories: $($CategoryRows.Count) | Articles: $TotalArticles | Local SEO images: $TotalImages | Updated: $(Get-Date -Format 'yyyy-MM-dd')</p>
        </section>

        <section class="section">
            <p class="section-kicker">Category Hubs</p>
            <h2>Browse by Automation Modality</h2>
            <div class="grid-3">
$($cards -join "`r`n")
            </div>
        </section>

        <section class="section">
            <div class="panel">
                <p class="section-kicker">Commercial Path</p>
                <h2>Use Technical Proof Before Checkout</h2>
                <p>Each rewritten guide is designed to build implementation trust first, then route users to comparison and promo pages with better conversion quality.</p>
                <div class="hero-actions">
                    <a class="btn btn-primary" href="/compare/multilogin-alternatives/">Open alternatives comparison</a>
                    <a class="btn btn-ghost" href="/promo/">Open promo verification hub</a>
                    <a class="btn btn-ghost" href="/tools/evidence-pack-builder/">Generate evidence pack</a>
                </div>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="container"><p class="small">&copy; <span data-year></span> SaaSVerdict.</p></div>
    </footer>

    <script src="/assets/js/site.js" defer></script>
</body>
</html>
"@
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceBase = Join-Path $repoRoot $SourceRoot
if (-not (Test-Path -LiteralPath $sourceBase)) {
    throw "Source root not found: $sourceBase"
}

if (-not $AllCategories -and (-not $Categories -or $Categories.Count -eq 0)) {
    throw 'Provide -AllCategories or one or more -Categories values.'
}

$categoryNames = @()
if ($AllCategories) {
    $categoryNames = Get-ChildItem -LiteralPath $sourceBase -Directory | Sort-Object Name | Select-Object -ExpandProperty Name
}
else {
    $categoryNames = $Categories
}

$guidesBase = Join-Path $repoRoot ('guides\' + $GuidesHubSlug)
$assetsBase = Join-Path $repoRoot ('assets\img\guides\' + $GuidesHubSlug)
New-Item -ItemType Directory -Force -Path $guidesBase | Out-Null
New-Item -ItemType Directory -Force -Path $assetsBase | Out-Null

$manifestRows = [System.Collections.Generic.List[object]]::new()
$categoryRows = [System.Collections.Generic.List[object]]::new()
$usedCategorySlugs = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

$totalArticles = 0
$totalImages = 0

$ignoreHeadingWords = @('website', 'server status', 'api documentation', 'blog', 'community', 'english', 'home', 'contact', 'login')

foreach ($categoryName in $categoryNames) {
    $sourceCategoryPath = Join-Path $sourceBase $categoryName
    if (-not (Test-Path -LiteralPath $sourceCategoryPath)) {
        Write-Warning "Category path not found, skipping: $sourceCategoryPath"
        continue
    }

    $categorySlug = Ensure-UniqueSlug -InputText $categoryName -UsedSlugs $usedCategorySlugs -Seed $categoryName -MaxLength $CategorySlugMaxLen
    $categoryGuideDir = Join-Path $guidesBase $categorySlug
    $categoryAssetDir = Join-Path $assetsBase $categorySlug
    New-Item -ItemType Directory -Force -Path $categoryGuideDir | Out-Null
    New-Item -ItemType Directory -Force -Path $categoryAssetDir | Out-Null

    $htmlFiles = Get-ChildItem -LiteralPath $sourceCategoryPath -File -Filter *.html | Sort-Object Name
    $categoryArticles = [System.Collections.Generic.List[object]]::new()
    $categoryImageCount = 0
    $usedArticleSlugs = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    foreach ($htmlFile in $htmlFiles) {
        $rawHtml = Get-Content -Raw -LiteralPath $htmlFile.FullName

        $fileBase = [System.IO.Path]::GetFileNameWithoutExtension($htmlFile.Name)
        $baseTitle = ($fileBase -replace '\s*-\s*Multilogin\s*$', '').Trim()

        $titleMatch = [regex]::Match($rawHtml, '(?is)<title>\s*(.*?)\s*</title>')
        $sourceTitle = if ($titleMatch.Success) { Clean-Text($titleMatch.Groups[1].Value) } else { $baseTitle }
        $sourceTitle = ($sourceTitle -replace '\s*-\s*Multilogin\s*$', '').Trim()
        if ([string]::IsNullOrWhiteSpace($sourceTitle)) { $sourceTitle = $baseTitle }

        $descMatch = [regex]::Match($rawHtml, '(?is)<meta[^>]*name=["'']description["''][^>]*content=["''](.*?)["'']')
        $description = if ($descMatch.Success) { Clean-Text($descMatch.Groups[1].Value) } else { "Practical implementation playbook rewritten by SaaSVerdict for $sourceTitle." }

        $canonicalMatch = [regex]::Match($rawHtml, '(?is)<link[^>]*rel=["'']canonical["''][^>]*href=["''](.*?)["'']')
        $sourceCanonical = if ($canonicalMatch.Success) { $canonicalMatch.Groups[1].Value.Trim() } else { '' }

        $articleSlug = Ensure-UniqueSlug -InputText $baseTitle -UsedSlugs $usedArticleSlugs -Seed $htmlFile.FullName -MaxLength $ArticleSlugMaxLen
        $targetArticleDir = Join-Path $categoryGuideDir $articleSlug
        New-Item -ItemType Directory -Force -Path $targetArticleDir | Out-Null

        $targetAssetArticleDir = Join-Path $categoryAssetDir $articleSlug
        New-Item -ItemType Directory -Force -Path $targetAssetArticleDir | Out-Null
        $articleHash = Get-ShortHash -inputText $htmlFile.FullName -length $ImageNameHashLen

        $headingMatches = [regex]::Matches($rawHtml, '(?is)<h[1-3][^>]*>(.*?)</h[1-3]>')
        $outline = [System.Collections.Generic.List[string]]::new()
        foreach ($hm in $headingMatches) {
            $text = Clean-Text($hm.Groups[1].Value)
            if ($text.Length -lt 10) { continue }
            $lc = $text.ToLowerInvariant()
            if ($ignoreHeadingWords -contains $lc) { continue }
            if ($outline -notcontains $text) {
                $outline.Add($text)
            }
            if ($outline.Count -ge 8) { break }
        }

        $imgMatches = [regex]::Matches($rawHtml, '(?is)src=["''](\./[^"'']+_files/[^"'']+\.(png|jpe?g|webp|gif|svg|avif))["'']')
        $localImageSrc = $imgMatches | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique

        $copiedImageWebPaths = [System.Collections.Generic.List[string]]::new()
        $imgIndex = 0
        foreach ($imgSrc in $localImageSrc) {
            $relImgPath = $imgSrc -replace '^\./', ''
            $sourceImagePath = Join-Path $sourceCategoryPath $relImgPath
            if (-not (Test-Path -LiteralPath $sourceImagePath)) { continue }

            $ext = [System.IO.Path]::GetExtension($sourceImagePath).ToLowerInvariant()
            $imgIndex++
            $newImgName = ('img-{0}-{1:d3}{2}' -f $articleHash, $imgIndex, $ext)
            $targetImagePath = Join-Path $targetAssetArticleDir $newImgName
            Copy-Item -LiteralPath $sourceImagePath -Destination $targetImagePath -Force

            $webPath = '/assets/img/guides/' + $GuidesHubSlug + '/' + $categorySlug + '/' + $articleSlug + '/' + $newImgName
            $copiedImageWebPaths.Add($webPath)
        }

        $canonical = "$SiteBaseUrl/guides/$GuidesHubSlug/$categorySlug/$articleSlug/"
        $pageContent = Build-ArticlePage -Title $sourceTitle -Description $description -Canonical $canonical -CategoryName $categoryName -CategorySlug $categorySlug -ArticleSlug $articleSlug -Outline @($outline) -ImageWebPaths @($copiedImageWebPaths) -SiteBaseUrl $SiteBaseUrl -GuidesHubSlug $GuidesHubSlug

        Set-Content -LiteralPath (Join-Path $targetArticleDir 'index.html') -Value $pageContent -Encoding UTF8

        $targetUrlPath = '/guides/' + $GuidesHubSlug + '/' + $categorySlug + '/' + $articleSlug + '/'
        $categoryArticles.Add([pscustomobject]@{
            page_title = $sourceTitle
            page_slug = $articleSlug
            target_url_path = $targetUrlPath
            meta_description = $description
            images_copied = $copiedImageWebPaths.Count
        })

        $manifestRows.Add([pscustomobject]@{
            category_name = $categoryName
            category_slug = $categorySlug
            source_html = $htmlFile.FullName.Substring($repoRoot.Length + 1).Replace('\\', '/')
            source_canonical = $sourceCanonical
            page_title = $sourceTitle
            page_slug = $articleSlug
            target_url = $canonical
            target_path = ('guides/' + $GuidesHubSlug + '/' + $categorySlug + '/' + $articleSlug + '/index.html')
            images_copied = $copiedImageWebPaths.Count
        })

        $totalArticles++
        $totalImages += $copiedImageWebPaths.Count
        $categoryImageCount += $copiedImageWebPaths.Count
    }

    $categoryHubContent = Build-CategoryHubPage -CategoryName $categoryName -CategorySlug $categorySlug -ArticleRows @($categoryArticles) -SiteBaseUrl $SiteBaseUrl -GuidesHubSlug $GuidesHubSlug
    Set-Content -LiteralPath (Join-Path $categoryGuideDir 'index.html') -Value $categoryHubContent -Encoding UTF8

    $categoryRows.Add([pscustomobject]@{
        category_name = $categoryName
        category_slug = $categorySlug
        article_count = $categoryArticles.Count
        image_count = $categoryImageCount
        hub_url = "$SiteBaseUrl/guides/$GuidesHubSlug/$categorySlug/"
    })
}

$mainHubContent = Build-MainHubPage -CategoryRows @($categoryRows) -SiteBaseUrl $SiteBaseUrl -GuidesHubSlug $GuidesHubSlug -TotalArticles $totalArticles -TotalImages $totalImages
Set-Content -LiteralPath (Join-Path $guidesBase 'index.html') -Value $mainHubContent -Encoding UTF8

$manifestPath = Join-Path $repoRoot 'distribution\multilogin-api-knowledge-import-manifest.csv'
$manifestRows | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding UTF8

Write-Output ('categories=' + $categoryRows.Count)
Write-Output ('articles=' + $totalArticles)
Write-Output ('images=' + $totalImages)
Write-Output ('main_hub=' + (Join-Path $guidesBase 'index.html'))
Write-Output ('manifest=' + $manifestPath)
