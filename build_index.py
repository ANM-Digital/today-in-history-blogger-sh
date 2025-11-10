python - <<'PY'
import os, json
posts_dir = "scripts/posts"
files = sorted([f for f in os.listdir(posts_dir) if f.endswith(".md")], reverse=True)
with open(os.path.join(posts_dir, "posts_index.json"), "w", encoding="utf-8") as f:
    json.dump(files, f, indent=2)
print("✅ posts_index.json created with", len(files), "files")
PY
