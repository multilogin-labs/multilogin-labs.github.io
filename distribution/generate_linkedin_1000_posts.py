#!/usr/bin/env python3
import csv
import os
from datetime import date, timedelta

OUTPUT_FILE = os.path.join('distribution', 'linkedin-5000-posts-en.csv')
TOTAL_POSTS = 5000
BASE_URL = 'https://saasverdict.com/go/multilogin'

hooks = [
    'Quick update:',
    'Pro tip for browser ops teams:',
    'Short reminder:',
    'Insight for automation engineers:',
    'If you care about multi-account reliability, note this:',
    'Smart operators do this:',
    'Today’s note on browser privacy:',
    'Here’s a strong rule for scale:',
    'A practical take:',
    'If you manage accounts at scale, this helps:',
]

pain_points = [
    'browser fingerprint drift under repeated runs',
    'promo claims with no proof',
    'fragile profile consistency',
    'API connection failures during scale',
    'manual discount checks before checkout',
    'privacy leaks in multi-account browsers',
    'team handoff friction with operational stacks',
    'unreliable anti-detect browser setup',
    'high subscription cost without a proper comparison',
    'unclear vendor tradeoffs for automation projects',
]

solution_framings = [
    'reliability-first comparisons beat feature lists when you want a stable stack',
    'promo verification keeps you from paying full price for unreliable claims',
    'a decision workflow is better than chasing every new tool',
    'API runbooks reduce downtime and release risk',
    'evidence-based guides make affiliate recommendations credible and sustainable',
    'browser privacy checks should include worker thread parity',
    'discounts perform better when shared with trust and context',
    'tool selection should prioritize profile stability and operational cost',
    'multi-account operations need both privacy controls and workflow quality',
    'automation scaling succeeds when you verify every new browser profile path',
]

benefits = [
    'save time on proof-of-concept and checkout due diligence',
    'avoid expensive surprises during browser stack migration',
    'build a durable affiliate funnel based on real QA',
    'keep browser sessions stable across repeating workflows',
    'convert more audiences by sharing trusted coupon evidence',
    'reduce risk in paid account operations',
    'stay in compliance while still selling privacy-first value',
    'use a structured checklist rather than guesswork',
    'increase your trust signals with verified discount guides',
    'improve your operational playbooks across Chrome and API workflows',
]

platform_mentions = [
    'LinkedIn audiences',
    'Telegram communities',
    'Twitter thread readers',
    'automation groups',
    'affiliate funnels',
    'browser ops channels',
    'privacy-savvy teams',
    'SaaS decision makers',
    'multilogin and alternative buyers',
    'browser privacy audiences',
]

ctas = [
    'Check the verified promo and use SAAS50 for 50% off.',
    'See the discount proof and apply SAAS50 at checkout.',
    'Use SAAS50 when you buy, and share the verified savings path.',
    'Open the promo hub, validate the offer, and use SAAS50.',
    'Use SAAS50 for your next Multilogin checkout with confidence.',
    'Bookmark the comparison hub and use SAAS50 for a better deal.',
    'Start with the reliability framework, then apply SAAS50.',
    'Follow the evidence-first process and use SAAS50 if it fits.',
    'Validate the stack, then apply SAAS50 for the discount.',
    'Use SAAS50 and keep recommending trusted, verified offers.',
]

strategy_closings = [
    'This is the kind of content that builds long-term affiliate trust.',
    'That’s how you scale browser operations without burning credibility.',
    'A strong affiliate strategy starts with useful technical insight.',
    'This keeps your promo posts smart, not spammy.',
    'Share it as a value-first takeaway, not just a coupon.',
    'That’s the difference between one-time clicks and repeat referrals.',
    'Build a reputation for reliability by sharing what actually works.',
    'Your audience will respect a clear, evidence-based recommendation.',
    'This approach works across desktop, browser, and API audiences.',
    'The smartest posts pair a workflow tip with a verified discount.',
]

review_focus = [
    'browser profile stability',
    'API integration quality',
    'promo verification evidence',
    'team handoff reliability',
    'leak and fingerprint parity',
    'operational cost transparency',
    'browser privacy controls',
    'discount validity checks',
    'multi-account workflow resilience',
    'comparison clarity for buyers',
]

