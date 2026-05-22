import random

# Core message parts
openings = [
    "Unlock 50% off Multilogin with code SAAS50!",
    "Get 50% discount on Multilogin using SAAS50.",
    "Try Multilogin now – use code SAAS50 for 50% off!",
    "Save 50% on Multilogin: apply code SAAS50.",
    "Exclusive: 50% off Multilogin with SAAS50.",
    "Multilogin users: grab 50% off with SAAS50!",
    "Don't miss 50% off Multilogin – code SAAS50.",
    "Special offer: Multilogin 50% off, code SAAS50.",
    "Boost your workflow with Multilogin – 50% off (SAAS50).",
    "Level up with Multilogin: 50% off, use SAAS50."
]

bodies = [
    "Perfect for marketers, agencies, and growth hackers.",
    "Great for managing multiple accounts securely.",
    "Ideal for teams needing browser automation.",
    "Works wonders for affiliate marketers.",
    "A must-have for digital professionals.",
    "Trusted by thousands worldwide.",
    "Seamless browser profile management.",
    "Take your online operations to the next level.",
    "Simplify your multi-account workflow.",
    "Enhance your privacy and productivity."
]

closings = [
    "Limited time only!",
    "Act fast before it expires!",
    "Don't miss out!",
    "Grab your deal today!",
    "Start saving now!",
    "Share with your network!",
    "Try it and thank me later!",
    "Let me know if you need help!",
    "Happy to share this deal!",
    "Hope this helps someone!"
]

# To ensure uniqueness, shuffle and combine with randomization
comments = set()
max_attempts = 20000
while len(comments) < 5000 and max_attempts > 0:
    opening = random.choice(openings)
    body = random.choice(bodies)
    closing = random.choice(closings)
    # Add a little randomization
    if random.random() < 0.5:
        comment = f"{opening} {body} {closing}"
    else:
        comment = f"{body} {opening} {closing}"
    # Add a random emoji sometimes
    if random.random() < 0.3:
        emoji = random.choice(["🚀", "🔥", "💡", "🎉", "✅", "🛡️", "💰", "🌟", "🔒", "✨"])
        comment = f"{emoji} {comment}"
    comments.add(comment)
    max_attempts -= 1

with open("multilogin_linkedin_comments.txt", "w", encoding="utf-8") as f:
    for c in comments:
        f.write(c + "\n")

print(f"Generated {len(comments)} unique comments in multilogin_linkedin_comments.txt")
