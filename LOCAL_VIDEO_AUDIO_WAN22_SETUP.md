# Local Wan 2.2 + FFmpeg + voiceover options

This adds two paths: NVIDIA Cosmos3 Nano hosted API (if your account has quota) and Wan 2.2 open weights on a GPU notebook or your own GPU, plus local Kokoro TTS and FFmpeg.

## Important: "unlimited free" is not realistic on hosted GPUs

Kaggle GPU access is free within its current quotas and session limits, not an always-on server. See [Kaggle Notebooks docs](https://www.kaggle.com/docs/notebooks) and [efficient GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage). Kaggle announced P100 retirement for September 15, 2026, with T4x2 remaining as an option: [Kaggle announcement](https://www.kaggle.com/product-announcements/735239).

Wan 2.2 TI2V-5B officially supports 720p text/image-to-video but documents at least 24 GB VRAM for single-GPU inference. Kaggle T4x2 has two separate 16 GB GPUs; VRAM is not automatically pooled, so it may run out of memory. A compatible 24 GB+ single GPU is safer. See [official Wan 2.2 repo](https://github.com/Wan-Video/Wan2.2).

## FFmpeg post-processing

Install FFmpeg:
- Windows: install an FFmpeg build and add its bin directory to PATH.
- Ubuntu/Kaggle: sudo apt-get update && sudo apt-get install -y ffmpeg
- macOS: brew install ffmpeg

Example:
    python scripts/ffmpeg_video_pipeline.py --input generated-videos/source.mp4 --voiceover generated-videos/narration.wav --music assets/licensed-music.mp3 --subtitles assets/captions.srt --aspect 9:16 --output generated-videos/final-short.mp4

Omit music or subtitles if not needed. The script preserves source audio when no extra audio inputs are supplied.

## Local voiceover with Kokoro

Install:
    python -m pip install -r requirements-kokoro.txt

Generate an English voiceover (verify voice/language IDs for your selected Kokoro version):
    python scripts/generate_voiceover_kokoro.py --text "Welcome to BizMate AI. Create and organize your business content faster." --output generated-videos/narration.wav --lang a --voice af_heart

Kokoro is local text-to-speech, not music generation. Voice/language coverage varies. First use downloads model assets and requires disk and compute. Review model license and pronunciation before commercial publishing.

## Kaggle Wan 2.2 notebook

Import notebooks/wan22_kaggle_starter.ipynb into Kaggle, select a GPU accelerator, enable Internet for initial repository/model downloads, and run cells in order. The notebook downloads Wan 2.2 TI2V-5B and FFmpeg. If runtime VRAM is insufficient, use a compatible GPU or lower-memory implementation; do not assume T4x2 VRAM is pooled.

The notebook uses upstream code and weights. Check upstream licenses and Kaggle terms before commercial use. Kaggle sessions are temporary; download outputs before session ends. Do not commit API keys, Hugging Face tokens, private footage, or secrets to the notebook.

## Hermes routing

- Prompt/script: content-creator
- Hosted short clip: video-generator + NVIDIA Cosmos3 Nano, if available
- Local video: Wan 2.2 notebook or owned compatible GPU
- Narration: audio-generator + Kokoro
- Formatting, captions and audio mixing: FFmpeg
- Posting: marketing-autopublish after platform authorization and campaign enablement

The local Wan path is not a persistent always-on API server. Kaggle is an interactive batch runner, not a dependable always-on Hermes backend. For automated jobs, run a worker on a machine you control or deploy a secured, authenticated queue-backed service on compute you are authorized to use.
