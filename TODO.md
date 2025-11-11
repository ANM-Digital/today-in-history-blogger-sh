# TODO: Automate Today in History Post Generation

## Tasks to Complete

- [x] Create .env file with placeholders for Blogger API variables (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, BLOG_ID)
- [x] Add python-dotenv to requirements.txt
- [x] Edit scripts/publish_to_blogger.py to load variables from .env instead of hardcoding
- [x] Create package.json with npm scripts: "generate", "publish", "build-index"
- [x] Create .github/workflows/daily-post.yml with the provided workflow content

## Followup Steps (for user)
- Fill .env with actual values locally
- Push changes to GitHub, set up secrets for workflow
- Test locally with npm run generate, etc.
