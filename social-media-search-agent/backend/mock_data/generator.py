"""
Mock social media post generator.
Produces realistic posts across 6 platforms with seeded relevance distributions.
"""
import re
import uuid
import random
from datetime import datetime, timedelta

# Platform post counts and character limits
PLATFORM_CONFIGS = {
    "twitter":   {"count": 150, "icon": "𝕏"},
    "reddit":    {"count": 100, "icon": "🔴"},
    "linkedin":  {"count": 75,  "icon": "💼"},
    "instagram": {"count": 75,  "icon": "📸"},
    "tiktok":    {"count": 60,  "icon": "🎵"},
    "youtube":   {"count": 40,  "icon": "▶️"},
}

# ── Relevant templates (use {kw1}, {kw2}, {kw3} placeholders) ──────────────────

RELEVANT = {
    "twitter": [
        "Hot take: {kw1} will completely reshape how we think about {kw2} over the next decade. The data backs this up. Thread 🧵👇",
        "Just read a compelling analysis on {kw1} and its impact on {kw2}. The implications are massive. Here's what caught my attention:",
        "The {kw1} space is evolving fast. {kw2} is emerging as the key differentiator. Staying ahead requires paying close attention. #{kw1} #{kw2}",
        "Breaking: major movement in {kw1}. What this means for {kw2} and everyone watching this space closely 👇",
        "Can we talk about how {kw1} is quietly disrupting {kw2}? The numbers are staggering and nobody's discussing this. #{kw1}",
        "5 things I learned studying {kw1} this week: 1) {kw2} matters more than anyone admits 2) the incumbents are scared 3) timing is everything",
        "Everyone's bullish on {kw1} but ignoring the {kw2} angle entirely. That's where the real story is. Let me explain why.",
        "The intersection of {kw1} and {kw2} is where all the genuine innovation is happening right now. Don't sleep on this. #{kw1} #{kw2}",
        "Unpopular opinion: {kw1} doesn't work without solving {kw2} first. Most people have the order backwards.",
        "New report on {kw1} just dropped. Key finding: {kw2} adoption is accelerating 3x faster than projected. #{kw1} #research",
        "Watching {kw1} closely lately. The {kw2} dimension keeps coming up in every conversation I have with experts. #{kw1}",
        "Thread on why {kw1} is the most underrated story in {kw2} right now 🧵 #1: The fundamentals are shifting quietly…",
        "{kw1} and {kw2} are converging faster than I expected. Here's my updated take after months of tracking this space.",
        "Just got off a call with founders building in {kw1}. Their take on {kw2} is unlike anything I've heard. Game-changing stuff.",
        "If you're not paying attention to {kw1} + {kw2} developments, you're going to be very surprised in 18 months. #{kw1}",
    ],
    "reddit": [
        "**Deep dive into {kw1}: What the experts aren't telling you about {kw2}**\n\nI've been researching {kw1} for the past year and the {kw2} angle is consistently under-discussed. Here's what I've pieced together from primary sources, interviews, and data analysis.\n\nThe core insight: {kw1} fundamentally changes the economics of {kw2} in ways that aren't obvious at first glance. The incumbents know this, which is why you're seeing so much noise designed to obscure what's actually happening.\n\nHappy to answer questions in the comments.",
        "**{kw1} megathread — discussing {kw2} and what comes next**\n\nLet's consolidate the {kw1} conversation here. Particularly interested in the {kw2} angle since it keeps getting its own post. Drop your best analysis, counterarguments, and source links below.\n\nI'll be moderating to keep quality high and off-topic posts removed.",
        "**Is {kw1} as transformative as claimed? Honest analysis of the {kw2} implications**\n\nBeen skeptical of {kw1} hype for a while, but after diving deep into the {kw2} data, I'm genuinely changing my view. Here's the analysis that moved me.\n\nTLDR at the bottom for those who don't want the full breakdown.",
        "**Resources for understanding {kw1} — especially the {kw2} side**\n\nCompiled everything worth reading on {kw1} with a focus on {kw2}. Took me three weeks. Sharing so you don't have to do what I did.\n\n- [Primary paper on {kw1} mechanisms]\n- [Best critical take on {kw2} assumptions]\n- [Data source everyone cites but few actually read]",
        "**Why {kw1} will redefine {kw2} — and the timeline is shorter than you think**\n\nMost predictions about {kw1} are wrong in one specific way: they underestimate how fast {kw2} adoption follows initial proof points. I've tracked five previous analogous transitions and the pattern is remarkably consistent.",
    ],
    "linkedin": [
        "After 10+ years watching this industry, I've seen many trends arrive and fade. {kw1} is different. Here's why it matters for {kw2} and what professionals need to understand:\n\n▶ The {kw1} transformation is already underway — most people just haven't noticed yet\n▶ {kw2} sits at the centre of this change, whether practitioners acknowledge it or not\n▶ Early movers will establish durable advantages that late adopters can't easily replicate\n\nWhat's your read on {kw1}? How is it affecting your work with {kw2}?\n\n#{kw1} #{kw2} #leadership #strategy",
        "Sharing insights from our research on {kw1} and its relationship to {kw2}. The findings are significant for anyone operating in this space.\n\nKey takeaways:\n• {kw1} adoption is accelerating faster than consensus forecasts suggest\n• {kw2} is the critical enabling layer — without it, {kw1} stalls\n• Organisations investing now will define the next competitive cycle\n\nFull analysis in the comments. I'd value your perspective.\n\n#{kw1} #{kw2} #innovation #futureofwork",
        "The future of {kw2} runs through {kw1}. I've been working at this intersection for the past eighteen months and here's what I know:\n\nThe companies getting this right are doing three things consistently: [1] treating {kw1} as strategic rather than tactical, [2] building {kw2} capability in-house rather than outsourcing it, [3] measuring outcomes over activity.\n\nThe companies getting it wrong are doing the opposite on all three counts.\n\n#{kw1} #professionalinsights",
        "Honest reflection: I underestimated {kw1} when it first emerged. The {kw2} argument seemed overstated.\n\nI was wrong.\n\nThe evidence is now unambiguous. {kw1} is reshaping {kw2} in ways I couldn't have predicted two years ago. Sharing this because intellectual honesty matters more than protecting a prior position.\n\nWhere are you on {kw1}?\n\n#{kw1} #{kw2} #growthmindset",
    ],
    "instagram": [
        "The {kw1} revolution is here and {kw2} is leading the charge 🔥🔥\n.\n.\n.\n#{kw1} #{kw2} #trending #innovation #future #breakthrough",
        "Obsessed with everything happening in {kw1} right now 🤯 The {kw2} developments are genuinely next level 💡✨\n.\n.\n#{kw1} #{kw2} #mindblown #innovation #tech",
        "When {kw1} meets {kw2}, something extraordinary happens ✨ Documenting every step of this journey 📱\n.\n.\n#{kw1} #{kw2} #trending #explore",
        "Can't stop thinking about how {kw1} is changing {kw2} 🌍 The scale of this shift is hard to overstate.\n.\n.\n#{kw1} #{kw2} #bigideas #futurism",
        "Daily reminder that {kw1} + {kw2} = the most interesting space to be right now ⚡\n.\n.\n#{kw1} #{kw2} #fyp #viral #innovation",
    ],
    "tiktok": [
        "POV: You just discovered how {kw1} is completely changing {kw2} and now you can't unsee it 🤯 #{kw1} #{kw2} #fyp #learnontiktok",
        "Explaining {kw1} and {kw2} in 60 seconds because everyone needs to understand this right now #{kw1} #learnontiktok #fyp",
        "Things the {kw1} industry doesn't want you to know about {kw2} 👀 Part 1 #{kw1} #{kw2} #fyp #viral #exposing",
        "The {kw1} to {kw2} pipeline is real and it's accelerating faster than anyone predicted 🚀 #{kw1} #{kw2} #trending #fyp",
        "Me before learning about {kw1}: 😐 Me after understanding the {kw2} implications: 😱 #{kw1} #mindblown #fyp",
        "3 {kw1} facts that will change how you think about {kw2} forever 🔥 #{kw1} #{kw2} #learnontiktok #fyp",
    ],
    "youtube": [
        "**{kw1}: How It's Transforming {kw2} (Full Analysis)**\nDescription: In this comprehensive video, we break down everything you need to know about {kw1} and explain why {kw2} is the critical variable most analysts are missing. We cover the fundamentals, review the latest data, interview three domain experts, and walk through concrete examples of what this means for practitioners. Timestamp breakdown in comments.",
        "**The {kw1} Deep Dive: {kw2} Edition**\nDescription: Join us for an in-depth exploration of {kw1} with a concentrated focus on {kw2}. This video is for people who've read the surface-level takes and want the real analysis. We don't dumb it down. Correction to last week's video also addressed at the 14-minute mark.",
        "**Why {kw1} Will Redefine {kw2} — Data-Driven Analysis**\nDescription: Everyone has an opinion on {kw1}. We built a model to test the claims. Here's what the data actually shows about {kw2} and where the consensus is wrong. Sources and methodology linked below.",
        "**{kw1} Explained: The {kw2} Connection Nobody Talks About**\nDescription: The relationship between {kw1} and {kw2} is poorly understood even by people who follow this space closely. This video is our attempt to fix that with clear explanations, good visuals, and zero filler.",
    ],
}

