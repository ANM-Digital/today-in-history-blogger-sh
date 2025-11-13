import requests
from datetime import datetime, UTC
import os
import sys
import random

# ============================
# 📌 CONSTANTS
# ============================
ICONS = ["⚔️", "🏰", "📜", "🛡️", "⚓", "🚀", "💼", "🎖️", "📡", "🏙️", "⚙️", "💥", "🕊️"]
POSTS_DIR = "./scripts/posts"

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
if len(sys.argv) > 1:
    try:
        today = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=UTC)
        print(f"📅 Generating history post for {today.strftime('%Y-%m-%d')}")
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2025-10-28).")
        sys.exit(1)
else:
    today = datetime.now(UTC)
    print(f"📅 Generating history post for today: {today.strftime('%Y-%m-%d')}")

month = today.strftime('%B')
day = today.day
date_str = today.strftime('%Y-%m-%d')

# ============================
# 📡 Fetch data from Wikipedia
# ============================
base_url = "https://en.wikipedia.org/api/rest_v1/feed/onthisday"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}

def fetch_data(endpoint):
    url = f"{base_url}/{endpoint}/{today.month}/{today.day}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"❌ Failed to fetch {endpoint}: {r.status_code}")
            return []
        return r.json().get(endpoint, [])
    except Exception as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return []

print("🌐 Fetching events and holidays...")
events_data = fetch_data("events")
holidays_data = fetch_data("holidays")

if not events_data:
    print(f"⚠️ No events found for {month} {day}.")
    sys.exit(0)

# ============================
# 📜 Extract events
# ============================
events = []
for event in events_data:
    year = event.get("year")
    if not isinstance(year, int):
        continue
    text = event.get("text", "").strip()
    wiki = event["pages"][0].get("content_urls", {}).get("desktop", {}).get("page", "") if event.get("pages") else ""
    events.append({"year": year, "text": text, "wiki": wiki})

# ============================
# 🧮 Filter and select events
# ============================
before_1800 = [e for e in events if e["year"] < 1800]
selected = {}

for e in sorted(before_1800, key=lambda x: x["year"]):
    century = (e["year"] // 100) * 100
    if century not in selected:
        selected[century] = e
    if len(selected) >= 15:
        break

chosen_events = list(selected.values())

# --- Fill with random newer events if fewer than 15 ---
if len(chosen_events) < 15:
    remaining = [e for e in events if e["year"] >= 1800 and e not in chosen_events]
    needed = 15 - len(chosen_events)
    chosen_events.extend(random.sample(remaining, min(needed, len(remaining))))
    print(f"ℹ️ Added {needed} random newer events to complete 15 total.")

# ============================
# 🎉 Extract holidays/celebrations
# ============================
celebrations = []
for h in holidays_data:
    title = h.get("text") or h.get("pages", [{}])[0].get("titles", {}).get("normalized", "")
    if title:
        celebrations.append(f"- {title}")

if not celebrations:
    celebrations.append("- No official holidays listed for today.")

# ============================
# 📝 Build Markdown
# ============================
formatted = [f"# 🏛️ Today in History\n"]

for i, e in enumerate(chosen_events):
    icon = ICONS[i % len(ICONS)]
    link = f" [Wikipedia]({e['wiki']})" if e["wiki"] else ""
    formatted.append(f"{icon} {e['year']} – {e['text']}.{link}")

# ✨ Fun Fact
fun_fact = random.choice(FUNNY_FACTS)
formatted.append("\n## ✨ Fun Fact")
formatted.append(fun_fact)

# 🎉 Today is celebrated as
formatted.append(f"\n## 🎉 {month} {day} is celebrated as:\n")
formatted.extend(celebrations)

# ============================
# 💾 Save Markdown
# ============================
os.makedirs(POSTS_DIR, exist_ok=True)
filepath = f"{POSTS_DIR}/{date_str}.md"

with open(filepath, "w", encoding="utf-8") as f:
    f.write("\n\n".join(formatted))

print(f"✅ History post generated: {filepath}")
print(f"📘 Selected {len(chosen_events)} events total ({len(before_1800)} before 1800).")


# --- existing imports and your post generation logic above ---
# (this part creates the .md file inside scripts/posts/)

# --- finally, update the index ---
import os, json

def update_post_index():
    """Create posts_index.json for the viewer."""
    posts_dir = os.path.join(os.path.dirname(__file__), "posts")
    files = sorted(
        [f for f in os.listdir(posts_dir) if f.endswith(".md")],
        reverse=True
    )
    index_path = os.path.join(posts_dir, "posts_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(files, f, indent=2)
    print(f"✅ Updated {index_path} with {len(files)} posts.")

if __name__ == "__main__":
    # 👇 your existing daily post creation code runs here first
    # generate_today_post()  ← example

    # 👇 run this last to rebuild the index
    update_post_index()



