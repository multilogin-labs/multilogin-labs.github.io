param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

$footerMarkup = @'
    <footer class="site-footer">
        <div class="container footer-top-grid">
            <div class="footer-brand-block">
                <a href="/" class="logo">SaaS<span>Verdict</span></a>
                <p class="small">Reliability-first publication for antidetect browser operations, automation workflows, and decision-grade implementation guidance.</p>
                <p class="small">Contact: <a href="mailto:admin@saasverdict.com">admin@saasverdict.com</a></p>
                <div class="footer-badges" aria-label="Publication principles">
                    <span>Updated monthly</span>
                    <span>Evidence-first</span>
                    <span>Implementation-ready</span>
                </div>
            </div>
            <div class="footer-col">
                <p class="footer-title">Start Here</p>
                <div class="footer-links">
                    <a href="/tools/">Tools hub</a>
                    <a href="/compare/">Comparison hub</a>
                    <a href="/guides/">Guides hub</a>
                    <a href="/promo/">Promo verification</a>
                    <a href="/tools/antidetect-browsers/">2026 rankings</a>
                    <a href="/compare/multilogin-alternatives/">Multilogin alternatives</a>
                    <a href="/tools/multilogin-discount/">Discount framework</a>
                </div>
            </div>
            <div class="footer-col">
                <p class="footer-title">Technical Playbooks</p>
                <div class="footer-links">
                    <a href="/guides/multilogin-x-api-playwright/">API + Playwright</a>
                    <a href="/guides/antidetection-ops-sop/">Ops SOP</a>
                    <a href="/guides/detection-tests/">Detection tests</a>
                    <a href="/guides/connection-leak-tests/">Leak tests</a>
                    <a href="/guides/antidetect-libs-playbook/">Anti-detect libs</a>
                    <a href="/guides/mlx-api-hub/">API knowledge hub</a>
                    <a href="/guides/benchmark-reports/">Benchmark reports</a>
                </div>
            </div>
            <div class="footer-col">
                <p class="footer-title">Trust and Company</p>
                <div class="footer-links">
                    <a href="/guides/evaluation-methodology/">Methodology</a>
                    <a href="/guides/methodology-changelog/">Methodology changelog</a>
                    <a href="/editorial-policy/">Editorial policy</a>
                    <a href="/about/">About</a>
                    <a href="/contact/">Contact</a>
                    <a href="/privacy-policy/">Privacy</a>
                    <a href="/terms/">Terms</a>
                </div>
            </div>
        </div>
        <div class="container footer-bottom-row">
            <p class="small">&copy; <span data-year></span> SaaSVerdict. All rights reserved.</p>
            <div class="footer-mini-links">
                <a href="/feeds/lab-updates.xml">Lab updates RSS</a>
                <a href="/sitemap/">HTML sitemap</a>
                <a href="/sitemap.xml">XML sitemap</a>
                <a href="/tools/benchmark-release-checker/">Release checker</a>
                <a href="/guides/">Guides</a>
                <a href="/compare/">Compare</a>
            </div>
        </div>
    </footer>
'@

$pattern = '(?is)<footer class="site-footer">.*?</footer>'

$files = Get-ChildItem -Path $Root -Recurse -File -Filter '*.html' |
    Where-Object {
        $_.FullName -notmatch '\\assets\\' -and
        $_.FullName -notmatch '\\distribution\\'
    }

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$updated = 0
$scanned = 0
$skipped = 0

foreach ($file in $files) {
    $scanned++
    $content = [System.IO.File]::ReadAllText($file.FullName)

    if (-not [regex]::IsMatch($content, $pattern)) {
        $skipped++
        continue
    }

    $newContent = [regex]::Replace($content, $pattern, $footerMarkup, 1)

    if ($newContent -ne $content) {
        [System.IO.File]::WriteAllText($file.FullName, $newContent, $utf8NoBom)
        $updated++
    }
}

Write-Output ('scanned=' + $scanned)
Write-Output ('updated=' + $updated)
Write-Output ('skipped=' + $skipped)
Write-Output ('root=' + $Root)