# ── Adjacent templates (keywords present but slightly off-topic) ───────────────

ADJACENT = {
    "twitter": [
        "Some thoughts on {kw1} from a slightly different angle — not sure I agree with the mainstream take on {kw2} here but curious what others think",
        "The {kw1} conversation keeps circling back to {kw2} but I think we're asking the wrong questions entirely",
        "Interesting to see {kw1} come up in the context of {kw2} again. The framing keeps shifting. Is anyone tracking this consistently?",
        "Attended a panel on {kw1} today. Decent discussion on {kw2} but nothing I hadn't seen before. The Q&A was better than the presentations honestly",
        "Counterpoint to the prevailing {kw1} consensus: {kw2} might be less central than most people claim. Minority view, I know.",
    ],
    "reddit": [
        "**Honest question: is {kw1} actually related to {kw2} or are we conflating two separate things?**\n\nEvery thread on {kw1} eventually ends up talking about {kw2} but I'm not sure the connection is as tight as people assume. Can someone help me understand the actual relationship?",
        "**{kw1} tangentially but mainly asking about the {kw2} side of things**\n\nI know this community focuses on {kw1} but my actual question is more about {kw2} in adjacent contexts. Posting here because the overlap seemed relevant.",
    ],
    "linkedin": [
        "Attended a conference session on {kw1} yesterday. There was a brief mention of {kw2} but it felt underexplored given its importance. These conversations need to go deeper.\n\n#{kw1} #conference",
        "Interesting use case involving {kw1} crossed my desk this week. The {kw2} element was peripheral but present. Made me think about adjacent applications I hadn't considered.",
    ],
    "instagram": [
        "Hearing {kw1} come up everywhere lately 🤔 Still figuring out what it means for {kw2} in my context\n.\n.\n#{kw1} #{kw2} #learning",
        "Somewhere between {kw1} hype and {kw2} reality 📊 The truth is probably more nuanced\n.\n.\n#{kw1} #{kw2}",
    ],
    "tiktok": [
        "Okay but what does {kw1} actually mean for {kw2} in practical terms because I'm still not sure 😅 #{kw1} #{kw2}",
        "Is {kw1} related to {kw2}? Asking because I keep seeing them mentioned together #{kw1} #question",
    ],
    "youtube": [
        "**{kw1} Overview (with brief notes on {kw2})**\nDescription: General overview of {kw1} aimed at newcomers. We touch on {kw2} briefly but this video is mainly about establishing baseline understanding.",
        "**Q&A: Your {kw1} Questions Answered** \nDescription: Answering subscriber questions. One section covers the {kw2} angle since several people asked.",
    ],
}

