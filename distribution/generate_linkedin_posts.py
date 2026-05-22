#!/usr/bin/env python3
import csv
import re
from datetime import date, timedelta
import os

# Files
groups_file = 'Linkedin Group.txt'
output_file = os.path.join('distribution', 'linkedin-posts-en.csv')

# Read groups from file
with open(groups_file, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

groups = []
for line in lines:
    if '|' in line:
        name, link = line.rsplit('|', 1)
        name = name.strip()
        link = link.strip()
    else:
        name = line.strip()
        link = ''
    groups.append((name, link))

# Helpers

def slugify(name):
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s[:60]

benefits = [
    "save hours each week",
    "reduce errors and manual reviews",
    "improve conversion",
    "recover lost revenue",
    "free up time for strategy",
    "scale operations without more hires",
    "speed up reporting and decisions",
    "reduce alert noise and false positives",
    "cut repetitive work and focus on growth",
    "improve monitoring accuracy and actionability",
]

hooks = [
    "Quick tip:",
    "Pro tip:",
    "Heads up:",
    "One quick win:",
    "Short idea:",
    "Try this:",
    "Question:",
    "Here's a shortcut:",
    "A small win:",
    "Want a faster way?",
]

ctas = [
    "Try it free — use code SAAS50 for 50% off:",
    "Start a free trial — apply code SAAS50 for 50% off:",
    "See a quick demo — enter SAAS50 for 50% off:",
    "Get started free — use SAAS50 to save 50%:",
]


def choose_template(name):
    n = name.lower()
    if 'power bi' in n:
        return "Automate anomaly detection and report summaries to {benefit}."
    if 'ai' in n or 'machine' in n or 'ml' in n or 'artificial' in n or 'python' in n:
        return "Deploy and monitor models faster; {benefit}."
    if 'shopify' in n or 'dropshipping' in n or 'ecommerce' in n or 'store' in n:
        return "Automate cart recovery, inventory checks and promos to {benefit}."
    if 'crypto' in n or 'bitcoin' in n:
        return "Filter market noise and surface meaningful signals so you can {benefit}."
    if 'bank' in n or 'fintech' in n or 'banking' in n:
        return "Centralize alerts and compliance automations to {benefit}."
    if 'stock' in n or 'invest' in n or 'portfolio' in n:
        return "Get concise position alerts and summaries to {benefit}."
    if 'internet of things' in n or 'iot' in n or 'device' in n:
        return "Monitor device health and get concise alerts to {benefit}."
    if 'leadership' in n:
        return "Automate routine reports and team alerts so leaders can {benefit}."
    if 'make money' in n:
        return "Automate funnels and follow-ups to {benefit} for online revenue."
    if 'business' in n or 'founder' in n or 'start up' in n or 'startup' in n:
        return "Automate repeatable operations to {benefit} so you can focus on growth."
    if 'big data' in n or 'analytics' in n or 'business intelligence' in n:
        return "Automate anomaly detection and report delivery to {benefit} across datasets."
    return "Automate repetitive tasks to {benefit}."

# Generate posts
start_date = date(2026, 5, 1)
num_days = 365
rows = []
for i in range(num_days):
    day = start_date + timedelta(days=i)
    day_str = day.isoformat()
    group_name, group_link = groups[i % len(groups)]
    slug = slugify(group_name)
    hook = hooks[i % len(hooks)]
    benefit = benefits[(i // 10) % len(benefits)]
    cta = ctas[(i // 100) % len(ctas)]
    template = choose_template(group_name)
    post = f"{hook} {template.format(benefit=benefit)} {cta}"
    tracking_link = f"https://saasverdict.com/?utm_source=linkedin&utm_medium=group&utm_campaign=SAAS50&utm_content={slug}&utm_date={day.strftime('%Y%m%d')}"
    rows.append([day_str, group_name, group_link, "EN", post, tracking_link, ""])

# Write CSV
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['date','group_name','group_link','language','post_text','tracking_link','image'])
    writer.writerows(rows)

print(f"Wrote {len(rows)} posts to {output_file}")
