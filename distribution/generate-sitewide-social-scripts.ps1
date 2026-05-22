$ErrorActionPreference = 'Stop'

$root = 'c:\Users\Dalatmilkshop\Documents\GitHub\saasverdict.com'
$baseUrl = 'https://saasverdict.com'
$outCsv = Join-Path $root 'distribution\sitewide-social-scripts-en.csv'
$outTxt = Join-Path $root 'distribution\sitewide-social-scripts-en.txt'

function Get-MetaDescription([string]$html) {
    $m = [regex]::Match($html, '(?is)<meta[^>]*name=["'']description["''][^>]*content=["''](.*?)["'']')
    if ($m.Success) { return $m.Groups[1].Value.Trim() }

    $m = [regex]::Match($html, '(?is)<meta[^>]*content=["''](.*?)["''][^>]*name=["'']description["'']')
    if ($m.Success) { return $m.Groups[1].Value.Trim() }

    return ''
}

function Clean([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return '' }
    $x = $s -replace '\s+', ' '
    $x = $x -replace '[\r\n]', ' '
    return $x.Trim()
}

function Build-Post([string]$platform, [string]$title, [string]$desc, [string]$url) {
    $t = Clean($title)
    $d = Clean($desc)
    if (-not $d) {
        $d = 'Practical guide with actionable takeaways.'
    }

    switch ($platform) {
        'Facebook Page' {
            return "Looking into $($t)? $($d) Read the full guide: $($url). Comment 'checklist' if you want a quick evaluation sheet."
        }
        'Facebook Group' {
            return "Community question: what is your top decision factor for $($t)? I summarized the key points here: $($url). $($d) Share your real-world experience in the comments."
        }
        'LinkedIn' {
            return "If your team is evaluating $($t), this breakdown can save decision time. $($d) Full article: $($url). Reply 'template' if you want a scoring framework."
        }
        'X (Twitter)' {
            return "Evaluating $($t)? Start with decision quality, not only price. Key guide: $($url). $($d)"
        }
        'Reddit' {
            return "I reviewed this topic and documented a practical framework: $($t). $($d) Link: $($url). Curious what worked best for your workflow."
        }
        'Telegram Channel' {
            return "Quick resource: $($t). $($d) Read here: $($url). Reply if you want a condensed checklist version."
        }
        'Zalo OA' {
            return "New resource published: $($t). $($d) Read now: $($url). Message us to get the quick checklist."
        }
        'YouTube Community' {
            return "New guide is live: $($t). $($d) Read here: $($url). Comment if you want a video walkthrough."
        }
        'TikTok' {
            return "Hook: Stop guessing on $($t). Body: Use a clear framework and compare options with evidence. CTA: Full guide in bio link: $($url)."
        }
        'Email Newsletter' {
            return "Subject: New guide - $($t) Body: Hi, we published a practical breakdown on this topic. $($d) Read the full article: $($url)."
        }
        default {
            return "$($t) - $($d) $($url)"
        }
    }
}

$platforms = @(
    @{ Name = 'Facebook Page'; Format = 'Feed post' },
    @{ Name = 'Facebook Group'; Format = 'Discussion post' },
    @{ Name = 'LinkedIn'; Format = 'Professional post' },
    @{ Name = 'X (Twitter)'; Format = 'Single post' },
    @{ Name = 'Reddit'; Format = 'Title + body' },
    @{ Name = 'Telegram Channel'; Format = 'Channel post' },
    @{ Name = 'Zalo OA'; Format = 'OA broadcast' },
    @{ Name = 'YouTube Community'; Format = 'Community post' },
    @{ Name = 'TikTok'; Format = '30-40s script' },
    @{ Name = 'Email Newsletter'; Format = 'Subject + body' }
)

$files = Get-ChildItem -Path $root -Recurse -File -Filter index.html |
    Where-Object {
        $_.FullName -notmatch '\\assets\\' -and
        $_.FullName -notmatch '\\distribution\\'
    } |
    Sort-Object FullName

$rows = [System.Collections.Generic.List[object]]::new()
$txt = [System.Collections.Generic.List[string]]::new()
$pageIndex = 0

foreach ($file in $files) {
    $pageIndex++

    $rel = $file.FullName.Substring($root.Length + 1).Replace('\', '/')

    if ($rel -eq 'index.html') {
        $urlPath = '/'
    }
    else {
        $parent = (Split-Path $rel -Parent).Replace('\', '/').Trim('/')
        $urlPath = '/' + $parent + '/'
    }

    $url = $baseUrl + $urlPath
    $html = Get-Content -Raw -LiteralPath $file.FullName

    $titleMatch = [regex]::Match($html, '(?is)<title>\s*(.*?)\s*</title>')
    if ($titleMatch.Success) {
        $title = Clean($titleMatch.Groups[1].Value)
    }
    else {
        if ($urlPath -eq '/') {
            $title = 'Home'
        }
        else {
            $title = ((Split-Path $urlPath.Trim('/') -Leaf) -replace '-', ' ')
        }
    }

    $desc = Clean((Get-MetaDescription $html))

    $txt.Add("==== PAGE $pageIndex ====")
    $txt.Add("Title: $title")
    $txt.Add("URL: $url")
    $txt.Add('')

    foreach ($p in $platforms) {
        $post = Build-Post -platform $p.Name -title $title -desc $desc -url $url

        $rows.Add([pscustomobject]@{
            page_id = $pageIndex
            page_title = $title
            page_url = $url
            platform = $p.Name
            format = $p.Format
            post_copy = $post
        })

        $txt.Add("[$($p.Name)]")
        $txt.Add($post)
        $txt.Add('')
    }
}

$rows | Export-Csv -NoTypeInformation -Encoding UTF8 -LiteralPath $outCsv

$header = @(
    'SITEWIDE ENGLISH SOCIAL SCRIPTS',
    "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "Total pages: $($files.Count)",
    "Platforms per page: $($platforms.Count)",
    "Total scripts: $($rows.Count)",
    ''
)

Set-Content -LiteralPath $outTxt -Value ($header + $txt) -Encoding UTF8

Write-Output "pages=$($files.Count)"
Write-Output "platforms=$($platforms.Count)"
Write-Output "scripts=$($rows.Count)"
Write-Output "csv=$outCsv"
Write-Output "txt=$outTxt"
