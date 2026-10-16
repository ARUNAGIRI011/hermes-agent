---
name: audio-generator
description: Generate local narration with Kokoro text-to-speech and combine narration, licensed music, subtitles, and generated footage with FFmpeg.
---

# Audio Generator and FFmpeg Finishing

## Purpose
Use the optional local Kokoro TTS script for speech synthesis and FFmpeg for video finishing. This can run locally after weights are cached, subject to compute and licensing constraints.

## Workflow
1. Get the approved script from content-creator and check names, numbers, claims, language, and pronunciation.
2. Generate a WAV using scripts/generate_voiceover_kokoro.py. The default voice and language are for American English; select a compatible voice and language code supported by the installed Kokoro version. Do not claim Tamil support unless a compatible voice is verified.
3. Use FFmpeg via scripts/ffmpeg_video_pipeline.py to format video, mix narration and optional licensed music, burn SRT subtitles, normalize audio, and export MP4.
4. Inspect audio/video sync, clipped words, subtitle timing, aspect ratio, loudness, and licensing.
5. Keep generated media outside Git. Publishing is separate and requires configured platform connectors.

## Limits and safety
- Open weights do not mean zero resource cost: first use downloads model assets and generation consumes CPU/GPU and disk.
- Kokoro may require network access for initial assets and phonemization dependencies; local inference can run offline only after assets are cached.
- Use only audio/music assets with appropriate rights. Do not clone a real person's voice without authorization.
- No unlimited compute is implied. Kaggle/Colab have quotas and session limits.
- Never upload API keys or private assets to public notebooks.