# ── Noise templates (completely unrelated) ─────────────────────────────────────

NOISE = {
    "twitter": [
        "Just made the most incredible pasta carbonara and I genuinely cannot stop thinking about it 🍝 #foodie #cooking",
        "My dog learned to open the fridge today. This is either amazing or a disaster. Jury's still out. 🐕",
        "Hot take: morning people and night owls are just different species pretending to coexist 🌙",
        "Can we normalise taking a real lunch break? Eating at your desk while scrolling Slack is not a personality. 🥗",
        "Just walked past someone playing full-volume phone calls on speaker in a coffee shop. Who raised these people.",
        "The weekend felt like 45 minutes. The Tuesday commute felt like a geological epoch. Physics is broken.",
        "Reminder that 'we should grab coffee sometime' is the adult equivalent of 'let's stay friends' 😅",
        "Saw a pigeon confidently walking into a Pret. No hesitation. Big energy. Respect.",
        "Currently trapped in a meeting that is definitely an email wearing a suit. 📧",
        "The gym is just outdoor temperature but worse and more expensive. I said what I said. 💪",
        "Honestly if autumn wasn't such a vibe I would riot. The leaves understood the assignment 🍂",
        "New rule: if the slide deck has more than 15 slides you owe everyone in the room a coffee.",
        "Just discovered you can freeze cheese. My life is different now. 🧀",
        "The concept of 'inbox zero' is a lie told by people who have assistants. 📬",
        "Current status: telling myself I'll start the thing tomorrow for the 47th consecutive day.",
    ],
    "reddit": [
        "**Best sandwiches in the city — a running list with actual opinions**\n\nI've been doing this systematically for eight months. Ranked by the bread-to-filling ratio, sauce quality, and whether the whole thing held together to the last bite. Local spots only, no chains.",
        "**My neighbour's cat has adopted my doormat as its primary napping location. What are my rights?**\n\nIt's been three weeks. The cat arrives at 7am and leaves around noon. My neighbour says it's 'a free spirit.' I'm not mad I just want to understand the situation.",
        "**Watched all six seasons of a show I didn't even like. How does this keep happening?**\n\nStarted it because I had nothing else on. By season two I actively disliked the main character. By season four I was angry at the writing. I finished season six last night. Someone explain this phenomenon.",
        "**Budget travel tips that are actually useful — not 'just cook your own meals' level obvious**\n\nAfter twelve years of travelling on a tight budget I've accumulated some genuinely non-obvious strategies. Sharing because the generic advice posts drive me mad.",
    ],
    "linkedin": [
        "Leadership lesson I had to learn the hard way: the meeting that could have been an email usually should have been neither.\n\nThe best leaders I've worked with protect their team's attention as aggressively as any other resource.\n\n#leadership #productivity",
        "Three years ago I took a role that looked like a step backward on paper. It was the best professional decision I ever made.\n\nSometimes the unconventional move is the right one. Don't let your CV make decisions for you.\n\n#career #growthmindset",
        "Unpopular opinion: the 'hustle culture' content on this platform does more harm than good.\n\nBurnout isn't a badge of honour. Sustainable performance over time beats sprint-and-crash every time.\n\n#mentalhealth #work",
    ],
    "instagram": [
        "Sunday reset complete ✅ Clean space, good coffee, ready for the week 🌿\n.\n.\n#sundayreset #selfcare #cosy #aesthetic",
        "Autumn walks > everything else 🍂🌫️\n.\n.\n#autumn #nature #walks #weekend",
        "This city never gets old honestly 🏙️✨\n.\n.\n#citylife #photography #explore #urban",
        "Homemade sourdough attempt number seven. This time I think I've got it 🍞\n.\n.\n#sourdough #baking #homemade #breadbaking",
        "The light at golden hour is genuinely undefeated ☀️📸\n.\n.\n#goldenhour #photography #sunset #naturephotography",
    ],
    "tiktok": [
        "Things my dog does that I could never get away with #dogsoftiktok #fyp #relatable",
        "Trying every coffee shop in the city before I die #coffeeshop #fyp #lifestyle",
        "POV: it's 2am and you're in a Wikipedia rabbit hole about obscure historical events #fyp #history #insomnia",
        "Rating every pasta shape on texture alone because someone has to #foodtok #pasta #fyp",
        "The difference between people who make their bed and people who don't #fyp #lifestyle #psychology",
        "Day in my life: absolute chaos edition 🫠 #dayinmylife #fyp #relatable",
    ],
    "youtube": [
        "**We Tried Every Ramen Shop in the City — Here's the Definitive Ranking**\nDescription: Eight months, 34 restaurants, way too much sodium. This is our definitive ramen guide with honest scores across five categories. No sponsored content, no brand deals, just opinions.",
        "**Moving to a New Country with £1,000: The Honest Version**\nDescription: Not a highlight reel. This is the actual experience of relocating internationally on a tight budget — what went right, what went badly wrong, and what we'd do differently.",
        "**I Read 52 Books This Year. Here's What I Actually Learned.**\nDescription: One book a week for an entire year. What changed, what didn't, and which books were genuinely worth the time. Honest takes only.",
    ],
}


