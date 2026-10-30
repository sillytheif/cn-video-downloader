from pathlib import Path
from app import downloader

def test_args(monkeypatch, tmp_path):
    monkeypatch.setattr(downloader, 'downloader_command', lambda: ['yt-dlp.exe'])
    monkeypatch.setattr(downloader, 'runtime_dir', lambda: tmp_path)
    (tmp_path / 'ffmpeg').touch()
    (tmp_path / 'ffmpeg.exe').touch()
    args = downloader.build_args('https://a.cn/?a=1&b=2', Path('视频 空格'))
    assert args[-2:] == ['--', 'https://a.cn/?a=1&b=2']
    assert args[args.index('-o')+1] == str(Path('视频 空格') / '%(title).80B [%(id)s].%(ext)s')
    assert '--ffmpeg-location' in args
    assert '--ignore-config' in args
    assert '--no-playlist' in args
