#!/usr/bin/env python3
"""Generate MP4 clips using NVIDIA Cosmos 3 Nano's hosted API.

Set NVIDIA_API_KEY in the environment. Do not pass API keys on the command line.
Default endpoint is NVIDIA's hosted Cosmos3 Nano API Catalog route.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

DEFAULT_ENDPOINT = "https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano"
MAX_RESPONSE_BYTES = 300 * 1024 * 1024


def image_reference(path_or_url: str) -> str:
    parsed = urlparse(path_or_url)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return path_or_url
    path = Path(path_or_url).expanduser()
    if not path.is_file():
        raise ValueError(f"Image file not found: {path}")
    suffix = path.suffix.lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(suffix)
    if not mime:
        raise ValueError("Image must be JPG, PNG, or WebP.")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate MP4 clips using NVIDIA Cosmos 3 Nano.")
    parser.add_argument("--endpoint", default=os.getenv("NVIDIA_COSMOS_ENDPOINT", DEFAULT_ENDPOINT),
                        help="Hosted API Catalog endpoint or a verified self-hosted NIM endpoint.")
    parser.add_argument("--output-dir", default="generated-videos", help="Output directory (keep generated media out of Git).")
    sub = parser.add_subparsers(dest="mode", required=True)

    def add_common(p):
        p.add_argument("--prompt", required=True, help="Describe the scene, action, camera, lighting and style.")
        p.add_argument("--resolution", choices=("256_16_9", "256_9_16", "256_1_1", "480_16_9", "480_9_16", "480_1_1", "720_16_9", "720_9_16", "720_1_1"), default="480_9_16")
        p.add_argument("--frames", type=int, default=49, help="Frame count; 480 tier accepts 25–297, 720 tier 25–197.")
        p.add_argument("--fps", type=float, default=24.0)
        p.add_argument("--steps", type=int, default=35)
        p.add_argument("--seed", type=int, default=42)
        p.add_argument("--filename", default=None, help="Optional output filename, ending in .mp4.")

    text = sub.add_parser("text", help="Generate a clip from text.")
    add_common(text)

    image = sub.add_parser("image", help="Animate a still image you own or are authorized to use.")
    add_common(image)
    image.add_argument("--image", required=True, help="Local image path or public HTTP(S) image URL.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY is not set. Configure it locally; never commit it.", file=sys.stderr)
        return 2

    if not args.prompt.strip():
        print("ERROR: --prompt cannot be empty.", file=sys.stderr)
        return 2
    if args.frames < 25:
        print("ERROR: --frames must be at least 25 for Cosmos3 Nano video.", file=sys.stderr)
        return 2
    max_frames = 197 if args.resolution.startswith("720") else 297 if args.resolution.startswith("480") else 397
    if args.frames > max_frames:
        print(f"ERROR: --frames exceeds the documented limit {max_frames} for this resolution tier.", file=sys.stderr)
        return 2
    if args.fps <= 0 or args.fps > 60:
        print("ERROR: --fps must be greater than 0 and no more than 60.", file=sys.stderr)
        return 2
    if args.steps < 1 or args.steps > 100:
        print("ERROR: --steps must be between 1 and 100.", file=sys.stderr)
        return 2

    payload = {
        "model_mode": "text2video" if args.mode == "text" else "image2video",
        "prompt": args.prompt.strip(),
        "resolution": args.resolution,
        "num_frames": args.frames,
        "num_inference_steps": args.steps,
        "fps": args.fps,
        "seed": args.seed,
    }
    if args.mode == "image":
        try:
            payload["input_reference"] = image_reference(args.image)
        except (ValueError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = args.filename or f"cosmos3_{args.mode}_{int(time.time())}.mp4"
    if Path(filename).name != filename or not filename.lower().endswith(".mp4"):
        print("ERROR: --filename must be a plain filename ending in .mp4.", file=sys.stderr)
        return 2
    output_path = output_dir / filename

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        # Video generation may take minutes. Do not blindly retry a timeout:
        # the provider may have completed generation even if the response was lost.
        response = requests.post(args.endpoint, headers=headers, json=payload, timeout=(20, 1800))
        if not response.ok:
            detail = response.text[:3000]
            print(f"ERROR: NVIDIA API returned HTTP {response.status_code}: {detail}", file=sys.stderr)
            return 1
        try:
            result = response.json()
        except json.JSONDecodeError:
            print("ERROR: NVIDIA API response was not valid JSON.", file=sys.stderr)
            return 1
        encoded = result.get("b64_video")
        if not isinstance(encoded, str) or not encoded:
            print("ERROR: API response did not include b64_video. Response keys: "
                  + ", ".join(sorted(result.keys())), file=sys.stderr)
            return 1
        try:
            video = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error):
            print("ERROR: API returned invalid base64 video data.", file=sys.stderr)
            return 1
        if not video:
            print("ERROR: Decoded video is empty.", file=sys.stderr)
            return 1
        if len(video) > MAX_RESPONSE_BYTES:
            print("ERROR: Generated file exceeds the configured 300 MiB safety limit.", file=sys.stderr)
            return 1
        output_path.write_bytes(video)
    except requests.Timeout:
        print("ERROR: Request timed out; generation outcome may be unknown. Check provider history/status before retrying to avoid duplicate usage.", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"ERROR: Network/API request failed: {exc}", file=sys.stderr)
        return 1

    duration = args.frames / args.fps
    print("Video generation succeeded.")
    print(f"Output: {output_path.resolve()}")
    print(f"Mode: {args.mode}; resolution: {args.resolution}; frames: {args.frames}; fps: {args.fps}; approximate duration: {duration:.2f}s")
    print("Review visual quality and rights before using the clip in a campaign.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