def _extract_keywords(boolean_queries: dict) -> list:
    """Pull meaningful keywords from boolean query strings."""
    all_text = " ".join(boolean_queries.values())
    stop = {
        "and", "or", "not", "the", "has", "lang", "from", "since",
        "until", "to", "is", "in", "a", "an", "of", "for", "on",
        "title", "selftext", "subreddit", "true", "false", "min",
        "max", "filter", "safe", "near", "within",
    }
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]{2,}\b', all_text)
    seen, keywords = set(), []
    for w in words:
        lw = w.lower().strip("#")
        if lw not in stop and lw not in seen:
            seen.add(lw)
            keywords.append(lw)
    return keywords[:6]


def _make_post(platform: str, template: str, kws: list, author_seed: int) -> dict:
    """Fill a template and wrap it into a post dict."""
    rng = random.Random(author_seed)
    kw1 = kws[0] if len(kws) > 0 else "this topic"
    kw2 = kws[1] if len(kws) > 1 else "the field"
    kw3 = kws[2] if len(kws) > 2 else "the ecosystem"

    text = (
        template
        .replace("{kw1}", kw1)
        .replace("{kw2}", kw2)
        .replace("{kw3}", kw3)
    )

    ts = datetime.utcnow() - timedelta(
        days=rng.randint(0, 30),
        hours=rng.randint(0, 23),
    )

    authors = {
        "twitter": lambda: f"@{rng.choice(['tech','data','market','analyst','insider','observer'])}_"
                           f"{rng.choice(['hawk','watch','signal','brief','daily'])}",
        "reddit": lambda: f"u/{rng.choice(['curious','skeptical','longtime','actual','real'])}_"
                          f"{''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=6))}",
        "linkedin": lambda: f"{rng.choice(['Sarah','James','Alex','Maria','David','Priya'])} "
                            f"{rng.choice(['Chen','Okonkwo','Patel','Rivera','Schmidt','Kim'])}",
        "instagram": lambda: f"@{rng.choice(['the','real','original','official'])}_"
                             f"{''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=5))}",
        "tiktok": lambda: f"@{''.join(rng.choices('abcdefghijklmnopqrstuvwxyz', k=8))}",
        "youtube": lambda: f"{rng.choice(['The','Real','Official','Actual'])} "
                           f"{rng.choice(['Analyst','Observer','Insider','Expert','Channel'])}",
    }

    engagement = {
        "twitter":   {"likes": rng.randint(0, 50000),   "retweets": rng.randint(0, 8000)},
        "reddit":    {"upvotes": rng.randint(0, 40000),  "comments": rng.randint(0, 1500)},
        "linkedin":  {"reactions": rng.randint(0, 5000), "comments": rng.randint(0, 300)},
        "instagram": {"likes": rng.randint(0, 200000),   "comments": rng.randint(0, 5000)},
        "tiktok":    {"likes": rng.randint(0, 500000),   "shares": rng.randint(0, 20000)},
        "youtube":   {"views": rng.randint(0, 2000000),  "likes": rng.randint(0, 80000)},
    }

    return {
        "id": str(uuid.uuid4()),
        "platform": platform,
        "text": text,
        "author": authors[platform](),
        "timestamp": ts.isoformat() + "Z",
        "url": f"https://{platform}.com/post/{uuid.uuid4().hex[:12]}",
        "engagement": engagement[platform],
        "score": None,
        "reason": None,
        "kept_by_filter": None,
    }


