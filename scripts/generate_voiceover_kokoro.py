#!/usr/bin/env python3
"""Optional local Kokoro text-to-speech voiceover generator."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description="Generate a voiceover WAV with Kokoro TTS.")
    p.add_argument("--text",required=True); p.add_argument("--output",required=True)
    p.add_argument("--lang",default="a"); p.add_argument("--voice",default="af_heart")
    a=p.parse_args()
    try:
        import soundfile as sf
        import numpy as np
        from kokoro import KPipeline
    except ImportError:
        print("ERROR: Install requirements-kokoro.txt first.",file=sys.stderr); return 2
    try:
        pipeline=KPipeline(lang_code=a.lang)
        chunks=[np.asarray(audio).reshape(-1) for _,_,audio in pipeline(a.text,voice=a.voice) if audio is not None]
        if not chunks: print("ERROR: No audio returned; check language and voice IDs.",file=sys.stderr); return 1
        out=Path(a.output).expanduser(); out.parent.mkdir(parents=True,exist_ok=True)
        sf.write(str(out),np.concatenate(chunks),24000)
        print(f"Voiceover generated: {out.resolve()}"); print("Review pronunciation and license before publishing."); return 0
    except Exception as e:
        print(f"ERROR: TTS failed: {e}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
