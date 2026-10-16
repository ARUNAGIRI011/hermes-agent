# NVIDIA Cosmos 3 video generation for Hermes

This optional integration adds text-to-video and image-to-video MP4 generation to the Hermes marketing workflow.

## What it uses

- Hosted endpoint: https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano
- Model: NVIDIA Cosmos3 Nano
- Authentication: an NVIDIA API Catalog key supplied by your account/deployment
- Output: MP4 video returned as b64_video
- Modes: text-to-video and image-to-video
- Short-form aspect ratio: 480_9_16 (vertical), where supported by the selected endpoint

Official references:
- [Cosmos3 Nano model card and API quickstart](https://build.nvidia.com/nvidia/cosmos3-nano/modelcard)
- [NVIDIA NIM API quickstart](https://docs.api.nvidia.com/nim/docs/api-quickstart)
- [NVIDIA Cosmos 3 documentation](https://docs.nvidia.com/cosmos/latest/cosmos3/quickstart_guide.html)

## Free access caveat

NVIDIA's model catalog labels Cosmos3 Nano as a free API endpoint for development, and notes requests may be rate-limited. Availability, eligibility, quota, and trial terms can change. This is **not a guarantee of unlimited free generation or production/business use**. Sign in to the model page and confirm the current API-key flow, quota, and trial terms before relying on it for scheduled campaigns. Do not circumvent quotas or create multiple accounts to bypass limits.

Cosmos3 Nano is designed primarily for Physical AI and world generation (for example robotics, industrial environments, and autonomous systems). Evaluate its output quality for generic lifestyle/product marketing before depending on it. The service applies input screening and SynthID video watermarking; do not attempt to remove required provenance marks.

## 1. Get an API key

1. Open the [Cosmos3 Nano model page](https://build.nvidia.com/nvidia/cosmos3-nano).
2. Sign in or join the NVIDIA Developer Program.
3. Use **Get API Key** if it is available for your account. Follow the current API Catalog flow and terms.
4. Store the key in your local shell or a secret manager. Never commit it, add it to an example file with a real value, or paste it into chat.

PowerShell for the current terminal session:

    $env:NVIDIA_API_KEY = "PASTE_YOUR_KEY_LOCALLY"

Do not include the key in screenshots, logs, issue reports, or shell history when possible. For a persistent production setup, use the deployment's secret manager instead.

## 2. Install the optional dependency

From the Hermes repository root:

    python -m pip install -r requirements-nvidia-video.txt

## 3. Generate a vertical short clip from text

    python scripts/nvidia_cosmos_video.py text --prompt "A cinematic close-up of a small robotic arm assembling a precision component in a clean modern workshop, slow camera push-in, warm studio lighting, realistic materials, no text or logos" --resolution 480_9_16 --frames 49 --fps 24 --output-dir generated-videos

This example is about 2 seconds long (49 frames / 24 FPS). For a longer short, increase frames within the API's documented limits; longer generations can take more time and quota. Start small, then review output quality.

## 4. Animate a still image

Use a JPG, PNG, or WebP image that you own or have permission to use:

    python scripts/nvidia_cosmos_video.py image --image ".\assets\campaign-keyframe.png" --prompt "Animate the scene with gentle camera movement and natural motion; preserve the key subject and composition; no text or logos" --resolution 480_9_16 --frames 49 --fps 24 --output-dir generated-videos

A public HTTP(S) image URL is also supported by the client; use only an image URL that the endpoint is allowed to fetch.

## 5. Use the output in the marketing workflow

1. Content Creator produces the script, hook, shot list, captions, CTA, and a visual prompt.
2. Video Generator generates the source clip.
3. An editor or creative tool adds voiceover, music, subtitles, brand assets, transitions, and final export. This connector does not synthesize audio or edit a complete social video.
4. Review rights, visual quality, factual claims, accessibility, and platform synthetic-media disclosure requirements.
5. The publishing connector handles posting separately. Generating a clip never enables publishing by itself.

## Endpoint and self-hosting

Set NVIDIA_COSMOS_ENDPOINT to override the default hosted URL. A directly self-hosted NIM may use POST /v1/infer and may require a different request contract; verify it against the exact deployed NIM version before using this client. Do not point the client at an unknown endpoint or forward API keys to result-download URLs.

## Troubleshooting

- **401/403:** verify key, account entitlement, endpoint access, and current trial terms.
- **429:** quota/rate limit; wait or check account limits. Do not hammer retries.
- **422:** inspect the error message, mode, resolution, frame count, and safety refusal details.
- **Timeout:** the request may still have completed. Check provider history/status before retrying to avoid duplicate usage.
- **No b64_video:** save the sanitized error details and compare the response schema with the current official model card.