def generate_posts(
    boolean_queries: dict,
    count: int = 500,
    relevance_ratio: float = 0.65,
    adjacent_ratio: float = 0.15,
) -> list:
    """
    Generate `count` mock posts across all platforms.

    relevance_ratio: fraction that are clearly relevant (score high with Claude)
    adjacent_ratio:  fraction that are adjacent/partial (score middling)
    remainder:       noise (score low)
    """
    keywords = _extract_keywords(boolean_queries)
    if not keywords:
        keywords = ["topic", "subject", "issue"]

    rng = random.Random(42)
    posts = []
    seed_counter = 0

    for platform, cfg in PLATFORM_CONFIGS.items():
        platform_count = cfg["count"] if count == 500 else int(count * cfg["count"] / 500)
        n_relevant  = int(platform_count * relevance_ratio)
        n_adjacent  = int(platform_count * adjacent_ratio)
        n_noise     = platform_count - n_relevant - n_adjacent

        rel_tmpl  = RELEVANT.get(platform, [])
        adj_tmpl  = ADJACENT.get(platform, [])
        noise_tmpl = NOISE.get(platform, [])

        for _ in range(n_relevant):
            if rel_tmpl:
                tmpl = rng.choice(rel_tmpl)
                posts.append(_make_post(platform, tmpl, keywords, seed_counter))
            seed_counter += 1

        for _ in range(n_adjacent):
            if adj_tmpl:
                tmpl = rng.choice(adj_tmpl)
                posts.append(_make_post(platform, tmpl, keywords, seed_counter))
            seed_counter += 1

        for _ in range(n_noise):
            if noise_tmpl:
                tmpl = rng.choice(noise_tmpl)
                posts.append(_make_post(platform, tmpl, [], seed_counter))
            seed_counter += 1

    rng.shuffle(posts)
    return posts[:count]


def generate_broader_posts(boolean_queries: dict, count: int = 750) -> list:
    """
    Generate broader posts with lower raw relevance (~45%).
    Used after query broadening — more volume, noisier signal.
    """
    return generate_posts(
        boolean_queries,
        count=count,
        relevance_ratio=0.45,
        adjacent_ratio=0.20,
    )
