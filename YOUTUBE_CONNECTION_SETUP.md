# Connect YouTube to Hermes Marketing Agent

This optional connector uses the official YouTube Data API v3 and Google user OAuth. It does not use a YouTube password, cookies, browser scraping, or a service account.

## 1. Create OAuth credentials

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. In **APIs & Services → Library**, enable **YouTube Data API v3**.
4. In **Google Auth Platform** (or **APIs & Services → OAuth consent screen**), configure the app name, support email, and audience. If the app is in Testing mode, add the Google account that owns the channel as a test user.
5. Under **Clients**, create an OAuth client with application type **Desktop app**.
6. Download the JSON file. Keep it on your own computer; do not commit it or paste its contents into chat. The connector uses the following scopes:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube.readonly`

Google may require additional verification or restrict uploads for unverified projects. Review Google's current policy and any warnings shown during setup.

## 2. Install the optional dependencies

Run these commands from the repository root in a terminal with Python 3.11 or later:

```powershell
python -m pip install -r requirements-youtube.txt
```

## 3. Authorize the channel

Save the downloaded OAuth JSON somewhere private, for example:
`$HOME\hermes-secrets\youtube-client.json`

Then run:

```powershell
python scripts/youtube_publish.py --client-secrets "$HOME\hermes-secrets\youtube-client.json" connect
```

A browser window opens. Sign in with the Google account that manages the intended YouTube channel and approve access. The refresh token is stored by default under your home directory at `~/.config/hermes/youtube/token.json`, outside this repository. On Windows, keep that file private and do not sync it into a public repository. You can override the location with `--token-file`.

The command should print the channel title and ID. If it does not, do not proceed to upload; resolve the OAuth or channel-access issue first.

## 4. Upload a private test video

Use a small video file you own or have permission to publish:

```powershell
python scripts/youtube_publish.py --client-secrets "$HOME\hermes-secrets\youtube-client.json" upload --file ".\test-video.mp4" --title "Hermes private connection test" --description "Private API connection test"
```

The default visibility is **private**. Confirm the upload in YouTube Studio before changing any campaign settings. The script refuses a public upload unless `--confirm-public` is also supplied.

For a public upload after the private test, explicitly pass:
`--visibility public --confirm-public`

## 5. Enable campaign publishing only after the test passes

The repo's campaign config intentionally starts disabled. Do not enable unattended publishing until OAuth, a private upload, video processing, and the intended channel are verified. Use the global pause switch if anything looks wrong. Ad spending is not part of this connector.

## Troubleshooting

- **Access blocked / app not verified:** check the OAuth consent-screen audience, add the channel-owning Google account as a test user while in Testing, and follow any Google verification requirements. Do not bypass account security warnings.
- **No channel returned:** sign in with the Google account that owns or manages the YouTube channel.
- **Quota / 403:** check that YouTube Data API v3 is enabled, quota is available, and the project/account is allowed to upload.
- **Token revoked:** delete only the local token file, then rerun `connect` and consent again.
- **Never commit:** OAuth client JSON, `token.json`, access tokens, refresh tokens, or API secrets.
