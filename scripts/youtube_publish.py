#!/usr/bin/env python3
"""Optional YouTube Data API connector for Hermes Marketing Agent.

Uses user OAuth (not a service account). Credentials and refresh tokens are
stored outside the repository. Upload defaults to private visibility.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
DEFAULT_TOKEN_PATH = Path.home() / ".config" / "hermes" / "youtube" / "token.json"


def _google_clients():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise RuntimeError(
            "YouTube dependencies are missing. Install requirements-youtube.txt first."
        ) from exc
    return Request, Credentials, InstalledAppFlow, build, MediaFileUpload


def get_service(args):
    Request, Credentials, InstalledAppFlow, build, _ = _google_clients()
    client_file = Path(args.client_secrets).expanduser()
    token_file = Path(args.token_file).expanduser()
    if not client_file.is_file():
        raise RuntimeError(
            f"OAuth client JSON not found at {client_file}. See "
            "YOUTUBE_CONNECTION_SETUP.md; do not commit this file."
        )

    token_file.parent.mkdir(parents=True, exist_ok=True)
    # Best-effort private permissions on POSIX; Windows uses its account ACLs.
    try:
        token_file.parent.chmod(0o700)
    except OSError:
        pass

    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES) if token_file.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        token_file.write_text(creds.to_json(), encoding="utf-8")
        try:
            token_file.chmod(0o600)
        except OSError:
            pass
    elif not token_file.exists():
        token_file.write_text(creds.to_json(), encoding="utf-8")
        try:
            token_file.chmod(0o600)
        except OSError:
            pass

    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def do_connect(args):
    youtube = get_service(args)
    response = youtube.channels().list(part="snippet", mine=True).execute()
    channels = response.get("items", [])
    if not channels:
        raise RuntimeError(
            "Google OAuth succeeded, but no YouTube channel was returned for this account. "
            "Check that the selected Google account owns or manages a YouTube channel."
        )
    for channel in channels:
        print(f"Connected channel: {channel['snippet']['title']}")
        print(f"Channel ID: {channel['id']}")
    print("OAuth token saved outside the repository.")
    print("Publishing remains disabled until a private test upload succeeds and config is enabled.")


def do_upload(args):
    media_path = Path(args.file).expanduser()
    if not media_path.is_file():
        raise RuntimeError(f"Video file not found: {media_path}")
    if media_path.stat().st_size == 0:
        raise RuntimeError("Video file is empty.")
    if not args.title.strip():
        raise RuntimeError("Title must not be empty.")
    if args.visibility not in {"private", "unlisted", "public"}:
        raise RuntimeError("Visibility must be private, unlisted, or public.")
    if args.visibility == "public" and not args.confirm_public:
        raise RuntimeError(
            "Public uploads require --confirm-public. Test with --visibility private first."
        )

    Request, Credentials, InstalledAppFlow, build, MediaFileUpload = _google_clients()
    youtube = get_service(args)
    body = {
        "snippet": {
            "title": args.title.strip(),
            "description": args.description or "",
            "categoryId": args.category,
        },
        "status": {
            "privacyStatus": args.visibility,
            "selfDeclaredMadeForKids": bool(args.made_for_kids),
        },
    }
    tags = [tag.strip() for tag in (args.tags or "").split(",") if tag.strip()]
    if tags:
        body["snippet"]["tags"] = tags

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(media_path), mimetype="video/*", resumable=True),
        notifySubscribers=not args.no_subscriber_notification,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    video_id = response.get("id")
    if not video_id:
        raise RuntimeError("YouTube did not return a video ID.")
    print(f"Upload complete. Video ID: {video_id}")
    print(f"Visibility: {args.visibility}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    if args.visibility == "private":
        print("The video is private; it is not publicly visible.")


def parser():
    p = argparse.ArgumentParser(description="Connect Hermes to YouTube using official OAuth/API.")
    p.add_argument("--client-secrets", default=os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json"),
                   help="Path to downloaded Google OAuth Desktop client JSON.")
    p.add_argument("--token-file", default=os.getenv("YOUTUBE_TOKEN_FILE", str(DEFAULT_TOKEN_PATH)),
                   help="Local token path (default is outside the repository).")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("connect", help="Authorize Google OAuth and display the connected YouTube channel.")

    upload = sub.add_parser("upload", help="Upload a video; private is the default.")
    upload.add_argument("--file", required=True, help="Path to the video file.")
    upload.add_argument("--title", required=True, help="YouTube title.")
    upload.add_argument("--description", default="", help="Video description.")
    upload.add_argument("--tags", default="", help="Comma-separated tags.")
    upload.add_argument("--category", default="22", help="YouTube category ID (default 22: People & Blogs).")
    upload.add_argument("--visibility", choices=("private", "unlisted", "public"), default="private")
    upload.add_argument("--confirm-public", action="store_true",
                        help="Required with --visibility public.")
    upload.add_argument("--made-for-kids", action="store_true",
                        help="Declare the video as made for kids only when accurate.")
    upload.add_argument("--no-subscriber-notification", action="store_true")
    return p


def main():
    args = parser().parse_args()
    try:
        if args.command == "connect":
            do_connect(args)
        elif args.command == "upload":
            do_upload(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
