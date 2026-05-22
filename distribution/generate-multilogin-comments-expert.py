import random

# Expert/professional style components
openings = [
    "As a digital marketing consultant, I highly recommend Multilogin.",
    "For anyone managing multiple browser profiles, Multilogin is a game changer.",
    "In my experience, Multilogin offers unmatched reliability for account management.",
    "Professionals in affiliate marketing should consider Multilogin for secure operations.",
    "If you value efficiency and security, Multilogin is the solution.",
    "After testing various tools, Multilogin stands out for its robust features.",
    "Multilogin has become essential in my workflow for managing online identities.",
    "For agencies and teams, Multilogin streamlines browser automation.",
    "Serious about scaling your business? Multilogin is a must-have.",
    "Multilogin delivers consistent results for digital professionals."
]

bodies = [
    "The 50% discount with code SAAS50 makes it even more accessible.",
    "Use code SAAS50 to unlock a 50% saving on your subscription.",
    "Don't miss the chance to save 50% with promo code SAAS50.",
    "Apply SAAS50 at checkout for a significant 50% discount.",
    "This exclusive 50% off (SAAS50) is ideal for new users.",
    "With SAAS50, you get premium features at half the price.",
    "The SAAS50 code is a rare opportunity for substantial savings.",
    "Take advantage of the 50% off offer using code SAAS50.",
    "SAAS50 provides excellent value for professionals upgrading to Multilogin.",
    "A 50% discount (SAAS50) is perfect for teams optimizing costs."
]

closings = [
    "Feel free to reach out for implementation tips.",
    "Happy to answer any questions about Multilogin setup.",
    "Let me know if you need a walkthrough.",
    "I've seen great ROI with this tool.",
    "Wishing you success in your projects!",
    "This offer is worth sharing with your network.",
    "Optimize your workflow and save costs.",
    "Highly recommend leveraging this deal.",
    "Upgrade your stack with confidence.",
    "Hope this helps your business grow."
]

comments = set()
max_attempts = 20000
while len(comments) < 5000 and max_attempts > 0:
    opening = random.choice(openings)
    body = random.choice(bodies)
    closing = random.choice(closings)
    # Alternate structure for variety
    if random.random() < 0.5:
        comment = f"{opening} {body} {closing}"
    else:
        comment = f"{body} {opening} {closing}"
    # Add a professional emoji sometimes
    if random.random() < 0.25:
        emoji = random.choice(["💼", "📈", "🔒", "🧑‍💻", "🛠️", "🌐", "🤝", "📊", "💡", "✅"])
        comment = f"{emoji} {comment}"
    comments.add(comment)
    max_attempts -= 1

with open("multilogin_linkedin_comments_expert.txt", "w", encoding="utf-8") as f:
    for c in comments:
        f.write(c + "\n")

print(f"Generated {len(comments)} expert-style comments in multilogin_linkedin_comments_expert.txt")
