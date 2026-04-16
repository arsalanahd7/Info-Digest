"""
Info Digest — Daily AI Intelligence Briefing
Reads Arsalan's OS context, researches the web, pushes digest to Notion.

Setup:
    pip install anthropic notion-client python-dotenv

Run:
    python info_digest.py

Automate (cron, runs at 7am daily):
    0 7 * * * /usr/bin/python3 /path/to/info_digest.py >> /path/to/digest.log 2>&1
"""

import os
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from notion_client import Client

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
NOTION_API_KEY    = os.environ["NOTION_API_KEY"]
INFO_DIGEST_PAGE_ID = "344d7b57-ec43-8181-ae85-cf296288a95f"  # Hub child page created above

# ── OS Context (pulled from your Systems Manual) ────────────────────────────────

OS_CONTEXT = """
ARSALAN'S OPERATING SYSTEM — APRIL–AUGUST 2026

ACTIVE GOALS:
- Work: $180k revenue, close 40 deals, 130 scheduled calls, self-book 60 calls
- AI: Build 1 top-level dashboard, build 6 automations
- Health: 80 workouts, reach 14% body fat, 95% nutrition adherence
- Business Knowledge: Read 4 books (Pyramid Principle, Good Strategy/Bad Strategy, Never Split the Difference, HBR Writing), re-listen to 10 hrs course content
- Networking: Build 10 strong relationships (targeting: 2–4 yrs ahead, consulting, entrepreneurial exposure)
- Money: $30k total cash by August, $4,664 TFSA contribution
- Relationships: Call a family member 100 times

ACTIVE SYSTEMS:
- Work System: Sales closer at AdmissionPrep (high school admissions consulting), booking system, PCC system, conversion improvement loop
- AI/Automation System: Building 6 automations — CRM tracker, call summary generator, follow-up message generator, pipeline KPI dashboard, booking tracker, weekly review automation
- Health System: 5x/week training, macro targets 1800 kcal / 180g protein / 140g carbs / 40g fat

PATHWAY PLANS IN PROGRESS:
- Consulting Pathway (for post-undergrad)
- YC Startup Pathway
- AdmissionPrep growth (current employer)
- Own Business Content Plan

TOOLS IN USE:
- Notion, Claude, Lovable, Supabase, Stripe, Claude Code, NotebookLM, Perplexity, Captions
"""

# ── Research Prompts per Section ────────────────────────────────────────────────

