---
name: video-generator
description: Generate short video clips and Shorts/Reels source footage using NVIDIA Cosmos 3 Nano through the official NVIDIA hosted API or a configured self-hosted NIM endpoint. Use when the user asks to create video clips from text or animate a still image.
---

# Video Generator — NVIDIA Cosmos 3

## Purpose
Use the optional scripts/nvidia_cosmos_video.py client to generate a source MP4 from a text prompt or a still image. This skill is an asset-generation stage; it does not edit a finished social video, create voiceover/music/captions automatically, or publish to platforms.

## Provider and setup
- Hosted default: NVIDIA API Catalog Cosmos3 Nano endpoint https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano.
- Configure NVIDIA_API_KEY in the local environment or secret manager. Never request, print, commit, or include it in prompts/logs.
- Optional self-hosted endpoint: set NVIDIA_COSMOS_ENDPOINT to a trusted deployment URL. Self-hosted NIM may use a different API route/contract; verify it against that deployment's docs.
- Hosted trial availability, request limits, quotas, eligibility and commercial-use terms can change. Do not promise unlimited or permanently free generation. Check current NVIDIA API Catalog terms and account quota.
- Cosmos3 Nano is primarily a Physical AI/world-generation model; results may be best suited to industrial, robotics, autonomous-driving and simulation concepts. Test suitability for general lifestyle/brand footage before building a campaign around it.

## Workflow
1. Receive a content brief and scene concept from content-creator. Create one self-contained scene prompt describing subject, action, setting, camera, lighting, visual style, and motion. Avoid text overlays/logos inside the generated video; add legible text later in an editor.
2. For YouTube Shorts/Reels, use a vertical resolution such as 480_9_16 if supported by the chosen endpoint. Use short, low-cost tests first; 25 frames is the minimum supported for the documented 480 tier. Choose frame count and FPS explicitly.
3. Generate from text, or use image-to-video only when the user has rights to the supplied image.
4. Validate API response, decode b64_video, save the MP4 to an output folder outside Git, and report the exact path and settings. Never claim to have generated a file if the API call failed.
5. Review clip quality for subject consistency, motion artifacts, brand safety, licensing, and suitability. Mark generated footage as AI-generated when required by platform policy or law.
6. Hand the resulting local media path to a video editor/creative tool for voiceover, music, captions, logo, transitions, CTA, crop, and final export. If no editor is connected, return the raw clip and an editing plan.

## Automation guardrails
- Generate only after an explicit content request or an enabled campaign job. Never generate paid volumes without checking available quota.
- Limit concurrent jobs and use long request timeouts. If a request times out after submission, its outcome may be unknown; inspect the provider response/history before retrying to avoid duplicate usage.
- Do not retry permanent API errors or safety refusals automatically.
- Keep source images and outputs private until the user chooses to publish them.
- Publishing is a separate step owned by marketing-autopublish; generated media does not authorize publication.
- Do not generate unlicensed likenesses or reuse competitor creative. Respect platform synthetic-media disclosure requirements.
