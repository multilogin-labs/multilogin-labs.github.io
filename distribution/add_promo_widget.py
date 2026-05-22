#!/usr/bin/env python3
"""
Insert a promo widget (SAAS50 + affiliate link) into all HTML pages under site root.

Usage:
  python distribution/add_promo_widget.py --root . [--dry-run]

This looks for HTML files (skipping `assets` and `distribution`) and inserts
the widget before `</footer>` if present, otherwise before `</body>`, or at
the end of file. It avoids double-inserting by checking a marker comment.
"""
import argparse
from pathlib import Path
import sys

PROMO_OPEN = '<!-- SAASVERDICT_PROMO_WIDGET -->'
PROMO_CLOSE = '<!-- /SAASVERDICT_PROMO_WIDGET -->'

PROMO_HTML = r'''
<!-- SAASVERDICT_PROMO_WIDGET -->
<div class="saas-promo" id="saas-promo" role="region" aria-label="Promo">
  <style>
  .saas-promo{border-top:1px solid #e6e6e6;background:#fff;padding:12px 16px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;font-family:inherit}
  .saas-promo .info{font-size:14px;color:#111}
  .saas-promo .code{font-weight:700;color:#000;padding-left:6px}
  .saas-promo .actions{display:flex;align-items:center;gap:8px}
  .saas-promo .btn{background:#0074D9;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer;font-weight:600}
  .saas-promo .btn:active{transform:scale(.99)}
  .saas-promo .feedback{color:#2d861f;font-weight:600;font-size:13px;display:inline-block;margin-left:8px}
  @media(max-width:640px){.saas-promo{flex-direction:column;align-items:stretch;text-align:center}.saas-promo .actions{justify-content:center}}
  </style>
  <div class="info">Mã giảm giá: <span class="code" id="sv-code">SAAS50</span></div>
  <div class="actions">
    <button type="button" class="btn" id="sv-copy-open" data-code="SAAS50" data-href="https://saasverdict.com/go/multilogin">Copy mã &amp; Mua</button>
    <span class="feedback" id="sv-feedback" aria-live="polite" style="display:none"></span>
  </div>
  <script>
  (function(){
    if(window.__sv_promo_initialized) return; window.__sv_promo_initialized = true;
    function fallbackCopy(text){
      try{
        var ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);ta.focus();ta.select();document.execCommand('copy');document.body.removeChild(ta);return true
      }catch(e){return false}
    }
    function show(msg){var fb=document.getElementById('sv-feedback');if(!fb) return;fb.style.display='inline-block';fb.textContent=msg;setTimeout(function(){fb.style.display='none';fb.textContent=''},2200)}
    var btn=document.getElementById('sv-copy-open');
    if(!btn) return;
    btn.addEventListener('click',function(e){var code=this.getAttribute('data-code')||'SAAS50';var href=this.getAttribute('data-href')||'https://saasverdict.com/go/multilogin';var copied=false;try{copied=fallbackCopy(code)}catch(e){copied=false}if(!copied && navigator.clipboard && navigator.clipboard.writeText){navigator.clipboard.writeText(code).then(function(){show('Đã copy mã')},function(){show('Copy thất bại')})}else{show(copied?'Đã copy mã':'Copy thất bại')}try{var a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';document.body.appendChild(a);a.click();a.remove()}catch(err){window.open(href,'_blank')}
    },false);
  })();
  </script>
</div>
<!-- /SAASVERDICT_PROMO_WIDGET -->
'''


def should_skip(path: Path):
    parts = set(p.lower() for p in path.parts)
    if 'assets' in parts or 'distribution' in parts:
        return True
    return False


def insert_into_html(path: Path, dry_run: bool = False):
    try:
        s = path.read_text(encoding='utf-8')
    except Exception as e:
        print('Error reading', path, e, file=sys.stderr)
        return False
    if PROMO_OPEN in s:
        return False
    # prefer before </footer>, else before </body>, else append
    if '</footer>' in s.lower():
        idx = s.lower().rfind('</footer>')
        new = s[:idx] + PROMO_HTML + s[idx:]
    elif '</body>' in s.lower():
        idx = s.lower().rfind('</body>')
        new = s[:idx] + PROMO_HTML + s[idx:]
    else:
        new = s + PROMO_HTML

    if dry_run:
        print('[dry] would update:', path)
        return True

    try:
        path.write_text(new, encoding='utf-8')
        return True
    except Exception as e:
        print('Error writing', path, e, file=sys.stderr)
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='site root')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    root = Path(args.root)
    html_files = [p for p in root.rglob('*.html') if not should_skip(p)]
    updated = 0
    for f in html_files:
        ok = insert_into_html(f, dry_run=args.dry_run)
        if ok:
            updated += 1
    print('Processed', len(html_files), 'HTML files; updated:', updated)


if __name__ == '__main__':
    main()