extra_phrases = [
    'reliable browser automation stacks',
    'trusted vendor proof before purchase',
    'technical decision support for account ops',
    'compliance-aware automation playbooks',
    'risk-aware tools for market research',
    'proof-first promo sharing',
    'quality-first affiliate recommendations',
    'sustainable affiliate post cadence',
    'browser ops content that converts',
    'verification-first discount reports',
]

hashtag_buckets = {
    'Browser automation': ['#BrowserAutomation', '#BrowserOps', '#Automation'],
    'Promo verification': ['#PromoVerification', '#Coupon', '#Discount'],
    'Affiliate trust': ['#AffiliateMarketing', '#Trust', '#Revenue'],
    'Multi-account ops': ['#MultiAccount', '#AccountOps', '#Privacy'],
    'Workflow reliability': ['#Reliability', '#OpsQuality', '#TechOps'],
    'API runbooks': ['#APIRunbook', '#API', '#DevOps'],
    'Privacy engineering': ['#Privacy', '#AntiDetect', '#BrowserPrivacy'],
    'Cost sustainability': ['#SaaS', '#Sustainability', '#CostSavings'],
    'Review methodology': ['#ReviewMethodology', '#DecisionFramework', '#VendorReview'],
    'Comparison hub': ['#Comparison', '#ToolSelection', '#DecisionSupport'],
}

generic_hashtags = [
    '#SAAS50',
    '#SaaS',
    '#CyberSecurity',
    '#Marketing',
    '#Growth',
    '#Tech',
    '#Scale',
    '#Productivity',
    '#Startup',
    '#Business',
]


def build_hashtags(i, topic):
    base = hashtag_buckets.get(topic, ['#SAAS50', '#Automation'])
    extra = generic_hashtags[i % len(generic_hashtags)]
    extra2 = generic_hashtags[(i + 3) % len(generic_hashtags)]
    tags = []
    for tag in base + [extra, extra2]:
        if tag not in tags:
            tags.append(tag)
    return ' '.join(tags[:5])


def build_post(i):
    hook = hooks[i % len(hooks)]
    pain = pain_points[i % len(pain_points)]
    solution = solution_framings[(i // 10) % len(solution_framings)]
    benefit = benefits[(i // 25) % len(benefits)]
    platform = platform_mentions[(i // 17) % len(platform_mentions)]
    cta = ctas[i % len(ctas)]
    closing = strategy_closings[(i // 33) % len(strategy_closings)]
    review = review_focus[(i // 7) % len(review_focus)]
    extra = extra_phrases[(i // 12) % len(extra_phrases)]
    suffix = f"[{i+1}/{TOTAL_POSTS}]"

    sentence1 = f"{hook} Avoid {pain} when you build {extra}."
    sentence2 = f"Our site is about {solution} for {review}."
    sentence3 = f"It helps {platform} {benefit} while staying smart on affiliate messaging."
    sentence4 = f"{cta}"
    sentence5 = f"{closing} {suffix}"

    return ' '.join([sentence1, sentence2, sentence3, sentence4, sentence5]).replace('  ', ' ')


def build_topic(i):
    topics = [
        'Browser automation',
        'Promo verification',
        'Affiliate trust',
        'Multi-account ops',
        'Workflow reliability',
        'API runbooks',
        'Privacy engineering',
        'Cost sustainability',
        'Review methodology',
        'Comparison hub',
    ]
    return topics[i % len(topics)]


def build_tracking_link(i):
    return f"{BASE_URL}?utm_source=linkedin&utm_medium=auto_post&utm_campaign=SAAS50&utm_content=post{i+1:04d}"


def write_csv():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['post_number', 'topic', 'post_text', 'tracking_link', 'hashtags'])
        for i in range(TOTAL_POSTS):
            topic = build_topic(i)
            writer.writerow([i + 1, topic, build_post(i), build_tracking_link(i), build_hashtags(i, topic)])


if __name__ == '__main__':
    write_csv()
    print(f'Wrote {TOTAL_POSTS} posts to {OUTPUT_FILE}')
