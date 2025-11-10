from google_auth_oauthlib.flow import InstalledAppFlow

# Scope required for Blogger
SCOPES = ['https://www.googleapis.com/auth/blogger']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', SCOPES)
creds = flow.run_local_server(port=0)

print("\n✅ Your Access Token:\n")
print(creds.token)

# Optional: print refresh token for automation
if creds.refresh_token:
    print("\n🔁 Your Refresh Token:\n")
    print(creds.refresh_token)
