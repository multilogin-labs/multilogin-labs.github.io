#!/usr/bin/env python3
"""Single redirect stub template (noindex + canonical). Used by seo_optimize and migrate_site."""
from __future__ import annotations

REDIRECT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="robots" content="noindex,follow"/>
<meta http-equiv="refresh" content="0;url={url}"/>
<link rel="canonical" href="{canonical}"/>
<title>Moved: {title} | multilogin-labs</title>
</head>
<body>
<p>This URL has moved. <a href="{url}">{link_label}</a></p>
</body>
</html>
"""
