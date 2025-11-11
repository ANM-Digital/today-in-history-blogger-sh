import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ================================
# 🔐 GOOGLE OAUTH CONFIG
# ================================
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
ACCESS_TOKEN = None                   # auto-generated each run

# ================================
# 🌐 BLOGGER CONFIG
# ================================
BLOG_ID = os.getenv("BLOG_ID")
POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "posts")

# ================================
# 🔁 TOKEN REFRESH FUNCTION
# ================================
def get_access_token():
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    r = requests.post(url, data=data)
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("✅ Access token refreshed.")
        return token
    else:
        print("❌ Token refresh failed:", r.text)
        return None

ACCESS_TOKEN = get_access_token()
if not ACCESS_TOKEN:
    print("❌ Could not get access token — exiting.")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# ================================
# 📝 LOAD LATEST POST
# ================================
def get_latest_post():
    # Find the most recent markdown file in /posts
    files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    if not files:
        print("⚠️ No markdown files found in /posts.")
        return None
    latest_file = sorted(files)[-1]
    path = os.path.join(POSTS_DIR, latest_file)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return latest_file.replace(".md", ""), content

# ================================
# 🚀 PUBLISH TO BLOGGER
# ================================
def publish_post(date_str, content):
    title = f"Today in History: {datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')}"
    html_content = content.replace("\n", "<br>")

    data = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content
    }

    post_url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    r = requests.post(post_url, headers=HEADERS, data=json.dumps(data))
    if r.status_code == 200:
        post = r.json()
        print(f"✅ New post published: {post['url']}")
    else:
        print("❌ Failed to publish:", r.text)

# ================================
# 🧱 UPDATE MAIN PAGE
# ================================
def update_today_page(content):
    # Fetch all pages to find "Today in History"
    pages_url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/pages"
    r = requests.get(pages_url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ Failed to fetch pages:", r.text)
        return

    pages = r.json().get("items", [])
    page_id = None
    for p in pages:
        if "today in history" in p["title"].lower():
            page_id = p["id"]
            break

    if not page_id:
        print("⚠️ 'Today in History' page not found.")
        return

    html_content = content.replace("\n", "<br>")
    data = {
        "id": page_id,
        "title": "Today in History",
        "content": html_content
    }

    update_url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/pages/{page_id}"
    r = requests.put(update_url, headers=HEADERS, data=json.dumps(data))
    if r.status_code == 200:
        print("✅ 'Today in History' page updated.")
    else:
        print("❌ Failed to update page:", r.text)

# ================================
# 🏁 MAIN
# ================================
if __name__ == "__main__":
    result = get_latest_post()
    if not result:
        exit(0)
    date_str, content = result
    update_today_page(content)
    publish_post(date_str, content)
    print("🎉 Publishing completed successfully!")
