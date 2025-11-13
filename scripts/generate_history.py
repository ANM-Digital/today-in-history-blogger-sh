import requests
from datetime import datetime, UTC
import os
import sys
import random
import json

# ============================
# 📌 CONSTANTS
# ============================
ICONS = ["⚔️", "🏰", "📜", "🛡️", "⚓", "🚀", "💼", "🎖️", "📡", "🏙️", "⚙️", "💥", "🕊️"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, "posts")

FUNNY_FACTS = [
    "🎩 In 1752, Britain skipped 11 days. People thought the government stole their lives.",
    "🦴 Napoleon was once attacked by a horde of bunnies during a hunt.",
    "🐔 The first alarm clock could only ring at 4 A.M. — no snooze button in sight.",
    "🧀 The ancient Romans used crushed mouse brains as toothpaste. Yikes.",
    "📚 Before erasers, people used breadcrumbs to fix mistakes.",
    "🎻 Mozart wrote music faster than most people write texts today.",
    "🦆 Cleopatra lived closer to the Moon landing than to the building of the Pyramids.",
    "🧦 Socks were once a symbol of extreme wealth. Imagine flexing wool.",
    "🐈 In medieval times, cats were tried in court for witchcraft. No lawyer, though.",
    "🥔 Potatoes were once considered poisonous — then became French fries.",
]

# ============================
# 🗓️ Handle date input
# ============================
def get_today():
    if len(sys.argv) > 1:
        try:
            d = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=UTC)
            print(f"📅 Generating history post for {d.strftime('%Y-%m-%d')}")
            return d
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2025-10-28).")
            sys.exit(1)
    else:
        d = datetime.now(UTC)
        print(f"📅 Generating history post for today: {d.strftime('%Y-%m-%d')}")
        return d


# ============================
# 📡 Fetch data from Wikipedia
# ============================
def fetch_data(endpoint, today):
    base_url = "https://en.wikipedia.org/api/rest_v1/feed/onthisday"
    url = f"{base_url}/{endpoint}/{today.month}/{today.day}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"❌ Failed to fetch {endpoint}: {r.status_code}")
            return []
        return r.json().get(endpoint, [])
    except Exception as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return []


# ============================
# 🧠 Generate post
# ============================
def generate_post():
    today = get_today()
    month = today.strftime('%B')
    day = today.day
    date_str = today.strftime('%Y-%m-%d')

    print("🌐 Fetching events and holidays...")
    events_data = fetch_data("events", today)
    holidays_data = fetch_data("holidays", today)

    if not events_data:
        print(f"⚠️ No events found for {month} {day}.")
        return None

    # --- Extract events ---
    events = []
    for event in events_data:
        year = event.get("year")
        if not isinstance(year, int):
            continue
        text = event.get("text", "").strip()
        wiki = event["pages"][0].get("content_urls", {}).get("desktop", {}).get("page", "") if event.get("pages") else ""
        events.append({"year": year, "text": text, "wiki": wiki})

    # --- Filter & select ---
    before_1800 = [e for e in events if e["year"] < 1800]
    selected = {}
    for e in sorted(before_1800, key=lambda x: x["year"]):
        century = (e["year"] // 100) * 100
        if century not in selected:
            selected[century] = e
        if len(selected) >= 15:
            break
    chosen_events = list(selected.values())

    if len(chosen_events) < 15:
        remaining = [e for e in events if e["year"] >= 1800 and e not in chosen_events]
        needed = 15 - len(chosen_events)
        if remaining:
            chosen_events.extend(random.sample(remaining, min(needed, len(remaining))))
        print(f"ℹ️ Added {needed} newer events to reach 15 total.")

    # --- Holidays ---
    celebrations = []
    for h in holidays_data:
        title = h.get("text") or h.get("pages", [{}])[0].get("titles", {}).get("normalized", "")
        if title:
            celebrations.append(f"- {title}")
    if not celebrations:
        celebrations.append("- No official holidays listed for today.")

    # --- Build markdown ---
    formatted = [f"# 🏛️ Today in History\n"]
    for i, e in enumerate(chosen_events):
        icon = ICONS[i % len(ICONS)]
        link = f" [Wikipedia]({e['wiki']})" if e["wiki"] else ""
        formatted.append(f"{icon} {e['year']} – {e['text']}.{link}")

    fun_fact = random.choice(FUNNY_FACTS)
    formatted.append("\n## ✨ Fun Fact\n" + fun_fact)
    formatted.append(f"\n## 🎉 {month} {day} is celebrated as:\n" + "\n".join(celebrations))

    os.makedirs(POSTS_DIR, exist_ok=True)
    filepath = os.path.join(POSTS_DIR, f"{date_str}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n\n".join(formatted))

    print(f"✅ History post generated: {filepath}")
    return filepath


# ============================
# 📚 Update index
# ============================
def update_post_index():
    """Create posts_index.json for the viewer."""
    files = sorted(
        [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")],
        reverse=True
    )
    index_path = os.path.join(POSTS_DIR, "posts_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(files, f, indent=2)
    print(f"✅ Updated {index_path} with {len(files)} posts.")


# ============================
# 🚀 Main entry
# ============================
if __name__ == "__main__":
    md_file = generate_post()
    if md_file:
        update_post_index()
