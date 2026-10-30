#!/usr/bin/env python3
"""Fetch upstream Windows x64 binaries; works on Linux and Windows."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
YTDLP_URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe'
FFMPEG_URL = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'


def download(url: str, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size:
        return target
    temp = target.with_name(target.name + '.part')
    print(f'Download: {url}', flush=True)
    request = urllib.request.Request(url, headers={'User-Agent': 'CNVideoDownloader-build/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temp.open('wb') as output:
            shutil.copyfileobj(response, output)
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)
    return target


def fetch(runtime: Path):
    cache = ROOT / '.cache'
    binary = download(YTDLP_URL, cache / 'yt-dlp.exe')
    if binary.read_bytes()[:2] != b'MZ':
        raise ValueError('yt-dlp.exe is not a Windows executable')
    runtime.mkdir(parents=True, exist_ok=True)
    shutil.copy2(binary, runtime / 'yt-dlp.exe')
    archive = download(FFMPEG_URL, cache / 'ffmpeg-essentials.zip')
    with zipfile.ZipFile(archive) as source:
        for filename in ('ffmpeg.exe', 'ffprobe.exe'):
            member = next(n for n in source.namelist() if n.endswith('/bin/' + filename))
            with source.open(member) as inp, (runtime / filename).open('wb') as out:
                shutil.copyfileobj(inp, out)
        licenses = [n for n in source.namelist() if Path(n).name.lower().startswith(('license', 'readme'))]
        for member in licenses:
            (runtime / ('ffmpeg-' + Path(member).name)).write_bytes(source.read(member))
    manifest = {'sources': {'yt-dlp.exe': YTDLP_URL, 'ffmpeg': FFMPEG_URL},
                'sha256': {p.name: hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
                           for p in runtime.glob('*.exe')}}
    (runtime / 'binaries.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=ROOT / 'runtime')
    fetch(parser.parse_args().runtime)
