#!/usr/bin/env python3
"""FFmpeg finishing pipeline for generated social videos."""
from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path

def run(cmd):
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        print(result.stderr[-5000:], file=sys.stderr)
        raise RuntimeError(f"FFmpeg command failed with exit code {result.returncode}")

def main():
    p=argparse.ArgumentParser(description="Finish generated clips with FFmpeg.")
    p.add_argument("--input",required=True); p.add_argument("--output",required=True)
    p.add_argument("--voiceover"); p.add_argument("--music"); p.add_argument("--subtitles")
    p.add_argument("--aspect",choices=("9:16","16:9","1:1","keep"),default="9:16")
    p.add_argument("--width",type=int); p.add_argument("--height",type=int)
    p.add_argument("--fps",type=int,default=30); p.add_argument("--music-volume",type=float,default=0.12)
    p.add_argument("--crf",type=int,default=20); p.add_argument("--preset",choices=("ultrafast","superfast","veryfast","faster","fast","medium","slow"),default="medium")
    a=p.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("ERROR: ffmpeg and ffprobe must be on PATH.",file=sys.stderr); return 2
    src=Path(a.input).expanduser(); out=Path(a.output).expanduser()
    if not src.is_file(): print(f"ERROR: Source video not found: {src}",file=sys.stderr); return 2
    for item in (a.voiceover,a.music,a.subtitles):
        if item and not Path(item).expanduser().is_file():
            print(f"ERROR: Input file not found: {item}",file=sys.stderr); return 2
    if not 0 <= a.music_volume <= 1: print("ERROR: music volume must be 0..1",file=sys.stderr); return 2
    sizes={"9:16":(1080,1920),"16:9":(1920,1080),"1:1":(1080,1080)}
    if a.aspect=="keep":
        w,h=a.width or 1080,a.height or 1920
        vf=f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={a.fps}"
    else:
        dw,dh=sizes[a.aspect]; w,h=a.width or dw,a.height or dh
        vf=f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={a.fps}"
    out.parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-y","-i",str(src)]
    if a.voiceover: cmd += ["-i",str(Path(a.voiceover).expanduser())]
    if a.music: cmd += ["-i",str(Path(a.music).expanduser())]
    filters=[]; amap=None
    if a.voiceover and a.music:
        filters += ["[1:a]aresample=48000,volume=1.0[voice]",f"[2:a]aresample=48000,volume={a.music_volume}[music]","[voice][music]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-16:TP=-1.5:LRA=11[aout]"]; amap="[aout]"
    elif a.voiceover:
        filters += ["[1:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11[aout]"]; amap="[aout]"
    elif a.music:
        filters += [f"[1:a]aresample=48000,volume={a.music_volume},loudnorm=I=-18:TP=-1.5:LRA=11[aout]"]; amap="[aout]"
    if a.subtitles:
        sp=str(Path(a.subtitles).expanduser().resolve()).replace("\\","\\\\").replace(":","\\:").replace("'","\\'")
        vf += f",subtitles='{sp}'"
    if filters: cmd += ["-filter_complex",";".join(filters)]
    cmd += ["-vf",vf,"-map","0:v:0"]
    if amap: cmd += ["-map",amap]
    elif not a.voiceover and not a.music: cmd += ["-map","0:a:0?"]
    cmd += ["-c:v","libx264","-preset",a.preset,"-crf",str(a.crf),"-pix_fmt","yuv420p","-movflags","+faststart","-c:a","aac","-b:a","192k","-shortest",str(out)]
    try:
        run(cmd)
        probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration,size","-of","default=noprint_wrappers=1",str(out)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        print("Video finishing succeeded."); print(f"Output: {out.resolve()}"); print(probe.stdout.strip()); return 0
    except (RuntimeError,subprocess.CalledProcessError) as e:
        print(f"ERROR: {e}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