SECTIONS = [
    {
        "id": "ai_tools",
        "emoji": "🤖",
        "title": "AI & Tools",
        "prompt": (
            "You are a research assistant for a 19-year-old builder who is: "
            "building 6 automations in his personal OS, using Claude Code, Lovable, Supabase, and Notion. "
            "Search the web for the most relevant AI and automation news from the past 24–48 hours. "
            "Focus on: new AI tools, Claude/Anthropic updates, automation frameworks, no-code/low-code tools, "
            "anything directly useful to someone building personal productivity automations and small software products. "
            "Return 3–5 specific, actionable findings. Be concrete — name tools, link capabilities, note relevance."
        )
    },
    {
        "id": "sales_admissions",
        "emoji": "💼",
        "title": "Sales & Admissions",
        "prompt": (
            "You are a research assistant for a high-ticket sales closer at an admissions consulting company "
            "targeting high school students (grades 9–12) and their families in Canada. "
            "Search the web for the latest news on: Canadian university admissions trends, high school consulting industry, "
            "sales and closing techniques, EdTech industry, anything relevant to someone closing $4k–$8k education packages. "
            "Return 3–5 specific findings from the past 48 hours. Be concrete and direct."
        )
    },
    {
        "id": "business_consulting",
        "emoji": "📈",
        "title": "Business & Consulting",
        "prompt": (
            "You are a research assistant for a 19-year-old Commerce student building toward a consulting career and eventual startup. "
            "He is reading: The Pyramid Principle, Good Strategy/Bad Strategy, Never Split the Difference. "
            "Search the web for: consulting industry news, YC/startup ecosystem updates, business strategy frameworks, "
            "notable entrepreneur moves, anything a future consultant or founder should know today. "
            "Return 3–5 specific findings from the past 48 hours."
        )
    },
    {
        "id": "finance_investing",
        "emoji": "💰",
        "title": "Finance & Investing",
        "prompt": (
            "You are a research assistant for a 19-year-old Canadian building toward $30k savings by August, "
            "with a $4,664 TFSA contribution target. "
            "Search the web for: Canadian personal finance news, TFSA strategies, interest rates, investment opportunities "
            "relevant to a young person in Canada, any financial news affecting young Canadians. "
            "Return 3–5 specific findings from the past 48 hours. Be direct and actionable."
        )
    },
    {
        "id": "health_performance",
        "emoji": "🏋️",
        "title": "Health & Performance",
        "prompt": (
            "You are a research assistant for a 19-year-old who trains 5x/week, targets 14% body fat, "
            "and follows macros of 1800 kcal / 180g protein / 140g carbs / 40g fat. "
            "Search the web for: latest research on body recomposition, protein timing, training optimization, "
            "recovery science, nutrition findings — anything directly useful to someone serious about physique and performance. "
            "Return 3–5 specific findings from the past 48 hours. Skip generic advice."
        )
    },
    {
        "id": "networking_intel",
        "emoji": "🌐",
        "title": "Networking Intel",
        "prompt": (
            "You are a research assistant for a 19-year-old Commerce student in Canada targeting: "
            "relationships with people 2–4 years ahead, in consulting or entrepreneurship. "
            "Search the web for: networking events in Toronto/Vancouver/Canada for young professionals, "
            "notable figures in Canadian business/consulting/startups worth following, "
            "LinkedIn or community opportunities relevant to an ambitious 19-year-old. "
            "Return 3–5 specific and actionable findings."
        )
    },
]

# ── Research via Claude with Web Search ────────────────────────────────────────

def research_section(client: anthropic.Anthropic, section: dict) -> str:
    """Use Claude with web search to research one digest section."""
    print(f"  Researching: {section['emoji']} {section['title']}...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": section["prompt"] + "\n\nFormat your response as a tight bulleted list. No preamble."
            }
        ]
    )

    # Extract text from response (may include tool use blocks)
    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text += block.text

    return result_text.strip() if result_text else "No findings retrieved."


# ── Push to Notion ─────────────────────────────────────────────────────────────

def push_to_notion(notion: Client, sections_data: list[dict]):
    """Create a new child page under the Info Digest hub page."""
    today = datetime.now().strftime("%B %d, %Y")
    page_title = f"📰 Info Digest — {today}"

    notion.pages.create(
        parent={"page_id": INFO_DIGEST_PAGE_ID},
        icon={"type": "emoji", "emoji": "📰"},
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": page_title}}]
            }
        },
        children=[
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": f"Auto-generated on {today} · Powered by Claude + Web Search"}}],
                    "icon": {"type": "emoji", "emoji": "⚡"},
                    "color": "gray_background"
                }
            },
            *[build_section_blocks(s) for s in sections_data],
        ]
    )
    print(f"\n✅ Digest pushed to Notion: {page_title}")


def build_section_blocks(section: dict) -> dict:
    """Convert a section into a Notion toggle block."""
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": f"{section['emoji']} {section['title']}"},
                    "annotations": {"bold": True}
                }
            ],
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": section["content"]}}
                        ]
                    }
                }
            ]
        }
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("🗞️  Info Digest — Starting research run...")
    print(f"   {datetime.now().strftime('%A, %B %d, %Y — %I:%M %p')}\n")

    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    notion_client = Client(auth=NOTION_API_KEY)

    sections_data = [
        {
            "emoji": section["emoji"],
            "title": section["title"],
            "content": research_section(anthropic_client, section),
        }
        for section in SECTIONS
    ]

    print("\n📝 Building digest and pushing to Notion...")
    push_to_notion(notion_client, sections_data)


if __name__ == "__main__":
    main()
